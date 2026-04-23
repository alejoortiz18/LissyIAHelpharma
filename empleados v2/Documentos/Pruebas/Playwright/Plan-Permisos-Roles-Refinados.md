# Pitch — Corrección Integral de Permisos por Cargo
## Sistema de Administración de Empleados — GestionPersonal

> **Metodología:** Shape Up (Basecamp)  
> **Stack:** C# ASP.NET Core MVC / .NET 10 · Cookie Authentication · RolUsuario enum  
> **Ciclo:** Small Batch  
> **Última actualización:** Abril 2026

---

## El Problema

El plan original de permisos identifica correctamente qué debe poder hacer cada cargo, pero no traduce esas reglas al estado real del código. El resultado es que hoy mismo, un usuario **Farmacéutico Regente** (`CargoId = 2`) puede navegar a `/Empleado/Nuevo` y registrar un empleado al que no debería tener acceso. Un **Auxiliar Regente** (`CargoId = 4`) puede aprobar horas extras de empleados que no son sus subordinados. Un **Auxiliar de Farmacia** (`CargoId = 3`) tiene el ítem "Empleados" visible en el menú lateral aunque el controlador lo redirija en silencio.

Estos comportamientos no son errores de diseño sino **gaps de implementación**: la lógica de negocio existe y está documentada, pero no se ha aplicado de forma consistente en todos los módulos ni en el frontend. Cada gap es un vector de acceso indebido a datos sensibles de otros empleados.

El riesgo concreto:
- Un Regente de Sede Medellín puede ver y aprobar las horas extras de empleados que dependen de otro Regente en la misma sede.
- El Jefe de sede puede aparecer en la lista de "Personal a cargo" del Regente.
- El Auxiliar de Farmacia ve en su menú opciones que no le corresponden, generando confusión y eventual intento de acceso.

---

## Appetite

**Small Batch — 1 a 2 días de trabajo por cargo involucrado.**

Cuatro cargos, enfoque secuencial:

| Cargo | Appetite estimado |
|-------|-------------------|
| CargoId 3 — Auxiliar de Farmacia | Día 1 (solo frontend y redirección) |
| CargoId 2 — Farmacéutico Regente | Días 2-3 (backend + frontend) |
| CargoId 4 — Auxiliar Regente | Día 4 (hereda lógica del Regente) |
| CargoId 1 — Jefe de Sede | Día 5 (verificación de acceso total) |

> El tiempo no se gasta en reescribir la arquitectura. Cada ajuste es quirúrgico: condición `if (rol == ...)` en el controlador correspondiente o un `@if (User.IsInRole(...))` en la vista.

---

## Mapa de Roles — CargoId → RolUsuario

La regla de negocio define cargos (`CargoId`). El código los implementa como `RolUsuario` (enum en `GestionPersonal.Models.Enums`). Esta tabla es la fuente de verdad para todos los filtros:

| CargoId | Nombre del Cargo | RolUsuario (enum) | Descripción en código |
|---------|-----------------|-------------------|-----------------------|
| 1 | Jefe de Sede | `RolUsuario.Jefe` | Acceso total por sede |
| 2 | Farmacéutico Regente | `RolUsuario.Regente` | Solo su jerarquía directa |
| 3 | Auxiliar de Farmacia | `RolUsuario.Operario` | Solo información propia |
| 4 | Auxiliar Regente | `RolUsuario.AuxiliarRegente` | Idéntico al Regente |

> El claim `ClaimTypes.Role` en la cookie de sesión contiene el nombre del enum (ej. `"Regente"`). El `SesionHelper.GetRol(User)` lo parsea a `RolUsuario`. El `SesionHelper.GetEmpleadoId(User)` retorna el `EmpleadoId` del usuario autenticado, clave para el filtro por `JefeInmediatoId`.

---

## Solución

### Principio de filtrado jerárquico

El filtro central para Regente y AuxiliarRegente es:

```csharp
// Leer de los claims
var rol          = SesionHelper.GetRol(User);
var miEmpleadoId = SesionHelper.GetEmpleadoId(User);

// Aplicar en cualquier listado
if (rol == RolUsuario.Regente || rol == RolUsuario.AuxiliarRegente)
{
    if (miEmpleadoId.HasValue)
        query = query.Where(e =>
            e.EmpleadoId == miEmpleadoId.Value ||       // recursos propios
            e.Empleado.JefeInmediatoId == miEmpleadoId.Value); // recursos de subordinados
}
```

Este patrón se replica en cada módulo con la variación correspondiente al modelo de datos.

---

### Módulo 1 — Empleados (`EmpleadoController`)

#### Estado actual

| Acción | Jefe | Regente | Aux. Farmacia | Aux. Regente |
|--------|------|---------|---------------|--------------|
| `Index` (listado) | ✅ Todos | ✅ Solo subordinados | ✅ Redirige a Perfil | ✅ Solo subordinados |
| `Nuevo` / `Crear` | ✅ | ❌ **Puede crear** | ✅ Retorna 403 | ❌ **Puede crear** |
| `Editar` / `Actualizar` | ✅ | ❌ **Edita cualquiera** | ✅ Retorna 403 | ❌ **Edita cualquiera** |
| `Perfil` | ✅ | ✅ Solo propios/subordinados (pendiente) | ✅ Solo propio | ✅ Solo propios/subordinados (pendiente) |

#### Cambios requeridos (backend)

**`EmpleadoController.Nuevo` y `EmpleadoController.Crear`:**
```csharp
// Agregar junto al check de Operario existente
if (rol == RolUsuario.Regente || rol == RolUsuario.AuxiliarRegente)
    return Forbid();
```

**`EmpleadoController.Editar` y `EmpleadoController.Actualizar`:**
```csharp
// Verificar que el empleado a editar es subordinado directo o sí mismo
if (rol == RolUsuario.Regente || rol == RolUsuario.AuxiliarRegente)
{
    var objetivo = await _empleadoService.ObtenerPerfilAsync(id);
    if (objetivo.Datos?.JefeInmediatoId != miEmpleadoId && objetivo.Datos?.Id != miEmpleadoId)
        return Forbid();
}
```

**`EmpleadoController.Perfil`:**
```csharp
// Regente/AuxiliarRegente: solo puede ver su perfil o el de sus subordinados
if (rol == RolUsuario.Regente || rol == RolUsuario.AuxiliarRegente)
{
    var objetivo = await _empleadoService.ObtenerPerfilAsync(id);
    var esPropio       = objetivo.Datos?.Id == miEmpleadoId;
    var esSubordinado  = objetivo.Datos?.JefeInmediatoId == miEmpleadoId;
    if (!esPropio && !esSubordinado)
        return Forbid();
}
```

#### Cambios requeridos (frontend — `_Layout.cshtml`)

El ítem "Empleados" del sidebar actualmente es visible para todos. Para Operario debe cambiarse a "Mi Perfil":
```html
@if (User.IsInRole("Operario"))
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

| Acción | Jefe | Regente | Aux. Farmacia | Aux. Regente |
|--------|------|---------|---------------|--------------|
| `Index` (listado) | ✅ Todos de sede | ❌ **Todos de sede** | ✅ Solo propias | ❌ **Todos de sede** |
| `RegistrarAjax` | ✅ | ❌ **Para cualquier empleado** | ✅ Solo propias | ❌ **Para cualquier empleado** |
| `AprobarAjax` | ✅ | ❌ **Aprueba cualquiera** | ❌ No puede | ❌ **Aprueba cualquiera** |
| `RechazarAjax` | ✅ | ❌ **Rechaza cualquiera** | ❌ No puede | ❌ **Rechaza cualquiera** |

#### Cambios requeridos (backend — `HoraExtraController.Index`)

```csharp
IReadOnlyList<HoraExtraDto> todos;
if (rol == RolUsuario.Operario && empId.HasValue)
    todos = await _horaExtraService.ObtenerPorEmpleadoAsync(empId.Value);
else
    todos = await _horaExtraService.ObtenerPorSedeAsync(sedeId);

// Nuevo filtro para Regente / AuxiliarRegente
if ((rol == RolUsuario.Regente || rol == RolUsuario.AuxiliarRegente) && empId.HasValue)
    todos = todos.Where(h => h.EmpleadoId == empId.Value || h.JefeInmediatoId == empId.Value).ToList();
```

> Para que `h.JefeInmediatoId` esté disponible, agregar `JefeInmediatoId` al `HoraExtraDto` y mapearlo en `HoraExtraService.MapToDto` desde `h.Empleado.JefeInmediatoId`.

#### Cambios requeridos (backend — `HoraExtraController.AprobarAjax` y `RechazarAjax`)

```csharp
// Antes de delegar al service, verificar jerarquía
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

| Acción | Jefe | Regente | Aux. Farmacia | Aux. Regente |
|--------|------|---------|---------------|--------------|
| `Index` (listado) | ✅ Todos de sede | ❌ **Todos de sede** | ❌ Sin acceso (menú oculto) | ❌ **Todos de sede** |
| `RegistrarAjax` | ✅ | ❌ **Para cualquier empleado** | ❌ | ❌ **Para cualquier empleado** |
| `AnularAjax` | ✅ | ❌ **Anula cualquiera** | ❌ | ❌ **Anula cualquiera** |

#### Cambios requeridos (backend — `EventoLaboralController.Index`)

```csharp
var todos = await _eventoService.ObtenerPorSedeAsync(sedeId);

// Filtro jerárquico
if ((rol == RolUsuario.Regente || rol == RolUsuario.AuxiliarRegente) && empId.HasValue)
    todos = todos.Where(e => e.EmpleadoId == empId.Value || e.JefeInmediatoId == empId.Value).ToList();
```

> Requiere agregar `JefeInmediatoId` a `EventoLaboralDto` y mapearlo en `EventoLaboralService.MapToDto`.

#### Cambios requeridos (backend — `EventoLaboralController.RegistrarAjax` y `AnularAjax`)

```csharp
if (rol == RolUsuario.Regente || rol == RolUsuario.AuxiliarRegente)
{
    // Para RegistrarAjax: verificar que el empleadoId del dto es subordinado
    var empObjetivo = await _empleadoService.ObtenerPerfilAsync(dto.EmpleadoId);
    if (empObjetivo.Datos?.JefeInmediatoId != empId && empObjetivo.Datos?.Id != empId)
        return Json(new { exito = false, mensaje = "No puedes registrar eventos para este empleado." });
}
```

---

### Módulo 4 — Turnos (`TurnoController`)

#### Estado actual

| Acción | Jefe | Regente | Aux. Farmacia | Aux. Regente |
|--------|------|---------|---------------|--------------|
| `Index` (plantillas + asignaciones) | ✅ Todos de sede | ❌ **Todos de sede** | ❌ Sin acceso (menú oculto) | ❌ **Todos de sede** |
| `AsignarTurnoAjax` | ✅ | ❌ **Para cualquier empleado** | ❌ | ❌ **Para cualquier empleado** |
| `EliminarAsignacionAjax` | ✅ | ✅ Solo si es programador o jefe | ✅ | ✅ Solo si es programador o jefe |

#### Cambios requeridos (backend — `TurnoController.Index`)

```csharp
var asignaciones = await _turnoService.ObtenerAsignacionesPorSedeAsync(sedeId);

// Filtro jerárquico para Regente / AuxiliarRegente
if ((rol == RolUsuario.Regente || rol == RolUsuario.AuxiliarRegente) && empId.HasValue)
    asignaciones = asignaciones
        .Where(a => a.EmpleadoId == empId.Value || a.JefeInmediatoId == empId.Value)
        .ToList();
```

> Requiere agregar `JefeInmediatoId` al `AsignacionTurnoDto` y mapearlo en `TurnoService.ObtenerAsignacionesPorSedeAsync`.

#### Cambios requeridos (backend — `TurnoController.AsignarTurnoAjax`)

```csharp
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

| Rol | Dashboard | Menú visible |
|-----|-----------|--------------|
| Jefe | ✅ | ✅ |
| Regente | ✅ Accede al endpoint | ❌ **Menú oculto** |
| Aux. Farmacia | ✅ Accede al endpoint | ❌ Menú oculto (correcto) |
| Aux. Regente | ✅ Accede al endpoint | ❌ **Menú oculto** |

#### Cambios requeridos (frontend — `_Layout.cshtml`)

El Dashboard solo aparece para `Jefe` y `Administrador`. Según las reglas de negocio, `Regente` y `AuxiliarRegente` también deben tenerlo:

```html
@if (User.IsInRole("Jefe") || User.IsInRole("Administrador")
     || User.IsInRole("Regente") || User.IsInRole("AuxiliarRegente"))
{
  <a asp-controller="Dashboard" asp-action="Index" class="@NavClass("Dashboard")">
    <span class="nav-text">Dashboard</span>
  </a>
}
```

> El `DashboardController.Index` filtra por `SedeId` y este filtro ya restringe los datos al ámbito del usuario. No se requieren cambios en el backend para este módulo.

---

### Módulo 6 — Catálogos (`CatalogoController`, `SedeController`, `CargoController`, `EmpresaTemporalController`)

#### Estado actual

El menú de Catálogos ya está oculto para roles que no sean Jefe o Administrador. No se detectan gaps en este módulo.

| Rol | Acceso backend | Menú visible |
|-----|----------------|--------------|
| Jefe | ✅ | ✅ |
| Regente | Sin restricción backend explícita | ❌ Oculto |
| Aux. Farmacia | Sin restricción backend explícita | ❌ Oculto |
| Aux. Regente | Sin restricción backend explícita | ❌ Oculto |

#### Cambios requeridos (backend — todos los controladores de catálogo)

Aunque el menú esté oculto, los endpoints son accesibles por URL directa. Agregar restricción explícita:

```csharp
// En cada controlador de catálogo (SedeController, CargoController, EmpresaTemporalController)
var rol = SesionHelper.GetRol(User);
if (rol != RolUsuario.Jefe && rol != RolUsuario.Administrador)
    return Forbid();
```

---

## Matriz de Permisos Refinada

| Funcionalidad | Jefe de Sede | Regente | Aux. Farmacia | Aux. Regente | Implementado |
|---------------|:---:|:---:|:---:|:---:|:---:|
| **Dashboard** | ✅ | ✅ | ❌ | ✅ | ⚠️ Parcial |
| **Ver listado empleados** | ✅ Todos | ✅ Solo subordinados | ❌ Mi perfil | ✅ Solo subordinados | ⚠️ Parcial |
| **Ver todo el personal** | ✅ | ❌ | ❌ | ❌ | ✅ |
| **Crear personas** | ✅ | ❌ | ❌ | ❌ | ❌ Gap |
| **Editar empleados** | ✅ Cualquiera | ✅ Solo subordinados | ❌ | ✅ Solo subordinados | ❌ Gap |
| **Ver perfil de empleados** | ✅ | ✅ Propio + subordinados | ✅ Solo propio | ✅ Propio + subordinados | ❌ Gap |
| **Ver eventos laborales** | ✅ Todos | ✅ Solo subordinados | ❌ | ✅ Solo subordinados | ❌ Gap |
| **Registrar eventos** | ✅ | ✅ Para subordinados | ❌ | ✅ Para subordinados | ❌ Gap |
| **Anular eventos** | ✅ | ✅ De subordinados | ❌ | ✅ De subordinados | ❌ Gap |
| **Ver turnos / horarios** | ✅ Todos | ✅ Solo subordinados | ❌ | ✅ Solo subordinados | ❌ Gap |
| **Asignar turnos** | ✅ | ✅ Solo subordinados | ❌ | ✅ Solo subordinados | ❌ Gap |
| **Ver horas extras** | ✅ Todos | ✅ Propias + subordinados | ✅ Solo propias | ✅ Propias + subordinados | ❌ Gap |
| **Registrar horas extras** | ✅ | ✅ Para subordinados | ✅ Propias | ✅ Para subordinados | ❌ Gap |
| **Aprobar/Rechazar HE** | ✅ | ✅ De subordinados | ❌ | ✅ De subordinados | ❌ Gap |
| **Catálogo de sistemas** | ✅ | ❌ | ❌ | ❌ | ⚠️ Solo frontend |

**Leyenda:** ✅ Permitido · ❌ Bloqueado · ⚠️ Parcialmente implementado · Gap = pendiente de corrección

---

## Estado de Implementación

### ✅ Ya implementado y validado

- [x] `EmpleadoController.Index`: filtro `JefeInmediatoId` para Regente/AuxiliarRegente
- [x] `EmpleadoController.Index`: Operario redirigido a su propio perfil
- [x] `EmpleadoController.Nuevo` y `Crear`: Operario recibe 403
- [x] `HoraExtraController.Index`: Operario ve solo sus propias HE
- [x] `TurnoController.EliminarAsignacionAjax`: valida que solo el programador o el jefe puede eliminar
- [x] Sidebar — Dashboard: oculto para Operario (correcto para ese rol)
- [x] Sidebar — Catálogos: visible solo para Jefe/Administrador
- [x] Sidebar — Eventos y Turnos: ocultos para Operario
- [x] `JefeInmediatoId` incluido en `EmpleadoListaDto` y mapeado en `EmpleadoService`

### ❌ Pendiente de implementación

- [ ] **Empleados — Crear/Nuevo**: bloquear Regente y AuxiliarRegente
- [ ] **Empleados — Editar/Actualizar**: validar jerarquía para Regente y AuxiliarRegente
- [ ] **Empleados — Perfil**: validar jerarquía para Regente y AuxiliarRegente
- [ ] **HorasExtras — Index**: agregar filtro por JefeInmediato para Regente/AuxiliarRegente
- [ ] **HorasExtras — AprobarAjax/RechazarAjax**: validar jerarquía antes de aprobar/rechazar
- [ ] **HoraExtraDto**: agregar campo `JefeInmediatoId` y mapeo en service
- [ ] **EventosLaborales — Index**: filtro por JefeInmediato para Regente/AuxiliarRegente
- [ ] **EventosLaborales — RegistrarAjax**: validar que el empleado es subordinado
- [ ] **EventosLaborales — AnularAjax**: validar jerarquía
- [ ] **EventoLaboralDto**: agregar campo `JefeInmediatoId` y mapeo en service
- [ ] **Turnos — Index**: filtro de asignaciones por JefeInmediato para Regente/AuxiliarRegente
- [ ] **Turnos — AsignarTurnoAjax**: validar que el empleado es subordinado
- [ ] **AsignacionTurnoDto**: agregar campo `JefeInmediatoId` y mapeo en service
- [ ] **Sidebar — Dashboard**: agregar visibilidad para Regente y AuxiliarRegente
- [ ] **Sidebar — Empleados**: cambiar a "Mi Perfil" para Operario
- [ ] **Catálogos — Backend**: agregar restricción explícita en todos los controllers de catálogo

---

## Casos de Prueba Playwright

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
| 1 | Carlos Alberto Rodríguez Mora | Jefe de Sede | Jefe | `carlos.rodriguez@yopmail.com` | `Usuario1` |
| 2 | Laura Patricia Sánchez Gómez | Farmacéutico Regente | Regente | `laura.sanchez@yopmail.com` | `Usuario1` |
| 3 | Hernán David Castillo Mejía | Farmacéutico Regente | Regente | `hernan.castillo@yopmail.com` | `Usuario1` |
| 4 | Andrés Felipe Torres Ruiz | Auxiliar de Farmacia | Operario | `andres.torres@yopmail.com` | `Usuario1` |
| (Aux. Regente) | *(definido en seeding)* | Auxiliar Regente | AuxiliarRegente | *(ver seeding)* | `Usuario1` |

> **Nota:** Todos los usuarios tienen `DebeCambiarPassword = 1` en el primer login. Usar la fixture `do_login_completo(page, correo, password)` que maneja el flujo de cambio de contraseña automáticamente, o aplicar el SQL de reset antes de cada ejecución.

```sql
-- Reset DebeCambiarPassword para todos los usuarios de prueba
UPDATE dbo.Usuarios SET DebeCambiarPassword = 0
WHERE CorreoAcceso IN (
    'carlos.rodriguez@yopmail.com',
    'laura.sanchez@yopmail.com',
    'hernan.castillo@yopmail.com',
    'andres.torres@yopmail.com'
);
```

---

### Scope A — CargoId 1 | Jefe de Sede (Verificación de acceso total)

**Archivo:** `Tests/test_permisos_jefe.py`

| ID | Caso | Acción | Resultado esperado |
|---|---|---|---|
| TC-PR-01 | Dashboard visible y accesible | Login como Carlos → navegar a `/Dashboard` | Página carga con KPIs completos |
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

### Scope B — CargoId 2 | Farmacéutico Regente (Aislamiento jerárquico)

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
| TC-PR-13 | No ve al Jefe | Buscar `Carlos` en filtro | 0 resultados |
| TC-PR-14 | No ve empleados de otro Regente | Buscar `Natalia` o `Paula` | 0 resultados |
| TC-PR-15 | No puede crear personas | GET `/Empleado/Nuevo` | HTTP 403 |
| TC-PR-16 | Puede editar a un subordinado | GET `/Empleado/Editar/4` | HTTP 200 (Andrés es subordinado de Laura) |
| TC-PR-17 | No puede editar al Jefe | GET `/Empleado/Editar/1` | HTTP 403 |
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
| TC-PR-40 | No puede acceder a Eventos por URL | GET `/EventoLaboral` | HTTP 403 o redirect a su perfil |
| TC-PR-41 | Turnos ocultos en menú | Inspeccionar sidebar | Ítem "Horarios y Turnos" ausente |
| TC-PR-42 | No puede acceder a Turnos por URL | GET `/Turno` | HTTP 403 |
| TC-PR-43 | Ve solo sus propias HE | Navegar a `/HoraExtra` | Solo HE con EmpleadoId=4 |
| TC-PR-44 | No puede aprobar HE | POST `/HoraExtra/AprobarAjax` con id de HE propia | `{ exito: false, mensaje: "No tienes permisos..." }` |
| TC-PR-45 | Catálogos ocultos en menú | Inspeccionar sidebar | Ítem "Catálogos" ausente |
| TC-PR-46 | No puede acceder a catálogos por URL | GET `/Catalogos` | HTTP 403 |

**Definición de "done":** Los 14 casos (TC-PR-33 a TC-PR-46) pasan en verde.

---

### Scope D — CargoId 4 | Auxiliar Regente (Idéntico al Regente)

**Archivo:** `Tests/test_permisos_aux_regente.py`

> Los casos del Auxiliar Regente replican exactamente los del Scope B (Regente). Se ejecutan con el usuario correspondiente del seeding (rol `AuxiliarRegente`).

| ID | Equivalente | Descripción |
|---|---|---|
| TC-PR-47 | TC-PR-10 | Dashboard visible en menú |
| TC-PR-48 | TC-PR-12 | Solo ve sus subordinados en Empleados |
| TC-PR-49 | TC-PR-15 | No puede crear personas |
| TC-PR-50 | TC-PR-17 | No puede editar al Jefe |
| TC-PR-51 | TC-PR-19 | Solo ve eventos de sus subordinados |
| TC-PR-52 | TC-PR-23 | Solo ve asignaciones de sus subordinados |
| TC-PR-53 | TC-PR-27 | Ve HE propias y de subordinados |
| TC-PR-54 | TC-PR-29 | Puede aprobar HE de subordinado |
| TC-PR-55 | TC-PR-31 | No ve catálogos en menú |
| TC-PR-56 | TC-PR-32 | No puede acceder a catálogos por URL |

**Definición de "done":** Los 10 casos (TC-PR-47 a TC-PR-56) pasan en verde.

---

### Comandos de ejecución

```powershell
# Desde la raíz del proyecto
cd "c:\Users\alejandro.ortiz\Documents\helpharma\Desarrollos\lissy\IA\LissyIAHelpharma\empleados v2"

# Todos los scopes de permisos
.\.venv\Scripts\python.exe -m pytest Tests/test_permisos_jefe.py Tests/test_permisos_regente.py Tests/test_permisos_auxiliar.py Tests/test_permisos_aux_regente.py -v

# Un scope individual (útil durante implementación)
.\.venv\Scripts\python.exe -m pytest Tests/test_permisos_regente.py -v --headed

# Solo los casos de restricción (smoke de seguridad)
.\.venv\Scripts\python.exe -m pytest Tests/ -k "TC_PR_15 or TC_PR_17 or TC_PR_32 or TC_PR_37" -v
```

---

## Rabbit Holes

| Riesgo | Decisión |
|---|---|
| **`JefeInmediatoId` no está en los DTOs de HE, Eventos y Turnos** | Agregar el campo al DTO y mapearlo en el service correspondiente. Es un cambio de 2 líneas por módulo. No justifica un rediseño del repositorio. |
| **Regente puede tener subordinados en múltiples sedes** | El seeding actual no define este escenario. Para v1 asumir que el Regente tiene subordinados solo en su sede. Si en el futuro cambia, el filtro por `JefeInmediatoId` seguirá siendo correcto independientemente de la sede. |
| **¿Qué pasa si `EmpleadoId` del claim es null para un Regente?** | Si `SesionHelper.GetEmpleadoId(User)` retorna null, el filtro no aplica y el Regente vería todos los registros de la sede. Agregar un `return Forbid()` explícito cuando `empId` sea null para Regente/AuxiliarRegente. |
| **`DebeCambiarPassword = 1` bloquea el login de prueba** | Resetear con el SQL provisto antes de cada ejecución de pruebas, o usar la fixture de primer ingreso que ya existe en `helpers.py`. |
| **Catálogos: el acceso por URL directa no está bloqueado en backend** | Agregar el check de rol al inicio de cada action de catálogo. No requiere nuevo filtro global; el check in-line es suficiente para el appetite actual. |
| **Operario con `EmpleadoId` null en el claim** | Si un usuario `Operario` no tiene `EmpleadoId` en el claim (usuario sin empleado asociado), el sistema ya maneja esto con la redirección a Dashboard. No agregar nueva lógica. |

---

## No-gos

Lo siguiente queda **explícitamente fuera** de este ciclo:

- ❌ Implementación de un sistema de permisos dinámico basado en tabla de BD — las reglas son fijas por cargo y se implementan con condiciones en código
- ❌ Auditoría de intentos de acceso no autorizado (logging de seguridad) — se puede agregar en un ciclo futuro
- ❌ Restricciones sobre el campo `Catálogo de Empresas Temporales` en el formulario de creación de empleados
- ❌ Validación de permisos a nivel de `service` para los módulos de Eventos, Turnos y HE — el filtro vive en el controller para mantener consistencia con el patrón existente
- ❌ Pruebas cross-browser — solo Chromium headless en este ciclo
- ❌ Pruebas de rol `Administrador` — no está en el seeding de datos de prueba actuales
- ❌ Permisos sobre el módulo de desvinculación de empleados — ya está restringido a Jefe en el código actual
- ❌ UI adaptativa por rol dentro de la misma vista (mostrar/ocultar botones específicos) — fuera del appetite del ciclo corto

---

## Resultado Esperado

Al finalizar el ciclo, el sistema debe garantizar que:

1. Cada usuario puede acceder únicamente a las rutas autorizadas para su cargo, tanto por menú como por URL directa.
2. Los datos mostrados en listados (empleados, eventos, turnos, horas extras) corresponden estrictamente al ámbito jerárquico del usuario autenticado.
3. Las operaciones de escritura (crear, editar, aprobar, rechazar, anular) son rechazadas con `403 Forbidden` o mensaje de error cuando el objetivo no pertenece a la jerarquía del usuario.
4. Los 56 casos de prueba Playwright pasan en verde en ambiente local con el seeding aplicado.
