# Pitch — Autogestión de Solicitudes para Auxiliar de Farmacia

> Formato: **Shape Up** · [basecamp.com/shapeup](https://basecamp.com/shapeup)  
> Ciclo sugerido: **Small Batch — 2 semanas**  
> Estado: **Decisiones de diseño confirmadas — listo para implementar**  
> Última revisión: 25/04/2026

---

## 1. Problema

Los roles **Operario** (Auxiliar de Farmacia, CargoId = 3) y **Direccionador** no pueden registrar ni consultar sus propias novedades laborales en el sistema.  

Hoy, si un auxiliar necesita reportar una incapacidad, solicitar vacaciones o pedir un permiso, debe acudir verbalmente a su jefe o esperar que alguien más lo registre. El sistema tiene el módulo `EventoLaboral` completamente funcional, pero ese rol está explícitamente bloqueado con `Forbid()` en el controlador actual.

**Historia concreta:** Ana, auxiliar de Sede Norte, tuvo que ausentarse por incapacidad médica. Su regente no estaba disponible ese día. El evento quedó sin registrar por 3 días, afectando el historial del empleado y la trazabilidad del área.

El sistema ya tiene todo el andamiaje; solo falta abrir la puerta correcta, con el scope adecuado.

---

## 2. Appetite

**2 semanas de trabajo** (Small Batch).

El módulo de eventos ya existe: entidad `EventoLaboral`, `IEventoLaboralService`, repositorio, DTOs y vistas de lista/modal. No hay que construir desde cero. El trabajo se limita a:

- Habilitar los roles Operario y Direccionador con scope restringido a "mis solicitudes"
- Ampliar `EstadoEvento` con los nuevos valores del ciclo de vida de solicitudes
- Ajustar la vista de lista para mostrar únicamente los registros propios
- Mostrar claramente el aprobador (campo `AutorizadoPor`) cuando el estado cambie
- Agregar entrada de menú condicionada a ambos roles

Si después de 2 semanas el trabajo no está listo, **no se extiende**: se recorta alcance hasta lo que esté terminado y se deja lo restante para el siguiente ciclo.

---

## 3. Solución

### Elementos principales

#### A · Nueva entrada de menú — "Mis Solicitudes"

La barra lateral (`_Layout.cshtml`) ya renderiza ítems de menú condicionados a rol. Se agrega un ítem visible **para `RolUsuario.Operario` y `RolUsuario.Direccionador`**:

```
Sidebar
  ├── Dashboard
  ├── Mi perfil
  └── [Operario | Direccionador] Mis solicitudes  →  /Solicitud
```

El resto del menú (Empleados, Eventos, Turnos, etc.) permanece **sin cambios**.

---

#### B · Ruta y controlador — `SolicitudController`

Controlador nuevo y ligero. **No se modifica** `EventoLaboralController`.

```
GET  /Solicitud          →  Index   (lista mis solicitudes)
POST /Solicitud/Crear    →  Crear   (registrar nueva solicitud)
```

Restricción en servidor:

```csharp
[Authorize(Roles = "Operario,Direccionador")]
public class SolicitudController : Controller
{
    // Solo lee y escribe eventos donde EmpleadoId == empId del claim
}
```

---

#### C · Pantalla "Mis Solicitudes" — lista

Reutiliza el mismo diseño de tabla del módulo `EventoLaboral` existente (mismo estándar visual: encabezados, paginación de 15 registros, buscador, formato de fechas `dd/MM/yyyy`).

Columnas:

| # | Tipo solicitud | Fecha solicitud | Fecha inicio | Fecha fin | Estado | Aprobado por | Fecha aprobación |
|---|---|---|---|---|---|---|---|
| 1 | Permiso | 25/04/2026 | 26/04/2026 | 26/04/2026 | Aprobado | María Gómez | 25/04/2026 09:35 |

La columna **"Aprobado por"** muestra `—` cuando el estado es `Pendiente`.  
No se muestran solicitudes de otros empleados; la consulta filtra por `EmpleadoId = empId` del claim.

---

#### D · Modal "Nueva Solicitud"

Reutiliza el mismo componente modal del módulo `EventoLaboral`. Campos:

| Campo | Control | Requerido |
|---|---|---|
| Tipo solicitud | `<select>` (lista de tipos existentes) | Sí |
| Fecha inicio | `<input type="date">` | Sí |
| Fecha fin | `<input type="date">` | Sí |
| Motivo | `<textarea>` | Sí |
| Observaciones | `<textarea>` | No |

`EmpleadoId` se toma del claim de sesión; el usuario **no puede seleccionarlo**.  
Estado inicial: `Pendiente` (nuevo valor en `EstadoEvento`). El campo `AutorizadoPor` (obligatorio NOT NULL en la entidad existente) se rellena automáticamente con el texto fijo `'Pendiente de aprobación'` al crearse la solicitud — el supervisor lo actualizará con su nombre al aprobar/rechazar desde `/EventoLaboral`.

---

#### E · Restricción de servicio / repositorio

`EventoLaboralService` ya existe. Se crea un método de consulta adicional:

```csharp
Task<IReadOnlyList<EventoLaboralListaDto>> ObtenerPropiosAsync(int empleadoId);
```

Este método aplica `WHERE EmpleadoId = @empleadoId`. El controller lo llama pasando el `EmpleadoId` del claim — nunca un valor enviado por el cliente.

---

### Flujo de pantallas (breadboard)

```
[Login] → [Dashboard]
                 └── (rol Operario | Direccionador) Mis solicitudes
                            ├── Lista  → "Nueva solicitud" (modal)
                            │               └── POST /Solicitud/Crear
                            │                        └── AutorizadoPor = "Pendiente de aprobación"
                            │                        └── Estado inicial = Pendiente
                            │                        └── Redirige a lista con mensaje
                            └── Fila de la lista
                                    └── Columna "Autorizado por" (solo lectura)
                                    └── Badge de estado con color por valor
```

---

## 4. Rabbit Holes

### RH-1 · El sistema usa `RolUsuario`, no `CargoId`

El requerimiento original menciona `CargoId = 3`. El sistema de permisos **no trabaja con CargoId** — trabaja con el enum `RolUsuario` que viene del claim de sesión.

**Decisión confirmada:** el módulo aplica a `RolUsuario.Operario` **y** `RolUsuario.Direccionador`. Se usa `[Authorize(Roles = "Operario,Direccionador")]`. No se agrega nuevo valor al enum ni se cambia la tabla de cargos.

> Si en el futuro se necesita distinguir "Auxiliar de Farmacia" de otros Operarios, ese cambio se shapes por separado.

---

### RH-2 · `EventoLaboralController` bloquea a Operario y Direccionador con `Forbid()`

La línea actual:
```csharp
if (rol == RolUsuario.Operario || rol == RolUsuario.Direccionador)
    return Forbid();
```
...es correcta y **no se toca**. Ambos roles acceden por la ruta `/Solicitud`, no por `/EventoLaboral`. Las rutas coexisten sin conflicto.

---

### RH-3 · `AutorizadoPor` es NOT NULL — se rellena con texto fijo al crear

La entidad `EventoLaboral.AutorizadoPor` es `string NOT NULL`. **Decisión confirmada:** al crear una solicitud desde `/Solicitud`, se guarda automáticamente el valor `'Pendiente de aprobación'`. El supervisor lo actualiza con su nombre cuando cambia el estado desde `/EventoLaboral`. El `SolicitudController` solo muestra este campo, no lo modifica. No hay que construir flujo de aprobación en este ciclo.

---

### RH-4 · Paginación y búsqueda

El componente de paginación existente requiere `TotalRegistros` y `TotalPaginas`. El `ViewModel` de la lista de solicitudes debe incluirlos desde el inicio; de lo contrario, la paginación HTML no renderiza. No es opcional, es trabajo base.

---

## 5. No-Gos

Estos elementos están **explícitamente fuera** de este ciclo:

| # | Fuera de alcance | Razón |
|---|---|---|
| 1 | Adjuntos / subida de archivos | Requiere infraestructura de almacenamiento adicional; ciclo separado |
| 2 | Flujo de aprobación dentro de `/Solicitud` | El supervisor aprueba desde `/EventoLaboral`; no duplicar UX |
| 3 | Notificaciones por correo al crear solicitud | Módulo de email tiene su propio ciclo de mejoras |
| 4 | Editar o cancelar una solicitud ya enviada | Incrementa complejidad de estados; evaluar en ciclo siguiente |
| 5 | Ver solicitudes de compañeros del mismo cargo | Viola el principio de privacidad del módulo |
| 6 | Cambiar el sistema de permisos existente | No se toca `RolUsuario`, `SesionHelper`, ni claims de sesión |
| 7 | Nuevo diseño visual o cambio de layout | Se reutilizan exactamente los mismos componentes CSS/JS del sistema |
| 8 | Reportes o exportación a Excel/PDF | Fuera de alcance para v1 |

---

## 6. Alcance técnico resumido

### Archivos nuevos

| Capa | Archivo | Descripción |
|---|---|---|
| Web | `Controllers/SolicitudController.cs` | CRUD restringido a Operario y Direccionador |
| Web | `Views/Solicitud/Index.cshtml` | Lista "Mis solicitudes" |
| Application | `Interfaces/ISolicitudService.cs` | Interfaz con `ObtenerPropiosAsync` |
| Application | `Services/SolicitudService.cs` | Delegación a `IEventoLaboralService` con filtro de empleado |

### Archivos modificados

| Archivo | Cambio |
|---|---|
| `Models/Enums/EstadoEvento.cs` | Agregar valores: `Pendiente`, `Aprobado`, `Rechazado`, `Cancelado`, `EnRevision` |
| `Views/Shared/_Layout.cshtml` | Ítem de menú condicional para `Operario` y `Direccionador` |
| `Program.cs` | Registrar `ISolicitudService` en DI |

### Tablas de BD

**Reutiliza `EventosLaborales`** existente.  
**Requiere migración:** ampliar el `CHECK CONSTRAINT` de la columna `Estado` en la tabla `EventosLaborales` para incluir los nuevos valores del enum.  
Solo se agrega un índice de cobertura si las consultas por `EmpleadoId` muestran lentitud en pruebas.

---

## 7. Criterios de done

- [ ] Operario y Direccionador pueden crear solicitud propia desde `/Solicitud`
- [ ] Cada rol ve únicamente sus propios registros (filtro por `EmpleadoId` del claim)
- [ ] Al crear, `AutorizadoPor` se guarda como `'Pendiente de aprobación'` y estado = `Pendiente`
- [ ] La columna "Autorizado por" en la lista muestra `—` cuando el valor es el texto fijo
- [ ] Otros roles no pueden acceder a `/Solicitud` (devuelve 403)
- [ ] El módulo `/EventoLaboral` sigue funcionando igual para todos los demás roles
- [ ] El enum `EstadoEvento` tiene los nuevos valores y el CHECK CONSTRAINT de BD está actualizado
- [ ] El diseño visual es indistinguible del resto del sistema (misma tabla, mismo modal, misma tipografía)
- [ ] Sin errores de compilación ni warnings de EF Core en consola

---

## 8. Decisiones tomadas

| Pregunta | Decisión confirmada |
|---|---|
| ¿Solo Operario o también Direccionador? | **Ambos**: `Operario` y `Direccionador` |
| ¿Tabla nueva o reutilizar `EventosLaborales`? | **Reutilizar** `EventosLaborales` ampliando `EstadoEvento` |
| ¿Tipos de solicitud? | **Solo los 3 existentes**: Vacaciones, Incapacidad, Permiso |
| ¿Qué va en `AutorizadoPor` al crear? | Texto fijo **`'Pendiente de aprobación'`** |
| ¿El auxiliar puede cancelar solicitudes? | **No** en este ciclo (No-Go #4) |
