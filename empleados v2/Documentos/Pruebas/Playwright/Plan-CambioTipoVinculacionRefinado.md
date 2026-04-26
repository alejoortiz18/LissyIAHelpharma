# Plan Refinado — Cambio de Tipo de Vinculación: Temporal → Directo
## Sistema de Administración de Empleados — GestionPersonal

> **Basado en:** `Documentos/Requerimientos/Plan-CambioTipoVinculacion.md`
> **Metodología:** Shape Up (Basecamp) — https://basecamp.com/shapeup
> **Ejecutor:** GitHub Copilot (requiere aprobación previa del usuario)
> **Orden de implementación:** DTO → Service → View → JS → Tests → Verificación
> **Granularidad:** Una tarea por archivo modificado
> **Verificación:** Build por fase (no archivo a archivo)
> **Última actualización:** Abril 2026

---

## PITCH — Shape Up

### Problema

Un empleado contratado vía empresa temporal puede pasar a nómina directa al vencer su contrato. Hoy no existe un camino claro en el sistema para registrar ese cambio: el formulario de edición del empleado no permite modificar el `TipoVinculacion`, por lo que el registro queda atascado como "Temporal" indefinidamente aunque el empleado ya esté vinculado de forma directa.

Esto genera tres inconsistencias:

1. **Contadores erróneos**: el saldo de vacaciones sigue calculándose desde `FechaInicioContrato` del período temporal, acumulando días que no corresponden al nuevo tipo de vinculación.
2. **Datos basura**: `EmpresaTemporalId` y `FechaFinContrato` persisten en el registro aunque ya no apliquen.
3. **Reporte incorrecto**: el listado de empleados sigue mostrando al empleado como "Temporal" en los filtros.

> *Historia representativa:* Marco Antonio Díaz Peña lleva un año como temporal en ManpowerGroup Colombia. Su contrato venció el 25 de abril de 2026 y la empresa decidió vincularlo directamente. La analista Sofía Gómez intenta editar su perfil para reflejar el cambio pero no encuentra ningún campo de "Tipo de vinculación" en el formulario de edición. El empleado sigue apareciendo como temporal en el sistema.

---

### Apetito

**Small Batch — 1 semana**

La infraestructura de edición de empleados ya existe (`/Empleado/Editar`, `EditarAsync`, `EmpleadoService`). Lo que falta es mínimo y acotado:

| Componente | Lo que falta |
|---|---|
| `EditarEmpleadoDto` | Agregar la propiedad `TipoVinculacion` |
| `EmpleadoService.EditarAsync` | Asignar `emp.TipoVinculacion` y limpiar campos temporales al cambiar a Directo |
| `Editar.cshtml` | Agregar el `<select>` de TipoVinculacion; conectar visibilidad de `#seccion-temporal` con JS |
| Prueba Playwright | Verificar el flujo completo + cálculo de vacaciones post-cambio |

No se construye nada nuevo desde cero. Solo se completan los hilos que quedaron cortados.

---

### Solución

#### Scopes

**Scope A — DTO (datos de entrada)**
Agregar `TipoVinculacion` a `EditarEmpleadoDto` para que el modelo binding del formulario capture el valor seleccionado.

**Scope B — Lógica de negocio (service)**
En `EmpleadoService.EditarAsync`, cuando el nuevo tipo sea `Directo`:
- `emp.TipoVinculacion = "Directo"`
- `emp.EmpresaTemporalId = null`
- `emp.FechaFinContrato = null`
- `emp.FechaInicioContrato` = el valor enviado por el formulario (analista ingresa la fecha de inicio del contrato directo, típicamente la fecha del cambio)

**Scope C — Formulario y comportamiento de UI**
Agregar en `Editar.cshtml` un `<select>` para `TipoVinculacion` con opciones `Directo` / `Temporal`. Añadir un bloque `<script>` que muestre u oculte `#seccion-temporal` al cambiar la selección.

**Scope D — Verificación de vacaciones**
Confirmar que `ObtenerSaldoVacacionesAsync` retorna `0` inmediatamente tras el cambio (porque `FechaInicioContrato` = hoy → `meses = 0` → `(int)(0 * 1.25) = 0`), y que crece correctamente a partir del nuevo contrato.

#### Breadboard simplificado

```
[Analista] → /Empleado/Editar/{id}
               ↓
        [select TipoVinculacion]
         Directo ──────────────────→ oculta #seccion-temporal (JS)
         Temporal ─────────────────→ muestra #seccion-temporal (JS)
               ↓
        [Guardar cambios] POST /Empleado/Actualizar
               ↓
        EmpleadoService.EditarAsync
         Si Directo → EmpresaTemporalId=null, FechaFinContrato=null
               ↓
        Redirect → /Empleado/Perfil/{id}
               ↓
        TipoVinculacion = "Directo" visible
        FechaInicioContrato = fecha nueva
        Saldo vacaciones = 0 días
```

---

### Rabbit Holes

- **¿Qué pasa si la analista ingresa una `FechaInicioContrato` anterior a hoy?** El sistema no valida esto hoy. El plan de pruebas cubre solo la fecha del día del cambio. No se construye validación de fecha retroactiva en este ciclo.
- **¿El cambio es reversible (Directo → Temporal)?** El formulario lo permitiría técnicamente, pero este plan solo cubre Temporal → Directo. Una reversión requiere volver a seleccionar empresa temporal y fechas.
- **¿Qué pasa con los días de vacaciones acumulados en el período temporal?** Por decisión de negocio (confirmada): el contador *no* se transfiere. Comienza en `0` desde la nueva `FechaInicioContrato`.

---

### No-Gos

- ❌ No se construye alerta automática cuando `FechaFinContrato` se aproxima.
- ❌ No se registra auditoría del cambio (quién lo hizo, cuándo). 
- ❌ No se hace migración masiva para empleados temporales históricos cuyo contrato ya venció.
- ❌ No se agrega validación de que `FechaInicioContrato` no sea anterior a `FechaIngreso`.
- ❌ No se construye lógica de cambio en lote (cambio para múltiples empleados a la vez).

---

## Estado actual del código (diagnóstico previo)

| Elemento | Archivo | Estado actual | Acción requerida |
|---|---|---|---|
| `TipoVinculacion` en entidad `Empleado` | `GestionPersonal.Domain/Entities/Empleado.cs` | ✅ Existe como `string` | Solo referencia |
| `TipoVinculacion` en `EditarEmpleadoDto` | `GestionPersonal.Models/DTOs/Empleado/EditarEmpleadoDto.cs` | ❌ **No existe** | Agregar propiedad `string TipoVinculacion` |
| Asignación `emp.TipoVinculacion` en `EditarAsync` | `GestionPersonal.Application/Services/EmpleadoService.cs` | ❌ **No existe** | Agregar asignación + lógica de limpieza |
| `<select>` TipoVinculacion en editar | `GestionPersonal.Web/Views/Empleado/Editar.cshtml` | ❌ **No existe** (solo en `Nuevo.cshtml`) | Agregar `<select>` con opciones |
| JS toggle de `#seccion-temporal` | `GestionPersonal.Web/Views/Empleado/Editar.cshtml` | ❌ **No existe** | Agregar `<script>` con evento `change` |
| Cálculo saldo vacaciones | `GestionPersonal.Application/Services/EventoLaboralService.cs` | ✅ Existe (`ObtenerSaldoVacacionesAsync`) | Solo verificar con nueva fecha |
| Vista temporal en `Perfil.cshtml` | `GestionPersonal.Web/Views/Empleado/Perfil.cshtml` | ✅ Condicional `if (esTemporal)` | Solo verificar ocultamiento |

---

## Decisiones de diseño resueltas

| Decisión | Resolución confirmada con usuario |
|---|---|
| ¿`FechaInicioContrato` toma la fecha del cambio o se preserva? | **Toma la fecha del cambio** (analista la ingresa). No se preserva la del período temporal. |
| ¿`FechaIngreso` cambia? | **No**. `FechaIngreso` es la fecha de ingreso a la empresa y nunca se modifica. |
| ¿Los días de vacaciones del período temporal se transfieren? | **No**. El contador comienza en `0` desde la nueva `FechaInicioContrato`. |
| ¿Solo el rol Analista puede hacer este cambio? | **Sí**. Solo `sofia.gomez@yopmail.com` (Analista) puede editar el tipo de vinculación. |
| ¿`TipoVinculacion` es string o enum en la BD? | **String** en la entidad (`"Directo"` / `"Temporal"`). Enum `TipoVinculacion` existe en `GestionPersonal.Models.Enums` pero la entidad usa string. |

---

## Usuarios de prueba

| EmpleadoId | Nombre | Correo | Password | Rol | Uso |
|---|---|---|---|---|---|
| 8 | Sofía Gómez Herrera | `sofia.gomez@yopmail.com` | `Usuario1` | Analista | Ejecuta el cambio |
| (nuevo) | Marco Antonio Díaz Peña | `marco.diaz@yopmail.com` | `Usuario1` | Operario | CC: `99887766` — empleado que cambia |

> **Empresa temporal usada en el seeding:** ManpowerGroup Colombia  
> **Datos iniciales de Marco:** `FechaIngreso = 2025-04-25`, `FechaInicioContrato = 2025-04-25`, `FechaFinContrato = 2026-04-25`, `TipoVinculacion = Temporal`  
> **Datos post-cambio:** `TipoVinculacion = Directo`, `FechaInicioContrato = 2026-04-25`, `EmpresaTemporalId = null`, `FechaFinContrato = null`

---

## Prerequisitos (verificar antes de ejecutar)

- [ ] Seeding `Documentos/BD/Seeding_Completo.sql` aplicado en `(localdb)\MSSQLLocalDB`
- [ ] Empleado Marco Antonio Díaz Peña (CC `99887766`) existe con `TipoVinculacion = Temporal`
- [ ] Proyecto compila sin errores: `dotnet build GestionPersonal.slnx`
- [ ] La aplicación levanta en `http://localhost:5002`
- [ ] Entorno virtual Python activo: `.venv\Scripts\Activate.ps1`
- [ ] `pytest-playwright` instalado: `pip install pytest-playwright`

---

## Resumen de Tareas

| # | Fase | Archivo | Descripción | Estado |
|---|---|---|---|---|
| 1.1 | DTO | `EditarEmpleadoDto.cs` | Agregar propiedad `TipoVinculacion` | ⏳ Pendiente |
| — | Build | Build Fase 1 | Verificar compilación | ⏳ Pendiente |
| 2.1 | Service | `EmpleadoService.cs` | Asignar `TipoVinculacion` + limpiar campos temporales | ⏳ Pendiente |
| — | Build | Build Fase 2 | Verificar compilación | ⏳ Pendiente |
| 3.1 | View | `Editar.cshtml` | Agregar `<select>` TipoVinculacion + variable `esTemporal` corregida | ⏳ Pendiente |
| 3.2 | View | `Editar.cshtml` | Agregar `<script>` para toggle de `#seccion-temporal` | ⏳ Pendiente |
| — | Build | Build Fase 3 (final) | Verificar compilación | ⏳ Pendiente |
| 4.1 | Tests | `conftest.py` | Agregar fixture `reset_empleado_marco` | ⏳ Pendiente |
| 4.2 | Tests | `test_cambio_vinculacion.py` | Crear archivo con 9 casos (TC-VIN-01 a TC-VIN-09) | ⏳ Pendiente |
| 5.1 | Verificación | Levantar aplicación | `dotnet run --launch-profile http` | ⏳ Pendiente |
| 5.2 | Verificación | Ejecutar tests | `pytest test_cambio_vinculacion.py -v` | ⏳ Pendiente |

**Total: 5 tareas de implementación + 3 builds + 2 verificaciones**

---

## Fase 1 — DTO (`GestionPersonal.Models/DTOs/Empleado/`)

> **Objetivo:** Exponer `TipoVinculacion` en el DTO de edición para que el model binding capture el valor del formulario y lo transmita al service.

### Tarea 1.1 — `EditarEmpleadoDto.cs`

**Ruta:** `Proyecto MVC/GestionPersonal.Models/DTOs/Empleado/EditarEmpleadoDto.cs`  
**Cambio:** Agregar la propiedad `TipoVinculacion` junto a las propiedades de contrato temporal

```csharp
// Agregar ANTES de las propiedades de contrato temporal:
// "// Contrato temporal"
[Required(ErrorMessage = "El tipo de vinculación es obligatorio.")]
public string TipoVinculacion { get; set; } = "Directo";

// Contrato temporal
public int? EmpresaTemporalId { get; set; }
public DateOnly? FechaInicioContrato { get; set; }
public DateOnly? FechaFinContrato { get; set; }
```

**Criterio de done:** El archivo compila y `TipoVinculacion` es accesible desde `EmpleadoService.EditarAsync`.

---

### ✅ Build Fase 1

```powershell
cd "Proyecto MVC"
dotnet build GestionPersonal.slnx --no-incremental 2>&1 | Select-String "error CS|Build succeeded|FAILED"
```

**Criterio de done:** `Build succeeded` sin errores `error CS`.

---

## Fase 2 — Service (`GestionPersonal.Application/Services/`)

> **Objetivo:** Implementar la lógica de negocio del cambio: asignar el nuevo tipo y limpiar los campos que aplican solo a Temporal cuando el nuevo tipo es Directo.

### Tarea 2.1 — `EmpleadoService.cs`

**Ruta:** `Proyecto MVC/GestionPersonal.Application/Services/EmpleadoService.cs`  
**Método:** `EditarAsync`  
**Cambio:** Agregar asignación de `TipoVinculacion` y lógica condicional de limpieza

```csharp
// Reemplazar el bloque de asignaciones de contrato temporal existente:
//   emp.EmpresaTemporalId  = dto.EmpresaTemporalId;
//   emp.FechaInicioContrato = dto.FechaInicioContrato;
//   emp.FechaFinContrato   = dto.FechaFinContrato;
// Por:

emp.TipoVinculacion = dto.TipoVinculacion;
if (dto.TipoVinculacion == "Directo")
{
    emp.EmpresaTemporalId  = null;
    emp.FechaInicioContrato = dto.FechaInicioContrato;
    emp.FechaFinContrato   = null;
}
else
{
    emp.EmpresaTemporalId  = dto.EmpresaTemporalId;
    emp.FechaInicioContrato = dto.FechaInicioContrato;
    emp.FechaFinContrato   = dto.FechaFinContrato;
}
```

**Criterio de done:** Al guardar con `TipoVinculacion = "Directo"`, los campos `EmpresaTemporalId` y `FechaFinContrato` quedan `null` en BD.

---

### ✅ Build Fase 2

```powershell
dotnet build GestionPersonal.slnx --no-incremental 2>&1 | Select-String "error CS|Build succeeded|FAILED"
```

**Criterio de done:** `Build succeeded` sin errores.

---

## Fase 3 — View (`GestionPersonal.Web/Views/Empleado/`)

> **Objetivo:** Exponer el selector de TipoVinculacion en el formulario de edición y controlar dinámicamente la visibilidad de la sección de contrato temporal.

### Tarea 3.1 — `Editar.cshtml` — Select TipoVinculacion

**Ruta:** `Proyecto MVC/GestionPersonal.Web/Views/Empleado/Editar.cshtml`  
**Cambio A — Corregir la variable `esTemporal`** (línea ~7):  
La condición actual es `Model.Dto.EmpresaTemporalId.HasValue`. Debe depender del tipo de vinculación para coherencia:

```cshtml
@{
    // Cambiar de:
    // bool esTemporal = Model.Dto.EmpresaTemporalId.HasValue;
    // A:
    bool esTemporal = Model.Dto.TipoVinculacion == "Temporal";
}
```

**Cambio B — Agregar el `<select>` de TipoVinculacion** en la sección de vinculación laboral (junto a SedeId/CargoId):

```cshtml
<div class="form-group">
  <label asp-for="Dto.TipoVinculacion" class="form-label">Tipo de vinculación</label>
  <select asp-for="Dto.TipoVinculacion" id="TipoVinculacion" class="form-select">
    <option value="Directo">Directo</option>
    <option value="Temporal">Empresa temporal</option>
  </select>
  <span asp-validation-for="Dto.TipoVinculacion" class="form-error"></span>
</div>
```

**Criterio de done:** El formulario muestra el selector; el valor correcto queda preseleccionado según el empleado cargado.

---

### Tarea 3.2 — `Editar.cshtml` — Script JS toggle

**Ruta:** `Proyecto MVC/GestionPersonal.Web/Views/Empleado/Editar.cshtml`  
**Cambio:** Agregar al final del archivo (antes de `</form>` o después de los botones), el bloque de script que controla la visibilidad de `#seccion-temporal`:

```html
@section Scripts {
<script>
(function () {
    const sel = document.getElementById('TipoVinculacion');
    const sec = document.getElementById('seccion-temporal');
    if (!sel || !sec) return;

    function toggle() {
        if (sel.value === 'Temporal') {
            sec.removeAttribute('hidden');
        } else {
            sec.setAttribute('hidden', '');
            // Limpiar valores para que no se envíen al servidor
            const empSelect = sec.querySelector('select[name$="EmpresaTemporalId"]');
            const fechaInicio = sec.querySelector('input[name$="FechaInicioContrato"]');
            const fechaFin = sec.querySelector('input[name$="FechaFinContrato"]');
            if (empSelect) empSelect.value = '';
            if (fechaFin) fechaFin.value = '';
        }
    }

    sel.addEventListener('change', toggle);
    // Ejecutar al cargar la página
    toggle();
})();
</script>
}
```

> **Nota:** `FechaInicioContrato` no se limpia al cambiar a Directo porque la analista debe ingresar la nueva fecha de inicio del contrato directo.

**Criterio de done:** Al seleccionar "Directo", la sección `#seccion-temporal` se oculta y los campos de empresa temporal / fin de contrato se limpian. Al seleccionar "Temporal", la sección reaparece.

---

### ✅ Build Fase 3 (Final)

```powershell
dotnet build GestionPersonal.slnx --no-incremental 2>&1 | Select-String "error CS|Build succeeded|FAILED"
```

**Criterio de done:** `Build succeeded` sin errores.

---

## Fase 4 — Tests Playwright (`Tests/`)

> **Objetivo:** Crear las pruebas automatizadas que validan el flujo completo del cambio Temporal → Directo.

### Tarea 4.1 — `conftest.py` — Fixture de reset

**Ruta:** `Tests/conftest.py`  
**Cambio:** Agregar el fixture `reset_empleado_marco` que restaura el estado del empleado Marco Antonio Díaz Peña (CC `99887766`) antes de cada prueba que lo modifique.

```python
import pyodbc
import pytest

CONN_STR = (
    "DRIVER={ODBC Driver 17 for SQL Server};"
    "SERVER=(localdb)\\MSSQLLocalDB;"
    "DATABASE=GestionPersonal;"
    "Trusted_Connection=yes;"
)

@pytest.fixture
def reset_empleado_marco():
    """Restaura a Marco Antonio Díaz Peña a su estado temporal antes de cada test."""
    yield
    with pyodbc.connect(CONN_STR) as conn:
        cursor = conn.cursor()
        # Obtener el SedeId y CargoId actual del empleado (no los tocamos)
        cursor.execute("""
            UPDATE Empleados
            SET TipoVinculacion   = 'Temporal',
                EmpresaTemporalId = (SELECT TOP 1 Id FROM EmpresasTemporales WHERE Nombre LIKE '%ManpowerGroup%'),
                FechaInicioContrato = '2025-04-25',
                FechaFinContrato    = '2026-04-25'
            WHERE NumeroIdentificacion = '99887766'
        """)
        conn.commit()
```

> **Nota:** Si Marco no existe en la BD, se debe crear primero ejecutando el seeding y el test TC-VIN-01.

---

### Tarea 4.2 — `test_cambio_vinculacion.py` — Archivo de pruebas

**Ruta:** `Tests/test_cambio_vinculacion.py`

```python
"""
Pruebas E2E — Cambio de Tipo de Vinculación: Temporal → Directo
Plan: Documentos/Pruebas/Playwright/Plan-CambioTipoVinculacionRefinado.md
"""
import re
import pytest
from playwright.sync_api import Page, expect
from helpers import hacer_login_completo, hacer_logout, BASE_URL

ANALISTA_EMAIL    = "sofia.gomez@yopmail.com"
ANALISTA_PASSWORD = "Usuario1"

MARCO_CC          = "99887766"
MARCO_EMAIL       = "marco.diaz@yopmail.com"
MARCO_PASSWORD    = "Usuario1"

FECHA_INICIO_DIRECTO = "2026-04-25"


def buscar_empleado_marco(page: Page) -> str:
    """Navega a la lista de empleados, busca a Marco y retorna la URL de su perfil."""
    page.goto(f"{BASE_URL}/Empleado")
    page.wait_for_load_state("networkidle")
    page.fill("input[name=buscar]", MARCO_CC)
    page.keyboard.press("Enter")
    page.wait_for_load_state("networkidle")
    fila = page.locator("table tbody tr").first
    enlace = fila.locator("a[href*='/Empleado/Perfil/']").first
    href = enlace.get_attribute("href")
    return href  # Ej: /Empleado/Perfil/9


def obtener_id_marco(page: Page) -> int:
    """Retorna el EmpleadoId numérico de Marco buscando en la lista."""
    href = buscar_empleado_marco(page)
    return int(href.split("/")[-1])


# ---------------------------------------------------------------------------
# TC-VIN-01 — El formulario de edición muestra el selector TipoVinculacion
# ---------------------------------------------------------------------------
def test_tc_vin_01_formulario_muestra_selector_tipo_vinculacion(page: Page):
    """TC-VIN-01: El formulario /Empleado/Editar/{id} muestra el select TipoVinculacion."""
    hacer_login_completo(page, ANALISTA_EMAIL, ANALISTA_PASSWORD)
    emp_id = obtener_id_marco(page)
    page.goto(f"{BASE_URL}/Empleado/Editar/{emp_id}")
    page.wait_for_load_state("networkidle")

    selector = page.locator("#TipoVinculacion")
    expect(selector).to_be_visible()
    # El empleado es temporal, debe estar preseleccionado "Temporal"
    expect(selector).to_have_value("Temporal")


# ---------------------------------------------------------------------------
# TC-VIN-02 — Al seleccionar Directo, la sección temporal se oculta
# ---------------------------------------------------------------------------
def test_tc_vin_02_seleccionar_directo_oculta_seccion_temporal(page: Page):
    """TC-VIN-02: Al cambiar TipoVinculacion a Directo, #seccion-temporal se oculta."""
    hacer_login_completo(page, ANALISTA_EMAIL, ANALISTA_PASSWORD)
    emp_id = obtener_id_marco(page)
    page.goto(f"{BASE_URL}/Empleado/Editar/{emp_id}")
    page.wait_for_load_state("networkidle")

    # La sección debe estar visible inicialmente (es temporal)
    seccion = page.locator("#seccion-temporal")
    expect(seccion).to_be_visible()

    # Cambiar a Directo
    page.select_option("#TipoVinculacion", "Directo")

    # La sección debe ocultarse
    expect(seccion).to_be_hidden()


# ---------------------------------------------------------------------------
# TC-VIN-03 — Al seleccionar Temporal, la sección temporal reaparece
# ---------------------------------------------------------------------------
def test_tc_vin_03_seleccionar_temporal_muestra_seccion_temporal(page: Page):
    """TC-VIN-03: Al cambiar TipoVinculacion de Directo a Temporal, la sección reaparece."""
    hacer_login_completo(page, ANALISTA_EMAIL, ANALISTA_PASSWORD)
    emp_id = obtener_id_marco(page)
    page.goto(f"{BASE_URL}/Empleado/Editar/{emp_id}")
    page.wait_for_load_state("networkidle")

    page.select_option("#TipoVinculacion", "Directo")
    seccion = page.locator("#seccion-temporal")
    expect(seccion).to_be_hidden()

    page.select_option("#TipoVinculacion", "Temporal")
    expect(seccion).to_be_visible()


# ---------------------------------------------------------------------------
# TC-VIN-04 — Cambio exitoso: Temporal → Directo (flujo principal)
# ---------------------------------------------------------------------------
def test_tc_vin_04_cambio_exitoso_temporal_a_directo(page: Page, reset_empleado_marco):
    """TC-VIN-04: El analista guarda el cambio Temporal→Directo con FechaInicioContrato."""
    hacer_login_completo(page, ANALISTA_EMAIL, ANALISTA_PASSWORD)
    emp_id = obtener_id_marco(page)
    page.goto(f"{BASE_URL}/Empleado/Editar/{emp_id}")
    page.wait_for_load_state("networkidle")

    page.select_option("#TipoVinculacion", "Directo")
    # Ingresar la fecha de inicio del contrato directo
    page.fill("input[name$='FechaInicioContrato']", FECHA_INICIO_DIRECTO)

    page.click("button[type=submit]")
    page.wait_for_load_state("networkidle")

    # Debe redirigir al perfil
    assert "/Empleado/Perfil/" in page.url

    # Verificar mensaje de éxito
    exito = page.locator(".alert-success, [data-exito], .toast-success")
    expect(exito.first).to_be_visible()


# ---------------------------------------------------------------------------
# TC-VIN-05 — El perfil muestra TipoVinculacion = Directo tras el cambio
# ---------------------------------------------------------------------------
def test_tc_vin_05_perfil_muestra_tipo_directo(page: Page, reset_empleado_marco):
    """TC-VIN-05: Tras el cambio, el perfil del empleado muestra 'Directo' y oculta sección temporal."""
    hacer_login_completo(page, ANALISTA_EMAIL, ANALISTA_PASSWORD)
    emp_id = obtener_id_marco(page)
    page.goto(f"{BASE_URL}/Empleado/Editar/{emp_id}")
    page.wait_for_load_state("networkidle")

    page.select_option("#TipoVinculacion", "Directo")
    page.fill("input[name$='FechaInicioContrato']", FECHA_INICIO_DIRECTO)
    page.click("button[type=submit]")
    page.wait_for_load_state("networkidle")

    # Perfil del empleado
    perfil_tipo = page.locator(".dl-value", has_text="Directo")
    expect(perfil_tipo.first).to_be_visible()

    # La sección "Contrato temporal" NO debe mostrarse en el perfil
    seccion_temporal_perfil = page.locator("text=Contrato temporal")
    expect(seccion_temporal_perfil).to_be_hidden()


# ---------------------------------------------------------------------------
# TC-VIN-06 — FechaIngreso no cambia tras el cambio de vinculación
# ---------------------------------------------------------------------------
def test_tc_vin_06_fecha_ingreso_no_cambia(page: Page, reset_empleado_marco):
    """TC-VIN-06: FechaIngreso permanece igual (2025-04-25) tras el cambio."""
    hacer_login_completo(page, ANALISTA_EMAIL, ANALISTA_PASSWORD)
    emp_id = obtener_id_marco(page)
    page.goto(f"{BASE_URL}/Empleado/Editar/{emp_id}")
    page.wait_for_load_state("networkidle")

    page.select_option("#TipoVinculacion", "Directo")
    page.fill("input[name$='FechaInicioContrato']", FECHA_INICIO_DIRECTO)
    page.click("button[type=submit]")
    page.wait_for_load_state("networkidle")

    # Verificar FechaIngreso en el perfil (debe conservar 25/04/2025)
    perfil = page.locator(".dl-item", has_text="Fecha de ingreso")
    expect(perfil).to_contain_text("2025")


# ---------------------------------------------------------------------------
# TC-VIN-07 — Saldo vacaciones = 0 inmediatamente tras el cambio
# ---------------------------------------------------------------------------
def test_tc_vin_07_saldo_vacaciones_es_cero_post_cambio(page: Page, reset_empleado_marco):
    """TC-VIN-07: Tras el cambio con FechaInicioContrato=hoy, el saldo de vacaciones es 0."""
    hacer_login_completo(page, ANALISTA_EMAIL, ANALISTA_PASSWORD)
    emp_id = obtener_id_marco(page)
    page.goto(f"{BASE_URL}/Empleado/Editar/{emp_id}")
    page.wait_for_load_state("networkidle")

    page.select_option("#TipoVinculacion", "Directo")
    page.fill("input[name$='FechaInicioContrato']", FECHA_INICIO_DIRECTO)
    page.click("button[type=submit]")
    page.wait_for_load_state("networkidle")

    # Ir al perfil, tab de datos
    page.goto(f"{BASE_URL}/Empleado/Perfil/{emp_id}?tab=datos")
    page.wait_for_load_state("networkidle")

    # El saldo de vacaciones debe ser 0
    saldo = page.locator(".dl-item", has_text="Vacaciones disponibles")
    expect(saldo).to_contain_text("0")


# ---------------------------------------------------------------------------
# TC-VIN-08 — Solo el Analista puede ejecutar el cambio (control de acceso)
# ---------------------------------------------------------------------------
def test_tc_vin_08_solo_analista_puede_cambiar_tipo_vinculacion(page: Page):
    """TC-VIN-08: Un usuario Operario no puede acceder al formulario de edición."""
    hacer_login_completo(page, MARCO_EMAIL, MARCO_PASSWORD)
    emp_id = obtener_id_marco(page)
    page.goto(f"{BASE_URL}/Empleado/Editar/{emp_id}")
    page.wait_for_load_state("networkidle")

    # Operario debe recibir Forbid o redirección
    assert "Acceso-Denegado" in page.url or page.url.endswith("/")


# ---------------------------------------------------------------------------
# TC-VIN-09 — EmpresaTemporalId y FechaFinContrato quedan null en la BD
# ---------------------------------------------------------------------------
def test_tc_vin_09_campos_temporales_quedan_nulos(page: Page, reset_empleado_marco):
    """TC-VIN-09: Tras el cambio a Directo, EmpresaTemporalId y FechaFinContrato = null (UI)."""
    hacer_login_completo(page, ANALISTA_EMAIL, ANALISTA_PASSWORD)
    emp_id = obtener_id_marco(page)
    page.goto(f"{BASE_URL}/Empleado/Editar/{emp_id}")
    page.wait_for_load_state("networkidle")

    page.select_option("#TipoVinculacion", "Directo")
    page.fill("input[name$='FechaInicioContrato']", FECHA_INICIO_DIRECTO)
    page.click("button[type=submit]")
    page.wait_for_load_state("networkidle")

    # Volver a abrir el formulario de edición
    page.goto(f"{BASE_URL}/Empleado/Editar/{emp_id}")
    page.wait_for_load_state("networkidle")

    # EmpresaTemporalId debe estar vacío
    empresa_select = page.locator("select[name$='EmpresaTemporalId']")
    expect(empresa_select).to_have_value("")

    # FechaFinContrato debe estar vacío
    fecha_fin = page.locator("input[name$='FechaFinContrato']")
    expect(fecha_fin).to_have_value("")

    # TipoVinculacion debe ser Directo
    expect(page.locator("#TipoVinculacion")).to_have_value("Directo")
```

---

## Fase 5 — Verificación

### Tarea 5.1 — Levantar la aplicación

```powershell
cd "Proyecto MVC/GestionPersonal.Web"
dotnet run --launch-profile http
```

Esperar hasta ver: `Now listening on: http://localhost:5002`

### Tarea 5.2 — Ejecutar los tests

```powershell
cd Tests
.\.venv\Scripts\Activate.ps1
pytest test_cambio_vinculacion.py -v --tb=short
```

#### Resultado esperado

```
Tests/test_cambio_vinculacion.py::test_tc_vin_01_formulario_muestra_selector_tipo_vinculacion PASSED
Tests/test_cambio_vinculacion.py::test_tc_vin_02_seleccionar_directo_oculta_seccion_temporal PASSED
Tests/test_cambio_vinculacion.py::test_tc_vin_03_seleccionar_temporal_muestra_seccion_temporal PASSED
Tests/test_cambio_vinculacion.py::test_tc_vin_04_cambio_exitoso_temporal_a_directo PASSED
Tests/test_cambio_vinculacion.py::test_tc_vin_05_perfil_muestra_tipo_directo PASSED
Tests/test_cambio_vinculacion.py::test_tc_vin_06_fecha_ingreso_no_cambia PASSED
Tests/test_cambio_vinculacion.py::test_tc_vin_07_saldo_vacaciones_es_cero_post_cambio PASSED
Tests/test_cambio_vinculacion.py::test_tc_vin_08_solo_analista_puede_cambiar_tipo_vinculacion PASSED
Tests/test_cambio_vinculacion.py::test_tc_vin_09_campos_temporales_quedan_nulos PASSED

9 passed in X.XXs
```

---

## Resumen de Casos de Prueba

| ID | Scope | Descripción | Actor | Tipo |
|---|---|---|---|---|
| TC-VIN-01 | C — UI | Formulario muestra `<select>` TipoVinculacion preseleccionado | Analista | Funcional |
| TC-VIN-02 | C — UI | Seleccionar Directo oculta sección temporal | Analista | Funcional |
| TC-VIN-03 | C — UI | Seleccionar Temporal muestra sección temporal | Analista | Funcional |
| TC-VIN-04 | B + C | Flujo principal: cambio guardado correctamente | Analista | E2E |
| TC-VIN-05 | B + D | Perfil refleja Directo y oculta sección temporal | Analista | E2E |
| TC-VIN-06 | B | FechaIngreso permanece inalterada tras el cambio | Analista | Regresión |
| TC-VIN-07 | D | Saldo vacaciones = 0 inmediatamente después del cambio | Analista | Funcional |
| TC-VIN-08 | A | Control de acceso: Operario no puede acceder a Editar | Operario | Seguridad |
| TC-VIN-09 | B | EmpresaTemporalId y FechaFinContrato quedan null en UI | Analista | E2E |
