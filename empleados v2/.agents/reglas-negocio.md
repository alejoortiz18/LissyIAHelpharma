# Reglas de Negocio del Proyecto — GestionPersonal

> **Stack:** C# ASP.NET Core MVC (.NET 10)  
> **Última actualización:** Abril 2026  
> **Dominio de pruebas:** `@yopmail.com` — **regla obligatoria para todos los entornos de prueba**

---

## 1. Comportamiento del Agente ante Ambigüedades

El agente **nunca debe suponer**. Si existe cualquier duda sobre:

- Qué tabla/campo aplicar un cambio
- Qué flujo de negocio sigue una operación
- Qué datos usar para una prueba
- Qué comportamiento espera el usuario en la UI

→ **El agente debe preguntar al usuario antes de proceder.**

---

## 2. Contraseña Genérica de la Plataforma

| Parámetro        | Valor       |
|------------------|-------------|
| Contraseña       | `Usuario1`  |
| Algoritmo        | PBKDF2 / SHA-256 |
| PasswordHash     | `VARBINARY(32)` — 32 bytes |
| PasswordSalt     | `VARBINARY(16)` — 16 bytes |

**Hash precalculado para `Usuario1`:**

```sql
DECLARE @PwdHash VARBINARY(32) = 0x7DED37B4612147C18EBDFA1F6DEB4709EC9D511DA20641214F1F97612DF2CEAE;
DECLARE @PwdSalt VARBINARY(16) = 0xF2B483C7DAC61EC2CA7F1331C95D6800;
```

Esta contraseña aplica a **todos los usuarios** creados para pruebas y para el seeding inicial.

---

## 3. Datos de Prueba — Archivo de Referencia

### Fuente principal

El archivo de referencia para todos los datos de prueba es:

```
Documentos/BD/Seeding_Completo.sql
```

### Reglas de uso

1. **Siempre usar `Seeding_Completo.sql` como primera fuente** de datos al ejecutar pruebas o validaciones.
2. **Solo si es estrictamente necesario** (datos no cubiertos por el seeding), se puede hacer `SELECT` directo a las tablas para conocer el estado actual de la base de datos.
3. Si los `SELECT` revelan datos diferentes al seeding, **el agente debe actualizar `Seeding_Completo.sql`** para mantenerlo sincronizado.
4. El archivo de seeding es la **fuente de verdad** para el estado esperado de los datos.

### Estructura del seeding (resumen)

| # | Sección                  | Registros |
|---|--------------------------|-----------|
| 1 | Sedes                    | 2         |
| 2 | Cargos                   | 8         |
| 3 | Empresas Temporales      | 3         |
| 4 | Plantillas de Turno      | 3         |
| 5 | Usuarios                 | 13 activos + 3 inactivos |
| 6 | Empleados                | 13 activos + 3 inactivos |
| 7 | Contactos de Emergencia  | 12        |
| 8 | Historial Desvinculaciones | 3       |
| 9 | Asignaciones de Turno    | con historial de cambios |
| 10| Eventos Laborales        | todos los tipos/estados  |
| 11| Horas Extras             | todos los estados        |
| 12| Tokens de Recuperación   | 3 casos  |

### Correos de prueba (dominio `@yopmail.com`)

| Usuario               | Correo                            | Rol             |
|-----------------------|-----------------------------------|-----------------|
| Carlos Rodríguez      | carlos.rodriguez@yopmail.com      | Jefe            |
| Laura Sánchez         | laura.sanchez@yopmail.com         | Regente         |
| Hernán Castillo       | hernan.castillo@yopmail.com       | Regente         |
| Andrés Torres         | andres.torres@yopmail.com         | AuxiliarRegente |
| Diana Vargas          | diana.vargas@yopmail.com          | Operario        |
| Jorge Herrera         | jorge.herrera@yopmail.com         | Operario        |
| Natalia Bermúdez      | natalia.bermudez@yopmail.com      | Operario        |
| Paula Quintero        | paula.quintero@yopmail.com        | Operario        |
| Camila Ríos           | camila.rios@yopmail.com           | Operario        |
| Valentina Ospina      | valentina.ospina@yopmail.com      | Operario (Inactivo) |
| Sebastián Moreno      | sebastian.moreno@yopmail.com      | Operario (Inactivo) |
| Ricardo Useche        | ricardo.useche@yopmail.com        | Operario (Inactivo) |

---

## 4. Dominio de Correo para Pruebas — `@yopmail.com`

### Regla

**Todos los correos electrónicos usados en pruebas deben usar el dominio `@yopmail.com`**, sin excepción.  
Esto incluye usuarios nuevos, seeding, pruebas de login, pruebas de reseteo de contraseña y cualquier flujo que involucre correo electrónico.

### Por qué `@yopmail.com`

- Es un servicio de correo temporal público, **sin registro requerido**.
- Permite recibir y leer correos en tiempo real en [https://yopmail.com](https://yopmail.com).
- Es ideal para probar flujos de **reseteo de contraseña** y **notificaciones por email** sin necesidad de cuentas reales.
- Cualquier dirección `cualquier.cosa@yopmail.com` es válida y su bandeja de entrada es accesible de inmediato.

### Cómo verificar un correo de prueba

1. Abrir [https://yopmail.com](https://yopmail.com)
2. Ingresar el nombre de usuario (ej. `carlos.rodriguez`) en el campo de búsqueda
3. La bandeja de entrada se muestra automáticamente

### Formato obligatorio para correos de prueba

```
{nombre}.{apellido}@yopmail.com
```

Ejemplos:
- `carlos.rodriguez@yopmail.com`
- `laura.sanchez@yopmail.com`
- `nuevo.empleado@yopmail.com`

### Flujo de reseteo de contraseña (prueba completa)

| Paso | Acción | Verificación |
|------|--------|--------------|
| 1 | Solicitar reseteo con el correo del usuario | El sistema envía el token al correo `@yopmail.com` |
| 2 | Abrir yopmail.com con ese correo | Se recibe el email con el enlace/token |
| 3 | Usar el enlace para cambiar la contraseña | El token se marca como usado en `TokensRecuperacion` |
| 4 | Intentar login con la nueva contraseña | Login exitoso |
| 5 | Intentar usar el mismo token nuevamente | El sistema rechaza el token (ya expirado/usado) |

---

## 5. Validaciones y Pruebas

### Principios

- Las pruebas deben ejecutarse de forma **profesional**, con casos positivos y negativos.
- Antes de ejecutar pruebas, el agente debe **cargar los skills disponibles** relevantes a la tarea.
- Si una validación requiere un skill no instalado, el agente debe:
  1. Identificar el skill faltante.
  2. Buscarlo en [https://skills.sh/](https://skills.sh/).
  3. **Proponer al usuario instalarlo** antes de continuar (nunca instalarlo sin confirmación).

### Skills aplicables a este proyecto

| Skill                        | Cuándo usarlo |
|------------------------------|---------------|
| `dotnet-layered-architecture` | Al crear/modificar Controllers, Services, Repositories, Helpers, Mappers, Constants, Cookies de sesión |
| `efcore-best-practices`       | Al configurar DbContext, escribir queries LINQ, crear migraciones, manejar relaciones y transacciones |
| `sqlserver-conventions`       | Al diseñar tablas, queries SQL, índices, revisar el esquema |
| `sqlserver-stored-procedures` | Al crear/modificar/revisar Stored Procedures |
| `web-design-guidelines`       | Al revisar UI, accesibilidad, UX o código de vistas |
| `requesting-code-review`      | Al completar implementaciones importantes o antes de hacer merge |

---

## 6. Stack Tecnológico

- **Lenguaje:** C#
- **Framework:** ASP.NET Core MVC — .NET 10
- **ORM:** Entity Framework Core
- **Base de datos:** SQL Server / LocalDB
- **Arquitectura:** Capas (Web / Application / Domain / Infrastructure / Models / Helpers / Constants)
- **Pruebas:** pytest (Tests/) para pruebas de integración/e2e del sistema

---

## 7. Jerarquía de Roles del Sistema

```
Jefe
 ├── Regente (puede haber uno por sede)
 │    ├── AuxiliarRegente
 │    └── Operario
```

| Rol              | Acceso                                   |
|------------------|------------------------------------------|
| Jefe             | Acceso total a todas las sedes           |
| Regente          | Gestión de su sede y subordinados        |
| AuxiliarRegente  | Apoyo operativo al Regente               |
| Operario         | Solo visualización de su propia info     |

---

## 8. Convenciones Generales

- Todos los campos de estado usan valores en español: `Activo/Inactivo`, `Activa/Inactiva`, `Finalizado`, `Anulado`.
- Las fechas se almacenan en formato `YYYY-MM-DD`.
- Los correos de prueba **siempre** usan el dominio `@yopmail.com`. Nunca usar correos reales ni de otros dominios en pruebas.
- Al crear un usuario de prueba nuevo, el correo sigue el patrón `{nombre}.{apellido}@yopmail.com`.
- El campo `DebeCambiarPassword` se inicializa en `1` para todos los usuarios nuevos, excepto el Jefe.
- Los empleados desvinculados conservan su historial completo (contactos, eventos, turnos).
