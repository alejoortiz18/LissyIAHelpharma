# Plan de Ejecución — Corrección Integral de Permisos por Cargo
## Sistema de Administración de Empleados — GestionPersonal

> **Basado en:** Plan-Permisos-Roles-Refinados.md  
> **Ejecutor:** GitHub Copilot (requiere aprobación previa del usuario)  
> **Orden de implementación:** DTOs → Services → Controllers → Frontend → Tests → Verificación  
> **Granularidad:** Una tarea por archivo modificado  
> **Verificación:** Build por fase (no archivo a archivo)  
> **Última actualización:** Abril 2026

---

## Correcciones de Datos Detectadas

Antes de iniciar la ejecución, se identificaron dos discrepancias entre el plan refinado y el código/seeding real. Estas se reflejan en la tabla de usuarios de prueba de este documento.

| # | Hallazgo | Impacto |
|---|---|---|
| 1 | `CatalogosController` ya tiene `[Authorize(Roles = "Jefe,Administrador")]` en el atributo de clase | La tarea "Catálogos — Backend" del plan refinado **ya está implementada**. Se omite como tarea de código; se conserva como caso de prueba de verificación. |
| 2 | `Andrés Torres` (EmpleadoId=4) es `AuxiliarRegente` en el seeding, no Operario | El usuario de prueba para **Scope C** (Auxiliar de Farmacia) debe ser **Diana Vargas** (EmpleadoId=5), no Andrés Torres. Andrés Torres es el usuario de **Scope D**. |

---

## Tabla de Usuarios de Prueba (Corregida)

| EmpleadoId | Nombre | Cargo real | RolUsuario | Correo | Password inicial | Scope |
|---|---|---|---|---|---|---|
| 1 | Carlos Alberto Rodríguez Mora | Jefe de Sede | `Jefe` | `carlos.rodriguez@yopmail.com` | `Usuario1` | A |
| 2 | Laura Patricia Sánchez Gómez | Farmacéutico Regente | `Regente` | `laura.sanchez@yopmail.com` | `Usuario1` | B |
| 4 | Andrés Felipe Torres Ruiz | Auxiliar Regente | `AuxiliarRegente` | `andres.torres@yopmail.com` | `Usuario1` | D |
| 5 | Diana Marcela Vargas López | Auxiliar de Farmacia | `Operario` | `diana.vargas@yopmail.com` | `Usuario1` | C |

> **Jerarquía relevante:** Carlos (Jefe) → Laura (Regente) → {Andrés Torres (AuxiliarRegente), Diana Vargas (Operario), Jorge Herrera (Operario)}

---

## Prerequisitos (verificar antes de ejecutar)

- [ ] Seeding `Documentos/BD/Seeding_Completo.sql` aplicado en `(localdb)\MSSQLLocalDB`
- [ ] Proyecto compila sin errores (`dotnet build GestionPersonal.slnx`)
- [ ] La aplicación puede levantarse en `http://localhost:5002`
- [ ] El entorno virtual de Python está activo (`.venv\Scripts\Activate.ps1`)
- [ ] `pytest-playwright` instalado (`pip install pytest-playwright`)

---

## Resumen de Tareas

| # | Fase | Archivo | Descripción | Estado |
|---|---|---|---|---|
| 1.1 | DTOs | `HoraExtraDto.cs` | Agregar `JefeInmediatoId` | ⏳ Pendiente |
| 1.2 | DTOs | `EventoLaboralDto.cs` | Agregar `JefeInmediatoId` | ⏳ Pendiente |
| 1.3 | DTOs | `AsignacionTurnoDto.cs` | Agregar `JefeInmediatoId` | ⏳ Pendiente |
| — | Build | Build Fase 1 | Verificar compilación | ⏳ Pendiente |
| 2.1 | Services | `HoraExtraService.cs` | Mapear `JefeInmediatoId` en `MapToDto` | ⏳ Pendiente |
| 2.2 | Services | `EventoLaboralService.cs` | Mapear `JefeInmediatoId` en `MapToDto` | ⏳ Pendiente |
| 2.3 | Services | `TurnoService.cs` | Mapear `JefeInmediatoId` en `ObtenerAsignacionesPorSedeAsync` | ⏳ Pendiente |
| — | Build | Build Fase 2 | Verificar compilación | ⏳ Pendiente |
| 3.1 | Controllers | `EmpleadoController.cs` — Nuevo/Crear | Bloquear Regente y AuxiliarRegente | ⏳ Pendiente |
| 3.2 | Controllers | `EmpleadoController.cs` — Editar/Actualizar | Validar jerarquía para Regente/AuxiliarRegente | ⏳ Pendiente |
| 3.3 | Controllers | `EmpleadoController.cs` — Perfil | Validar jerarquía para Regente/AuxiliarRegente | ⏳ Pendiente |
| 3.4 | Controllers | `HoraExtraController.cs` — Index | Filtro por `JefeInmediatoId` para Regente/AuxiliarRegente | ⏳ Pendiente |
| 3.5 | Controllers | `HoraExtraController.cs` — AprobarAjax/RechazarAjax | Validar jerarquía antes de aprobar/rechazar | ⏳ Pendiente |
| 3.6 | Controllers | `EventoLaboralController.cs` — Index | Filtro por `JefeInmediatoId` para Regente/AuxiliarRegente | ⏳ Pendiente |
| 3.7 | Controllers | `EventoLaboralController.cs` — RegistrarAjax/AnularAjax | Validar que el empleado es subordinado | ⏳ Pendiente |
| 3.8 | Controllers | `TurnoController.cs` — Index | Filtro de asignaciones por `JefeInmediatoId` | ⏳ Pendiente |
| 3.9 | Controllers | `TurnoController.cs` — AsignarTurnoAjax | Validar que el empleado es subordinado | ⏳ Pendiente |
| — | Build | Build Fase 3 | Verificar compilación | ⏳ Pendiente |
| 4.1 | Frontend | `_Layout.cshtml` — Dashboard | Mostrar ítem a Regente y AuxiliarRegente | ⏳ Pendiente |
| 4.2 | Frontend | `_Layout.cshtml` — Empleados | Cambiar a "Mi Perfil" con link directo para Operario | ⏳ Pendiente |
| — | Build | Build Fase 4 (Final) | Verificar compilación | ⏳ Pendiente |
| 5.1 | Tests | `conftest.py` | Ampliar `reset_estado_db` con Diana Vargas y Andrés Torres | ⏳ Pendiente |
| 5.2 | Tests | `helpers.py` | Agregar `hacer_login_completo`, `verificar_http` | ⏳ Pendiente |
| 5.3 | Tests | `test_permisos_jefe.py` | Crear — Scope A, 9 casos TC-PR-01 a TC-PR-09 | ⏳ Pendiente |
| 5.4 | Tests | `test_permisos_regente.py` | Crear — Scope B, 23 casos TC-PR-10 a TC-PR-32 | ⏳ Pendiente |
| 5.5 | Tests | `test_permisos_auxiliar.py` | Crear — Scope C, 14 casos TC-PR-33 a TC-PR-46 (Diana Vargas) | ⏳ Pendiente |
| 5.6 | Tests | `test_permisos_aux_regente.py` | Crear — Scope D, 10 casos TC-PR-47 a TC-PR-56 (Andrés Torres) | ⏳ Pendiente |
| 6.1 | Verificación | Levantar aplicación | `dotnet run --launch-profile http` | ⏳ Pendiente |
| 6.2 | Verificación | Ejecutar Scope A | `pytest test_permisos_jefe.py -v` | ⏳ Pendiente |
| 6.3 | Verificación | Ejecutar Scope B | `pytest test_permisos_regente.py -v` | ⏳ Pendiente |
| 6.4 | Verificación | Ejecutar Scope C | `pytest test_permisos_auxiliar.py -v` | ⏳ Pendiente |
| 6.5 | Verificación | Ejecutar Scope D | `pytest test_permisos_aux_regente.py -v` | ⏳ Pendiente |

**Total: 25 tareas de implementación + 5 builds/ejecuciones**

---

## Fase 1 — DTOs (`GestionPersonal.Models/DTOs/`)

> **Objetivo:** Exponer `JefeInmediatoId` en los DTOs de los módulos donde el filtro jerárquico aún no existe. Sin este campo, los controllers no pueden filtrar por jerarquía en memoria.

### Tarea 1.1 — `HoraExtraDto.cs`

**Ruta:** `GestionPersonal.Models/DTOs/HoraExtra/HoraExtraDto.cs`  
**Cambio:** Agregar propiedad `JefeInmediatoId`

```csharp
// Agregar junto a EmpleadoId
public int? JefeInmediatoId { get; init; }
```

**Criterio de done:** El archivo compila y `JefeInmediatoId` es accesible desde `HoraExtraController`.

---

### Tarea 1.2 — `EventoLaboralDto.cs`

**Ruta:** `GestionPersonal.Models/DTOs/EventoLaboral/EventoLaboralDto.cs`  
**Cambio:** Agregar propiedad `JefeInmediatoId`

```csharp
public int? JefeInmediatoId { get; init; }
```

**Criterio de done:** El archivo compila y `JefeInmediatoId` es accesible desde `EventoLaboralController`.

---

### Tarea 1.3 — `AsignacionTurnoDto.cs`

**Ruta:** `GestionPersonal.Models/DTOs/Turno/AsignacionTurnoDto.cs`  
**Cambio:** Agregar propiedad `JefeInmediatoId`

```csharp
public int? JefeInmediatoId { get; init; }
```

**Criterio de done:** El archivo compila y `JefeInmediatoId` es accesible desde `TurnoController`.

---

### ✅ Build Fase 1

```powershell
cd "...Proyecto MVC"
dotnet build GestionPersonal.slnx --no-incremental 2>&1 | Select-String "error CS|Build succeeded|FAILED"
```

**Criterio de done:** `Build succeeded` sin errores `error CS`.

---

## Fase 2 — Services (`GestionPersonal.Application/Services/`)

> **Objetivo:** Mapear `JefeInmediatoId` en los métodos de conversión de entidades a DTOs. Sin este mapeo, el campo queda null aunque exista en el DTO.

### Tarea 2.1 — `HoraExtraService.cs`

**Ruta:** `GestionPersonal.Application/Services/HoraExtraService.cs`  
**Método:** `MapToDto` (método privado estático al final del archivo)  
**Cambio:** Agregar asignación de `JefeInmediatoId` en el inicializador del DTO

```csharp
// Agregar en el return de MapToDto
JefeInmediatoId = h.Empleado?.JefeInmediatoId,
```

**Criterio de done:** Al obtener una hora extra, `HoraExtraDto.JefeInmediatoId` refleja el valor de `Empleado.JefeInmediatoId`.

---

### Tarea 2.2 — `EventoLaboralService.cs`

**Ruta:** `GestionPersonal.Application/Services/EventoLaboralService.cs`  
**Método:** `MapToDto` (método privado estático al final del archivo)  
**Cambio:** Agregar asignación de `JefeInmediatoId`

```csharp
JefeInmediatoId = e.Empleado?.JefeInmediatoId,
```

**Criterio de done:** `EventoLaboralDto.JefeInmediatoId` refleja el valor correcto de la entidad.

---

### Tarea 2.3 — `TurnoService.cs`

**Ruta:** `GestionPersonal.Application/Services/TurnoService.cs`  
**Método:** `ObtenerAsignacionesPorSedeAsync` (proyección `.Select(...)` sobre la lista de asignaciones)  
**Cambio:** Agregar `JefeInmediatoId` en la proyección del `AsignacionTurnoDto`

```csharp
JefeInmediatoId = a.Empleado.JefeInmediatoId,
```

**Criterio de done:** `AsignacionTurnoDto.JefeInmediatoId` refleja el valor correcto de `Empleado.JefeInmediatoId`.

---

### ✅ Build Fase 2

```powershell
dotnet build GestionPersonal.slnx --no-incremental 2>&1 | Select-String "error CS|Build succeeded|FAILED"
```

**Criterio de done:** `Build succeeded` sin errores.

---

## Fase 3 — Controllers (`GestionPersonal.Web/Controllers/`)

> **Objetivo:** Aplicar las reglas de acceso en cada action. Principio: leer `rol` y `empId` de los claims → aplicar `Forbid()` o filtro en memoria según corresponda.

### Tarea 3.1 — `EmpleadoController.cs` — Nuevo y Crear

**Ruta:** `GestionPersonal.Web/Controllers/EmpleadoController.cs`  
**Actions afectadas:** `Nuevo` (GET) y `Crear` (POST)  
**Cambio:** Agregar bloqueo para `Regente` y `AuxiliarRegente` junto al check de `Operario` ya existente

```csharp
// En Nuevo() y Crear(), inmediatamente después del check de Operario:
if (rol == RolUsuario.Regente || rol == RolUsuario.AuxiliarRegente)
    return Forbid();
```

**Criterio de done:** `GET /Empleado/Nuevo` devuelve HTTP 403 cuando el usuario es Laura (Regente) o Andrés Torres (AuxiliarRegente).

---

### Tarea 3.2 — `EmpleadoController.cs` — Editar y Actualizar

**Ruta:** `GestionPersonal.Web/Controllers/EmpleadoController.cs`  
**Actions afectadas:** `Editar` (GET) y `Actualizar` (POST)  
**Cambio:** Después del check de `Operario`, agregar validación de jerarquía

```csharp
if (rol == RolUsuario.Regente || rol == RolUsuario.AuxiliarRegente)
{
    var miEmpleadoId = SesionHelper.GetEmpleadoId(User);
    if (!miEmpleadoId.HasValue) return Forbid();

    var objetivo = await _empleadoService.ObtenerPerfilAsync(id);
    if (!objetivo.Exito || objetivo.Datos is null) return NotFound();

    var esPropio      = objetivo.Datos.Id == miEmpleadoId.Value;
    var esSubordinado = objetivo.Datos.JefeInmediatoId == miEmpleadoId.Value;
    if (!esPropio && !esSubordinado)
        return Forbid();
}
```

> En `Actualizar` (POST), el `id` se obtiene de `vm.Dto.Id`.

**Criterio de done:** `GET /Empleado/Editar/1` (Carlos) devuelve 403 para Laura; `GET /Empleado/Editar/5` (Diana, subordinada) devuelve 200 para Laura.

---

### Tarea 3.3 — `EmpleadoController.cs` — Perfil

**Ruta:** `GestionPersonal.Web/Controllers/EmpleadoController.cs`  
**Action afectada:** `Perfil` (GET)  
**Cambio:** Después del check de `Operario`, agregar validación de jerarquía para Regente/AuxiliarRegente

```csharp
if (rol == RolUsuario.Regente || rol == RolUsuario.AuxiliarRegente)
{
    var miEmpleadoId = SesionHelper.GetEmpleadoId(User);
    if (!miEmpleadoId.HasValue) return Forbid();

    var objetivo = await _empleadoService.ObtenerPerfilAsync(id);
    if (!objetivo.Exito || objetivo.Datos is null) return NotFound();

    var esPropio      = objetivo.Datos.Id == miEmpleadoId.Value;
    var esSubordinado = objetivo.Datos.JefeInmediatoId == miEmpleadoId.Value;
    if (!esPropio && !esSubordinado)
        return Forbid();
}
```

**Criterio de done:** `GET /Empleado/Perfil/1` devuelve 403 para Laura; `GET /Empleado/Perfil/2` devuelve 200 para Laura (su propio perfil).

---

### Tarea 3.4 — `HoraExtraController.cs` — Index

**Ruta:** `GestionPersonal.Web/Controllers/HoraExtraController.cs`  
**Action afectada:** `Index` (GET)  
**Cambio:** Agregar filtro por `JefeInmediatoId` después de la obtención inicial de `todos`

```csharp
// Agregar inmediatamente después de que 'todos' es asignado (tras el if Operario):
if ((rol == RolUsuario.Regente || rol == RolUsuario.AuxiliarRegente) && empId.HasValue)
    todos = todos.Where(h =>
        h.EmpleadoId == empId.Value ||
        h.JefeInmediatoId == empId.Value
    ).ToList();
```

**Criterio de done:** Laura solo ve las HE de sí misma y sus subordinados directos (Diana, Jorge, Andrés Torres).

---

### Tarea 3.5 — `HoraExtraController.cs` — AprobarAjax y RechazarAjax

**Ruta:** `GestionPersonal.Web/Controllers/HoraExtraController.cs`  
**Actions afectadas:** `AprobarAjax` (POST) y `RechazarAjax` (POST)  
**Cambio:** Agregar validación de jerarquía antes de delegar al service

```csharp
// Agregar al inicio de AprobarAjax y RechazarAjax, antes de llamar al service:
var rol   = SesionHelper.GetRol(User);
var empId = SesionHelper.GetEmpleadoId(User);

if (rol == RolUsuario.Regente || rol == RolUsuario.AuxiliarRegente)
{
    if (!empId.HasValue) return Json(new { exito = false, mensaje = "Sin permisos." });
    var lista = await _horaExtraService.ObtenerPorEmpleadoAsync(id);
    // Obtener la HE por id para verificar el JefeInmediatoId
    var heTarget = (await _horaExtraService.ObtenerPorSedeAsync(SesionHelper.GetSedeId(User)))
                   .FirstOrDefault(h => h.Id == id);
    if (heTarget is null || heTarget.JefeInmediatoId != empId.Value)
        return Json(new { exito = false, mensaje = "No tienes permisos para gestionar esta hora extra." });
}
```

> **Nota de implementación:** Se requiere exponer `ObtenerPorIdAsync` en `IHoraExtraService` o usar el listado de sede + filtro por `id`. Preferir lo que ya exista en la interfaz para no ampliar el scope.

**Criterio de done:** POST a `AprobarAjax` con id de HE de Carlos devuelve `{ exito: false }` para Laura.

---

### Tarea 3.6 — `EventoLaboralController.cs` — Index

**Ruta:** `GestionPersonal.Web/Controllers/EventoLaboralController.cs`  
**Action afectada:** `Index` (GET)  
**Cambio:** Agregar filtro por `JefeInmediatoId` después de `ObtenerPorSedeAsync`

```csharp
// Agregar lectura de empId al inicio del action:
var empId = SesionHelper.GetEmpleadoId(User);

// Agregar después de: var todos = await _eventoService.ObtenerPorSedeAsync(sedeId);
if ((rol == RolUsuario.Regente || rol == RolUsuario.AuxiliarRegente) && empId.HasValue)
    todos = todos.Where(e =>
        e.EmpleadoId == empId.Value ||
        e.JefeInmediatoId == empId.Value
    ).ToList();
```

**Criterio de done:** Laura solo ve eventos de sí misma y sus subordinados.

---

### Tarea 3.7 — `EventoLaboralController.cs` — RegistrarAjax y AnularAjax

**Ruta:** `GestionPersonal.Web/Controllers/EventoLaboralController.cs`  
**Actions afectadas:** `RegistrarAjax` (POST) y `AnularAjax` (POST)

**Cambio en `RegistrarAjax`:** Validar que el empleado del DTO pertenece a la jerarquía del usuario

```csharp
var rol   = SesionHelper.GetRol(User);
var empId = SesionHelper.GetEmpleadoId(User);

if (rol == RolUsuario.Regente || rol == RolUsuario.AuxiliarRegente)
{
    if (!empId.HasValue)
        return Json(new { exito = false, mensaje = "Sin permisos." });

    var empObjetivo = await _empleadoService.ObtenerPerfilAsync(dto.EmpleadoId);
    if (!empObjetivo.Exito || empObjetivo.Datos is null)
        return Json(new { exito = false, mensaje = "Empleado no encontrado." });

    var esPropio      = empObjetivo.Datos.Id == empId.Value;
    var esSubordinado = empObjetivo.Datos.JefeInmediatoId == empId.Value;
    if (!esPropio && !esSubordinado)
        return Json(new { exito = false, mensaje = "No puedes registrar eventos para este empleado." });
}
```

**Cambio en `AnularAjax`:** Validar que el evento pertenece a un empleado de su jerarquía

```csharp
var rol   = SesionHelper.GetRol(User);
var empId = SesionHelper.GetEmpleadoId(User);

if (rol == RolUsuario.Regente || rol == RolUsuario.AuxiliarRegente)
{
    if (!empId.HasValue)
        return Json(new { exito = false, mensaje = "Sin permisos." });

    var todos = await _eventoService.ObtenerPorSedeAsync(SesionHelper.GetSedeId(User));
    var eventoTarget = todos.FirstOrDefault(e => e.Id == id);
    if (eventoTarget is null || (eventoTarget.EmpleadoId != empId.Value && eventoTarget.JefeInmediatoId != empId.Value))
        return Json(new { exito = false, mensaje = "No puedes anular este evento." });
}
```

**Criterio de done:** POST a `RegistrarAjax` con `EmpleadoId=1` (Carlos) devuelve `{ exito: false }` para Laura.

---

### Tarea 3.8 — `TurnoController.cs` — Index

**Ruta:** `GestionPersonal.Web/Controllers/TurnoController.cs`  
**Action afectada:** `Index` (GET)  
**Cambio:** Agregar lectura de `rol` y `empId`, y filtro de asignaciones por jerarquía

```csharp
// Agregar al inicio del action (actualmente no lee rol ni empId):
var rol   = SesionHelper.GetRol(User);
var empId = SesionHelper.GetEmpleadoId(User);

// Agregar después de: var asignaciones = await _turnoService.ObtenerAsignacionesPorSedeAsync(sedeId);
if ((rol == RolUsuario.Regente || rol == RolUsuario.AuxiliarRegente) && empId.HasValue)
    asignaciones = asignaciones.Where(a =>
        a.EmpleadoId == empId.Value ||
        a.JefeInmediatoId == empId.Value
    ).ToList();
```

**Criterio de done:** Laura solo ve las asignaciones de turno de sí misma y sus subordinados.

---

### Tarea 3.9 — `TurnoController.cs` — AsignarTurnoAjax

**Ruta:** `GestionPersonal.Web/Controllers/TurnoController.cs`  
**Action afectada:** `AsignarTurnoAjax` (POST)  
**Cambio:** Agregar validación de jerarquía antes de delegar al service

```csharp
var rol   = SesionHelper.GetRol(User);
var empId = SesionHelper.GetEmpleadoId(User);

if (rol == RolUsuario.Regente || rol == RolUsuario.AuxiliarRegente)
{
    if (!empId.HasValue)
        return Json(new { exito = false, mensaje = "Sin permisos." });

    var empObjetivo = await _empleadoService.ObtenerPerfilAsync(dto.EmpleadoId);
    if (!empObjetivo.Exito || empObjetivo.Datos is null)
        return Json(new { exito = false, mensaje = "Empleado no encontrado." });

    var esPropio      = empObjetivo.Datos.Id == empId.Value;
    var esSubordinado = empObjetivo.Datos.JefeInmediatoId == empId.Value;
    if (!esPropio && !esSubordinado)
        return Json(new { exito = false, mensaje = "No puedes asignar turnos a este empleado." });
}
```

**Criterio de done:** POST a `AsignarTurnoAjax` con `EmpleadoId=1` (Carlos) devuelve `{ exito: false }` para Laura.

---

### ✅ Build Fase 3

```powershell
dotnet build GestionPersonal.slnx --no-incremental 2>&1 | Select-String "error CS|Build succeeded|FAILED"
```

**Criterio de done:** `Build succeeded` sin errores.

---

## Fase 4 — Frontend (`GestionPersonal.Web/Views/Shared/_Layout.cshtml`)

### Tarea 4.1 — Dashboard visible para Regente y AuxiliarRegente

**Ruta:** `GestionPersonal.Web/Views/Shared/_Layout.cshtml`  
**Línea actual:** `@if (User.IsInRole("Jefe") || User.IsInRole("Administrador"))`  
**Cambio:** Ampliar la condición para incluir `Regente` y `AuxiliarRegente`

```html
@if (User.IsInRole("Jefe") || User.IsInRole("Administrador")
     || User.IsInRole("Regente") || User.IsInRole("AuxiliarRegente"))
{
  <!-- bloque del link Dashboard — sin cambios internos -->
}
```

**Criterio de done:** Al iniciar sesión como Laura, el ítem "Dashboard" aparece en el sidebar.

---

### Tarea 4.2 — Ítem "Empleados" → "Mi Perfil" para Operario

**Ruta:** `GestionPersonal.Web/Views/Shared/_Layout.cshtml`  
**Cambio:** Envolver el link de Empleados en una condición que diferencie Operario del resto

```html
@if (User.IsInRole("Operario"))
{
  <a asp-controller="Empleado" asp-action="Perfil"
     asp-route-id="@User.FindFirstValue("EmpleadoId")"
     class="@NavClass("Empleado")"
     aria-current="@(ctrl == "Empleado" ? "page" : null)">
    <!-- mismo SVG del icono actual -->
    <span class="nav-text">Mi Perfil</span>
  </a>
}
else
{
  <a asp-controller="Empleado" asp-action="Index"
     class="@NavClass("Empleado")"
     aria-current="@(ctrl == "Empleado" ? "page" : null)">
    <!-- mismo SVG del icono actual -->
    <span class="nav-text">Empleados</span>
  </a>
}
```

**Criterio de done:** Al iniciar sesión como Diana Vargas (Operario), el sidebar muestra "Mi Perfil" con link a `/Empleado/Perfil/5`.

---

### ✅ Build Fase 4 (Build Final)

```powershell
dotnet build GestionPersonal.slnx --no-incremental 2>&1 | Select-String "error CS|Build succeeded|FAILED"
```

**Criterio de done:** `Build succeeded`. El proyecto compila limpiamente con todos los cambios aplicados.

---

## Fase 5 — Tests Playwright (`Tests/`)

> Los tests se crean usando el patrón establecido en `test_xcargo.py`. Se mantiene coherencia en estructura de fixtures, helpers, y nomenclatura.

### Tarea 5.1 — `conftest.py` — Ampliar reset de BD

**Ruta:** `Tests/conftest.py`  
**Cambio:** Agregar reset de `DebeCambiarPassword = 0` para `diana.vargas@yopmail.com` y `andres.torres@yopmail.com` en la fixture `reset_estado_db` existente.

**Criterio de done:** Al ejecutar cualquier scope de pruebas, todos los usuarios de prueba tienen `DebeCambiarPassword = 0` y pueden hacer login sin flujo de cambio de contraseña.

---

### Tarea 5.2 — `helpers.py` — Agregar funciones de soporte

**Ruta:** `Tests/helpers.py`  
**Cambio:** Agregar las siguientes funciones al archivo existente

```python
def hacer_login_completo(page, correo: str, password: str, nueva_password: str = "NuevaClave2026!"):
    """Login con manejo automático del flujo CambiarPassword si DebeCambiarPassword=1."""
    hacer_login(page, correo, password)
    if "/Cuenta/CambiarPassword" in page.url:
        page.fill("#Dto_PasswordActual", password)
        page.fill("#Dto_NuevoPassword", nueva_password)
        page.fill("#Dto_ConfirmarPassword", nueva_password)
        page.click("button[type=submit]")
        page.wait_for_load_state("networkidle")


def verificar_acceso_http(page, url: str) -> int:
    """Navega a una URL y retorna el código HTTP efectivo (200, 403, 404)."""
    response = page.goto(f"{BASE_URL}{url}")
    page.wait_for_load_state("networkidle")
    return response.status if response else 0


def elemento_sidebar_visible(page, texto: str) -> bool:
    """Verifica si un ítem del sidebar es visible por su texto."""
    return page.locator(f".sidebar-nav a:has-text('{texto}')").is_visible()
```

**Criterio de done:** Las funciones están disponibles para importar desde los archivos de test.

---

### Tarea 5.3 — `test_permisos_jefe.py` — Scope A (9 casos)

**Ruta:** `Tests/test_permisos_jefe.py` (archivo nuevo)  
**Usuario:** Carlos Alberto Rodríguez Mora — `carlos.rodriguez@yopmail.com`  
**Casos:** TC-PR-01 al TC-PR-09

| Caso | Test function | Acción | Assert |
|---|---|---|---|
| TC-PR-01 | `test_tc_pr_01_dashboard_accesible` | GET `/Dashboard` | Status 200 + selector de KPIs visible |
| TC-PR-02 | `test_tc_pr_02_ve_todo_personal` | GET `/Empleado` | Filas en tabla ≥ total de empleados de la sede |
| TC-PR-03 | `test_tc_pr_03_puede_crear` | GET `/Empleado/Nuevo` | Status 200 |
| TC-PR-04 | `test_tc_pr_04_puede_editar_cualquiera` | GET `/Empleado/Editar/5` | Status 200 |
| TC-PR-05 | `test_tc_pr_05_ve_eventos` | GET `/EventoLaboral` | Tabla visible, sin redirect |
| TC-PR-06 | `test_tc_pr_06_ve_turnos` | GET `/Turno` | Tabla visible, sin redirect |
| TC-PR-07 | `test_tc_pr_07_ve_horas_extras` | GET `/HoraExtra` | Tabla visible, sin redirect |
| TC-PR-08 | `test_tc_pr_08_accede_catalogos` | GET `/Catalogos` | Status 200 |
| TC-PR-09 | `test_tc_pr_09_menu_completo` | Inspeccionar sidebar | Dashboard, Empleados, Eventos, Turnos, HE, Catálogos visibles |

**Criterio de done:** Los 9 tests pasan en verde.

---

### Tarea 5.4 — `test_permisos_regente.py` — Scope B (23 casos)

**Ruta:** `Tests/test_permisos_regente.py` (archivo nuevo)  
**Usuario:** Laura Patricia Sánchez Gómez — `laura.sanchez@yopmail.com`  
**Casos:** TC-PR-10 al TC-PR-32

| Caso | Test function | Assert clave |
|---|---|---|
| TC-PR-10 | `test_tc_pr_10_dashboard_visible_menu` | `elemento_sidebar_visible(page, "Dashboard")` = True |
| TC-PR-11 | `test_tc_pr_11_dashboard_accesible` | Status 200 en `/Dashboard` |
| TC-PR-12 | `test_tc_pr_12_solo_ve_subordinados` | Filas en tabla = 4 (Laura + 3 subordinados activos) |
| TC-PR-13 | `test_tc_pr_13_no_ve_jefe` | Buscar "Carlos" → 0 resultados |
| TC-PR-14 | `test_tc_pr_14_no_ve_otro_regente` | Buscar "Hernán" → 0 resultados |
| TC-PR-15 | `test_tc_pr_15_no_puede_crear` | GET `/Empleado/Nuevo` → Status 403 |
| TC-PR-16 | `test_tc_pr_16_puede_editar_subordinado` | GET `/Empleado/Editar/5` → Status 200 |
| TC-PR-17 | `test_tc_pr_17_no_puede_editar_jefe` | GET `/Empleado/Editar/1` → Status 403 |
| TC-PR-18 | `test_tc_pr_18_no_puede_editar_ajeno` | GET `/Empleado/Editar/7` → Status 403 |
| TC-PR-19 | `test_tc_pr_19_eventos_solo_subordinados` | No aparecen Carlos, Natalia en la tabla |
| TC-PR-20 | `test_tc_pr_20_no_eventos_ajenos` | Count de Carlos/Natalia/Paula = 0 |
| TC-PR-21 | `test_tc_pr_21_registra_evento_subordinado` | POST RegistrarAjax EmpleadoId=5 → `exito: true` |
| TC-PR-22 | `test_tc_pr_22_no_registra_evento_ajeno` | POST RegistrarAjax EmpleadoId=1 → `exito: false` |
| TC-PR-23 | `test_tc_pr_23_turnos_solo_subordinados` | Solo asignaciones de subordinados visibles |
| TC-PR-24 | `test_tc_pr_24_no_turnos_ajenos` | Carlos no aparece en tabla de turnos |
| TC-PR-25 | `test_tc_pr_25_asigna_turno_subordinado` | POST AsignarTurnoAjax EmpleadoId=5 → `exito: true` |
| TC-PR-26 | `test_tc_pr_26_no_asigna_turno_ajeno` | POST AsignarTurnoAjax EmpleadoId=1 → `exito: false` |
| TC-PR-27 | `test_tc_pr_27_he_propias_y_subordinados` | Solo HE de Laura, Diana, Jorge, Andrés visibles |
| TC-PR-28 | `test_tc_pr_28_no_he_ajenas` | Carlos no aparece en tabla de HE |
| TC-PR-29 | `test_tc_pr_29_aprueba_he_subordinado` | POST AprobarAjax con HE de Diana → `exito: true` |
| TC-PR-30 | `test_tc_pr_30_no_aprueba_he_ajena` | POST AprobarAjax con HE de Carlos → `exito: false` |
| TC-PR-31 | `test_tc_pr_31_no_ve_catalogos_menu` | `elemento_sidebar_visible(page, "Catálogos")` = False |
| TC-PR-32 | `test_tc_pr_32_no_accede_catalogos_url` | GET `/Catalogos` → Status 403 |

**Criterio de done:** Los 23 tests pasan en verde.

---

### Tarea 5.5 — `test_permisos_auxiliar.py` — Scope C (14 casos)

**Ruta:** `Tests/test_permisos_auxiliar.py` (archivo nuevo)  
**Usuario:** Diana Marcela Vargas López — `diana.vargas@yopmail.com` — EmpleadoId = 5  
**Casos:** TC-PR-33 al TC-PR-46

| Caso | Test function | Assert clave |
|---|---|---|
| TC-PR-33 | `test_tc_pr_33_dashboard_no_visible` | `elemento_sidebar_visible(page, "Dashboard")` = False |
| TC-PR-34 | `test_tc_pr_34_menu_mi_perfil` | Sidebar tiene link con texto "Mi Perfil" apuntando a `/Empleado/Perfil/5` |
| TC-PR-35 | `test_tc_pr_35_redirige_perfil` | GET `/Empleado` → URL final contiene `/Empleado/Perfil/5` |
| TC-PR-36 | `test_tc_pr_36_no_perfil_otro` | GET `/Empleado/Perfil/1` → Status 403 |
| TC-PR-37 | `test_tc_pr_37_no_puede_crear` | GET `/Empleado/Nuevo` → Status 403 |
| TC-PR-38 | `test_tc_pr_38_no_edita_otros` | GET `/Empleado/Editar/1` → Status 403 |
| TC-PR-39 | `test_tc_pr_39_eventos_ocultos_menu` | `elemento_sidebar_visible(page, "Eventos")` = False |
| TC-PR-40 | `test_tc_pr_40_no_accede_eventos_url` | GET `/EventoLaboral` → Status 403 o redirect |
| TC-PR-41 | `test_tc_pr_41_turnos_ocultos_menu` | `elemento_sidebar_visible(page, "Horarios")` = False |
| TC-PR-42 | `test_tc_pr_42_no_accede_turnos_url` | GET `/Turno` → Status 403 |
| TC-PR-43 | `test_tc_pr_43_solo_propias_he` | GET `/HoraExtra` → Solo HE con nombre de Diana |
| TC-PR-44 | `test_tc_pr_44_no_puede_aprobar_he` | POST AprobarAjax con id de HE propia → `exito: false` |
| TC-PR-45 | `test_tc_pr_45_catalogos_ocultos_menu` | `elemento_sidebar_visible(page, "Catálogos")` = False |
| TC-PR-46 | `test_tc_pr_46_no_accede_catalogos_url` | GET `/Catalogos` → Status 403 |

**Criterio de done:** Los 14 tests pasan en verde.

---

### Tarea 5.6 — `test_permisos_aux_regente.py` — Scope D (10 casos)

**Ruta:** `Tests/test_permisos_aux_regente.py` (archivo nuevo)  
**Usuario:** Andrés Felipe Torres Ruiz — `andres.torres@yopmail.com` — EmpleadoId = 4  
**Casos:** TC-PR-47 al TC-PR-56

> Andrés Torres es `AuxiliarRegente` y subordinado directo de Laura. **Verificar en seeding** si Andrés tiene subordinados propios (JefeInmediatoId = 4). Si no los tiene, las pruebas de "ver solo subordinados" se ajustan para validar que ve solo su propio perfil.

| Caso | Test function | Equivalente Scope B | Assert clave |
|---|---|---|---|
| TC-PR-47 | `test_tc_pr_47_dashboard_visible` | TC-PR-10 | Dashboard visible en sidebar |
| TC-PR-48 | `test_tc_pr_48_solo_ve_subordinados` | TC-PR-12 | Solo empleados con `JefeInmediatoId=4` o él mismo |
| TC-PR-49 | `test_tc_pr_49_no_puede_crear` | TC-PR-15 | GET `/Empleado/Nuevo` → 403 |
| TC-PR-50 | `test_tc_pr_50_no_edita_jefe` | TC-PR-17 | GET `/Empleado/Editar/1` → 403 |
| TC-PR-51 | `test_tc_pr_51_eventos_solo_subordinados` | TC-PR-19 | Solo eventos propios y de subordinados |
| TC-PR-52 | `test_tc_pr_52_turnos_solo_subordinados` | TC-PR-23 | Solo asignaciones propias y de subordinados |
| TC-PR-53 | `test_tc_pr_53_he_propias_y_subordinados` | TC-PR-27 | Solo HE propias y de subordinados |
| TC-PR-54 | `test_tc_pr_54_aprueba_he_subordinado` | TC-PR-29 | POST AprobarAjax con HE de subordinado → `exito: true` (o skip si no tiene subordinados) |
| TC-PR-55 | `test_tc_pr_55_no_ve_catalogos_menu` | TC-PR-31 | Catálogos no visible en sidebar |
| TC-PR-56 | `test_tc_pr_56_no_accede_catalogos_url` | TC-PR-32 | GET `/Catalogos` → 403 |

**Criterio de done:** Los 10 tests pasan en verde.

---

## Fase 6 — Verificación y Ejecución

### Tarea 6.1 — Levantar la aplicación

```powershell
cd "c:\Users\alejandro.ortiz\Documents\helpharma\Desarrollos\lissy\IA\LissyIAHelpharma\empleados v2\Proyecto MVC"
dotnet run --project GestionPersonal.Web/GestionPersonal.Web.csproj --launch-profile http
```

**Criterio de done:** `Now listening on: http://localhost:5002` en la consola.

---

### Tarea 6.2 — Ejecutar Scope A (Jefe)

```powershell
cd "c:\Users\alejandro.ortiz\Documents\helpharma\Desarrollos\lissy\IA\LissyIAHelpharma\empleados v2"
.\.venv\Scripts\python.exe -m pytest Tests/test_permisos_jefe.py -v
```

**Criterio de done:** 9/9 PASSED.

---

### Tarea 6.3 — Ejecutar Scope B (Regente)

```powershell
.\.venv\Scripts\python.exe -m pytest Tests/test_permisos_regente.py -v
```

**Criterio de done:** 23/23 PASSED.

---

### Tarea 6.4 — Ejecutar Scope C (Auxiliar de Farmacia)

```powershell
.\.venv\Scripts\python.exe -m pytest Tests/test_permisos_auxiliar.py -v
```

**Criterio de done:** 14/14 PASSED.

---

### Tarea 6.5 — Ejecutar Scope D (Auxiliar Regente)

```powershell
.\.venv\Scripts\python.exe -m pytest Tests/test_permisos_aux_regente.py -v
```

**Criterio de done:** 10/10 PASSED.

---

## Definición Global de "Done"

El ciclo se considera **completo** cuando:

1. `dotnet build GestionPersonal.slnx` → `Build succeeded` sin errores `error CS`
2. **56 casos** de prueba Playwright pasan en verde (9 + 23 + 14 + 10)
3. No existe ningún endpoint de la lista de pendientes que devuelva datos fuera del ámbito jerárquico del usuario autenticado
4. Ningún acceso por URL directa (sin menú) vulnera la restricción del cargo

---

## Notas para la Ejecución

- **No modificar** `conftest.py` de forma que rompa los tests existentes (`test_login.py`, `test_xcargo.py`, etc.). Solo agregar al fixture existente.
- Si una fase produce errores de compilación, detener y corregir antes de continuar con la siguiente.
- Si un test falla después de implementar el código, corregir el código (no el test).
- La tarea **3.5 (HoraExtraController — AprobarAjax/RechazarAjax)** requiere revisar la interfaz `IHoraExtraService` antes de implementar. Notificar al usuario si se necesita ampliar el scope.
