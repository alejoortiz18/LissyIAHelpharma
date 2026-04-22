using GestionPersonal.Application.Interfaces;
using GestionPersonal.Domain.Interfaces;
using GestionPersonal.Models.DTOs.Dashboard;
using GestionPersonal.Models.Enums;
using GestionPersonal.Models.Models;

namespace GestionPersonal.Application.Services;

public class DashboardService : IDashboardService
{
    private readonly IEmpleadoRepository _empleadoRepo;
    private readonly IEventoLaboralRepository _eventoRepo;
    private readonly IHoraExtraRepository _horaExtraRepo;

    public DashboardService(
        IEmpleadoRepository empleadoRepo,
        IEventoLaboralRepository eventoRepo,
        IHoraExtraRepository horaExtraRepo)
    {
        _empleadoRepo  = empleadoRepo;
        _eventoRepo    = eventoRepo;
        _horaExtraRepo = horaExtraRepo;
    }

    public async Task<ResultadoOperacion<DashboardKpiDto>> ObtenerKpisAsync(int sedeId, CancellationToken ct = default)
    {
        var hoy   = DateOnly.FromDateTime(DateTime.Today);
        var anio  = DateTime.Today.Year;
        var mes   = DateTime.Today.Month;

        var empleados       = await _empleadoRepo.ObtenerPorSedeAsync(sedeId, ct);
        var novedadesHoy    = await _eventoRepo.ObtenerActivosHoyPorSedeAsync(sedeId, hoy, ct);
        var horasPendientes = await _horaExtraRepo.ContarPendientesPorSedeAsync(sedeId, ct);
        var horasAprobadas  = await _horaExtraRepo.ContarAprobadasEsteMesPorSedeAsync(sedeId, anio, mes, ct);
        var totalHoras      = await _horaExtraRepo.SumarHorasAprobadasEsteMesPorSedeAsync(sedeId, anio, mes, ct);

        var activos    = empleados.Count(e => e.Estado == EstadoEmpleado.Activo);
        var inactivos  = empleados.Count(e => e.Estado == EstadoEmpleado.Inactivo);
        var directos   = empleados.Count(e => e.TipoVinculacion == TipoVinculacion.Directo);
        var temporales = empleados.Count(e => e.TipoVinculacion == TipoVinculacion.Temporal);

        var kpi = new DashboardKpiDto
        {
            TotalEmpleados              = empleados.Count,
            EmpleadosActivos            = activos,
            EmpleadosInactivos          = inactivos,
            EmpleadosDirectos           = directos,
            EmpleadosTemporales         = temporales,
            EmpleadosConNovedad         = novedadesHoy.Select(n => n.EmpleadoId).Distinct().Count(),
            EnVacaciones                = novedadesHoy.Count(n => n.TipoEvento == TipoEvento.Vacaciones),
            ConIncapacidad              = novedadesHoy.Count(n => n.TipoEvento == TipoEvento.Incapacidad),
            ConPermiso                  = novedadesHoy.Count(n => n.TipoEvento == TipoEvento.Permiso),
            HorasExtrasPendientes       = horasPendientes,
            HorasExtrasAprobadasEsteMes = horasAprobadas,
            TotalHorasAprobadasEsteMes  = totalHoras
        };

        return ResultadoOperacion<DashboardKpiDto>.Ok(kpi);
    }

    public async Task<IReadOnlyList<NovedadHoyDto>> ObtenerNovedadesHoyAsync(int sedeId, CancellationToken ct = default)
    {
        var hoy    = DateOnly.FromDateTime(DateTime.Today);
        var lista  = await _eventoRepo.ObtenerActivosHoyPorSedeAsync(sedeId, hoy, ct);

        return lista.Select(e => new NovedadHoyDto
        {
            EmpleadoId    = e.EmpleadoId,
            EmpleadoNombre = e.Empleado?.NombreCompleto   ?? string.Empty,
            SedeNombre    = e.Empleado?.Sede?.Nombre      ?? string.Empty,
            TipoNovedad   = e.TipoEvento.ToString(),
            Periodo       = $"{e.FechaInicio:dd/MMM} – {e.FechaFin:dd/MMM}",
            Estado        = e.Estado.ToString()
        }).ToList();
    }

    public async Task<IReadOnlyList<HoraExtraPendienteDto>> ObtenerHorasExtrasPendientesAsync(int sedeId, CancellationToken ct = default)
    {
        var lista = await _horaExtraRepo.ObtenerPendientesPorSedeAsync(sedeId, ct);

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
}
