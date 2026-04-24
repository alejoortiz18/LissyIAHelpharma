# Pitch — Corrección Integral de Permisos por Cargo
## Sistema de Administración de Empleados — GestionPersonal

> **Metodología:** Shape Up (Basecamp)  
> **Stack:** C# ASP.NET Core MVC / .NET 10 · Cookie Authentication · RolUsuario enum  
> **Ciclo:** Small Batch  
> **Última actualización:** Abril 2026  
> **Versión:** 2.0 — Nueva Jerarquía Organizacional

---

## 1. El Problema

Sandra acaba de ser asignada como **Analista de Servicios Farmacéuticos** — el cargo con autoridad superior dentro de la operación farmacéutica. Intenta ingresar al Dashboard para revisar los indicadores de todas las sedes, pero el sistema no muestra el menú de Dashboard para su rol. Cuando intenta registrar una novedad en un empleado de otra sede, el sistema la redirige silenciosamente. No hay error, no hay 403 — simplemente no funciona.

Al mismo tiempo, Carlos — ahora con cargo de **Director Técnico** (antes llamado "Jefe de Sede") — sigue viendo su cargo nombrado incorrectamente en reportes y pantallas. El código referencia `RolUsuario.Jefe` pero el organigrama oficial usa "Director Técnico". Los nuevos **Direccionadores** que ingresaron esta semana tienen el ítem "Empleados" visible en el menú, cuando solo deberían ver su propio perfil. Y el **Administrador de plataforma** — rol técnico que gestiona usuarios, catálogos y configuración del sistema — no tiene un usuario de prueba definido en el seeding, por lo que no puede verificarse su acceso.

Estos fallos no son defectos de diseño original: la jerarquía organizacional fue actualizada formalmente (ver `Correccion-Roles.md`) pero el sistema no fue adaptado. El resultado es una brecha entre la estructura real y los permisos que el software aplica, con tres vectores de riesgo concretos:

1. Un **Regente de Farmacia** puede ver y aprobar horas extras de empleados que no dependen de él, porque el filtro por `JefeInmediatoId` no está aplicado en `HoraExtraController`.
2. Un **Direccionador** (nuevo cargo operativo) no tiene rol mapeado en el sistema y hereda permisos incorrectos por defecto.
3. El **Analista** puede acceder al sistema pero sus permisos de acceso total multi-sede no están implementados — ni en frontend ni en backend.

---

## 2. Appetite

**Small Batch — máximo 7 días calendario.**

Ocho roles, enfoque secuencial por prioridad de riesgo y complejidad:

| Orden | Cargo / Rol | Appetite | Motivo |
|-------|-------------|----------|--------|
| 1 | CargoId 3 — Auxiliar de Farmacia | Día 1 | Solo frontend y redirección |
| 2 | CargoId 6 — Direccionador | Día 1 | Hereda lógica del Auxiliar |
| 3 | CargoId 2 — Regente de Farmacia | Días 2-3 | Backend + frontend, filtro jerárquico |
| 4 | CargoId 4 — Auxiliar Regente | Día 4 | Hereda lógica del Regente |
| 5 | CargoId 1 — Director Técnico | Día 4 | Renombrado + verificación de acceso total por sede |
| 6 | CargoId 5 — Analista de Servicios Farmacéuticos | Días 5-6 | Acceso total multi-sede, todos los módulos |
| 7 | Rol técnico — Administrador de Plataforma | Día 7 | Superusuario, seeding + verificación |

> Cada ajuste es quirúrgico: una condición `if (rol == ...)` en el controlador o un `@if (User.IsInRole(...))` en la vista. El tiempo no se gasta en redesign de arquitectura ni en sistema de permisos dinámico.

---

## 3. Mapa de Roles — Nueva Jerarquía Organizacional

La jerarquía oficial (definida en `Correccion-Roles.md`) se traduce al código mediante el enum `RolUsuario`. Esta tabla es la **fuente de verdad** para todos los filtros y condiciones del ciclo.

El **Administrador** es un rol técnico de plataforma: no pertenece al organigrama farmacéutico, no tiene `EmpleadoId` asociado y su existencia es independiente de las sedes.

```text
[Administrador de Plataforma]          ← Rol técnico, fuera del organigrama

Analista de Servicios Farmacéuticos   ← Nivel 1 — autoridad superior operativa
            │                            Acceso total a TODAS las sedes
            ▼
     Director Técnico                 ← Nivel 2 (renombrado desde "Jefe de Sede")
            │                            Acceso total por sede
 ┌──────────┼──────────────┐
 ▼          ▼              ▼
Regente  Auxiliar     Direccionador   ← Nivel 3/4
   │     de Farmacia    (nuevo)
   └── Auxiliar Regente               ← Nivel 3 (apoyo operativo)
```

| CargoId | Nombre del Cargo | RolUsuario (enum) | Nivel | Cambio |
|---------|-----------------|-------------------|-------|--------|
| — | Administrador de Plataforma | `RolUsuario.Administrador` | Técnico | Superusuario sin restricciones |
| 1 | Director Técnico | `RolUsuario.DirectorTecnico` | 2 | Renombrado desde `Jefe` |
| 2 | Regente de Farmacia | `RolUsuario.Regente` | 3 | Renombrado en negocio, mismo enum |
| 3 | Auxiliar de Farmacia | `RolUsuario.Operario` | 4 | Sin cambio |
| 4 | Auxiliar Regente | `RolUsuario.AuxiliarRegente` | 3 | Sin cambio |
| 5 | Analista de Servicios Farmacéuticos | `RolUsuario.Analista` | 1 | **Nuevo** — acceso total multi-sede |
| 6 | Direccionador | `RolUsuario.Direccionador` | 4 | **Nuevo** |

> **Migración de enum requerida:** `RolUsuario.Jefe` debe renombrarse a `RolUsuario.DirectorTecnico` en `GestionPersonal.Models.Enums`. Todos los `if (rol == RolUsuario.Jefe)` en controllers y vistas deben actualizarse. El claim `"Jefe"` en cookies activas se invalida — los usuarios afectados deben re-autenticarse.
>
> El claim `ClaimTypes.Role` en la cookie de sesión contiene el nombre del enum (ej. `"Regente"`). El `SesionHelper.GetRol(User)` lo parsea a `RolUsuario`. El `SesionHelper.GetEmpleadoId(User)` retorna el `EmpleadoId` del usuario autenticado, clave para el filtro por `JefeInmediatoId`. El Administrador **no tiene** `EmpleadoId` en sus claims.

---

## 4. Solución

### Principio de filtrado jerárquico

**Administrador y Analista** nunca pasan por ningún filtro de jerarquía ni de sede. Tienen paso libre en todos los endpoints de lectura y escritura.

```csharp
// Cortocircuito para roles sin restricción
var rol          = SesionHelper.GetRol(User);
var miEmpleadoId = SesionHelper.GetEmpleadoId(User);

if (rol == RolUsuario.Administrador || rol == RolUsuario.Analista)
    // no aplicar ningún filtro — acceso total
    goto ProceedWithoutFilter; // o simplemente no entrar en los bloques siguientes
```

El filtro central para Regente y AuxiliarRegente es:

```csharp
// Aplicar en cualquier listado
if (rol == RolUsuario.Regente || rol == RolUsuario.AuxiliarRegente)
{
    if (miEmpleadoId.HasValue)
        query = query.Where(e =>
            e.EmpleadoId == miEmpleadoId.Value ||               // recursos propios
            e.Empleado.JefeInmediatoId == miEmpleadoId.Value);  // recursos de subordinados
    else
        return Forbid(); // Regente sin EmpleadoId en claims es un error de configuración
}
```

Este patrón se replica en cada módulo con la variación correspondiente al modelo de datos.

---

### Módulo 0 — Migración de enum `RolUsuario` (prerequisito)

Antes de cualquier cambio funcional, renombrar el valor del enum y agregar los dos nuevos:

**`GestionPersonal.Models/Enums/RolUsuario.cs`:**
```csharp
public enum RolUsuario
{
    Administrador,        // Rol técnico de plataforma — superusuario sin restricciones
    DirectorTecnico,      // Renombrado desde: Jefe
    Regente,
    Operario,
    AuxiliarRegente,
    Analista,             // Nuevo — autoridad superior, acceso total multi-sede
    Direccionador         // Nuevo — operativo, solo información propia
}
```

> Buscar y reemplazar `RolUsuario.Jefe` → `RolUsuario.DirectorTecnico` en toda la solución. El claim almacenado en la cookie cambia de `"Jefe"` a `"DirectorTecnico"` — los usuarios activos deben cerrar sesión.

---

### Módulo 1 — Empleados (`EmpleadoController`)

#### Estado actual

| Acción | Administrador | Analista | Director Técnico | Regente | Aux. Farmacia | Aux. Regente | Direccionador |
|--------|:---:|:---:|:---:|:---:|:---:|:---:|:---:|
| `Index` (listado) | ✅ Todos | ⚠️ Sin filtro multi-sede | ✅ Todos | ✅ Solo subordinados | ✅ Redirige a Perfil | ✅ Solo subordinados | ⚠️ Sin filtro |
| `Nuevo` / `Crear` | ✅ | ❌ **Puede crear** | ✅ | ❌ **Puede crear** | ✅ Retorna 403 | ❌ **Puede crear** | ❌ **Puede crear** |
| `Editar` / `Actualizar` | ✅ | ❌ **Edita cualquiera** | ✅ | ❌ **Edita cualquiera** | ✅ Retorna 403 | ❌ **Edita cualquiera** | ✅ Retorna 403 |
| `Perfil` | ✅ | ✅ Cualquiera | ✅ | ✅ Solo propios/subordinados (pendiente) | ✅ Solo propio | ✅ Solo propios/subordinados (pendiente) | ✅ Solo propio |

#### Cambios requeridos (backend)

**`EmpleadoController.Nuevo` y `EmpleadoController.Crear`:**
```csharp
// Administrador y Analista tienen acceso total — no requieren verificación adicional.
// Bloquear todo rol operativo por debajo del Director Técnico:
if (rol == RolUsuario.Regente || rol == RolUsuario.AuxiliarRegente
    || rol == RolUsuario.Operario || rol == RolUsuario.Direccionador)
    return Forbid();
```

**`EmpleadoController.Editar` y `EmpleadoController.Actualizar`:**
```csharp
// Direccionador y Operario: sin acceso a edición
if (rol == RolUsuario.Operario || rol == RolUsuario.Direccionador)
    return Forbid();

// Regente/AuxiliarRegente: solo subordinados directos o sí mismo
if (rol == RolUsuario.Regente || rol == RolUsuario.AuxiliarRegente)
{
    var objetivo = await _empleadoService.ObtenerPerfilAsync(id);
    if (objetivo.Datos?.JefeInmediatoId != miEmpleadoId && objetivo.Datos?.Id != miEmpleadoId)
        return Forbid();
}
// Administrador y Analista: sin restricción adicional
```

**`EmpleadoController.Perfil`:**
```csharp
// Direccionador: solo su propio perfil
if (rol == RolUsuario.Direccionador)
{
    if (id != miEmpleadoId) return Forbid();
}

// Regente/AuxiliarRegente: solo su perfil o el de sus subordinados
if (rol == RolUsuario.Regente || rol == RolUsuario.AuxiliarRegente)
{
    var objetivo = await _empleadoService.ObtenerPerfilAsync(id);
    var esPropio      = objetivo.Datos?.Id == miEmpleadoId;
    var esSubordinado = objetivo.Datos?.JefeInmediatoId == miEmpleadoId;
    if (!esPropio && !esSubordinado)
        return Forbid();
}
// Administrador y Analista: pueden ver cualquier perfil — sin restricción
```

#### Cambios requeridos (frontend — `_Layout.cshtml`)

```html
@if (User.IsInRole("Operario") || User.IsInRole("Direccionador"))
{
  <a asp-controller="Empleado" asp-action="Perfil"
     asp-route-id="@User.FindFirstValue("EmpleadoId")"
     class="@NavClass("Empleado")">
    <span class="nav-text">Mi Perfil</span>
  </a>
}
else
{
  <a asp-controller="Empleado" asp-action="Index" class="@NavClass("Empleado")">
    <span class="nav-text">Empleados</span>
  </a>
}
```

---

### Módulo 2 — Horas Extras (`HoraExtraController`)

#### Estado actual

| Acción | Administrador | Analista | Director Técnico | Regente | Aux. Farmacia | Aux. Regente | Direccionador |
|--------|:---:|:---:|:---:|:---:|:---:|:---:|:---:|
| `Index` (listado) | ✅ Todos | ⚠️ Sin acceso multi-sede | ✅ Todos de sede | ❌ **Todos de sede** | ✅ Solo propias | ❌ **Todos de sede** | ⚠️ Sin acceso definido |
| `RegistrarAjax` | ✅ | ❌ **Para cualquier emp.** | ✅ | ❌ **Para cualquier emp.** | ✅ Solo propias | ❌ **Para cualquier emp.** | ✅ Solo propias |
| `AprobarAjax` | ✅ | ❌ **Aprueba cualquiera** | ✅ | ❌ **Aprueba cualquiera** | ❌ No puede | ❌ **Aprueba cualquiera** | ❌ |
| `RechazarAjax` | ✅ | ❌ **Rechaza cualquiera** | ✅ | ❌ **Rechaza cualquiera** | ❌ No puede | ❌ **Rechaza cualquiera** | ❌ |

#### Cambios requeridos (backend — `HoraExtraController.Index`)

```csharp
IReadOnlyList<HoraExtraDto> todos;

// Administrador y Analista: acceso total sin restricción de sede
if (rol == RolUsuario.Administrador || rol == RolUsuario.Analista)
    todos = await _horaExtraService.ObtenerTodasAsync();
else if (rol == RolUsuario.Operario && empId.HasValue)
    todos = await _horaExtraService.ObtenerPorEmpleadoAsync(empId.Value);
else if (rol == RolUsuario.Direccionador && empId.HasValue)
    todos = await _horaExtraService.ObtenerPorEmpleadoAsync(empId.Value);
else
    todos = await _horaExtraService.ObtenerPorSedeAsync(sedeId);

// Filtro jerárquico para Regente / AuxiliarRegente
if ((rol == RolUsuario.Regente || rol == RolUsuario.AuxiliarRegente) && empId.HasValue)
    todos = todos.Where(h => h.EmpleadoId == empId.Value || h.JefeInmediatoId == empId.Value).ToList();
```

> Para que `h.JefeInmediatoId` esté disponible, agregar `JefeInmediatoId` al `HoraExtraDto` y mapearlo en `HoraExtraService.MapToDto` desde `h.Empleado.JefeInmediatoId`.

#### Cambios requeridos (backend — `HoraExtraController.AprobarAjax` y `RechazarAjax`)

```csharp
// Administrador y Analista: sin restricción — pueden aprobar cualquier HE

// Direccionador: sin permiso de aprobación
if (rol == RolUsuario.Direccionador)
    return Json(new { exito = false, mensaje = "No tienes permisos para gestionar horas extras." });

// Regente/AuxiliarRegente: solo subordinados directos
if (rol == RolUsuario.Regente || rol == RolUsuario.AuxiliarRegente)
{
    var he = await _horaExtraService.ObtenerPorIdAsync(id);
    if (he?.JefeInmediatoId != empId)
        return Json(new { exito = false, mensaje = "No tienes permisos para gestionar esta hora extra." });
}
```

---

### Módulo 3 — Eventos Laborales (`EventoLaboralController`)

#### Estado actual

| Acción | Administrador | Analista | Director Técnico | Regente | Aux. Farmacia | Aux. Regente | Direccionador |
|--------|:---:|:---:|:---:|:---:|:---:|:---:|:---:|
| `Index` (listado) | ✅ Todos | ⚠️ Sin acceso multi-sede | ✅ Todos de sede | ❌ **Todos de sede** | ❌ Sin acceso | ❌ **Todos de sede** | ❌ Sin acceso |
| `RegistrarAjax` | ✅ | ❌ **Para cualquier emp.** | ✅ | ❌ **Para cualquier emp.** | ❌ | ❌ **Para cualquier emp.** | ❌ |
| `AnularAjax` | ✅ | ❌ **Anula cualquiera** | ✅ | ❌ **Anula cualquiera** | ❌ | ❌ **Anula cualquiera** | ❌ |

#### Cambios requeridos (backend — `EventoLaboralController.Index`)

```csharp
// Operario, Direccionador: sin acceso al módulo de eventos
if (rol == RolUsuario.Operario || rol == RolUsuario.Direccionador)
    return Forbid();

IReadOnlyList<EventoLaboralDto> todos;

// Administrador y Analista: acceso total sin restricción de sede
if (rol == RolUsuario.Administrador || rol == RolUsuario.Analista)
    todos = await _eventoService.ObtenerTodosAsync();
else
    todos = await _eventoService.ObtenerPorSedeAsync(sedeId);

// Filtro jerárquico para Regente / AuxiliarRegente
if ((rol == RolUsuario.Regente || rol == RolUsuario.AuxiliarRegente) && empId.HasValue)
    todos = todos.Where(e => e.EmpleadoId == empId.Value || e.JefeInmediatoId == empId.Value).ToList();
```

> Requiere agregar `JefeInmediatoId` a `EventoLaboralDto` y mapearlo en `EventoLaboralService.MapToDto`.

#### Cambios requeridos (backend — `EventoLaboralController.RegistrarAjax` y `AnularAjax`)

```csharp
// Administrador y Analista: sin restricción

// Operario, Direccionador: sin permiso de escritura sobre eventos
if (rol == RolUsuario.Operario || rol == RolUsuario.Direccionador)
    return Json(new { exito = false, mensaje = "No puedes registrar eventos laborales." });

// Regente/AuxiliarRegente: solo subordinados
if (rol == RolUsuario.Regente || rol == RolUsuario.AuxiliarRegente)
{
    var empObjetivo = await _empleadoService.ObtenerPerfilAsync(dto.EmpleadoId);
    if (empObjetivo.Datos?.JefeInmediatoId != empId && empObjetivo.Datos?.Id != empId)
        return Json(new { exito = false, mensaje = "No puedes registrar eventos para este empleado." });
}
```

---

### Módulo 4 — Turnos (`TurnoController`)

#### Estado actual

| Acción | Administrador | Analista | Director Técnico | Regente | Aux. Farmacia | Aux. Regente | Direccionador |
|--------|:---:|:---:|:---:|:---:|:---:|:---:|:---:|
| `Index` (plantillas + asignaciones) | ✅ Todos | ⚠️ Sin acceso multi-sede | ✅ Todos de sede | ❌ **Todos de sede** | ❌ Sin acceso | ❌ **Todos de sede** | ❌ Sin acceso |
| `AsignarTurnoAjax` | ✅ | ❌ **Para cualquier emp.** | ✅ | ❌ **Para cualquier emp.** | ❌ | ❌ **Para cualquier emp.** | ❌ |
| `EliminarAsignacionAjax` | ✅ | ✅ | ✅ | ✅ Solo si es programador o jefe | ✅ | ✅ Solo si es programador o jefe | ❌ |

#### Cambios requeridos (backend — `TurnoController.Index`)

```csharp
// Operario, Direccionador: sin acceso al módulo de turnos
if (rol == RolUsuario.Operario || rol == RolUsuario.Direccionador)
    return Forbid();

// Administrador y Analista: acceso total sin restricción de sede
var asignaciones = (rol == RolUsuario.Administrador || rol == RolUsuario.Analista)
    ? await _turnoService.ObtenerTodasAsignacionesAsync()
    : await _turnoService.ObtenerAsignacionesPorSedeAsync(sedeId);

// Filtro jerárquico para Regente / AuxiliarRegente
if ((rol == RolUsuario.Regente || rol == RolUsuario.AuxiliarRegente) && empId.HasValue)
    asignaciones = asignaciones
        .Where(a => a.EmpleadoId == empId.Value || a.JefeInmediatoId == empId.Value)
        .ToList();
```

> Requiere agregar `JefeInmediatoId` al `AsignacionTurnoDto` y mapearlo en `TurnoService`.

#### Cambios requeridos (backend — `TurnoController.AsignarTurnoAjax`)

```csharp
// Administrador y Analista: sin restricción

// Operario, Direccionador: sin acceso a asignación de turnos
if (rol == RolUsuario.Operario || rol == RolUsuario.Direccionador)
    return Json(new { exito = false, mensaje = "No tienes permisos para asignar turnos." });

// Regente/AuxiliarRegente: solo subordinados
if (rol == RolUsuario.Regente || rol == RolUsuario.AuxiliarRegente)
{
    var empObjetivo = await _empleadoService.ObtenerPerfilAsync(dto.EmpleadoId);
    if (empObjetivo.Datos?.JefeInmediatoId != empId && empObjetivo.Datos?.Id != empId)
        return Json(new { exito = false, mensaje = "No puedes asignar turnos a este empleado." });
}
```

---

### Módulo 5 — Dashboard (`DashboardController`)

#### Estado actual

| Rol | Dashboard backend | Menú visible |
|-----|:-----------------:|:---:|
| Director Técnico | ✅ | ✅ |
| Regente de Farmacia | ✅ Accede al endpoint | ❌ **Menú oculto** |
| Aux. Farmacia | ✅ Accede | ❌ Correcto |
| Aux. Regente | ✅ Accede al endpoint | ❌ **Menú oculto** |
| Analista | ✅ Accede | ❌ **Menú oculto** |
| Direccionador | ✅ Accede | ❌ Correcto |

#### Cambios requeridos (frontend — `_Layout.cshtml`)

```html
@if (User.IsInRole("DirectorTecnico") || User.IsInRole("Administrador")
     || User.IsInRole("Regente") || User.IsInRole("AuxiliarRegente")
     || User.IsInRole("Analista"))
{
  <a asp-controller="Dashboard" asp-action="Index" class="@NavClass("Dashboard")">
    <span class="nav-text">Dashboard</span>
  </a>
}
```

> El `DashboardController.Index` ya filtra por `SedeId`. Para el Analista, ampliar el filtro para mostrar KPIs de todas las sedes. Si el scope de esa vista multi-sede excede el appetite, el Analista accede al Dashboard de su sede asignada como primera iteración.

---

### Módulo 6 — Catálogos (`CatalogoController`, `SedeController`, `CargoController`, `EmpresaTemporalController`)

#### Estado actual

El menú ya está oculto para todos excepto Director Técnico y Administrador. El backend carece de restricción explícita.

| Rol | Acceso backend | Menú visible |
|-----|:--------------:|:---:|
| Administrador | Sin restricción | ✅ |
| Analista | Sin restricción | ❌ Oculto |
| Director Técnico | Sin restricción | ✅ |
| Regente de Farmacia | Sin restricción | ❌ Oculto |
| Aux. Farmacia | Sin restricción | ❌ Oculto |
| Aux. Regente | Sin restricción | ❌ Oculto |
| Direccionador | Sin restricción | ❌ Oculto |

#### Cambios requeridos (backend — todos los controladores de catálogo)

```csharp
// Solo Administrador y DirectorTecnico pueden acceder a catálogos.
// El Analista NO tiene acceso a catálogos en este ciclo.
var rol = SesionHelper.GetRol(User);
if (rol != RolUsuario.DirectorTecnico && rol != RolUsuario.Administrador)
    return Forbid();
```

---

## 5. Matriz de Permisos Refinada

> El **Administrador** es superusuario sin restricciones en toda la plataforma (columna omitida — siempre ✅).

| Funcionalidad | Analista | Director Técnico | Regente | Aux. Farmacia | Aux. Regente | Direccionador | Implementado |
|---------------|:---:|:---:|:---:|:---:|:---:|:---:|:---:|
| **Dashboard** | ✅ | ✅ | ✅ | ❌ | ✅ | ❌ | ⚠️ Parcial |
| **Ver listado empleados** | ✅ Todos (multi-sede) | ✅ Todos (sede) | ✅ Subordinados | ❌ Mi perfil | ✅ Subordinados | ❌ Mi perfil | ⚠️ Parcial |
| **Crear personas** | ✅ | ✅ | ❌ | ❌ | ❌ | ❌ | ❌ Gap |
| **Editar empleados** | ✅ Cualquiera | ✅ Cualquiera (sede) | ✅ Subordinados | ❌ | ✅ Subordinados | ❌ | ❌ Gap |
| **Ver perfil de empleados** | ✅ Cualquiera | ✅ | ✅ Propio+sub | ✅ Solo propio | ✅ Propio+sub | ✅ Solo propio | ❌ Gap |
| **Ver eventos laborales** | ✅ Todos (multi-sede) | ✅ Todos (sede) | ✅ Subordinados | ❌ | ✅ Subordinados | ❌ | ❌ Gap |
| **Registrar eventos** | ✅ Para cualquier emp. | ✅ | ✅ Subordinados | ❌ | ✅ Subordinados | ❌ | ❌ Gap |
| **Anular eventos** | ✅ Cualquiera | ✅ | ✅ Subordinados | ❌ | ✅ Subordinados | ❌ | ❌ Gap |
| **Ver turnos / horarios** | ✅ Todos (multi-sede) | ✅ Todos (sede) | ✅ Subordinados | ❌ | ✅ Subordinados | ❌ | ❌ Gap |
| **Asignar turnos** | ✅ Para cualquier emp. | ✅ | ✅ Subordinados | ❌ | ✅ Subordinados | ❌ | ❌ Gap |
| **Ver horas extras** | ✅ Todos (multi-sede) | ✅ Todos (sede) | ✅ Propias+sub | ✅ Solo propias | ✅ Propias+sub | ✅ Solo propias | ❌ Gap |
| **Registrar horas extras** | ✅ Para cualquier emp. | ✅ | ✅ Subordinados | ✅ Propias | ✅ Subordinados | ✅ Propias | ❌ Gap |
| **Aprobar/Rechazar HE** | ✅ Cualquiera | ✅ | ✅ Subordinados | ❌ | ✅ Subordinados | ❌ | ❌ Gap |
| **Catálogo de sistemas** | ❌ | ✅ | ❌ | ❌ | ❌ | ❌ | ⚠️ Solo frontend |

**Leyenda:** ✅ Permitido · ❌ Bloqueado · ⚠️ Parcialmente implementado · Gap = pendiente

---

## 6. Estado de Implementación

### ✅ Ya implementado y validado

- [x] `EmpleadoController.Index`: filtro `JefeInmediatoId` para Regente/AuxiliarRegente
- [x] `EmpleadoController.Index`: Operario redirigido a su propio perfil
- [x] `EmpleadoController.Nuevo` y `Crear`: Operario recibe 403
- [x] `HoraExtraController.Index`: Operario ve solo sus propias HE
- [x] `TurnoController.EliminarAsignacionAjax`: valida que solo el programador o el Director puede eliminar
- [x] Sidebar — Dashboard: oculto para Operario (correcto para ese rol)
- [x] Sidebar — Catálogos: visible solo para DirectorTecnico/Administrador
- [x] Sidebar — Eventos y Turnos: ocultos para Operario
- [x] `JefeInmediatoId` incluido en `EmpleadoListaDto` y mapeado en `EmpleadoService`

### ❌ Pendiente de implementación

**Prerequisito estructural:**
- [ ] **`RolUsuario` enum**: renombrar `Jefe` → `DirectorTecnico`, agregar `Analista` y `Direccionador`
- [ ] **Seeding**: agregar usuario de prueba para `Analista` (`analista.prueba@yopmail.com`)
- [ ] **Seeding**: agregar usuario de prueba para `Direccionador` (`direccionador.prueba@yopmail.com`)
- [ ] **Seeding**: agregar usuario de prueba para `Administrador` (`admin.prueba@yopmail.com`)

**Empleados:**
- [ ] **Crear/Nuevo**: bloquear Regente, AuxiliarRegente, Operario, Direccionador
- [ ] **Editar/Actualizar**: validar jerarquía para Regente/AuxiliarRegente; bloquear Operario/Direccionador; Analista sin restricción
- [ ] **Perfil**: validar jerarquía para Regente/AuxiliarRegente; solo propio para Direccionador; Analista sin restricción
- [ ] **Sidebar**: cambiar a "Mi Perfil" para Operario **y** Direccionador

**Horas Extras:**
- [ ] **Index**: filtro por JefeInmediato para Regente/AuxiliarRegente; solo propias para Direccionador; total multi-sede para Analista y Administrador
- [ ] **AprobarAjax/RechazarAjax**: validar jerarquía para Regente/AuxiliarRegente; bloquear Direccionador; Analista sin restricción
- [ ] **HoraExtraDto**: agregar campo `JefeInmediatoId` y mapeo en service

**Eventos Laborales:**
- [ ] **Index**: filtro jerárquico para Regente/AuxiliarRegente; total multi-sede para Analista y Administrador; bloquear Operario/Direccionador
- [ ] **RegistrarAjax**: validar subordinado para Regente/AuxiliarRegente; Analista sin restricción; bloquear Operario/Direccionador
- [ ] **AnularAjax**: misma validación
- [ ] **EventoLaboralDto**: agregar campo `JefeInmediatoId` y mapeo en service

**Turnos:**
- [ ] **Index**: filtro jerárquico para Regente/AuxiliarRegente; total multi-sede para Analista y Administrador; bloquear Operario/Direccionador
- [ ] **AsignarTurnoAjax**: validar subordinado para Regente/AuxiliarRegente; Analista sin restricción; bloquear Operario/Direccionador
- [ ] **AsignacionTurnoDto**: agregar campo `JefeInmediatoId` y mapeo en service

**Dashboard y Catálogos:**
- [ ] **Sidebar — Dashboard**: agregar visibilidad para Regente, AuxiliarRegente, Analista
- [ ] **Catálogos — Backend**: restricción explícita en todos los controllers de catálogo

---

## 7. Casos de Prueba Playwright

### Ambiente y herramientas

| Elemento | Valor |
|---|---|
| Herramienta | Python + Playwright (pytest-playwright) |
| Navegador | Chromium headless |
| URL base | `http://localhost:5002` |
| BD | `GestionPersonal` en `(localdb)\MSSQLLocalDB` |
| Seeding | `Documentos/BD/Seeding_Completo.sql` |

### Prerequisito: levantar la aplicación

```powershell
cd "c:\Users\alejandro.ortiz\Documents\helpharma\Desarrollos\lissy\IA\LissyIAHelpharma\empleados v2\Proyecto MVC"
dotnet run --project GestionPersonal.Web/GestionPersonal.Web.csproj --launch-profile http
```

### Datos de prueba (del seeding)

| EmpleadoId | Nombre | Cargo | RolUsuario | Correo | Password inicial |
|---|---|---|---|---|---|
| 1 | Carlos Alberto Rodríguez Mora | Director Técnico | DirectorTecnico | `carlos.rodriguez@yopmail.com` | `Usuario1` |
| 2 | Laura Patricia Sánchez Gómez | Regente de Farmacia | Regente | `laura.sanchez@yopmail.com` | `Usuario1` |
| 3 | Hernán David Castillo Mejía | Regente de Farmacia | Regente | `hernan.castillo@yopmail.com` | `Usuario1` |
| 4 | Andrés Felipe Torres Ruiz | Auxiliar de Farmacia | Operario | `andres.torres@yopmail.com` | `Usuario1` |
| 5 | *(definido en seeding)* | Auxiliar Regente | AuxiliarRegente | *(ver seeding)* | `Usuario1` |
| 6 | *(agregar en seeding)* | Analista de Servicios Farmacéuticos | Analista | `analista.prueba@yopmail.com` | `Usuario1` |
| 7 | *(agregar en seeding)* | Direccionador | Direccionador | `direccionador.prueba@yopmail.com` | `Usuario1` |

> **Nota:** Todos los usuarios tienen `DebeCambiarPassword = 1` en el primer login. Usar la fixture `do_login_completo(page, correo, password)` que maneja el flujo de cambio de contraseña automáticamente, o aplicar el SQL de reset antes de cada ejecución.

```sql
-- Reset DebeCambiarPassword para todos los usuarios de prueba
UPDATE dbo.Usuarios SET DebeCambiarPassword = 0
WHERE CorreoAcceso IN (
    'carlos.rodriguez@yopmail.com',
    'laura.sanchez@yopmail.com',
    'hernan.castillo@yopmail.com',
    'andres.torres@yopmail.com',
    'analista.prueba@yopmail.com',
    'direccionador.prueba@yopmail.com'
);
```

---

### Scope A — CargoId 1 | Director Técnico (Verificación de acceso total por sede)

**Archivo:** `Tests/test_permisos_jefe.py`

| ID | Caso | Acción | Resultado esperado |
|---|---|---|---|
| TC-PR-01 | Dashboard visible y accesible | Login como Carlos → navegar a `/Dashboard` | Página carga con KPIs completos de la sede |
| TC-PR-02 | Ve todo el personal | Navegar a `/Empleado` | Tabla muestra todos los empleados de la sede (activos e inactivos) |
| TC-PR-03 | Puede crear empleados | Navegar a `/Empleado/Nuevo` | Formulario de creación accesible (HTTP 200) |
| TC-PR-04 | Puede editar cualquier empleado | Navegar a `/Empleado/Editar/4` | Formulario de edición accesible (HTTP 200) |
| TC-PR-05 | Ve todos los eventos de la sede | Navegar a `/EventoLaboral` | Lista completa de eventos de la sede |
| TC-PR-06 | Ve todos los turnos de la sede | Navegar a `/Turno` | Lista completa de asignaciones de la sede |
| TC-PR-07 | Ve todas las horas extras | Navegar a `/HoraExtra` | Lista completa de HE de la sede |
| TC-PR-08 | Accede a catálogos | Navegar a `/Catalogos` | Página de catálogos accesible (HTTP 200) |
| TC-PR-09 | Menú completo visible | Inspeccionar sidebar | Dashboard, Empleados, Eventos, Turnos, HE, Catálogos visibles |

**Definición de "done":** Los 9 casos pasan en verde.

---

### Scope B — CargoId 2 | Regente de Farmacia (Aislamiento jerárquico)

**Archivo:** `Tests/test_permisos_regente.py`

#### B.1 — Dashboard

| ID | Caso | Acción | Resultado esperado |
|---|---|---|---|
| TC-PR-10 | Dashboard visible en menú | Login como Laura → inspeccionar sidebar | Ítem "Dashboard" presente |
| TC-PR-11 | Dashboard accesible | Navegar a `/Dashboard` | HTTP 200, datos de la sede de Laura |

#### B.2 — Empleados

| ID | Caso | Acción | Resultado esperado |
|---|---|---|---|
| TC-PR-12 | Solo ve sus subordinados | Navegar a `/Empleado` | Solo Andrés Torres, Diana Vargas, Jorge Herrera (activos de Laura) |
| TC-PR-13 | No ve al Director Técnico | Buscar `Carlos` en filtro | 0 resultados |
| TC-PR-14 | No ve empleados de otro Regente | Buscar `Natalia` o `Paula` | 0 resultados |
| TC-PR-15 | No puede crear personas | GET `/Empleado/Nuevo` | HTTP 403 |
| TC-PR-16 | Puede editar a un subordinado | GET `/Empleado/Editar/4` | HTTP 200 (Andrés es subordinado de Laura) |
| TC-PR-17 | No puede editar al Director Técnico | GET `/Empleado/Editar/1` | HTTP 403 |
| TC-PR-18 | No puede editar empleado de otro Regente | GET `/Empleado/Editar/7` | HTTP 403 |

#### B.3 — Eventos Laborales

| ID | Caso | Acción | Resultado esperado |
|---|---|---|---|
| TC-PR-19 | Solo ve eventos de sus subordinados | Navegar a `/EventoLaboral` | Solo eventos de Andrés, Diana, Jorge (y propios) |
| TC-PR-20 | No ve eventos de empleados ajenos | Verificar que no aparecen nombres de otros | 0 eventos de Carlos, Natalia, Paula |
| TC-PR-21 | Puede registrar evento para subordinado | POST `/EventoLaboral/RegistrarAjax` con EmpleadoId=4 | `{ exito: true }` |
| TC-PR-22 | No puede registrar para empleado ajeno | POST `/EventoLaboral/RegistrarAjax` con EmpleadoId=1 | `{ exito: false }` |

#### B.4 — Turnos

| ID | Caso | Acción | Resultado esperado |
|---|---|---|---|
| TC-PR-23 | Solo ve asignaciones de sus subordinados | Navegar a `/Turno` | Solo asignaciones de Andrés, Diana, Jorge |
| TC-PR-24 | No ve turnos de otros | Verificar que Carlos no aparece en tabla | 0 asignaciones de otros |
| TC-PR-25 | Puede asignar turno a subordinado | POST `/Turno/AsignarTurnoAjax` con EmpleadoId=4 | `{ exito: true }` |
| TC-PR-26 | No puede asignar turno a empleado ajeno | POST `/Turno/AsignarTurnoAjax` con EmpleadoId=1 | `{ exito: false }` |

#### B.5 — Horas Extras

| ID | Caso | Acción | Resultado esperado |
|---|---|---|---|
| TC-PR-27 | Ve HE propias y de subordinados | Navegar a `/HoraExtra` | Solo HE de Laura, Andrés, Diana, Jorge |
| TC-PR-28 | No ve HE de empleados ajenos | Verificar que Carlos no aparece | 0 HE de Carlos, Natalia |
| TC-PR-29 | Puede aprobar HE de subordinado | POST `/HoraExtra/AprobarAjax` con id de HE de Andrés | `{ exito: true }` |
| TC-PR-30 | No puede aprobar HE de empleado ajeno | POST `/HoraExtra/AprobarAjax` con id de HE de Carlos | `{ exito: false }` |

#### B.6 — Restricciones de catálogos

| ID | Caso | Acción | Resultado esperado |
|---|---|---|---|
| TC-PR-31 | No ve catálogos en menú | Inspeccionar sidebar | Ítem "Catálogos" ausente |
| TC-PR-32 | No puede acceder a catálogos por URL | GET `/Catalogos` | HTTP 403 |

**Definición de "done":** Los 23 casos (TC-PR-10 a TC-PR-32) pasan en verde.

---

### Scope C — CargoId 3 | Auxiliar de Farmacia (Acceso solo a información propia)

**Archivo:** `Tests/test_permisos_auxiliar.py`

| ID | Caso | Acción | Resultado esperado |
|---|---|---|---|
| TC-PR-33 | Dashboard NO visible en menú | Login como Andrés → inspeccionar sidebar | Ítem "Dashboard" ausente |
| TC-PR-34 | Menú "Empleados" muestra "Mi Perfil" | Inspeccionar sidebar | Link apunta a `/Empleado/Perfil/{empId}` |
| TC-PR-35 | Redirigido al propio perfil | GET `/Empleado` | Redirige a `/Empleado/Perfil/4` |
| TC-PR-36 | No puede acceder al perfil de otro | GET `/Empleado/Perfil/1` | HTTP 403 |
| TC-PR-37 | No puede crear personas | GET `/Empleado/Nuevo` | HTTP 403 |
| TC-PR-38 | No puede editar otros empleados | GET `/Empleado/Editar/1` | HTTP 403 |
| TC-PR-39 | Eventos Laborales ocultos en menú | Inspeccionar sidebar | Ítem "Eventos Laborales" ausente |
| TC-PR-40 | No puede acceder a Eventos por URL | GET `/EventoLaboral` | HTTP 403 |
| TC-PR-41 | Turnos ocultos en menú | Inspeccionar sidebar | Ítem "Horarios y Turnos" ausente |
| TC-PR-42 | No puede acceder a Turnos por URL | GET `/Turno` | HTTP 403 |
| TC-PR-43 | Ve solo sus propias HE | Navegar a `/HoraExtra` | Solo HE con EmpleadoId=4 |
| TC-PR-44 | No puede aprobar HE | POST `/HoraExtra/AprobarAjax` con id de HE propia | `{ exito: false, mensaje: "No tienes permisos..." }` |
| TC-PR-45 | Catálogos ocultos en menú | Inspeccionar sidebar | Ítem "Catálogos" ausente |
| TC-PR-46 | No puede acceder a catálogos por URL | GET `/Catalogos` | HTTP 403 |

**Definición de "done":** Los 14 casos (TC-PR-33 a TC-PR-46) pasan en verde.

---

### Scope D — CargoId 4 | Auxiliar Regente (Idéntico al Regente de Farmacia)

**Archivo:** `Tests/test_permisos_aux_regente.py`

> Los casos del Auxiliar Regente replican los del Scope B (Regente de Farmacia). Se ejecutan con el usuario de seeding con rol `AuxiliarRegente`.

| ID | Equivalente | Descripción |
|---|---|---|
| TC-PR-47 | TC-PR-10 | Dashboard visible en menú |
| TC-PR-48 | TC-PR-12 | Solo ve sus subordinados en Empleados |
| TC-PR-49 | TC-PR-15 | No puede crear personas |
| TC-PR-50 | TC-PR-17 | No puede editar al Director Técnico |
| TC-PR-51 | TC-PR-19 | Solo ve eventos de sus subordinados |
| TC-PR-52 | TC-PR-23 | Solo ve asignaciones de sus subordinados |
| TC-PR-53 | TC-PR-27 | Ve HE propias y de subordinados |
| TC-PR-54 | TC-PR-29 | Puede aprobar HE de subordinado |
| TC-PR-55 | TC-PR-31 | No ve catálogos en menú |
| TC-PR-56 | TC-PR-32 | No puede acceder a catálogos por URL |

**Definición de "done":** Los 10 casos (TC-PR-47 a TC-PR-56) pasan en verde.

---

### Scope E — CargoId 5 | Analista de Servicios Farmacéuticos (Acceso total multi-sede)

**Archivo:** `Tests/test_permisos_analista.py`

| ID | Caso | Acción | Resultado esperado |
|---|---|---|---|
| TC-PR-57 | Dashboard visible en menú | Login como Analista → inspeccionar sidebar | Ítem "Dashboard" presente |
| TC-PR-58 | Dashboard accesible | Navegar a `/Dashboard` | HTTP 200 |
| TC-PR-59 | Ve todo el personal (multi-sede) | Navegar a `/Empleado` | Tabla muestra empleados de **todas** las sedes |
| TC-PR-60 | Puede ver perfil de cualquier empleado | GET `/Empleado/Perfil/1` | HTTP 200 |
| TC-PR-61 | Puede crear personas | GET `/Empleado/Nuevo` | HTTP 200 (formulario accesible) |
| TC-PR-62 | Puede editar empleados | GET `/Empleado/Editar/1` | HTTP 200 |
| TC-PR-63 | Ve eventos laborales de todas las sedes | Navegar a `/EventoLaboral` | Lista sin filtro de sede |
| TC-PR-64 | Puede registrar eventos | POST `/EventoLaboral/RegistrarAjax` | `{ exito: true }` |
| TC-PR-65 | Ve turnos de todas las sedes | Navegar a `/Turno` | Lista sin filtro de sede |
| TC-PR-66 | Puede asignar turnos | POST `/Turno/AsignarTurnoAjax` | `{ exito: true }` |
| TC-PR-67 | Ve horas extras de todas las sedes | Navegar a `/HoraExtra` | Lista completa multi-sede |
| TC-PR-68 | Puede aprobar HE | POST `/HoraExtra/AprobarAjax` | `{ exito: true }` |
| TC-PR-69 | No ve catálogos en menú | Inspeccionar sidebar | Ítem "Catálogos" ausente |
| TC-PR-70 | No puede acceder a catálogos por URL | GET `/Catalogos` | HTTP 403 |

**Definición de "done":** Los 14 casos (TC-PR-57 a TC-PR-70) pasan en verde.

---

### Scope F — CargoId 6 | Direccionador (Idéntico al Auxiliar de Farmacia)

**Archivo:** `Tests/test_permisos_direccionador.py`

| ID | Equivalente | Descripción |
|---|---|---|
| TC-PR-71 | TC-PR-33 | Dashboard NO visible en menú |
| TC-PR-72 | TC-PR-34 | Menú "Empleados" muestra "Mi Perfil" |
| TC-PR-73 | TC-PR-35 | Redirigido al propio perfil en `/Empleado` |
| TC-PR-74 | TC-PR-36 | No puede acceder al perfil de otro |
| TC-PR-75 | TC-PR-37 | No puede crear personas |
| TC-PR-76 | TC-PR-39 | Eventos Laborales ocultos en menú |
| TC-PR-77 | TC-PR-40 | No puede acceder a Eventos por URL |
| TC-PR-78 | TC-PR-41 | Turnos ocultos en menú |
| TC-PR-79 | TC-PR-42 | No puede acceder a Turnos por URL |
| TC-PR-80 | TC-PR-43 | Ve solo sus propias HE |
| TC-PR-81 | TC-PR-44 | No puede aprobar HE |
| TC-PR-82 | TC-PR-45 | Catálogos ocultos en menú |
| TC-PR-83 | TC-PR-46 | No puede acceder a catálogos por URL |

**Definición de "done":** Los 13 casos (TC-PR-71 a TC-PR-83) pasan en verde.

---

### Scope G — Administrador (Superusuario de plataforma)

**Archivo:** `Tests/test_permisos_administrador.py`

| ID | Caso | Acción | Resultado esperado |
|---|---|---|---|
| TC-PR-84 | Dashboard visible en menú | Login como Administrador → inspeccionar sidebar | Ítem "Dashboard" presente |
| TC-PR-85 | Dashboard accesible | Navegar a `/Dashboard` | HTTP 200 |
| TC-PR-86 | Ve todo el personal (multi-sede) | Navegar a `/Empleado` | Tabla sin filtro de sede |
| TC-PR-87 | Puede crear personas | GET `/Empleado/Nuevo` | HTTP 200 |
| TC-PR-88 | Puede editar empleados | GET `/Empleado/Editar/1` | HTTP 200 |
| TC-PR-89 | Ve eventos laborales de todas las sedes | Navegar a `/EventoLaboral` | Lista completa |
| TC-PR-90 | Puede registrar eventos | POST `/EventoLaboral/RegistrarAjax` | `{ exito: true }` |
| TC-PR-91 | Ve turnos de todas las sedes | Navegar a `/Turno` | Lista completa |
| TC-PR-92 | Puede asignar turnos | POST `/Turno/AsignarTurnoAjax` | `{ exito: true }` |
| TC-PR-93 | Ve horas extras de todas las sedes | Navegar a `/HoraExtra` | Lista completa |
| TC-PR-94 | Puede aprobar HE | POST `/HoraExtra/AprobarAjax` | `{ exito: true }` |
| TC-PR-95 | Ve catálogos en menú | Inspeccionar sidebar | Ítem "Catálogos" presente |
| TC-PR-96 | Puede acceder a catálogos | GET `/Catalogos` | HTTP 200 |

**Definición de "done":** Los 13 casos (TC-PR-84 a TC-PR-96) pasan en verde.

---

### Comandos de ejecución

```powershell
# Desde la raíz del proyecto
cd "c:\Users\alejandro.ortiz\Documents\helpharma\Desarrollos\lissy\IA\LissyIAHelpharma\empleados v2"

# Todos los scopes de permisos
.\.venv\Scripts\python.exe -m pytest Tests/test_permisos_jefe.py Tests/test_permisos_regente.py Tests/test_permisos_auxiliar.py Tests/test_permisos_aux_regente.py Tests/test_permisos_analista.py Tests/test_permisos_direccionador.py Tests/test_permisos_administrador.py -v

# Un scope individual (útil durante implementación)
.\.venv\Scripts\python.exe -m pytest Tests/test_permisos_analista.py -v --headed

# Solo los casos de restricción crítica (smoke de seguridad)
.\.venv\Scripts\python.exe -m pytest Tests/ -k "TC_PR_15 or TC_PR_17 or TC_PR_32 or TC_PR_37 or TC_PR_61 or TC_PR_70 or TC_PR_87 or TC_PR_95" -v
```

---

## 8. Rabbit Holes

| Riesgo | Decisión |
|---|---|
| **Renombrar `RolUsuario.Jefe` invalida cookies activas** | Aceptable. Los usuarios con sesión activa al momento del deploy serán desconectados automáticamente. No justifica mantener el nombre incorrecto. Documentar en las notas del release. |
| **`JefeInmediatoId` no está en los DTOs de HE, Eventos y Turnos** | Agregar el campo al DTO y mapearlo en el service correspondiente. Son 2 líneas por módulo. No justifica un rediseño del repositorio. |
| **Regente puede tener subordinados en múltiples sedes** | El seeding actual no define este escenario. Para v1 asumir que el Regente tiene subordinados solo en su sede. El filtro por `JefeInmediatoId` es correcto independientemente de la sede si esto cambia en el futuro. |
| **¿Qué pasa si `EmpleadoId` del claim es null para un Regente o Analista?** | Para Regente/AuxiliarRegente: retornar `Forbid()` explícito si `empId` es null. Para Analista: el acceso no depende de `EmpleadoId`, continuar normalmente. |
| **Administrador sin `EmpleadoId` en el claim** | El Administrador es un rol técnico sin empleado asociado en la BD. Asegurarse de que ninguna lógica llame `empId.Value` sin verificar primero si es null cuando el rol es Administrador. El patrón de cortocircuito (`Administrador || Analista`) garantiza que el código no llega al bloque que usa `empId`. |
| **Direccionador sin `EmpleadoId` en el claim** | Si el usuario Direccionador no tiene empleado asociado, el redirect a "Mi Perfil" fallará. Agregar el mismo fallback al Dashboard que ya existe para el Operario. |
| **`DebeCambiarPassword = 1` bloquea el login de prueba** | Resetear con el SQL provisto antes de cada ejecución de pruebas, o usar la fixture de primer ingreso que ya existe en `helpers.py`. |
| **Catálogos accesibles por URL directa** | Agregar el check de rol al inicio de cada action de catálogo. El check in-line es suficiente para el appetite actual, no se necesita filtro global. |

---

## 9. No-Gos

Lo siguiente queda **explícitamente fuera** de este ciclo:

- ❌ Sistema de permisos dinámico basado en tabla de BD — las reglas son fijas por cargo y se implementan con condiciones en código
- ❌ Acceso de lectura del Analista al catálogo de Sedes y Cargos — queda para el siguiente ciclo
- ❌ Auditoría de intentos de acceso no autorizado (logging de seguridad) — se agrega en un ciclo futuro
- ❌ Restricciones sobre el campo `Catálogo de Empresas Temporales` en el formulario de creación
- ❌ Validación de permisos a nivel de `service` para los módulos de Eventos, Turnos y HE — el filtro vive en el controller para mantener consistencia con el patrón existente
- ❌ Pruebas cross-browser — solo Chromium headless en este ciclo
- ❌ Permisos sobre el módulo de desvinculación de empleados — ya está restringido a DirectorTecnico en el código actual
- ❌ UI adaptativa por rol dentro de la misma vista (mostrar/ocultar botones específicos) — fuera del appetite del ciclo corto
- ❌ Creación de un rol intermedio entre Analista y Director Técnico — la jerarquía de `Correccion-Roles.md` es la fuente de verdad para este ciclo
- ❌ Pantalla de administración de usuarios para el rol Administrador (alta/baja de cuentas) — ciclo futuro

---

## Resultado Esperado

Al finalizar el ciclo, el sistema debe garantizar que:

1. Cada usuario puede acceder únicamente a las rutas autorizadas para su cargo, tanto por menú como por URL directa.
2. Los datos mostrados en listados (empleados, eventos, turnos, horas extras) corresponden estrictamente al ámbito jerárquico del usuario autenticado.
3. Las operaciones de escritura (crear, editar, aprobar, rechazar, anular) son rechazadas con `403 Forbidden` o mensaje de error cuando el objetivo no pertenece a la jerarquía del usuario.
4. Los **96 casos de prueba Playwright** (TC-PR-01 a TC-PR-96) pasan en verde en ambiente local con el seeding aplicado.
5. El enum `RolUsuario` refleja la nomenclatura oficial del organigrama (Director Técnico, Analista, Direccionador).
