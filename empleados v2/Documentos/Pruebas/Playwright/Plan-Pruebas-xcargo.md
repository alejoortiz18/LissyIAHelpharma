# Pitch — Pruebas de Visibilidad de Empleados por Cargo (Regente)
## Sistema de Administración de Empleados — GestionPersonal

> **Metodología:** Shape Up (Basecamp)
> **Stack:** C# ASP.NET Core MVC / .NET 10
> **Última actualización:** Abril 2026

---

## Problema

Un usuario con cargo **Farmacéutico Regente** (`cargoId = 2`) gestiona únicamente al personal que tiene asignado bajo su jefatura. Sin pruebas automatizadas que validen este aislamiento, cualquier cambio en la lógica del `EmpleadoController` o en los filtros del servicio podría exponer, sin saberlo, el listado completo de la empresa a un Regente — incluyendo empleados que dependen de otro Regente o incluso el propio Jefe.

**El riesgo sin pruebas:**

- Un Regente de Medellín podría ver empleados de Bogotá.
- El Jefe de sede (que está jerárquicamente por encima del Regente) podría aparecer en su listado.
- Un cambio de filtro en el servicio rompería el aislamiento sin que nadie lo note.

---

## Appetite

**Ciclo corto — 1 día de trabajo.**

El objetivo es validar que el filtro `JefeInmediatoId` funciona correctamente para el rol `Regente` en la vista `/Empleado`. No se prueba ningún otro módulo en este ciclo.

---

## Contexto técnico

### Corrección aplicada (previa a este plan)

El código original filtraba la vista de empleados únicamente por `SedeId`, lo que causaba que el Regente viera a todos los empleados de su sede — incluyendo al Jefe de sede y a empleados de otros Regentes si existieran en la misma sede.

**Corrección aplicada** en `EmpleadoController.cs`:

```csharp
// Regente / AuxiliarRegente: solo ve a sí mismo + sus subordinados directos
if (rol == RolUsuario.Regente || rol == RolUsuario.AuxiliarRegente)
{
    var miEmpleadoId = SesionHelper.GetEmpleadoId(User);
    if (miEmpleadoId.HasValue)
        query = query.Where(e => e.Id == miEmpleadoId.Value || e.JefeInmediatoId == miEmpleadoId.Value);
}
```

También se agregó `JefeInmediatoId` al `EmpleadoListaDto` y su mapeo en `EmpleadoService.MapToListaDto`.

---

## Solución

### Ambiente y herramientas

| Elemento | Valor |
|---|---|
| **Herramienta** | Python + Playwright (pytest-playwright) |
| **Navegador** | Chromium headless |
| **Ambiente** | Desarrollo local — `http://localhost:5002` |
| **BD** | `GestionPersonal` en `(localdb)\MSSQLLocalDB` |
| **Seeding** | `Documentos/BD/Seeding_Completo.sql` |

### Prerequisitos de entorno

**1. Levantar la aplicación** (terminal separada, dejarla corriendo)
```powershell
cd "c:\Users\alejandro.ortiz\Documents\helpharma\Desarrollos\lissy\IA\LissyIAHelpharma\empleados v2\Proyecto MVC"
dotnet run --project GestionPersonal.Web/GestionPersonal.Web.csproj --launch-profile http
```
Esperar: `Now listening on: http://localhost:5002`

**2. Verificar seeding aplicado**

Antes de correr las pruebas confirmar que el seeding está actualizado:
```sql
-- Verificar empleados bajo Laura Sánchez (EmpleadoId = 2)
SELECT Id, NombreCompleto, Estado, JefeInmediatoId
FROM dbo.Empleados
WHERE JefeInmediatoId = 2 OR Id = 2
ORDER BY Id;
```

Resultado esperado (7 filas):

| Id | NombreCompleto | Estado | JefeInmediatoId |
|---|---|---|---|
| 2 | Laura Patricia Sánchez Gómez | Activo | 1 (Carlos) |
| 4 | Andrés Felipe Torres Ruiz | Activo | 2 |
| 5 | Diana Marcela Vargas López | Activo | 2 |
| 6 | Jorge Armando Herrera Quintana | Activo | 2 |
| 10 | Valentina Ospina Restrepo | Inactivo | 2 |
| 12 | Ricardo Enrique Useche Paredes | Inactivo | 2 |

> Los Ids son los generados por el seeding en orden de inserción (IDENTITY con RESEED a 0).

---

### Datos de prueba

| Campo | Valor |
|---|---|
| **Usuario de prueba** | Laura Patricia Sánchez Gómez |
| **Correo** | `laura.sanchez@yopmail.com` |
| **Contraseña** | `Usuario1` |
| **Rol** | `Regente` |
| **CargoId** | `2` (Farmacéutico Regente) |
| **EmpleadoId** | `2` |
| **SedeId** | `1` (Sede Medellín) |
| **DebeCambiarPassword** | `1` → requiere cambio al primer ingreso |

> Nota: Al primer login Laura es redirigida a `/Cuenta/CambiarPassword`. Para los tests se usa una fixture que completa ese flujo o se resetea el seeding entre ejecuciones para controlar este estado.

---

### Empleados visibles esperados para Laura (Regente)

La vista `/Empleado` debe mostrar **únicamente** los siguientes empleados, tanto activos como inactivos:

| EmpleadoId | Nombre | Estado | Relación |
|---|---|---|---|
| **2** | Laura Patricia Sánchez Gómez | Activo | Ella misma |
| **4** | Andrés Felipe Torres Ruiz | Activo | JefeInmediato = 2 |
| **5** | Diana Marcela Vargas López | Activo | JefeInmediato = 2 |
| **6** | Jorge Armando Herrera Quintana | Activo | JefeInmediato = 2 |
| **10** | Valentina Ospina Restrepo | Inactivo | JefeInmediato = 2 |
| **12** | Ricardo Enrique Useche Paredes | Inactivo | JefeInmediato = 2 |

### Empleados que NO deben ser visibles para Laura

| EmpleadoId | Nombre | Motivo de exclusión |
|---|---|---|
| 1 | Carlos Alberto Rodríguez Mora | Jefe por encima de Laura |
| 3 | Hernán David Castillo Mejía | Regente de otra sede |
| 7 | Natalia Bermúdez Salazar | Subordinado de Hernán |
| 8 | Paula Andrea Quintero Ríos | Subordinado de Hernán |
| 9 | Camila Andrea Ríos Vargas | Subordinado de Hernán |
| 11 | Sebastián Andrés Moreno Parra | Subordinado de Hernán (inactivo) |

---

### Scopes de prueba

#### Scope 1 — Visibilidad de empleados activos

Valida que la tabla de empleados muestra únicamente los empleados activos bajo la jefatura de Laura.

| ID | Caso | Acción | Resultado esperado |
|---|---|---|---|
| TC-XC-01 | Login como Regente y navegar a Empleados | Login `laura.sanchez@yopmail.com` / `Usuario1` → navegar a `/Empleado` | Tabla visible con solo empleados activos de Laura: Andrés Torres, Diana Vargas, Jorge Herrera (3 activos excluyendo a Laura misma que también aparece) |
| TC-XC-02 | Contar total de empleados activos en la tabla | Revisar el contador de registros en la página | Total = 4 empleados activos (Laura + 3 subordinados activos) |
| TC-XC-03 | Verificar que Carlos Rodríguez NO aparece | Buscar `Carlos` en el filtro de búsqueda | 0 resultados — el Jefe no es visible para el Regente |
| TC-XC-04 | Verificar que Hernán Castillo NO aparece | Buscar `Hernán` en el filtro de búsqueda | 0 resultados — otro Regente no es visible |
| TC-XC-05 | Verificar que Natalia Bermúdez NO aparece | Buscar `Natalia` en el filtro de búsqueda | 0 resultados — empleado de otro Regente no es visible |

**Definición de "done":** Los 5 casos pasan en verde y se confirma el aislamiento en UI.

---

#### Scope 2 — Visibilidad con filtro de estado "Inactivo"

Valida que los empleados inactivos del Regente son visibles al filtrar, pero los inactivos de otros Regentes no.

| ID | Caso | Acción | Resultado esperado |
|---|---|---|---|
| TC-XC-06 | Aplicar filtro Estado = Inactivo | En `/Empleado` seleccionar `Estado = Inactivo` | Tabla muestra: Valentina Ospina y Ricardo Useche (2 empleados) |
| TC-XC-07 | Verificar que Sebastián Moreno NO aparece con filtro Inactivo | Buscar `Sebastián` con Estado = Inactivo | 0 resultados — inactivo de otro Regente no es visible |

**Definición de "done":** Los 2 casos pasan y confirman que el filtro de JefeInmediato aplica también a inactivos.

---

#### Scope 3 — Verificación en base de datos

Valida que el aislamiento coincide con lo que el seeding define en la tabla `dbo.Empleados`.

| ID | Caso | Acción | Resultado esperado |
|---|---|---|---|
| TC-XC-08 | Contar empleados con JefeInmediatoId = 2 en BD | Ejecutar query SQL (ver abajo) | 5 filas: Andrés, Diana, Jorge, Valentina, Ricardo |
| TC-XC-09 | Verificar que ningún empleado de Hernán tiene JefeInmediatoId = 2 | Query de cruce (ver abajo) | 0 filas |
| TC-XC-10 | Verificar que Carlos no tiene JefeInmediatoId = 2 | Query (ver abajo) | 0 filas — el Jefe no está bajo Laura |

**Queries de verificación:**

```sql
-- TC-XC-08: subordinados directos de Laura
SELECT Id, NombreCompleto, Estado
FROM dbo.Empleados
WHERE JefeInmediatoId = 2
ORDER BY Id;
-- Esperado: 5 filas

-- TC-XC-09: empleados de Bogotá que incorrectamente tendrían JefeInmediatoId = 2
SELECT Id, NombreCompleto
FROM dbo.Empleados
WHERE JefeInmediatoId = 2
  AND SedeId = (SELECT Id FROM dbo.Sedes WHERE Nombre = N'Sede Bogotá');
-- Esperado: 0 filas

-- TC-XC-10: Carlos no está bajo Laura
SELECT Id, NombreCompleto
FROM dbo.Empleados
WHERE Id = 1 AND JefeInmediatoId = 2;
-- Esperado: 0 filas
```

**Definición de "done":** Las 3 queries devuelven los resultados esperados.

---

### Estructura de archivos de prueba

```
empleados v2/
└── Tests/
    ├── conftest.py              ← Playwright config: browser, base_url, fixtures
    ├── helpers.py               ← do_login(), do_logout(), reset_seeding()
    └── test_xcargo.py           ← Scopes 1 y 2: TC-XC-01 a TC-XC-07
```

> El Scope 3 (queries SQL) se ejecuta manualmente en SQL Server Management Studio o con un script `pyodbc` si se conecta Python a la BD.

---

### Comandos de ejecución

```powershell
# Desde la raíz del proyecto
cd "c:\Users\alejandro.ortiz\Documents\helpharma\Desarrollos\lissy\IA\LissyIAHelpharma\empleados v2"

# Correr todos los casos de este plan
.\.venv\Scripts\python.exe -m pytest Tests/test_xcargo.py -v

# Modo headed (útil para depuración visual)
.\.venv\Scripts\python.exe -m pytest Tests/test_xcargo.py -v --headed

# Screenshots solo al fallar
.\.venv\Scripts\python.exe -m pytest Tests/test_xcargo.py -v --screenshot only-on-failure --output Tests/screenshots/
```

---

### Consideración sobre primer ingreso (`DebeCambiarPassword`)

Laura tiene `DebeCambiarPassword = 1` en el seeding. Al hacer login es redirigida a `/Cuenta/CambiarPassword` antes de llegar a `/Empleado`.

**Estrategias para los tests:**

**Opción A — Fixture que completa el primer ingreso (recomendada):**
```python
# En conftest.py o helpers.py
def do_login_regente_first_time(page, nueva_password="NuevaClave2026!"):
    page.goto("http://localhost:5002/Cuenta/Login")
    page.fill("#CorreoAcceso", "laura.sanchez@yopmail.com")
    page.fill("#Password", "Usuario1")
    page.click("button[type=submit]")
    # Redirige a CambiarPassword
    page.wait_for_url("**/CambiarPassword")
    page.fill("#NuevaPassword", nueva_password)
    page.fill("#ConfirmarPassword", nueva_password)
    page.click("button[type=submit]")
    page.wait_for_url("**/Dashboard")
```

**Opción B — Resetear seeding con `DebeCambiarPassword = 0` para Laura antes de correr:**
```sql
UPDATE dbo.Usuarios
SET DebeCambiarPassword = 0
WHERE CorreoAcceso = 'laura.sanchez@yopmail.com';
```

> Para re-ejecución limpia del Scope 1 y 2, reaplicar `Documentos/BD/Seeding_Completo.sql` antes de cada corrida completa.

---

## Rabbit Holes

| Riesgo | Decisión |
|---|---|
| `DebeCambiarPassword = 1` bloquea el acceso a `/Empleado` en el primer run | Usar Opción A (fixture de primer ingreso) o resetear la BD antes del test. |
| El total de registros en la paginación muestra un conteo diferente al esperado | Verificar que `TamanioPagina = 15` cubre todos los 6 empleados en una sola página (6 < 15, no hay paginación). |
| Los IDs de empleado cambian si el seeding se reaplica con diferente orden | Los IDs son fijos porque el seeding usa `RESEED, 0` y el orden de inserción está definido. Siempre reaplicar el mismo `Seeding_Completo.sql`. |
| El filtro de búsqueda busca parcialmente y podría dar falsos negativos | Buscar el nombre completo o al menos 5 caracteres únicos. |

---

## No-gos

Lo siguiente queda **explícitamente fuera** de este ciclo:

- ❌ Pruebas del mismo aislamiento para el rol `AuxiliarRegente` (queda para un ciclo futuro)
- ❌ Validación del módulo Eventos o Horas Extras con usuario Regente
- ❌ Pruebas de rendimiento o carga
- ❌ Validar comportamiento del Jefe (ya cubierto en otros planes)
- ❌ Pruebas cross-browser (solo Chromium headless en este ciclo)
