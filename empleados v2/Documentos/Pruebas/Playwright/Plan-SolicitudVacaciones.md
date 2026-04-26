# Plan — Solicitud de Vacaciones con Balance y Días a Disfrutar

## Contexto y objetivo

Actualmente el modal **"Nueva solicitud"** (ruta `Solicitud/Index`) que usan los roles `Operario` y
`Direccionador` no muestra el saldo de vacaciones disponible, ni permite al usuario elegir
explícitamente cuántos días quiere disfrutar.

El modal **"Registrar evento laboral"** (ruta `EventoLaboral/Index`) que usa el jefe/supervisor
sí muestra el balance (días acumulados, días tomados, saldo disponible) cuando selecciona
`Vacaciones`, pero carece de los campos **Motivo** y **Observaciones**.

El objetivo de este plan es:

1. Mostrar el bloque de balance de vacaciones (cuadro azul) en **ambos** modales cuando el tipo
   de evento es `Vacaciones`.
2. Agregar el campo **Días a disfrutar** (explícito, editable) en ambos modales, visible solo
   cuando el tipo es `Vacaciones`.
3. Garantizar que **Motivo** (obligatorio) y **Observaciones** (opcional) estén presentes en
   ambos modales.
4. Implementar todas las validaciones de negocio requeridas.

---

## Imágenes de referencia

| Modal usuario (antes) | Modal jefe (referencia de diseño) |
|---|---|
| `Documentos/Pruebas/img/Solicitudes/solicitudVacaionesUsuario.png` | `Documentos/Pruebas/img/Solicitudes/SolicitudVacacionJefe.png` |

El modal del usuario debe quedar visualmente igual al del jefe cuando el tipo es `Vacaciones`:
cuadro azul con Días acumulados / Días tomados / Saldo disponible + barra de progreso.

---

## Prerequisitos

- [ ] Proyecto compila sin errores: `dotnet build "Proyecto MVC/GestionPersonal.slnx"`
- [ ] Seeding `Documentos/BD/Seeding_Completo.sql` aplicado en `(localdb)\MSSQLLocalDB`
- [ ] Al menos un empleado con `FechaInicioContrato` no nulo (para que el cálculo de saldo funcione)
- [ ] Aplicación en `http://localhost:5002`
- [ ] Entorno virtual Python activo: `.venv\Scripts\Activate.ps1`

---

## Análisis de componentes existentes

| Componente | Ubicación | Estado actual |
|---|---|---|
| Modal usuario | `GestionPersonal.Web/Views/Solicitud/Index.cshtml` | Sin balance, sin días a disfrutar |
| Modal jefe | `GestionPersonal.Web/Views/EventoLaboral/Index.cshtml` | Con balance, sin días a disfrutar, sin Motivo/Observaciones |
| Endpoint balance | `GET /EventoLaboral/SaldoVacaciones?empleadoId=` | ✅ Existe y es accesible a todos los roles autenticados |
| `SaldoVacacionesDto` | `GestionPersonal.Models/DTOs/EventoLaboral/SaldoVacacionesDto.cs` | ✅ Acumulados, Tomados, Disponibles |
| `IEventoLaboralService.ObtenerSaldoVacacionesAsync` | Interface + Service | ✅ Implementado |
| `CrearEventoLaboralDto` | `GestionPersonal.Models/DTOs/EventoLaboral/CrearEventoLaboralDto.cs` | ❌ Sin `DiasDisfrutar` |
| `EventoLaboral` entity | `GestionPersonal.Models/Entities/GestionPersonalEntities/EventoLaboral.cs` | ❌ Sin columna `DiasDisfrutar` |
| `SolicitudController` | `GestionPersonal.Web/Controllers/SolicitudController.cs` | ❌ No expone `EmpleadoId` a la vista |
| `EventoLaboralService.CrearAsync` | Service | ❌ Sin validación de DiasDisfrutar vs saldo |

---

## Resumen de tareas

| # | Fase | Archivo | Descripción | Estado |
|---|---|---|---|---|
| 1.1 | Entidad | `EventoLaboral.cs` | Agregar propiedad `DiasDisfrutar` (nullable int) | ⏳ Pendiente |
| 1.2 | Migración | EF Core migration | Columna `DiasDisfrutar INT NULL` en tabla `EventosLaborales` | ⏳ Pendiente |
| 1.3 | DTO entrada | `CrearEventoLaboralDto.cs` | Agregar `DiasDisfrutar` nullable | ⏳ Pendiente |
| 1.4 | DTO salida | `EventoLaboralDto.cs` | Agregar `DiasDisfrutar` nullable | ⏳ Pendiente |
| — | Build | Build Fase 1 | Verificar compilación | ⏳ Pendiente |
| 2.1 | Service | `EventoLaboralService.CrearAsync` | Validar `DiasDisfrutar <= saldo.Disponibles` cuando tipo == Vacaciones | ⏳ Pendiente |
| 2.2 | Service | `EventoLaboralService.MapToDto` | Incluir `DiasDisfrutar` en el mapeo | ⏳ Pendiente |
| — | Build | Build Fase 2 | Verificar compilación | ⏳ Pendiente |
| 3.1 | Controller | `SolicitudController.Index` | Exponer `EmpleadoId` a la vista con `ViewBag.EmpleadoId` | ⏳ Pendiente |
| 3.2 | Controller | `SolicitudController.Crear` | Aceptar parámetro `int? diasDisfrutar` y mapearlo al DTO | ⏳ Pendiente |
| — | Build | Build Fase 3 | Verificar compilación | ⏳ Pendiente |
| 4.1 | Frontend | `Solicitud/Index.cshtml` — balance widget | Agregar bloque HTML del balance de vacaciones (igual al modal jefe) | ⏳ Pendiente |
| 4.2 | Frontend | `Solicitud/Index.cshtml` — campo días | Agregar campo "Días a disfrutar" (oculto por defecto) | ⏳ Pendiente |
| 4.3 | Frontend | `Solicitud/Index.cshtml` — JS | AJAX para cargar saldo, lógica show/hide, validaciones | ⏳ Pendiente |
| — | Build | Build Fase 4 | Verificar compilación | ⏳ Pendiente |
| 5.1 | Frontend | `EventoLaboral/Index.cshtml` — días disfrutar | Agregar campo "Días a disfrutar" en sección de vacaciones | ⏳ Pendiente |
| 5.2 | Frontend | `EventoLaboral/Index.cshtml` — motivo/obs | Agregar campos Motivo (obligatorio) y Observaciones a la sección de vacaciones | ⏳ Pendiente |
| 5.3 | Frontend | `EventoLaboral/Index.cshtml` — JS | Incluir `DiasDisfrutar` en serialización del form AJAX | ⏳ Pendiente |
| — | Build | Build Fase 5 (Final) | Verificar compilación limpia | ⏳ Pendiente |
| 6.1 | Tests | `Tests/test_solicitud_vacaciones.py` | Crear suite con TC-SOL-VAC-01 a TC-SOL-VAC-11 | ⏳ Pendiente |

---

## Detalle de cambios por fase

---

### Fase 1 — Modelo y DTOs

#### 1.1 `EventoLaboral.cs` — Agregar columna
**Ruta:** `GestionPersonal.Models/Entities/GestionPersonalEntities/EventoLaboral.cs`

Agregar después de `public string? Descripcion { get; set; }`:
```csharp
/// <summary>Días explícitamente solicitados para vacaciones. Null para otros tipos de evento.</summary>
public int? DiasDisfrutar { get; set; }
```

---

#### 1.2 Migración EF Core
Desde `Proyecto MVC/` ejecutar:
```bash
dotnet ef migrations add AddDiasDisfrutarToEventoLaboral --project GestionPersonal.Infrastructure --startup-project GestionPersonal.Web
dotnet ef database update --project GestionPersonal.Infrastructure --startup-project GestionPersonal.Web
```
La migración debe generar:
```csharp
migrationBuilder.AddColumn<int>(
    name: "DiasDisfrutar",
    table: "EventosLaborales",
    type: "int",
    nullable: true);
```
> Si se prefiere no usar migrations automáticas, el script SQL equivalente es:
> ```sql
> ALTER TABLE EventosLaborales ADD DiasDisfrutar INT NULL;
> ```

---

#### 1.3 `CrearEventoLaboralDto.cs` — Nuevo campo
**Ruta:** `GestionPersonal.Models/DTOs/EventoLaboral/CrearEventoLaboralDto.cs`

Agregar antes de `EstadoInicial`:
```csharp
/// <summary>Días explícitamente solicitados (solo Vacaciones). Validado contra saldo disponible.</summary>
[Range(1, 365, ErrorMessage = "Los días a disfrutar deben ser entre 1 y 365.")]
public int? DiasDisfrutar { get; set; }
```

---

#### 1.4 `EventoLaboralDto.cs` — Nuevo campo
**Ruta:** `GestionPersonal.Models/DTOs/EventoLaboral/EventoLaboralDto.cs`

Agregar:
```csharp
public int? DiasDisfrutar { get; init; }
```

---

### Fase 2 — Service: Validación de saldo

#### 2.1 `EventoLaboralService.CrearAsync` — Validación
**Ruta:** `GestionPersonal.Application/Services/EventoLaboralService.cs`

Dentro del método `CrearAsync`, antes de persistir el evento, agregar la validación para vacaciones:

```csharp
// Validación de saldo de vacaciones
if (dto.TipoEvento == TipoEvento.Vacaciones && dto.DiasDisfrutar.HasValue)
{
    var saldo = await ObtenerSaldoVacacionesAsync(dto.EmpleadoId, ct);
    if (saldo is null)
        return ResultadoOperacion.Fail("No se pudo calcular el saldo de vacaciones del empleado.");

    if (saldo.Disponibles <= 0)
        return ResultadoOperacion.Fail("El empleado no cuenta con días disponibles de vacaciones.");

    if (dto.DiasDisfrutar.Value > saldo.Disponibles)
        return ResultadoOperacion.Fail(
            $"Los días a disfrutar ({dto.DiasDisfrutar.Value}) superan el saldo disponible ({saldo.Disponibles} días).");
}
```

---

#### 2.2 `EventoLaboralService.MapToDto` — Mapeo
Incluir el nuevo campo en el método de mapeo privado:

```csharp
DiasDisfrutar = e.DiasDisfrutar,
```

---

### Fase 3 — Controller: SolicitudController

#### 3.1 `SolicitudController.Index` — Exponer EmpleadoId
**Ruta:** `GestionPersonal.Web/Controllers/SolicitudController.cs`

Dentro del método `Index`, después de obtener `empId`, agregar:
```csharp
ViewBag.EmpleadoId = empId.Value;
```
Esto permite que la vista JavaScript llame a `/EventoLaboral/SaldoVacaciones?empleadoId=X`.

---

#### 3.2 `SolicitudController.Crear` — Nuevo parámetro
Actualizar la firma del método para incluir `diasDisfrutar`:

```csharp
public async Task<IActionResult> Crear(
    string tipoEvento,
    string fechaInicio,
    string fechaFin,
    string? descripcion,
    string? observaciones,
    int? diasDisfrutar)      // ← nuevo
```

Agregar al bloque de construcción del DTO:
```csharp
DiasDisfrutar = (tipo == TipoEvento.Vacaciones && diasDisfrutar.HasValue && diasDisfrutar > 0)
    ? diasDisfrutar
    : null,
```

---

### Fase 4 — Frontend: Modal usuario (`Solicitud/Index.cshtml`)

#### 4.1 Balance widget — HTML
Agregar el siguiente bloque HTML **después del selector de tipo** y **antes del grid de fechas**,
dentro del `<form id="form-solicitud">`:

```html
<!-- Balance vacaciones (solo visible cuando tipo = Vacaciones) -->
<div id="sol-vac-balance-widget" hidden>
  <div class="vac-balance" aria-live="polite">
    <div class="vac-balance-row">
      <span class="vac-balance-label">Días acumulados</span>
      <span class="vac-balance-val" id="sol-vac-acumulados">—</span>
    </div>
    <div class="vac-balance-row">
      <span class="vac-balance-label">Días tomados</span>
      <span class="vac-balance-val" id="sol-vac-tomados">—</span>
    </div>
    <div class="vac-balance-row" style="margin-bottom:var(--sp-3)">
      <span class="vac-balance-label" style="font-weight:700">Saldo disponible</span>
      <span class="vac-balance-val" id="sol-vac-disponibles" style="font-size:1.125rem">—</span>
    </div>
    <div class="vac-bar-track" aria-hidden="true">
      <div class="vac-bar-fill" id="sol-vac-bar" style="width:0%"></div>
    </div>
  </div>
  <!-- Alerta sin saldo -->
  <div class="alert alert--warning" id="sol-vac-sin-saldo" hidden role="alert">
    <div class="alert-body">
      <p class="alert-title">Sin días disponibles</p>
      <p>Usted no cuenta con días disponibles de vacaciones.</p>
    </div>
  </div>
</div>
```

---

#### 4.2 Campo "Días a disfrutar" — HTML
Agregar **dentro del grid de fechas** (después del campo Fecha fin) o como campo independiente:

```html
<!-- Días a disfrutar (solo Vacaciones) -->
<div class="form-group" id="sol-campo-dias-disfrutar" hidden>
  <label class="form-label" for="sol-dias-disfrutar">
    Días a disfrutar <span class="required" aria-hidden="true">*</span>
  </label>
  <input class="form-input" type="number" id="sol-dias-disfrutar"
         name="diasDisfrutar" min="1" max="365" inputmode="numeric"
         placeholder="Ej: 5"
         style="max-width:10rem">
  <span class="form-hint" id="sol-dias-hint">Ingresa la cantidad de días que deseas disfrutar.</span>
</div>
```

---

#### 4.3 JavaScript actualizado
Reemplazar el bloque `@section Scripts` con la siguiente lógica ampliada:

```javascript
@section Scripts {
<script>
(function () {
  'use strict';

  var empId   = @ViewBag.EmpleadoId;
  var vacSaldo = null;

  var form         = document.getElementById('form-solicitud');
  var errBox       = document.getElementById('sol-error');
  var tipoSel      = document.getElementById('sol-tipo');
  var inicio       = document.getElementById('sol-inicio');
  var fin          = document.getElementById('sol-fin');
  var balanceWgt   = document.getElementById('sol-vac-balance-widget');
  var sinSaldoAlrt = document.getElementById('sol-vac-sin-saldo');
  var campoDias    = document.getElementById('sol-campo-dias-disfrutar');
  var inputDias    = document.getElementById('sol-dias-disfrutar');
  var hintDias     = document.getElementById('sol-dias-hint');
  var submitBtn    = document.getElementById('sol-submit');

  // ── Al cambiar el tipo de solicitud ───────────────────────────────
  tipoSel.addEventListener('change', onTipoChange);

  function onTipoChange() {
    if (tipoSel.value === 'Vacaciones') {
      cargarSaldo();
    } else {
      balanceWgt.hidden = true;
      campoDias.hidden  = true;
      inputDias.removeAttribute('required');
      inputDias.value   = '';
      vacSaldo = null;
      habilitarFormulario();
    }
  }

  // ── Cargar saldo vía AJAX ─────────────────────────────────────────
  function cargarSaldo() {
    fetch('/EventoLaboral/SaldoVacaciones?empleadoId=' + encodeURIComponent(empId))
      .then(function (r) { return r.ok ? r.json() : null; })
      .then(function (data) {
        if (!data) { balanceWgt.hidden = true; return; }

        vacSaldo = data;

        document.getElementById('sol-vac-acumulados').textContent  = data.acumulados + ' días';
        document.getElementById('sol-vac-tomados').textContent     = data.tomados    + ' días';
        document.getElementById('sol-vac-disponibles').textContent = data.disponibles + ' días';

        var pct = data.acumulados > 0
          ? Math.min(100, (data.disponibles / data.acumulados) * 100)
          : 0;
        var bar = document.getElementById('sol-vac-bar');
        bar.style.width = pct + '%';
        bar.className   = 'vac-bar-fill' +
          (pct <= 0 ? ' is-empty' : pct <= 40 ? ' is-low' : '');

        balanceWgt.hidden = false;

        if (data.disponibles <= 0) {
          // Sin saldo: mostrar alerta, deshabilitar campos de vacaciones
          sinSaldoAlrt.hidden = false;
          campoDias.hidden    = true;
          inputDias.value     = '';
          bloquearFormulario();
        } else {
          sinSaldoAlrt.hidden = true;
          campoDias.hidden    = false;
          inputDias.setAttribute('required', 'required');
          inputDias.setAttribute('max', data.disponibles);
          hintDias.textContent =
            'Máximo ' + data.disponibles + ' días disponibles.';
          habilitarFormulario();
        }
      })
      .catch(function () {
        balanceWgt.hidden = true;
        campoDias.hidden  = true;
      });
  }

  function bloquearFormulario() {
    inicio.disabled   = true;
    fin.disabled      = true;
    inputDias.disabled = true;
    submitBtn.disabled = true;
  }

  function habilitarFormulario() {
    inicio.disabled   = false;
    fin.disabled      = false;
    inputDias.disabled = false;
    submitBtn.disabled = false;
  }

  // ── Validación en submit ──────────────────────────────────────────
  form.addEventListener('submit', function (e) {
    errBox.hidden = true;
    var errors = [];

    if (!tipoSel.value)
      errors.push('Selecciona el tipo de solicitud.');
    if (!inicio.value)
      errors.push('Ingresa la fecha de inicio.');
    if (!fin.value)
      errors.push('Ingresa la fecha de fin.');
    if (inicio.value && fin.value && fin.value < inicio.value)
      errors.push('La fecha de fin no puede ser anterior a la fecha de inicio.');
    if (!document.getElementById('sol-descripcion').value.trim())
      errors.push('El motivo es obligatorio.');

    // Validaciones específicas de vacaciones
    if (tipoSel.value === 'Vacaciones') {
      var dias = parseInt(inputDias.value, 10);

      if (!inputDias.value || isNaN(dias) || dias < 1)
        errors.push('Ingresa una cantidad válida de días a disfrutar (mínimo 1).');
      else if (dias < 0)
        errors.push('Los días a disfrutar no pueden ser negativos.');
      else if (vacSaldo && dias > vacSaldo.disponibles)
        errors.push(
          'Los días a disfrutar (' + dias + ') superan tu saldo disponible (' +
          vacSaldo.disponibles + ' días).'
        );

      if (vacSaldo && vacSaldo.disponibles <= 0)
        errors.push('No cuentas con días disponibles de vacaciones.');
    }

    if (errors.length) {
      e.preventDefault();
      errBox.textContent = errors.join(' ');
      errBox.hidden = false;
    }
  });

  // ── Fechas mínimas ────────────────────────────────────────────────
  var hoy = new Date().toISOString().split('T')[0];
  inicio.setAttribute('min', hoy);
  inicio.addEventListener('change', function () {
    fin.setAttribute('min', inicio.value || hoy);
    if (fin.value && fin.value < inicio.value) fin.value = '';
  });

}());
</script>
}
```

---

### Fase 5 — Frontend: Modal jefe (`EventoLaboral/Index.cshtml`)

#### 5.1 Campo "Días a disfrutar" — HTML
Dentro del `#vac-balance-widget`, **después del bloque de la barra de progreso** y **antes de las
fechas**, agregar:

```html
<!-- Días a disfrutar (Vacaciones) -->
<div class="form-group" id="ev-campo-dias-disfrutar" hidden>
  <label class="form-label" for="ev-dias-disfrutar">
    Días a disfrutar <span class="required" aria-hidden="true">*</span>
  </label>
  <input class="form-input" type="number" id="ev-dias-disfrutar"
         name="DiasDisfrutar" min="1" max="365" inputmode="numeric"
         placeholder="Ej: 5" style="max-width:10rem">
  <span class="form-hint" id="ev-dias-hint">Ingresa los días de vacaciones a disfrutar.</span>
</div>
```

---

#### 5.2 Motivo y Observaciones — HTML
En la sección de Vacaciones (o como campos comunes siempre visibles), agregar **después de las
fechas y antes del campo "Autorizado por"**:

```html
<!-- Motivo y Observaciones (Vacaciones) -->
<div id="campos-vacaciones-descripcion" hidden>
  <div class="form-group">
    <label class="form-label" for="ev-vac-motivo">
      Motivo <span class="required" aria-hidden="true">*</span>
    </label>
    <textarea class="form-input" id="ev-vac-motivo" name="Descripcion"
              rows="3" maxlength="400"
              placeholder="Describe brevemente el motivo de tu solicitud de vacaciones…"></textarea>
  </div>
  <div class="form-group">
    <label class="form-label" for="ev-vac-observaciones">Observaciones</label>
    <textarea class="form-input" id="ev-vac-observaciones" name="Observaciones"
              rows="2" maxlength="300"
              placeholder="Información adicional (opcional)…"></textarea>
  </div>
</div>
```

> **Nota:** El campo `name="Observaciones"` deberá mapearse en `CrearEventoLaboralDto` o manejarse
> en el controller como campo adicional, similar a como `SolicitudController` combina motivo y
> observaciones en `Descripcion`.

---

#### 5.3 JavaScript — Actualización de `updateVacBalance` y validación

En la función `updateVacBalance` del modal jefe, después de actualizar el balance:
```javascript
// Mostrar/ocultar campos de vacaciones
var campoDiasDisfrutar = document.getElementById('ev-campo-dias-disfrutar');
var camposDesc = document.getElementById('campos-vacaciones-descripcion');

if (data.disponibles <= 0) {
  document.getElementById('vac-sin-saldo').hidden = false;
  campoDiasDisfrutar.hidden = true;
  camposDesc.hidden = false;   // sí mostrar motivo incluso sin saldo
  // Deshabilitar submit
} else {
  document.getElementById('vac-sin-saldo').hidden = true;
  campoDiasDisfrutar.hidden = false;
  camposDesc.hidden = false;
  var inputDiasEv = document.getElementById('ev-dias-disfrutar');
  inputDiasEv.setAttribute('max', data.disponibles);
  document.getElementById('ev-dias-hint').textContent =
    'Máximo ' + data.disponibles + ' días disponibles.';
}
```

En el evento `tipo.change`, cuando el tipo NO es Vacaciones:
```javascript
document.getElementById('ev-campo-dias-disfrutar').hidden = true;
document.getElementById('campos-vacaciones-descripcion').hidden = true;
```

En la validación de submit del modal jefe, agregar:
```javascript
if (tipo === 'Vacaciones') {
  var diasDisfrutar = parseInt(document.getElementById('ev-dias-disfrutar').value, 10);
  if (isNaN(diasDisfrutar) || diasDisfrutar < 1)
    errors.push('Ingresa los días a disfrutar.');
  else if (vacSaldo && diasDisfrutar > vacSaldo.disponibles)
    errors.push('Los días a disfrutar superan el saldo disponible.');

  if (!document.getElementById('ev-vac-motivo').value.trim())
    errors.push('El motivo es obligatorio.');
}
```

En `resetModal`, agregar:
```javascript
document.getElementById('ev-campo-dias-disfrutar').hidden = true;
document.getElementById('campos-vacaciones-descripcion').hidden = true;
document.getElementById('ev-dias-disfrutar').value = '';
document.getElementById('ev-vac-motivo').value = '';
document.getElementById('ev-vac-observaciones').value = '';
```

---

## Reglas de negocio y validaciones — Resumen

| Regla | Aplica a | Implementación |
|---|---|---|
| Balance (acumulados, tomados, disponible) solo aparece cuando tipo = Vacaciones | Ambos modales | JS `onTipoChange` / `updateVacBalance` |
| "Días a disfrutar" solo aparece cuando tipo = Vacaciones | Ambos modales | JS show/hide |
| Días a disfrutar no puede ser negativo ni cero | Ambos modales | HTML `min="1"` + validación JS + validación service |
| Días a disfrutar no puede superar el saldo disponible | Ambos modales | Validación JS + validación service |
| Si saldo = 0: mostrar formulario pero deshabilitado con mensaje "usted no cuenta con días disponibles" | Modal usuario | JS `bloquearFormulario()` + alerta |
| Si saldo = 0: mostrar alerta "Saldo insuficiente" | Modal jefe | Alerta existente `#vac-sin-saldo` |
| Motivo es obligatorio | Ambos modales | `required` en HTML + validación JS + validación controller |
| Observaciones es opcional | Ambos modales | Sin atributo `required` |

---

## Casos de prueba

### TC-SOL-VAC-01 — Balance visible al seleccionar Vacaciones (usuario)
- **Precondición:** Usuario con rol Operario o Direccionador, con días acumulados > 0.
- **Pasos:** Abrir modal "Nueva solicitud" → Seleccionar tipo "Vacaciones".
- **Resultado esperado:** Aparece el bloque azul con Días acumulados, Días tomados, Saldo disponible y barra de progreso. El campo "Días a disfrutar" es visible.

---

### TC-SOL-VAC-02 — Balance oculto para otros tipos (usuario)
- **Precondición:** Usuario con rol Operario o Direccionador.
- **Pasos:** Abrir modal → Seleccionar "Incapacidad" → Verificar que no aparece el balance.
  Luego cambiar a "Permiso" → Verificar que tampoco aparece. Cambiar a "Vacaciones" → Aparece.
- **Resultado esperado:** El balance y "Días a disfrutar" solo se muestran para Vacaciones.

---

### TC-SOL-VAC-03 — Campo "Días a disfrutar" no aparece para Incapacidad
- **Pasos:** Seleccionar "Incapacidad" en modal usuario.
- **Resultado esperado:** Campo "Días a disfrutar" permanece oculto (`hidden`).

---

### TC-SOL-VAC-04 — Campo "Días a disfrutar" no aparece para Permiso
- **Pasos:** Seleccionar "Permiso" en modal usuario.
- **Resultado esperado:** Campo "Días a disfrutar" permanece oculto (`hidden`).

---

### TC-SOL-VAC-05 — Validación: días > saldo disponible
- **Precondición:** Usuario con saldo disponible = 10 días.
- **Pasos:** Seleccionar Vacaciones → Ingresar 15 en "Días a disfrutar" → Completar fechas y motivo → Clic en "Enviar solicitud".
- **Resultado esperado:** El formulario NO se envía. Se muestra mensaje de error indicando que los días superan el saldo disponible (10 días).

---

### TC-SOL-VAC-06 — Validación: días negativos o cero
- **Pasos:** Seleccionar Vacaciones → Ingresar -1 o 0 en "Días a disfrutar" → Intentar enviar.
- **Resultado esperado:** El formulario NO se envía. Se muestra mensaje de error.

---

### TC-SOL-VAC-07 — Usuario sin saldo disponible
- **Precondición:** Usuario con `DiasSolicitados` histórico >= días acumulados (saldo = 0).
- **Pasos:** Abrir modal → Seleccionar Vacaciones.
- **Resultado esperado:** Aparece el bloque de balance mostrando 0 días disponibles. Se muestra el
  mensaje "Usted no cuenta con días disponibles". Los campos de fechas y "Días a disfrutar" están
  deshabilitados. El botón "Enviar solicitud" está deshabilitado.

---

### TC-SOL-VAC-08 — Motivo es obligatorio
- **Pasos:** Seleccionar Vacaciones → Completar fechas y días a disfrutar → Dejar Motivo vacío →
  Clic en "Enviar solicitud".
- **Resultado esperado:** El formulario NO se envía. Se muestra error indicando que el motivo es
  obligatorio.

---

### TC-SOL-VAC-09 — Envío exitoso de solicitud de vacaciones (usuario)
- **Precondición:** Usuario con saldo > 0.
- **Pasos:** Seleccionar Vacaciones → Ingresar días válidos (≤ saldo) → Completar fechas y motivo
  → Clic en "Enviar solicitud".
- **Resultado esperado:** La solicitud se crea con estado `Pendiente`. Se muestra mensaje de éxito.
  La solicitud aparece en la tabla de solicitudes del usuario.

---

### TC-SOL-VAC-10 — Jefe ve balance del empleado en su modal
- **Precondición:** Jefe con acceso a `EventoLaboral/Index`.
- **Pasos:** Abrir modal "Registrar evento laboral" → Seleccionar empleado → Seleccionar
  tipo "Vacaciones".
- **Resultado esperado:** Aparece el bloque azul con balance del empleado seleccionado. Aparece
  el campo "Días a disfrutar". Aparecen los campos Motivo y Observaciones.

---

### TC-SOL-VAC-11 — Jefe crea evento de vacaciones con días a disfrutar
- **Precondición:** Empleado con saldo > 0.
- **Pasos:** Seleccionar empleado → Vacaciones → Ingresar días válidos → Completar fechas, motivo
  y autorizado por → Clic en "Registrar evento".
- **Resultado esperado:** El evento se registra con `DiasDisfrutar` guardado. La solicitud aparece
  en el historial del empleado con los días solicitados reflejados.

---

## Comando de ejecución de pruebas

```powershell
cd "c:\Users\alejandro.ortiz\Documents\helpharma\Desarrollos\lissy\IA\LissyIAHelpharma\empleados v2"
$env:PYTHONIOENCODING='utf-8'
$fecha = Get-Date -Format "yyyy-MM-dd_HH-mm-ss"
$informe = "Tests\resultados\solicitud-vacaciones-$fecha.txt"
New-Item -ItemType Directory -Force -Path "Tests\resultados" | Out-Null
.venv\Scripts\python.exe -m pytest Tests/test_solicitud_vacaciones.py -v --headed --slowmo 800 -s 2>&1 | Tee-Object -FilePath $informe
Write-Host "`nInforme: $informe"
```

---

## Notas de implementación

1. **`EventoLaboralController.SaldoVacaciones`** ya tiene `[Authorize]` (sin restricción de rol),
   por lo que Operario y Direccionador pueden llamarlo directamente desde JavaScript con `fetch`.
   No es necesario agregar un nuevo endpoint en `SolicitudController`.

2. **Bloqueo del formulario vs. deshabilitado:** cuando el saldo es 0, deshabilitar visualmente
   los campos con `disabled` en JS es suficiente para UX. La validación en el service también
   rechazará el envío si alguien evade el bloqueo frontend.

3. **Campo `Observaciones` en el modal jefe:** el `CrearEventoLaboralDto` no tiene propiedad
   `Observaciones` independiente. Se recomienda combinar motivo y observaciones en `Descripcion`
   siguiendo el mismo patrón que `SolicitudController.CombinarDescripcion`.

4. **Migración:** si el equipo usa scripts SQL manuales en lugar de `dotnet ef migrations`, el
   script ALTER TABLE correspondiente debe agregarse a `Documentos/BD/` y aplicarse antes de
   desplegar.

5. **`DiasSolicitados` existente:** este campo se calcula automáticamente a partir de
   `FechaFin - FechaInicio` y se usa para el historial. `DiasDisfrutar` es el valor explícito
   ingresado por el usuario y es el que se valida contra el saldo. Son conceptualmente distintos.
