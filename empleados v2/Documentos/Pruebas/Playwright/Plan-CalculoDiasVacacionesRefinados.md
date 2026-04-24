# Plan de Ejecución — Trazabilidad de Eventos Laborales y Cálculo de Vacaciones
## Sistema GestionPersonal

> **Basado en:** `CalculoDiasVacacionesRefinado.md` (Shape Up Pitch)
> **Ejecutor:** GitHub Copilot (requiere aprobación previa del usuario)
> **Orden de implementación:** DTOs/ViewModels → Repository → Service → Controller → Frontend → Tests → Verificación
> **Granularidad:** Una tarea por archivo modificado
> **Verificación:** Build por fase (no archivo a archivo)
> **Última actualización:** Abril 2026

---

## Estado actual del código (diagnóstico previo)

Antes de iniciar, se verificó el estado base del sistema para identificar qué ya existe y qué debe crearse:

| Elemento | Estado actual | Acción requerida |
|---|---|---|
| `EventoLaboralDto.DiasSolicitados` | ✅ Ya existe (calculado en `MapToDto`) | Solo agregar al frontend |
| Columna "Días" en tabla Historial | ❌ No se muestra en `Perfil.cshtml` | Agregar `<th>` y `<td>` |
| Filtros Desde/Hasta en tab Historial | ❌ No existen | Crear en frontend + backend |
| `IEventoLaboralRepository` filtro por fecha | ❌ No existe | Agregar nuevo método |
| `IEventoLaboralService` filtro por fecha | ❌ No existe | Agregar nuevo método |
| Resumen por tipo de evento | ❌ No existe | DTO nuevo + cálculo en service/controller |
| `PerfilEmpleadoViewModel` filtros y resumen | ❌ No tiene | Agregar propiedades |
| `VacacionesDisponibles` (calculado) | ❌ No existe | Nuevo cálculo en controller |
| `ObtenerSaldoVacacionesAsync` | ⚠️ Existe pero lógica incorrecta | Corregir: usar `FechaInicioContrato × 1.25` |
| Tab Datos — campo "Vacaciones disponibles" | ❌ Muestra `DiasVacacionesPrevios` (DB) | Cambiar a valor calculado |

---

## Decisiones de diseño resueltas

Las siguientes decisiones marcadas como pendientes en el pitch fueron resueltas antes de implementar:

| Decisión | Resolución |
|---|---|
| Criterio de filtrado (FechaInicio vs solapamiento) | **Filtrar por `FechaInicio`** dentro del rango. Suficiente para el 95% de los casos de RRHH y mantiene la consulta simple. |
| Decimales en vacaciones disponibles | **Mostrar con un decimal** (ej: `10.8 días`). Más preciso sin ser confuso. |

---

## Prerequisitos (verificar antes de ejecutar)

- [ ] Seeding `Documentos/BD/Seeding_Completo.sql` aplicado en `(localdb)\MSSQLLocalDB`
- [ ] Al menos un empleado en la BD tiene `FechaInicioContrato` con valor no nulo
- [ ] Al menos un empleado tiene eventos tipo `Vacaciones` registrados (para verificar resumen y cálculo)
- [ ] Proyecto compila sin errores: `dotnet build GestionPersonal.slnx`
- [ ] La aplicación levanta en `http://localhost:5002`
- [ ] Entorno virtual Python activo: `.venv\Scripts\Activate.ps1`

---

## Resumen de Tareas

| # | Fase | Archivo | Descripción | Estado |
|---|---|---|---|---|
| 1.1 | DTOs | `ResumenEventoDto.cs` (nuevo) | Crear DTO con `TipoEvento` y `TotalDias` | ⏳ Pendiente |
| 1.2 | ViewModels | `PerfilEmpleadoViewModel.cs` | Agregar `VacacionesDisponibles`, `ResumenEventos`, `FiltroDesde`, `FiltroHasta` | ⏳ Pendiente |
| — | Build | Build Fase 1 | Verificar compilación | ⏳ Pendiente |
| 2.1 | Repository | `IEventoLaboralRepository.cs` | Agregar método `ObtenerPorEmpleadoConFiltroAsync(int, DateOnly?, DateOnly?)` | ⏳ Pendiente |
| 2.2 | Repository | `EventoLaboralRepository.cs` | Implementar el método con filtro LINQ/EF | ⏳ Pendiente |
| — | Build | Build Fase 2 | Verificar compilación | ⏳ Pendiente |
| 3.1 | Service | `IEventoLaboralService.cs` | Agregar método `ObtenerPorEmpleadoConFiltroAsync` | ⏳ Pendiente |
| 3.2 | Service | `EventoLaboralService.cs` — método nuevo | Implementar `ObtenerPorEmpleadoConFiltroAsync` con cálculo de resumen por tipo | ⏳ Pendiente |
| 3.3 | Service | `EventoLaboralService.cs` — `ObtenerSaldoVacacionesAsync` | Corregir lógica: usar `FechaInicioContrato × 1.25` en lugar de `FechaIngreso × 15` | ⏳ Pendiente |
| — | Build | Build Fase 3 | Verificar compilación | ⏳ Pendiente |
| 4.1 | Controller | `EmpleadoController.cs` — firma de `Perfil` | Agregar params `DateOnly? desde` y `DateOnly? hasta` | ⏳ Pendiente |
| 4.2 | Controller | `EmpleadoController.cs` — cuerpo de `Perfil` | Llamar versión filtrada de eventos, calcular `VacacionesDisponibles`, pasar todo al ViewModel | ⏳ Pendiente |
| — | Build | Build Fase 4 | Verificar compilación | ⏳ Pendiente |
| 5.1 | Frontend | `Perfil.cshtml` — tab Historial: filtros | Agregar form con inputs Desde/Hasta y botones Filtrar/Limpiar | ⏳ Pendiente |
| 5.2 | Frontend | `Perfil.cshtml` — tab Historial: resumen | Agregar tabla/tarjetas de resumen por tipo de evento (visible solo si hay eventos) | ⏳ Pendiente |
| 5.3 | Frontend | `Perfil.cshtml` — tab Historial: columna Días | Agregar `<th>Días</th>` y `<td>@ev.DiasSolicitados</td>` entre Período y Autorizado por | ⏳ Pendiente |
| 5.4 | Frontend | `Perfil.cshtml` — tab Datos: vacaciones | Cambiar label "Días de vacaciones previos" a "Vacaciones disponibles" y mostrar `VacacionesDisponibles` | ⏳ Pendiente |
| — | Build | Build Fase 5 (Final) | Verificar compilación limpia | ⏳ Pendiente |
| 6.1 | Tests | `test_vacaciones_historial.py` | Crear suite con casos TC-VAC-01 a TC-VAC-10 | ⏳ Pendiente |
| 7.1 | Verificación | Levantar aplicación | `dotnet run --project GestionPersonal.Web --urls "http://localhost:5002"` | ⏳ Pendiente |
| 7.2 | Verificación | Ejecutar suite de pruebas | `pytest Tests/test_vacaciones_historial.py -v --headed --slowmo 800` | ⏳ Pendiente |

---

## Detalle de Cambios por Fase

### Fase 1 — DTOs y ViewModel

#### 1.1 Nuevo archivo: `ResumenEventoDto.cs`
**Ruta:** `GestionPersonal.Models/DTOs/EventoLaboral/ResumenEventoDto.cs`

```csharp
public class ResumenEventoDto
{
    public string TipoEvento { get; init; } = null!;
    public int TotalDias { get; init; }
}
```

#### 1.2 `PerfilEmpleadoViewModel.cs`
Agregar cuatro propiedades nuevas:

```csharp
public IReadOnlyList<ResumenEventoDto> ResumenEventos { get; init; } = [];
public decimal? VacacionesDisponibles { get; init; }
public string? FiltroDesde { get; init; }
public string? FiltroHasta { get; init; }
```

---

### Fase 2 — Repository

#### 2.1 `IEventoLaboralRepository.cs`
Agregar firma:
```csharp
Task<IReadOnlyList<EventoLaboral>> ObtenerPorEmpleadoConFiltroAsync(
    int empleadoId, DateOnly? desde, DateOnly? hasta, CancellationToken ct = default);
```

#### 2.2 `EventoLaboralRepository.cs`
Implementar filtrando con EF Core:
```csharp
// WHERE EmpleadoId = @id
//   AND (@desde IS NULL OR FechaInicio >= @desde)
//   AND (@hasta IS NULL OR FechaInicio <= @hasta)
```

---

### Fase 3 — Service

#### 3.1 `IEventoLaboralService.cs`
Agregar firma:
```csharp
Task<IReadOnlyList<EventoLaboralDto>> ObtenerPorEmpleadoConFiltroAsync(
    int empleadoId, DateOnly? desde, DateOnly? hasta, CancellationToken ct = default);
```

#### 3.2 `EventoLaboralService.cs` — método nuevo
Implementar `ObtenerPorEmpleadoConFiltroAsync`:
- Llama al repository con filtros
- Aplica `MapToDto` a cada resultado
- Devuelve la lista (el resumen se calcula en el controller)

#### 3.3 `EventoLaboralService.cs` — `ObtenerSaldoVacacionesAsync` (corrección)
**Lógica actual (incorrecta):**
```csharp
var diasAntiguedad = (hoy - FechaIngreso).Days / 365.0;
var acumulados = (int)(diasAntiguedad * 15) + (int)empleado.DiasVacacionesPrevios;
```

**Nueva lógica correcta:**
```csharp
if (empleado.FechaInicioContrato is null) return null; // sin contrato directo
var meses = ((hoy.Year - inicio.Year) * 12) + hoy.Month - inicio.Month;
if (hoy.Day < inicio.Day) meses--;                    // ajuste de día
var causadas = meses * 1.25m;

var disfrutadas = vacaciones
    .Where(e => e.Estado != EstadoEvento.Anulado && e.FechaInicio >= inicio)
    .Sum(e => e.FechaFin.DayNumber - e.FechaInicio.DayNumber + 1);

var disponibles = Math.Max(0m, causadas - disfrutadas);
```

> ⚠️ Este cambio afecta `ObtenerSaldoVacacionesAsync` que puede usarse en otros lugares. Verificar usages antes de modificar.

---

### Fase 4 — Controller

#### 4.1 Firma de `Perfil`
```csharp
public async Task<IActionResult> Perfil(int id, string tab = "datos",
    DateOnly? desde = null, DateOnly? hasta = null)
```

#### 4.2 Cuerpo de `Perfil`
Reemplazar la línea:
```csharp
var eventos = await ObtenerEventosAsync(id);
```
Por:
```csharp
var eventos = await _eventoLaboralService.ObtenerPorEmpleadoConFiltroAsync(id, desde, hasta);

var resumen = eventos
    .Where(ev => ev.Estado != "Anulado")
    .GroupBy(ev => ev.TipoEvento)
    .Select(g => new ResumenEventoDto { TipoEvento = g.Key, TotalDias = g.Sum(e => e.DiasSolicitados) })
    .OrderByDescending(r => r.TotalDias)
    .ToList();

decimal? vacacionesDisponibles = null;
if (DateOnly.TryParseExact(empleado.FechaInicioContrato, "dd/MM/yyyy",
    CultureInfo.InvariantCulture, DateTimeStyles.None, out var inicioContrato))
{
    var hoy = DateOnly.FromDateTime(DateTime.Today);
    var meses = ((hoy.Year - inicioContrato.Year) * 12) + hoy.Month - inicioContrato.Month;
    if (hoy.Day < inicioContrato.Day) meses--;
    var causadas = meses * 1.25m;
    var disfrutadas = eventos
        .Where(ev => ev.TipoEvento == "Vacaciones" && ev.Estado != "Anulado"
            && DateOnly.TryParseExact(ev.FechaInicio, "dd/MM/yyyy",
               CultureInfo.InvariantCulture, DateTimeStyles.None, out var fi)
            && fi >= inicioContrato)
        .Sum(ev => ev.DiasSolicitados);
    vacacionesDisponibles = Math.Max(0m, causadas - disfrutadas);
}
```

Actualizar el ViewModel:
```csharp
var vm = new PerfilEmpleadoViewModel
{
    ...
    Eventos               = eventos,
    ResumenEventos        = resumen,
    VacacionesDisponibles = vacacionesDisponibles,
    FiltroDesde           = desde?.ToString("yyyy-MM-dd"),
    FiltroHasta           = hasta?.ToString("yyyy-MM-dd"),
    ...
};
```

---

### Fase 5 — Frontend (`Perfil.cshtml`)

#### 5.1 Form de filtros (tab Historial)
Agregar **encima** del `<h2>Eventos laborales</h2>` actual:
```html
<form method="get" asp-action="Perfil" asp-route-id="@e.Id"
      asp-route-tab="historial" class="ev-filtros">
  <input type="hidden" name="tab" value="historial" />
  <label>Desde <input type="date" name="desde" value="@Model.FiltroDesde" /></label>
  <label>Hasta <input type="date" name="hasta" value="@Model.FiltroHasta" /></label>
  <button type="submit" class="btn btn-sm btn-primary">Filtrar</button>
  <a asp-action="Perfil" asp-route-id="@e.Id" asp-route-tab="historial"
     class="btn btn-sm btn-ghost">Limpiar</a>
</form>
```

#### 5.2 Sección resumen por tipo (tab Historial)
Agregar **debajo de los filtros**, antes de la tabla, visible solo si hay eventos:
```html
@if (Model.ResumenEventos.Any())
{
  <div class="ev-resumen">
    <table class="table table-sm">
      <thead><tr><th>Tipo de evento</th><th>Total días</th></tr></thead>
      <tbody>
        @foreach (var r in Model.ResumenEventos)
        {
          <tr><td>@r.TipoEvento</td><td>@r.TotalDias</td></tr>
        }
      </tbody>
    </table>
  </div>
}
```

#### 5.3 Columna Días en la tabla
- `<thead>`: agregar `<th>Días</th>` entre `<th>Período</th>` y `<th>Autorizado por</th>`
- `<tbody>` (fila de eventos): agregar `<td>@ev.DiasSolicitados</td>` en la misma posición

#### 5.4 Tab Datos — Vacaciones disponibles
Reemplazar el `dl-item` actual:
```html
<!-- ANTES -->
<div class="dl-item"><p class="dl-label">Días de vacaciones previos</p><p class="dl-value">@e.DiasVacacionesPrevios</p></div>

<!-- DESPUÉS -->
<div class="dl-item">
  <p class="dl-label">Vacaciones disponibles</p>
  <p class="dl-value">
    @(Model.VacacionesDisponibles.HasValue
        ? $"{Model.VacacionesDisponibles:F1} días"
        : "—")
  </p>
</div>
```

---

## Casos de Prueba Playwright

**Archivo:** `Tests/test_vacaciones_historial.py`
**Usuario de prueba recomendado:** `carlos.rodriguez@yopmail.com` / `Usuario1` (Jefe — puede ver todos los perfiles)
**Empleado objetivo:** Usar el empleado que tenga `FechaInicioContrato` configurada y eventos de Vacaciones registrados.

> Verificar antes de ejecutar qué empleados del seeding cumplen ambas condiciones.

| ID | Nombre | Descripción | Condición de éxito |
|---|---|---|---|
| TC-VAC-01 | Columna Días visible | Navegar al tab Historial de un empleado con eventos | La columna `<th>Días</th>` existe en la tabla |
| TC-VAC-02 | Valor de Días correcto | Verificar un evento con fechas conocidas (ej: 14 días) | El valor en la celda coincide con `FechaFin - FechaInicio + 1` |
| TC-VAC-03 | Filtros visibles | Tab Historial cargado | Los inputs `name="desde"` y `name="hasta"` están presentes |
| TC-VAC-04 | Filtro por rango filtra eventos | Ingresar rango que incluye solo algunos eventos y filtrar | Solo aparecen eventos cuya FechaInicio está dentro del rango |
| TC-VAC-05 | Filtro sin resultados | Ingresar rango futuro sin eventos y filtrar | Aparece el estado vacío ("Sin eventos registrados") |
| TC-VAC-06 | Botón Limpiar restaura tabla | Después de filtrar, hacer click en "Limpiar" | La tabla muestra todos los eventos originales |
| TC-VAC-07 | Resumen visible con tipos | Tab Historial con eventos registrados | La sección resumen es visible con al menos una fila de tipo |
| TC-VAC-08 | Resumen cambia al filtrar | Aplicar filtro que excluye algunos eventos | Los totales del resumen reflejan solo el período filtrado |
| TC-VAC-09 | Vacaciones disponibles en tab Datos | Empleado con `FechaInicioContrato` y eventos de vacaciones | El campo muestra un valor numérico con formato `X.X días` |
| TC-VAC-10 | Vacaciones disponibles vacío | Empleado sin `FechaInicioContrato` | El campo muestra `—` |

---

## Comandos de Ejecución

### Levantar la aplicación (terminal dedicada)

```powershell
cd "c:\Users\alejandro.ortiz\Documents\helpharma\Desarrollos\lissy\IA\LissyIAHelpharma\empleados v2\Proyecto MVC"
dotnet run --project GestionPersonal.Web --urls "http://localhost:5002"
```

Esperar: `Now listening on: http://localhost:5002`

### Ejecutar suite de vacaciones e historial

```powershell
cd "c:\Users\alejandro.ortiz\Documents\helpharma\Desarrollos\lissy\IA\LissyIAHelpharma\empleados v2"
Set-ExecutionPolicy -Scope Process -ExecutionPolicy RemoteSigned
.venv\Scripts\Activate.ps1

$fecha = Get-Date -Format "yyyy-MM-dd_HH-mm-ss"
$informe = "Tests\resultados\vacaciones-historial-$fecha.txt"
New-Item -ItemType Directory -Force -Path "Tests\resultados" | Out-Null

.\.venv\Scripts\python.exe -m pytest Tests/test_vacaciones_historial.py `
  -v --headed --slowmo 800 -s `
  2>&1 | Tee-Object -FilePath $informe

Write-Host "`nInforme guardado en: $informe"
```

### Solo ejecutar una prueba específica

```powershell
.\.venv\Scripts\python.exe -m pytest Tests/test_vacaciones_historial.py::test_columna_dias_visible -v --headed --slowmo 800
```

### Restablecer BD antes de ejecutar (recomendado)

```powershell
sqlcmd -S "(localdb)\MSSQLLocalDB" -d GestionPersonal -i "Documentos\BD\Seeding_Completo.sql"
```

---

## Notas de Implementación

1. **`ObtenerEventosAsync` en `EmpleadoController`:** Este método helper privado actualmente llama a `ObtenerPorEmpleadoAsync`. Al migrar a `ObtenerPorEmpleadoConFiltroAsync`, el método helper puede eliminarse o refactorizarse inline en la acción `Perfil`.

2. **`ObtenerSaldoVacacionesAsync` en service:** Verificar si este método es invocado desde otros lugares del sistema además del plan. Si se usa en algún endpoint de saldo, la corrección de lógica puede cambiar su comportamiento. Confirmar antes de modificar.

3. **Filtro vía GET:** Los filtros se envían como query params (`?desde=2026-01-01&hasta=2026-04-30`). Esto permite compartir URLs con filtros aplicados, lo cual es un beneficio adicional para RRHH.

4. **`DiasSolicitados` para eventos sin `FechaFin`:** En la entidad actual, `FechaFin` es `DateOnly` (no nullable), por lo que siempre tiene valor. No es necesario manejar el caso nulo en este ciclo.
