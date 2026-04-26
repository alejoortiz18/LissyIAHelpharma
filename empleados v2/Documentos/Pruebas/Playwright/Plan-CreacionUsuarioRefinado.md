# Plan Refinado — Ajuste al Formulario de Creación de Empleado
## Sistema de Administración de Empleados — GestionPersonal

> **Basado en:** `Documentos/Requerimientos/RequerimientoCreacionUsuario.md`  
> **Metodología:** Shape Up (Basecamp) — https://basecamp.com/shapeup  
> **Ejecutor:** GitHub Copilot (requiere aprobación previa del usuario)  
> **Orden de implementación:** DTO → Service → View/JS → Tests → Verificación  
> **Granularidad:** Una tarea por archivo modificado  
> **Verificación:** Build por fase  
> **Última actualización:** Abril 2026

---

## Resumen del Pitch

| Ingrediente | Síntesis |
|---|---|
| **Problema** | EPS y Contacto de emergencia son obligatorios pero no siempre disponibles al registrar un empleado, forzando datos falsos (ej. `"Pendiente"`). El formulario tampoco diferencia campos según tipo de vinculación. |
| **Appetite** | Small Batch — 1 semana · 1 programador |
| **Solución** | EPS y ContactoEmergencia pasan a opcionales. Al elegir Contrato Directo: FechaIngreso visible y obligatoria, bloque temporal oculto. Al elegir Empresa Temporal: FechaIngreso oculta, bloque temporal visible. |
| **Rabbit Holes** | ContactoEmergencia como entidad separada; FechaIngreso NOT NULL en BD (se resuelve asignando FechaInicioContrato); validación server-side sin JS. |
| **No-Gos** | Sin cambio de esquema de BD, sin rediseño del formulario, sin nuevos campos. |

---

## Estado actual del código (diagnóstico)

| Elemento | Archivo | Estado actual | Acción requerida |
|---|---|---|---|
| `Eps` en `CrearEmpleadoDto` | `GestionPersonal.Models/DTOs/Empleado/CrearEmpleadoDto.cs` | `[Required]` — bloquea si vacío | Quitar `[Required]`; hacer `string?` |
| `ContactoEmergenciaNombre` en `CrearEmpleadoDto` | Ídem | `[Required]` — bloquea si vacío | Quitar `[Required]`; hacer `string?` |
| `ContactoEmergenciaTelefono` en `CrearEmpleadoDto` | Ídem | `[Required]` — bloquea si vacío | Quitar `[Required]`; hacer `string?` |
| `FechaIngreso` en `CrearEmpleadoDto` | Ídem | `[Required]` `DateOnly` (no nullable) | Hacer `DateOnly?`; validar en Service solo si Directo |
| `Eps` en `EditarEmpleadoDto` | `GestionPersonal.Models/DTOs/Empleado/EditarEmpleadoDto.cs` | `[Required]` | Quitar `[Required]`; hacer `string?` |
| `ContactoEmergenciaNombre/Telefono` en `EditarEmpleadoDto` | Ídem | `[Required]` | Quitar `[Required]`; hacer `string?` |
| `FechaIngreso` en `EditarEmpleadoDto` | Ídem | `DateOnly` no nullable | Hacer `DateOnly?`; validar condicionalmente |
| `CrearAsync` en `EmpleadoService` | `GestionPersonal.Application/Services/EmpleadoService.cs` | Crea `ContactoEmergencia` siempre | Crear solo si al menos un campo tiene valor; FechaIngreso = FechaInicioContrato si Temporal |
| `EditarAsync` en `EmpleadoService` | Ídem | Actualiza `ContactoEmergencia` siempre | Manejar caso nullable; validar FechaIngreso condicionalmente |
| **Validación cédula duplicada** | `EmpleadoService.cs` | ✅ Ya existe (`ExisteCedulaAsync`) — mensaje: *"Ya existe un empleado registrado con esa cédula."* | Solo agregar cobertura de tests |
| **Validación correo duplicado (Empleados)** | `EmpleadoService.cs` | ❌ **No existe** — solo el `UsuarioService` valida correo en tabla `Usuarios`; si `Empleados.CorreoElectronico` duplicado, la BD lanza excepción no controlada | Agregar `ExisteCorreoAsync` en `CrearAsync` antes de crear el usuario + constante `CorreoElectronicoDuplicado` |
| **Constante `CorreoElectronicoDuplicado`** | `GestionPersonal.Constants/Messages/EmpleadoConstant.cs` | ❌ **No existe** | Agregar constante con mensaje de error |
| `*` en EPS — Nuevo | `GestionPersonal.Web/Views/Empleado/Nuevo.cshtml` | Muestra asterisco `*` (obligatorio) | Quitar asterisco |
| `*` en ContactoEmergencia — Nuevo | Ídem | Muestra asterisco `*` en ambos campos | Quitar asteriscos |
| JS toggle `FechaIngreso` — Nuevo | Ídem | **No existe** — FechaIngreso siempre visible | Agregar `<script>` toggle; envolver FechaIngreso en `#seccion-fecha-ingreso` |
| JS toggle `#seccion-temporal` — Nuevo | Ídem | **No existe** — `#seccion-temporal` fijo como `hidden` | Agregar JS que muestre/oculte según selector |
| `*` en EPS — Editar | `GestionPersonal.Web/Views/Empleado/Editar.cshtml` | Muestra asterisco `*` | Quitar asterisco |
| `*` en ContactoEmergencia — Editar | Ídem | Muestra asterisco `*` en ambos campos | Quitar asteriscos |
| JS toggle `FechaIngreso` — Editar | Ídem | JS oculta `#seccion-temporal` pero no FechaIngreso | Extender JS para ocultar también `#seccion-fecha-ingreso` si Temporal |

---

## Usuarios de prueba

| Nombre | Correo | Password | Rol | Uso en tests |
|---|---|---|---|---|
| Carlos Alberto Rodríguez Mora | `carlos.rodriguez@yopmail.com` | `Usuario1` | Jefe | Crea empleados (único rol habilitado) |

> **Cédulas reservadas para pruebas:** `12345001` (Directo), `12345002` (Temporal)  
> Ambas cédulas se eliminan de la BD al finalizar cada test mediante la fixture `limpiar_empleado_prueba`.  
> **Empresa temporal disponible:** ManpowerGroup Colombia (en seeding).  
> **Sede de prueba:** Medellín (sede del Jefe).

---

## Prerequisitos (verificar antes de ejecutar)

- [ ] Seeding `Documentos/BD/Seeding_Completo.sql` aplicado en `(localdb)\MSSQLLocalDB`
- [ ] Proyecto compila sin errores: `dotnet build "Proyecto MVC/GestionPersonal.slnx"`
- [ ] Aplicación levanta en `http://localhost:5002`
- [ ] Entorno virtual Python activo: `.venv\Scripts\Activate.ps1`
- [ ] `pytest-playwright` instalado: `pip install pytest-playwright`

---

## Resumen de Tareas

| # | Fase | Archivo | Descripción | Estado |
|---|---|---|---|---|
| 1.1 | DTO Crear | `CrearEmpleadoDto.cs` | Quitar `[Required]` de Eps, Contacto; hacer FechaIngreso nullable | ⏳ Pendiente |
| 1.2 | DTO Editar | `EditarEmpleadoDto.cs` | Mismos cambios que 1.1 | ⏳ Pendiente |
| — | Build | Build Fase 1 | Verificar compilación | ⏳ Pendiente |
| 2.1 | Service | `EmpleadoService.CrearAsync` | FechaIngreso condicional + ContactoEmergencia nullable | ⏳ Pendiente |
| 2.2 | Service | `EmpleadoService.EditarAsync` | Ídem — ContactoEmergencia nullable en edición | ⏳ Pendiente |
| 2.3 | Service + Constante | `EmpleadoService.CrearAsync` + `EmpleadoConstant.cs` | Agregar `ExisteCorreoAsync` check + constante `CorreoElectronicoDuplicado` | ⏳ Pendiente |
| — | Build | Build Fase 2 | Verificar compilación | ⏳ Pendiente |
| 3.1 | View | `Nuevo.cshtml` | Quitar `*` de EPS y Contacto; envolver FechaIngreso en `#seccion-fecha-ingreso` | ⏳ Pendiente |
| 3.2 | JS | `Nuevo.cshtml` | Agregar `<script>` para toggle de FechaIngreso y #seccion-temporal | ⏳ Pendiente |
| 3.3 | View | `Editar.cshtml` | Quitar `*` de EPS y Contacto; envolver FechaIngreso en `#seccion-fecha-ingreso` | ⏳ Pendiente |
| 3.4 | JS | `Editar.cshtml` | Extender `<script>` existente para ocultar también `#seccion-fecha-ingreso` | ⏳ Pendiente |
| — | Build | Build Fase 3 (final) | Verificar compilación | ⏳ Pendiente |
| 4.1 | Tests | `conftest.py` | Agregar fixture `limpiar_empleado_prueba` | ⏳ Pendiente |
| 4.2 | Tests | `test_creacion_usuario.py` | Crear archivo con 14 casos (TC-CRE-01 a TC-CRE-14) | ⏳ Pendiente |
| 5.1 | Verificación | Levantar aplicación | `dotnet run --launch-profile http` | ⏳ Pendiente |
| 5.2 | Verificación | Ejecutar tests | `pytest Tests/test_creacion_usuario.py -v --headed --slowmo 800 -s` | ⏳ Pendiente |

**Total: 9 tareas de implementación + 3 builds + 2 verificaciones**

---

## Fase 1 — DTOs (`GestionPersonal.Models/DTOs/Empleado/`)

> **Objetivo:** Quitar restricciones `[Required]` de los campos que pasan a ser opcionales y hacer `FechaIngreso` nullable para que el model binding no rechace el formulario en el servidor antes de llegar al Service.

### Tarea 1.1 — `CrearEmpleadoDto.cs`

**Ruta:** `Proyecto MVC/GestionPersonal.Models/DTOs/Empleado/CrearEmpleadoDto.cs`

**Cambios:**

```csharp
// ANTES — Eps (línea ~57):
[Required(ErrorMessage = "La EPS es obligatoria.")]
[StringLength(200)]
public string Eps { get; set; } = null!;

// DESPUÉS:
[StringLength(200)]
public string? Eps { get; set; }

// ─────────────────────────────────────────────────────────────────────

// ANTES — ContactoEmergenciaNombre (línea ~45):
[Required(ErrorMessage = "El nombre del contacto de emergencia es obligatorio.")]
[StringLength(200)]
public string ContactoEmergenciaNombre { get; set; } = null!;

// DESPUÉS:
[StringLength(200)]
public string? ContactoEmergenciaNombre { get; set; }

// ─────────────────────────────────────────────────────────────────────

// ANTES — ContactoEmergenciaTelefono (línea ~49):
[Required(ErrorMessage = "El teléfono del contacto de emergencia es obligatorio.")]
[StringLength(20)]
public string ContactoEmergenciaTelefono { get; set; } = null!;

// DESPUÉS:
[StringLength(20)]
public string? ContactoEmergenciaTelefono { get; set; }

// ─────────────────────────────────────────────────────────────────────

// ANTES — FechaIngreso (línea ~74):
[Required(ErrorMessage = "La fecha de ingreso es obligatoria.")]
public DateOnly FechaIngreso { get; set; }

// DESPUÉS (validación se traslada al Service):
public DateOnly? FechaIngreso { get; set; }
```

**Criterio de done:** El DTO compila. Los campos opcionales ya no tienen `[Required]`. `FechaIngreso` es `DateOnly?`.

---

### Tarea 1.2 — `EditarEmpleadoDto.cs`

**Ruta:** `Proyecto MVC/GestionPersonal.Models/DTOs/Empleado/EditarEmpleadoDto.cs`

**Cambios:** Idénticos a los de `CrearEmpleadoDto` para los mismos cinco campos (`Eps`, `ContactoEmergenciaNombre`, `ContactoEmergenciaTelefono`, `FechaIngreso`).

**Criterio de done:** El DTO compila con los mismos tipos nullable.

---

### ✅ Build Fase 1

```powershell
cd "Proyecto MVC"
dotnet build GestionPersonal.slnx --no-incremental 2>&1 | Select-String "error CS|Build succeeded|FAILED"
```

**Criterio de done:** `Build succeeded` sin errores `error CS`.

---

## Fase 2 — Service (`GestionPersonal.Application/Services/`)

> **Objetivo:** Trasladar la validación de `FechaIngreso` al Service (donde se conoce el `TipoVinculacion`), manejar `ContactoEmergencia` como entidad opcional y asignar `FechaIngreso` automáticamente para empleados Temporales.

### Tarea 2.1 — `EmpleadoService.CrearAsync`

**Ruta:** `Proyecto MVC/GestionPersonal.Application/Services/EmpleadoService.cs`  
**Método:** `CrearAsync`

**Cambio 1 — Validación condicional de FechaIngreso:**

```csharp
// Agregar ANTES de crear el objeto Empleado:
if (dto.TipoVinculacion == TipoVinculacion.Directo && dto.FechaIngreso is null)
    return ResultadoOperacion.Fail("La fecha de ingreso es obligatoria para contrato directo.");

// Para Temporal, usar FechaInicioContrato como FechaIngreso (BD es NOT NULL)
var fechaIngreso = dto.TipoVinculacion == TipoVinculacion.Directo
    ? dto.FechaIngreso!.Value
    : (dto.FechaInicioContrato ?? DateOnly.FromDateTime(DateTime.UtcNow));
```

**Cambio 2 — Usar `fechaIngreso` al construir el objeto:**

```csharp
// Reemplazar:
FechaIngreso = dto.FechaIngreso,

// Por:
FechaIngreso = fechaIngreso,
```

**Cambio 3 — ContactoEmergencia opcional:**

```csharp
// Reemplazar el bloque de ContactoEmergencia en el inicializador:
ContactoEmergencia = new ContactoEmergencia
{
    NombreContacto   = dto.ContactoEmergenciaNombre,
    TelefonoContacto = dto.ContactoEmergenciaTelefono
}

// Por (solo crear si al menos uno de los dos campos tiene valor):
ContactoEmergencia = !string.IsNullOrWhiteSpace(dto.ContactoEmergenciaNombre)
                     || !string.IsNullOrWhiteSpace(dto.ContactoEmergenciaTelefono)
    ? new ContactoEmergencia
      {
          NombreContacto   = dto.ContactoEmergenciaNombre ?? string.Empty,
          TelefonoContacto = dto.ContactoEmergenciaTelefono ?? string.Empty
      }
    : null
```

**Criterio de done:** Al crear con `TipoVinculacion = Temporal` y sin `FechaIngreso`, el sistema usa `FechaInicioContrato`. Al crear sin contacto de emergencia, `ContactoEmergencia` queda `null` en BD.

---

### Tarea 2.2 — `EmpleadoService.EditarAsync`

**Ruta:** `Proyecto MVC/GestionPersonal.Application/Services/EmpleadoService.cs`  
**Método:** `EditarAsync`

**Cambio 1 — Validación condicional de FechaIngreso:**

```csharp
// Agregar ANTES de actualizar emp:
var tipoVinculacion = Enum.Parse<TipoVinculacion>(dto.TipoVinculacion);

if (tipoVinculacion == TipoVinculacion.Directo && dto.FechaIngreso is null)
    return ResultadoOperacion.Fail("La fecha de ingreso es obligatoria para contrato directo.");
```

**Cambio 2 — Actualizar FechaIngreso solo si Directo:**

```csharp
// En el bloque de asignaciones, agregar:
if (tipoVinculacion == TipoVinculacion.Directo && dto.FechaIngreso.HasValue)
    emp.FechaIngreso = dto.FechaIngreso.Value;
```

**Cambio 3 — ContactoEmergencia opcional en edición:**

```csharp
// Reemplazar el bloque if/else de ContactoEmergencia:
// ANTES:
if (emp.ContactoEmergencia is not null)
{
    emp.ContactoEmergencia.NombreContacto   = dto.ContactoEmergenciaNombre;
    emp.ContactoEmergencia.TelefonoContacto = dto.ContactoEmergenciaTelefono;
}
else
{
    emp.ContactoEmergencia = new ContactoEmergencia { ... };
}

// DESPUÉS:
bool tieneContacto = !string.IsNullOrWhiteSpace(dto.ContactoEmergenciaNombre)
                     || !string.IsNullOrWhiteSpace(dto.ContactoEmergenciaTelefono);

if (tieneContacto)
{
    if (emp.ContactoEmergencia is not null)
    {
        emp.ContactoEmergencia.NombreContacto   = dto.ContactoEmergenciaNombre ?? string.Empty;
        emp.ContactoEmergencia.TelefonoContacto = dto.ContactoEmergenciaTelefono ?? string.Empty;
    }
    else
    {
        emp.ContactoEmergencia = new ContactoEmergencia
        {
            EmpleadoId       = emp.Id,
            NombreContacto   = dto.ContactoEmergenciaNombre ?? string.Empty,
            TelefonoContacto = dto.ContactoEmergenciaTelefono ?? string.Empty
        };
    }
    // Si ambos están vacíos, no se modifica el registro existente (se preserva el dato anterior).
}
```

**Criterio de done:** Editar un empleado sin tocar el contacto de emergencia no borra el registro existente.

---

### Tarea 2.3 — Validaciones de unicidad en `EmpleadoService.CrearAsync`

**Ruta:** `Proyecto MVC/GestionPersonal.Application/Services/EmpleadoService.cs`  
**Ruta constante:** `Proyecto MVC/GestionPersonal.Constants/Messages/EmpleadoConstant.cs`

**Contexto:**
- La cédula ya se valida (`ExisteCedulaAsync`) — solo necesita cobertura de tests.
- El correo electrónico **no** se valida en `EmpleadoService`. `UsuarioService` sí verifica duplicados en la tabla `Usuarios`, pero si el correo ya existe en `Empleados.CorreoElectronico`, la BD lanza una excepción no controlada.

**Cambio 1 — nueva constante en `EmpleadoConstant.cs`:**

```csharp
public const string CorreoElectronicoDuplicado = "Ya existe un empleado registrado con ese correo electrónico.";
```

**Cambio 2 — agregar check de correo en `CrearAsync`, inmediatamente después del check de cédula:**

```csharp
// Antes (solo cédula):
if (await _repo.ExisteCedulaAsync(dto.Cedula, ct: ct))
    return ResultadoOperacion.Fail(EmpleadoConstant.CedulaDuplicada);

// Después (cédula + correo):
if (await _repo.ExisteCedulaAsync(dto.Cedula, ct: ct))
    return ResultadoOperacion.Fail(EmpleadoConstant.CedulaDuplicada);

if (await _repo.ExisteCorreoAsync(dto.CorreoElectronico, ct: ct))
    return ResultadoOperacion.Fail(EmpleadoConstant.CorreoElectronicoDuplicado);
```

**Criterio de done:** Intentar crear un empleado con un correo ya registrado devuelve el mensaje de error apropiado antes de llamar a `UsuarioService`.

---

### ✅ Build Fase 2

```powershell
dotnet build GestionPersonal.slnx --no-incremental 2>&1 | Select-String "error CS|Build succeeded|FAILED"
```

**Criterio de done:** `Build succeeded` sin errores `error CS`.

---

## Fase 3 — Vistas y JavaScript (`GestionPersonal.Web/Views/Empleado/`)

> **Objetivo:** Adaptar la interfaz para reflejar los campos opcionales y el comportamiento condicional según Tipo de Vinculación.

### Tarea 3.1 — `Nuevo.cshtml` — Ajustes de etiquetas

**Ruta:** `Proyecto MVC/GestionPersonal.Web/Views/Empleado/Nuevo.cshtml`

**Cambio 1 — Quitar asterisco de EPS:**
```diff
- EPS <span class="required" aria-hidden="true">*</span>
+ EPS
```

**Cambio 2 — Quitar asterisco de Contacto Emergencia (nombre y teléfono):**
```diff
- Nombre del contacto <span class="required" aria-hidden="true">*</span>
+ Nombre del contacto

- Teléfono del contacto <span class="required" aria-hidden="true">*</span>
+ Teléfono del contacto
```

**Cambio 3 — Envolver el campo FechaIngreso en un div con id `seccion-fecha-ingreso`:**
```html
<!-- El form-group de FechaIngreso queda dentro de: -->
<div id="seccion-fecha-ingreso">
  <div class="form-group">
    <label asp-for="Dto.FechaIngreso" class="form-label">
      Fecha de ingreso <span class="required" aria-hidden="true">*</span>
    </label>
    <input asp-for="Dto.FechaIngreso" type="date" class="form-input" />
    <span asp-validation-for="Dto.FechaIngreso" class="form-error"></span>
  </div>
</div>
```

**Criterio de done:** El HTML no muestra asteriscos en EPS ni Contacto de Emergencia. `#seccion-fecha-ingreso` existe en el DOM.

---

### Tarea 3.2 — `Nuevo.cshtml` — Script de comportamiento condicional

**Ruta:** `Proyecto MVC/GestionPersonal.Web/Views/Empleado/Nuevo.cshtml`

**Agregar al final del archivo (antes de `</form>` o como `@section Scripts`):**

```javascript
<script>
(function () {
    const selector    = document.getElementById('TipoVinculacion');
    const secTemporal = document.getElementById('seccion-temporal');
    const secIngreso  = document.getElementById('seccion-fecha-ingreso');
    const inputIngreso = document.querySelector("input[name='Dto.FechaIngreso']");

    function actualizarVisibilidad() {
        const esTemporal = selector.value === 'Temporal';
        // Bloque temporal
        secTemporal.hidden = !esTemporal;
        // Fecha ingreso solo aplica a Directo
        if (secIngreso) secIngreso.hidden = esTemporal;
        // Limpiar el valor si se oculta para evitar enviar datos inconsistentes
        if (esTemporal && inputIngreso) inputIngreso.value = '';
    }

    selector.addEventListener('change', actualizarVisibilidad);
    // Ejecutar al cargar (por si hay valor preseleccionado o re-render tras error)
    actualizarVisibilidad();
})();
</script>
```

**Criterio de done:** Al seleccionar "Contrato directo": `#seccion-temporal` oculto, `#seccion-fecha-ingreso` visible. Al seleccionar "Empresa temporal": lo contrario.

---

### Tarea 3.3 — `Editar.cshtml` — Ajustes de etiquetas

**Ruta:** `Proyecto MVC/GestionPersonal.Web/Views/Empleado/Editar.cshtml`

**Cambios idénticos a Tarea 3.1:** quitar `*` de EPS, quitar `*` de ContactoEmergenciaNombre y ContactoEmergenciaTelefono. Envolver `FechaIngreso` en `<div id="seccion-fecha-ingreso">`.

**Criterio de done:** El formulario de edición refleja los mismos cambios visuales que el de creación.

---

### Tarea 3.4 — `Editar.cshtml` — Script extendido

**Ruta:** `Proyecto MVC/GestionPersonal.Web/Views/Empleado/Editar.cshtml`

El formulario de edición ya tiene JS para ocultar `#seccion-temporal` al cambiar a Directo. **Extender** ese script (no reemplazarlo) para también ocultar `#seccion-fecha-ingreso` cuando el tipo es Temporal.

```javascript
// Dentro del handler de change existente, agregar:
const secIngreso   = document.getElementById('seccion-fecha-ingreso');
const inputIngreso = document.querySelector("input[name='Dto.FechaIngreso']");

if (secIngreso) secIngreso.hidden = esTemporal;
if (esTemporal && inputIngreso) inputIngreso.value = '';
```

**Criterio de done:** En el formulario de edición, cambiar a Temporal oculta FechaIngreso; cambiar a Directo la muestra.

---

### ✅ Build Fase 3 (final)

```powershell
dotnet build GestionPersonal.slnx --no-incremental 2>&1 | Select-String "error CS|Build succeeded|FAILED"
```

**Criterio de done:** `Build succeeded`. La aplicación levanta en `http://localhost:5002`.

---

## Fase 4 — Tests Playwright

### Fixture de limpieza — `conftest.py`

**Ruta:** `Tests/conftest.py`

Agregar fixture `limpiar_empleado_prueba` que borra de BD los empleados creados durante los tests, identificados por cédulas reservadas (`12345001`, `12345002`).

```python
import subprocess

CEDULAS_PRUEBA = ("'12345001'", "'12345002'")

@pytest.fixture(autouse=False)
def limpiar_empleado_prueba():
    """Elimina los empleados de prueba antes Y después de cada test que la use."""
    _borrar_empleados_prueba()
    yield
    _borrar_empleados_prueba()


def _borrar_empleados_prueba():
    cedulas = ", ".join(CEDULAS_PRUEBA)
    sql = (
        f"DELETE ce FROM dbo.ContactosEmergencia ce "
        f"INNER JOIN dbo.Empleados e ON ce.EmpleadoId = e.Id "
        f"WHERE e.Cedula IN ({cedulas}); "
        f"DELETE u FROM dbo.Usuarios u "
        f"INNER JOIN dbo.Empleados e ON e.UsuarioId = u.Id "
        f"WHERE e.Cedula IN ({cedulas}); "
        f"DELETE FROM dbo.Empleados WHERE Cedula IN ({cedulas});"
    )
    subprocess.run(
        ["sqlcmd", "-S", r"(localdb)\MSSQLLocalDB", "-d", "GestionPersonalDB",
         "-Q", sql],
        capture_output=True, text=True
    )
```

---

### Archivo de tests — `Tests/test_creacion_usuario.py`

```python
"""
Pruebas E2E — Ajuste al Formulario de Creación de Empleado
Plan: Documentos/Pruebas/Playwright/Plan-CreacionUsuarioRefinado.md

Rol ejecutor: Carlos Rodríguez (Jefe) — único rol habilitado para crear empleados.
Cédulas de prueba: 12345001 (Directo), 12345002 (Temporal)
"""
import pytest
from playwright.sync_api import Page, expect
from helpers import hacer_login_completo, hacer_logout, BASE_URL

JEFE_EMAIL    = "carlos.rodriguez@yopmail.com"
JEFE_PASSWORD = "Usuario1"

CC_DIRECTO  = "12345001"
CC_TEMPORAL = "12345002"
```

---

### Casos de prueba

| ID | Nombre | Tipo | Criterio de éxito |
|---|---|---|---|
| TC-CRE-01 | Selector Directo muestra FechaIngreso y oculta bloque temporal | UI/JS | `#seccion-fecha-ingreso` visible; `#seccion-temporal` oculto |
| TC-CRE-02 | Selector Temporal oculta FechaIngreso y muestra bloque temporal | UI/JS | `#seccion-fecha-ingreso` oculto; `#seccion-temporal` visible |
| TC-CRE-03 | EPS no muestra asterisco de obligatorio | UI | `label:has-text("EPS")` no contiene `span.required` visible |
| TC-CRE-04 | ContactoEmergencia no muestra asteriscos | UI | Ambos labels sin `span.required` visible |
| TC-CRE-05 | Creación exitosa Contrato Directo sin EPS ni Contacto | Happy path | Redirige a perfil; mensaje de éxito visible |
| TC-CRE-06 | Creación exitosa Empresa Temporal sin EPS ni Contacto | Happy path | Redirige a perfil; tipo "Temporal" en perfil; sección Contrato Temporal visible |
| TC-CRE-07 | Contrato Directo sin FechaIngreso es rechazado | Validación | Permanece en formulario; error de FechaIngreso visible |
| TC-CRE-08 | Empresa Temporal sin EmpresaTemporalId es rechazado | Validación | Permanece en formulario; error de EmpresaTemporalId visible |
| TC-CRE-09 | Perfil de empleado Directo muestra FechaIngreso | Perfil | Campo FechaIngreso visible y con valor correcto en la vista de perfil |
| TC-CRE-10 | Perfil de empleado Temporal no muestra "Fecha de ingreso" prominente | Perfil | Sección de contrato temporal visible; FechaIngreso no aparece como dato principal |
| TC-CRE-11 | Toggle Directo → Temporal limpia el campo FechaIngreso | UI/JS | `input[name='Dto.FechaIngreso']` tiene value vacío al cambiar a Temporal |
| TC-CRE-12 | Toggle Temporal → Directo re-muestra FechaIngreso vacío (no hereda fechas) | UI/JS | `#seccion-fecha-ingreso` visible; campo FechaIngreso vacío |
| TC-CRE-13 | Crear empleado con cédula ya existente es rechazado | Validación server | Permanece en formulario; mensaje "Ya existe un empleado registrado con esa cédula." visible |
| TC-CRE-14 | Crear empleado con correo ya existente es rechazado | Validación server | Permanece en formulario; mensaje "Ya existe un empleado registrado con ese correo electrónico." visible |

---

### Detalle de casos por scope

#### Scope A — Comportamiento de UI / JavaScript (TC-CRE-01, TC-CRE-02, TC-CRE-03, TC-CRE-04, TC-CRE-11, TC-CRE-12)

```python
def test_tc_cre_01_directo_muestra_fecha_ingreso_oculta_temporal(page: Page):
    """TC-CRE-01: Seleccionar 'Directo' → FechaIngreso visible, #seccion-temporal oculto."""
    hacer_login_completo(page, JEFE_EMAIL, JEFE_PASSWORD)
    page.goto(f"{BASE_URL}/Empleado/Nuevo")
    page.wait_for_load_state("networkidle")

    page.select_option("#TipoVinculacion", "Directo")

    expect(page.locator("#seccion-fecha-ingreso")).to_be_visible()
    expect(page.locator("#seccion-temporal")).to_be_hidden()


def test_tc_cre_02_temporal_oculta_fecha_ingreso_muestra_temporal(page: Page):
    """TC-CRE-02: Seleccionar 'Temporal' → FechaIngreso oculta, #seccion-temporal visible."""
    hacer_login_completo(page, JEFE_EMAIL, JEFE_PASSWORD)
    page.goto(f"{BASE_URL}/Empleado/Nuevo")
    page.wait_for_load_state("networkidle")

    page.select_option("#TipoVinculacion", "Temporal")

    expect(page.locator("#seccion-fecha-ingreso")).to_be_hidden()
    expect(page.locator("#seccion-temporal")).to_be_visible()


def test_tc_cre_03_eps_sin_asterisco(page: Page):
    """TC-CRE-03: El label de EPS NO debe contener span.required visible."""
    hacer_login_completo(page, JEFE_EMAIL, JEFE_PASSWORD)
    page.goto(f"{BASE_URL}/Empleado/Nuevo")
    page.wait_for_load_state("networkidle")

    # El campo EPS existe pero no tiene asterisco de requerido
    eps_input = page.locator("input[name='Dto.Eps']")
    expect(eps_input).to_be_visible()

    # El label del campo EPS no debe contener span.required
    eps_label = page.locator("label:has(+ input[name='Dto.Eps']), label[for$='Eps']")
    required_span = eps_label.locator("span.required")
    expect(required_span).to_have_count(0)


def test_tc_cre_04_contacto_emergencia_sin_asteriscos(page: Page):
    """TC-CRE-04: Los labels de Contacto de Emergencia no tienen span.required."""
    hacer_login_completo(page, JEFE_EMAIL, JEFE_PASSWORD)
    page.goto(f"{BASE_URL}/Empleado/Nuevo")
    page.wait_for_load_state("networkidle")

    for field in ["Dto.ContactoEmergenciaNombre", "Dto.ContactoEmergenciaTelefono"]:
        campo = page.locator(f"input[name='{field}']")
        expect(campo).to_be_visible()
        # No debe haber span.required en el form-group del campo
        form_group = campo.locator("xpath=ancestor::div[contains(@class,'form-group')]")
        expect(form_group.locator("span.required")).to_have_count(0)


def test_tc_cre_11_toggle_directo_temporal_limpia_fecha_ingreso(page: Page):
    """TC-CRE-11: Cambiar de Directo a Temporal limpia el valor de FechaIngreso."""
    hacer_login_completo(page, JEFE_EMAIL, JEFE_PASSWORD)
    page.goto(f"{BASE_URL}/Empleado/Nuevo")
    page.wait_for_load_state("networkidle")

    page.select_option("#TipoVinculacion", "Directo")
    page.fill("input[name='Dto.FechaIngreso']", "2026-04-25")

    page.select_option("#TipoVinculacion", "Temporal")

    valor = page.input_value("input[name='Dto.FechaIngreso']")
    assert valor == "", f"Se esperaba campo vacío, se obtuvo: '{valor}'"


def test_tc_cre_12_toggle_temporal_directo_fecha_ingreso_vacia(page: Page):
    """TC-CRE-12: Volver de Temporal a Directo → FechaIngreso re-aparece vacío."""
    hacer_login_completo(page, JEFE_EMAIL, JEFE_PASSWORD)
    page.goto(f"{BASE_URL}/Empleado/Nuevo")
    page.wait_for_load_state("networkidle")

    page.select_option("#TipoVinculacion", "Temporal")
    page.select_option("#TipoVinculacion", "Directo")

    expect(page.locator("#seccion-fecha-ingreso")).to_be_visible()
    valor = page.input_value("input[name='Dto.FechaIngreso']")
    assert valor == "", f"Se esperaba campo vacío, se obtuvo: '{valor}'"
```

---

#### Scope B — Happy Path (TC-CRE-05, TC-CRE-06)

```python
def test_tc_cre_05_creacion_exitosa_directo_sin_eps_sin_contacto(
    page: Page, limpiar_empleado_prueba
):
    """TC-CRE-05: Crear empleado Directo sin EPS ni contacto → éxito."""
    hacer_login_completo(page, JEFE_EMAIL, JEFE_PASSWORD)
    page.goto(f"{BASE_URL}/Empleado/Nuevo")
    page.wait_for_load_state("networkidle")

    # Datos personales
    page.fill("input[name='Dto.NombreCompleto']", "Empleado Prueba Directo")
    page.fill("input[name='Dto.Cedula']", CC_DIRECTO)
    page.fill("input[name='Dto.Telefono']", "3001234501")
    page.fill("input[name='Dto.CorreoElectronico']", "prueba.directo@yopmail.com")

    # Residencia
    page.fill("input[name='Dto.Direccion']", "Cra 1 #1-1")
    page.fill("input[name='Dto.Ciudad']", "Medellín")
    page.fill("input[name='Dto.Departamento']", "Antioquia")

    # Vinculación — Contrato Directo
    page.select_option("select[name='Dto.SedeId']", label="Medellín")
    page.select_option("select[name='Dto.CargoId']", index=1)
    page.select_option("select[name='Dto.Rol']", "Operario")
    page.select_option("#TipoVinculacion", "Directo")
    page.fill("input[name='Dto.FechaIngreso']", "2026-04-25")

    page.click("button[type=submit]")
    page.wait_for_load_state("networkidle")

    # Redirige a perfil o lista
    assert "/Empleado/" in page.url, f"URL inesperada: {page.url}"
    exito = page.locator(".alert--success, [class*='success']")
    expect(exito.first).to_be_visible()


def test_tc_cre_06_creacion_exitosa_temporal_sin_eps(
    page: Page, limpiar_empleado_prueba
):
    """TC-CRE-06: Crear empleado Temporal sin EPS → éxito; perfil muestra tipo Temporal."""
    hacer_login_completo(page, JEFE_EMAIL, JEFE_PASSWORD)
    page.goto(f"{BASE_URL}/Empleado/Nuevo")
    page.wait_for_load_state("networkidle")

    page.fill("input[name='Dto.NombreCompleto']", "Empleado Prueba Temporal")
    page.fill("input[name='Dto.Cedula']", CC_TEMPORAL)
    page.fill("input[name='Dto.Telefono']", "3001234502")
    page.fill("input[name='Dto.CorreoElectronico']", "prueba.temporal@yopmail.com")
    page.fill("input[name='Dto.Direccion']", "Cra 2 #2-2")
    page.fill("input[name='Dto.Ciudad']", "Medellín")
    page.fill("input[name='Dto.Departamento']", "Antioquia")

    page.select_option("select[name='Dto.SedeId']", label="Medellín")
    page.select_option("select[name='Dto.CargoId']", index=1)
    page.select_option("select[name='Dto.Rol']", "Operario")
    page.select_option("#TipoVinculacion", "Temporal")

    # Bloque temporal
    page.select_option("select[name='Dto.EmpresaTemporalId']", index=1)
    page.fill("input[name='Dto.FechaInicioContrato']", "2026-04-25")
    page.fill("input[name='Dto.FechaFinContrato']", "2026-10-25")

    page.click("button[type=submit]")
    page.wait_for_load_state("networkidle")

    assert "/Empleado/" in page.url, f"URL inesperada: {page.url}"
    exito = page.locator(".alert--success, [class*='success']")
    expect(exito.first).to_be_visible()
```

---

#### Scope C — Validaciones server-side (TC-CRE-07, TC-CRE-08, TC-CRE-13, TC-CRE-14)

```python
def test_tc_cre_07_directo_sin_fecha_ingreso_es_rechazado(page: Page):
    """TC-CRE-07: Contrato Directo sin FechaIngreso → error de validación del servidor."""
    hacer_login_completo(page, JEFE_EMAIL, JEFE_PASSWORD)
    page.goto(f"{BASE_URL}/Empleado/Nuevo")
    page.wait_for_load_state("networkidle")

    page.fill("input[name='Dto.NombreCompleto']", "Sin Fecha Ingreso")
    page.fill("input[name='Dto.Cedula']", "00000099")
    page.fill("input[name='Dto.Telefono']", "3001234503")
    page.fill("input[name='Dto.CorreoElectronico']", "sin.fecha@yopmail.com")
    page.fill("input[name='Dto.Direccion']", "Cra 3 #3-3")
    page.fill("input[name='Dto.Ciudad']", "Medellín")
    page.fill("input[name='Dto.Departamento']", "Antioquia")
    page.select_option("select[name='Dto.SedeId']", label="Medellín")
    page.select_option("select[name='Dto.CargoId']", index=1)
    page.select_option("select[name='Dto.Rol']", "Operario")
    page.select_option("#TipoVinculacion", "Directo")
    # NO se completa FechaIngreso — simular envío sin JS

    # Forzar envío sin FechaIngreso via JS (bypassear el hidden del seccion-fecha-ingreso)
    page.evaluate("document.getElementById('seccion-fecha-ingreso').hidden = false")
    page.click("button[type=submit]")
    page.wait_for_load_state("networkidle")

    # Debe permanecer en el formulario con error
    assert "/Empleado/Nuevo" in page.url or "/Empleado/Crear" in page.url or \
           page.locator(".form-error, .alert--error, [class*='error']").count() > 0


def test_tc_cre_08_temporal_sin_empresa_es_rechazado(page: Page):
    """TC-CRE-08: Empresa Temporal sin EmpresaTemporalId → error de validación."""
    hacer_login_completo(page, JEFE_EMAIL, JEFE_PASSWORD)
    page.goto(f"{BASE_URL}/Empleado/Nuevo")
    page.wait_for_load_state("networkidle")

    page.fill("input[name='Dto.NombreCompleto']", "Sin Empresa Temporal")
    page.fill("input[name='Dto.Cedula']", "00000098")
    page.fill("input[name='Dto.Telefono']", "3001234504")
    page.fill("input[name='Dto.CorreoElectronico']", "sin.empresa@yopmail.com")
    page.fill("input[name='Dto.Direccion']", "Cra 4 #4-4")
    page.fill("input[name='Dto.Ciudad']", "Medellín")
    page.fill("input[name='Dto.Departamento']", "Antioquia")
    page.select_option("select[name='Dto.SedeId']", label="Medellín")
    page.select_option("select[name='Dto.CargoId']", index=1)
    page.select_option("select[name='Dto.Rol']", "Operario")
    page.select_option("#TipoVinculacion", "Temporal")
    # No se selecciona empresa — dejar en blanco

    page.click("button[type=submit]")
    page.wait_for_load_state("networkidle")

    assert "/Empleado/Nuevo" in page.url or "/Empleado/Crear" in page.url or \
           page.locator(".form-error, .alert--error, [class*='error']").count() > 0
```

---

#### Scope C2 — Unicidad de cédula y correo (TC-CRE-13, TC-CRE-14)

> **Nota:** Estos tests usan registros ya existentes del seeding como datos duplicados. No requieren `limpiar_empleado_prueba` para el registro objetivo porque ese registro persiste desde el seeding.

```python
def test_tc_cre_13_cedula_duplicada_es_rechazada(page: Page, limpiar_empleado_prueba):
    """TC-CRE-13: Crear empleado con cédula ya existente → rechazado con mensaje de cédula duplicada."""
    hacer_login_completo(page, JEFE_EMAIL, JEFE_PASSWORD)

    # Obtener la cédula de un empleado existente del seeding
    # (usar el primer empleado visible en el listado)
    page.goto(f"{BASE_URL}/Empleado")
    page.wait_for_load_state("networkidle")
    cedula_existente = page.locator("table tbody tr:first-child td:nth-child(2)").inner_text().strip()

    page.goto(f"{BASE_URL}/Empleado/Nuevo")
    page.wait_for_load_state("networkidle")

    page.fill("input[name='Dto.NombreCompleto']", "Cédula Duplicada Test")
    page.fill("input[name='Dto.Cedula']", cedula_existente)  # cédula ya registrada
    page.fill("input[name='Dto.Telefono']", "3009999991")
    page.fill("input[name='Dto.CorreoElectronico']", "cedula.duplicada.test@yopmail.com")
    page.fill("input[name='Dto.Direccion']", "Cra 99 #1-1")
    page.fill("input[name='Dto.Ciudad']", "Medellín")
    page.fill("input[name='Dto.Departamento']", "Antioquia")
    page.select_option("select[name='Dto.SedeId']", index=1)
    page.select_option("select[name='Dto.CargoId']", index=1)
    page.select_option("select[name='Dto.Rol']", "Operario")
    page.select_option("#TipoVinculacion", "Directo")
    page.fill("input[name='Dto.FechaIngreso']", "2024-01-15")

    page.click("button[type=submit]")
    page.wait_for_load_state("networkidle")

    # Debe permanecer en el formulario
    assert "/Empleado/Nuevo" in page.url or "/Empleado/Crear" in page.url
    # Debe mostrar el mensaje de error de cédula duplicada
    assert page.locator("text=Ya existe un empleado registrado con esa cédula").count() > 0


def test_tc_cre_14_correo_duplicado_es_rechazado(page: Page, limpiar_empleado_prueba):
    """TC-CRE-14: Crear empleado con correo ya existente → rechazado con mensaje de correo duplicado."""
    hacer_login_completo(page, JEFE_EMAIL, JEFE_PASSWORD)

    # Correo de un empleado existente en el seeding
    CORREO_EXISTENTE = "carlos.rodriguez@yopmail.com"  # Jefe de sede — existe en seeding

    page.goto(f"{BASE_URL}/Empleado/Nuevo")
    page.wait_for_load_state("networkidle")

    page.fill("input[name='Dto.NombreCompleto']", "Correo Duplicado Test")
    page.fill("input[name='Dto.Cedula']", "99900014")  # cédula única
    page.fill("input[name='Dto.Telefono']", "3009999992")
    page.fill("input[name='Dto.CorreoElectronico']", CORREO_EXISTENTE)  # correo ya registrado
    page.fill("input[name='Dto.Direccion']", "Cra 99 #2-2")
    page.fill("input[name='Dto.Ciudad']", "Medellín")
    page.fill("input[name='Dto.Departamento']", "Antioquia")
    page.select_option("select[name='Dto.SedeId']", index=1)
    page.select_option("select[name='Dto.CargoId']", index=1)
    page.select_option("select[name='Dto.Rol']", "Operario")
    page.select_option("#TipoVinculacion", "Directo")
    page.fill("input[name='Dto.FechaIngreso']", "2024-01-15")

    page.click("button[type=submit]")
    page.wait_for_load_state("networkidle")

    # Debe permanecer en el formulario
    assert "/Empleado/Nuevo" in page.url or "/Empleado/Crear" in page.url
    # Debe mostrar el mensaje de error de correo duplicado
    assert page.locator("text=Ya existe un empleado registrado con ese correo electrónico").count() > 0
```

---

#### Scope D — Perfil post-creación (TC-CRE-09, TC-CRE-10)

```python
def test_tc_cre_09_perfil_directo_muestra_fecha_ingreso(
    page: Page, limpiar_empleado_prueba
):
    """TC-CRE-09: El perfil de un empleado Directo muestra su FechaIngreso correctamente."""
    hacer_login_completo(page, JEFE_EMAIL, JEFE_PASSWORD)
    # Reusar TC-CRE-05 para crear el empleado, luego verificar el perfil
    page.goto(f"{BASE_URL}/Empleado/Nuevo")
    page.wait_for_load_state("networkidle")

    _rellenar_formulario_directo(page, CC_DIRECTO, "2026-04-25")
    page.click("button[type=submit]")
    page.wait_for_load_state("networkidle")

    # Buscar el empleado y navegar al perfil
    page.goto(f"{BASE_URL}/Empleado")
    page.fill("input[name=buscar]", CC_DIRECTO)
    page.keyboard.press("Enter")
    page.wait_for_load_state("networkidle")

    fila = page.locator("table tbody tr").first
    fila.locator("a[href*='/Empleado/Perfil/']").first.click()
    page.wait_for_load_state("networkidle")

    # FechaIngreso debe aparecer en el perfil
    contenido = page.content()
    assert "25/04/2026" in contenido or "2026-04-25" in contenido, \
        "FechaIngreso no aparece en el perfil del empleado Directo"


def test_tc_cre_10_perfil_temporal_muestra_seccion_contrato(
    page: Page, limpiar_empleado_prueba
):
    """TC-CRE-10: El perfil de un empleado Temporal muestra la sección 'Contrato temporal'."""
    hacer_login_completo(page, JEFE_EMAIL, JEFE_PASSWORD)
    page.goto(f"{BASE_URL}/Empleado/Nuevo")
    page.wait_for_load_state("networkidle")

    _rellenar_formulario_temporal(page, CC_TEMPORAL, "2026-04-25", "2026-10-25")
    page.click("button[type=submit]")
    page.wait_for_load_state("networkidle")

    page.goto(f"{BASE_URL}/Empleado")
    page.fill("input[name=buscar]", CC_TEMPORAL)
    page.keyboard.press("Enter")
    page.wait_for_load_state("networkidle")

    fila = page.locator("table tbody tr").first
    fila.locator("a[href*='/Empleado/Perfil/']").first.click()
    page.wait_for_load_state("networkidle")

    # El perfil muestra el bloque de contrato temporal
    expect(page.locator("text=Temporal, text=Contrato temporal").first).to_be_visible()


# ── helpers de formulario ─────────────────────────────────────────────────────

def _rellenar_formulario_directo(page, cedula: str, fecha_ingreso: str):
    page.fill("input[name='Dto.NombreCompleto']", f"Prueba Directo {cedula}")
    page.fill("input[name='Dto.Cedula']", cedula)
    page.fill("input[name='Dto.Telefono']", "3001234501")
    page.fill("input[name='Dto.CorreoElectronico']", f"directo.{cedula}@yopmail.com")
    page.fill("input[name='Dto.Direccion']", "Cra 1 #1-1")
    page.fill("input[name='Dto.Ciudad']", "Medellín")
    page.fill("input[name='Dto.Departamento']", "Antioquia")
    page.select_option("select[name='Dto.SedeId']", label="Medellín")
    page.select_option("select[name='Dto.CargoId']", index=1)
    page.select_option("select[name='Dto.Rol']", "Operario")
    page.select_option("#TipoVinculacion", "Directo")
    page.fill("input[name='Dto.FechaIngreso']", fecha_ingreso)


def _rellenar_formulario_temporal(page, cedula: str, fecha_inicio: str, fecha_fin: str):
    page.fill("input[name='Dto.NombreCompleto']", f"Prueba Temporal {cedula}")
    page.fill("input[name='Dto.Cedula']", cedula)
    page.fill("input[name='Dto.Telefono']", "3001234502")
    page.fill("input[name='Dto.CorreoElectronico']", f"temporal.{cedula}@yopmail.com")
    page.fill("input[name='Dto.Direccion']", "Cra 2 #2-2")
    page.fill("input[name='Dto.Ciudad']", "Medellín")
    page.fill("input[name='Dto.Departamento']", "Antioquia")
    page.select_option("select[name='Dto.SedeId']", label="Medellín")
    page.select_option("select[name='Dto.CargoId']", index=1)
    page.select_option("select[name='Dto.Rol']", "Operario")
    page.select_option("#TipoVinculacion", "Temporal")
    page.select_option("select[name='Dto.EmpresaTemporalId']", index=1)
    page.fill("input[name='Dto.FechaInicioContrato']", fecha_inicio)
    page.fill("input[name='Dto.FechaFinContrato']", fecha_fin)
```

---

## Fase 5 — Verificación

### Tarea 5.1 — Levantar la aplicación

```powershell
cd "c:\Users\alejandro.ortiz\Documents\helpharma\Desarrollos\lissy\IA\LissyIAHelpharma\empleados v2\Proyecto MVC\GestionPersonal.Web"
dotnet run --launch-profile http
```

Esperar hasta ver: `Now listening on: http://localhost:5002`

---

### Tarea 5.2 — Ejecutar la suite de tests

```powershell
cd "c:\Users\alejandro.ortiz\Documents\helpharma\Desarrollos\lissy\IA\LissyIAHelpharma\empleados v2"
$env:PYTHONIOENCODING='utf-8'
$fecha = Get-Date -Format "yyyy-MM-dd_HH-mm-ss"
$informe = "Tests\resultados\creacion-usuario-$fecha.txt"
New-Item -ItemType Directory -Force -Path "Tests\resultados" | Out-Null
.venv\Scripts\python.exe -m pytest Tests/test_creacion_usuario.py -v --headed --slowmo 800 -s 2>&1 | Tee-Object -FilePath $informe
Write-Host "`nInforme: $informe"
```

**Criterio de done:** `14 passed` sin failures.

---

## Criterio de Done Global

- [ ] `Build succeeded` en las 3 fases
- [ ] Formulario `/Empleado/Nuevo`: EPS y Contacto sin asterisco; FechaIngreso visible solo al elegir Directo; bloque Temporal visible solo al elegir Temporal
- [ ] Formulario `/Empleado/Editar`: mismo comportamiento
- [ ] Crear empleado Directo sin EPS ni Contacto de Emergencia → guarda correctamente
- [ ] Crear empleado Temporal sin EPS → guarda correctamente; FechaIngreso tomada de FechaInicioContrato
- [ ] Contrato Directo sin FechaIngreso → server devuelve error
- [ ] 14 tests en `test_creacion_usuario.py` pasan (`14 passed`)
