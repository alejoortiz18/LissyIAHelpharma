using GestionPersonal.Application.Interfaces;
using GestionPersonal.Domain.Interfaces;
using GestionPersonal.Models.DTOs.Dashboard;
using GestionPersonal.Models.Enums;
using GestionPersonal.Models.Models;

namespace GestionPersonal.Application.Services;

public class DashboardService : IDashboardService
{
    private readonly IEmpleadoRepository      _empleadoRepo;
    private readonly IEventoLaboralRepository _eventoRepo;
    private readonly IHoraExtraRepository     _horaExtraRepo;

    public DashboardService(
        IEmpleadoRepository      empleadoRepo,
        IEventoLaboralRepository eventoRepo,
        IHoraExtraRepository     horaExtraRepo)
    {
        _empleadoRepo  = empleadoRepo;
        _eventoRepo    = eventoRepo;
        _horaExtraRepo = horaExtraRepo;
    }

    // ── Público ──────────────────────────────────────────────────────────────────

    public async Task<ResultadoOperacion<DashboardKpiDto>> ObtenerKpisAsync(
        int? filtrarPorJefeId, CancellationToken ct = default)
    {
        var hoy  = DateOnly.FromDateTime(DateTime.Today);
        var anio = DateTime.Today.Year;
        var mes  = DateTime.Today.Month;

        var empleadoIds = await ResolverAlcanceAsync(filtrarPorJefeId, ct);

        // Empleados dentro del alcance
        var todosEmpleados = await _empleadoRepo.ObtenerTodosAsync(ct);
        var empleados = empleadoIds is null
            ? todosEmpleados
            : todosEmpleados.Where(e => empleadoIds.Contains(e.Id)).ToList();

        // Novedades hoy
        var novedadesHoy = empleadoIds is null
            ? await _eventoRepo.ObtenerActivosHoyGlobalAsync(hoy, ct)
            : (await _eventoRepo.ObtenerActivosHoyGlobalAsync(hoy, ct))
                .Where(e => empleadoIds.Contains(e.EmpleadoId)).ToList();

        // Horas extras
        var horasAprobadas  = await _horaExtraRepo.ContarAprobadasEsteMesAsync(empleadoIds, anio, mes, ct);
        var totalHoras      = await _horaExtraRepo.SumarHorasAprobadasEsteMesAsync(empleadoIds, anio, mes, ct);
        var horasPendientes = (await _horaExtraRepo.ObtenerPendientesAsync(empleadoIds, ct)).Count;

        // Solicitudes pendientes de aprobación
        var solicitudesPendientes = await _eventoRepo.ContarPendientesAsync(empleadoIds, ct);

        // Empleados con novedad activa hoy → "No disponibles"
        var noDisponiblesIds = novedadesHoy.Select(n => n.EmpleadoId).ToHashSet();

        var kpi = new DashboardKpiDto
        {
            TotalEmpleados              = empleados.Count,
            EmpleadosActivos            = empleados.Count(e => e.Estado == EstadoEmpleado.Activo && !noDisponiblesIds.Contains(e.Id)),
            EmpleadosInactivos          = empleados.Count(e => e.Estado == EstadoEmpleado.Inactivo),
            EmpleadosDirectos           = empleados.Count(e => e.Estado == EstadoEmpleado.Activo && !noDisponiblesIds.Contains(e.Id) && e.TipoVinculacion == TipoVinculacion.Directo),
            EmpleadosTemporales         = empleados.Count(e => e.Estado == EstadoEmpleado.Activo && !noDisponiblesIds.Contains(e.Id) && e.TipoVinculacion == TipoVinculacion.Temporal),
            EmpleadosConNovedad         = novedadesHoy.Select(n => n.EmpleadoId).Distinct().Count(),
            EnVacaciones                = novedadesHoy.Count(n => EsTipo(n.TipoEvento, TipoEvento.Vacaciones)),
            ConIncapacidad              = novedadesHoy.Count(n => EsTipo(n.TipoEvento, TipoEvento.Incapacidad)),
            ConPermiso                  = novedadesHoy.Count(n => EsTipo(n.TipoEvento, TipoEvento.Permiso)),
            HorasExtrasPendientes       = horasPendientes,
            HorasExtrasAprobadasEsteMes = horasAprobadas,
            TotalHorasAprobadasEsteMes  = totalHoras,
            SolicitudesPendientes       = solicitudesPendientes,
        };

        return ResultadoOperacion<DashboardKpiDto>.Ok(kpi);
    }

    public async Task<IReadOnlyList<NovedadHoyDto>> ObtenerNovedadesHoyAsync(
        int? filtrarPorJefeId, CancellationToken ct = default)
    {
        var hoy         = DateOnly.FromDateTime(DateTime.Today);
        var empleadoIds = await ResolverAlcanceAsync(filtrarPorJefeId, ct);

        var lista = await _eventoRepo.ObtenerActivosHoyGlobalAsync(hoy, ct);

        if (empleadoIds is not null)
            lista = lista.Where(e => empleadoIds.Contains(e.EmpleadoId)).ToList();

        return lista.Select(e => new NovedadHoyDto
        {
            EmpleadoId     = e.EmpleadoId,
            EmpleadoNombre = e.Empleado?.NombreCompleto ?? string.Empty,
            SedeNombre     = e.Empleado?.Sede?.Nombre   ?? string.Empty,
            TipoNovedad    = e.TipoEvento,
            Periodo        = $"{e.FechaInicio:dd/MMM} – {e.FechaFin:dd/MMM}",
            Estado         = e.Estado.ToString()
        }).ToList();
    }

    public async Task<IReadOnlyList<HoraExtraPendienteDto>> ObtenerHorasExtrasPendientesAsync(
        int? filtrarPorJefeId, CancellationToken ct = default)
    {
        var empleadoIds = await ResolverAlcanceAsync(filtrarPorJefeId, ct);
        var lista       = await _horaExtraRepo.ObtenerPendientesAsync(empleadoIds, ct);

        return lista.Select(h => new HoraExtraPendienteDto
        {
            Id             = h.Id,
            EmpleadoId     = h.EmpleadoId,
            EmpleadoNombre = h.Empleado?.NombreCompleto ?? string.Empty,
            FechaTrabajada = h.FechaTrabajada.ToString("dd/MM/yyyy"),
            CantidadHoras  = h.CantidadHoras,
            Motivo         = h.Motivo
        }).ToList();
    }

    // ── Privados ─────────────────────────────────────────────────────────────────

    /// <summary>
    /// Devuelve el conjunto de empleadoIds visible para el caller.
    /// Null significa "todos" (alcance global del Analista).
    /// </summary>
    private async Task<IReadOnlySet<int>?> ResolverAlcanceAsync(int? jefeId, CancellationToken ct)
    {
        if (jefeId is null) return null;  // Analista: sin filtro

        var todos = await _empleadoRepo.ObtenerTodosAsync(ct);

        // Índice jefe → lista de subordinados directos
        var porJefe = todos
            .Where(e => e.JefeInmediatoId.HasValue)
            .GroupBy(e => e.JefeInmediatoId!.Value)
            .ToDictionary(g => g.Key, g => g.Select(e => e.Id).ToList());

        // BFS para obtener todos los descendientes
        var resultado = new HashSet<int> { jefeId.Value };  // el jefe también se ve a sí mismo
        var cola      = new Queue<int>();
        cola.Enqueue(jefeId.Value);

        while (cola.Count > 0)
        {
            var actual = cola.Dequeue();
            if (!porJefe.TryGetValue(actual, out var hijos)) continue;
            foreach (var hijo in hijos)
            {
                if (resultado.Add(hijo))
                    cola.Enqueue(hijo);
            }
        }

        return resultado;
    }

    private static bool EsTipo(string tipoCodigo, TipoEvento tipoReferencia) =>
        tipoCodigo.Equals(tipoReferencia.ToString(), StringComparison.OrdinalIgnoreCase);
}
