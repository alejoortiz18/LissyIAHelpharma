using GestionPersonal.Models.DTOs.EventoLaboral;
using GestionPersonal.Models.Models;

namespace GestionPersonal.Application.Interfaces;

public interface IEventoLaboralService
{
    Task<IReadOnlyList<EventoLaboralDto>> ObtenerPorSedeAsync(int sedeId, CancellationToken ct = default);
    Task<IReadOnlyList<EventoLaboralDto>> ObtenerPorEmpleadoAsync(int empleadoId, CancellationToken ct = default);

    /// <summary>Eventos del empleado filtrados opcionalmente por rango de FechaInicio.</summary>
    Task<IReadOnlyList<EventoLaboralDto>> ObtenerPorEmpleadoConFiltroAsync(
        int empleadoId, DateOnly? desde, DateOnly? hasta, CancellationToken ct = default);

    Task<ResultadoOperacion> CrearAsync(CrearEventoLaboralDto dto, int creadoPorUsuarioId, CancellationToken ct = default);
    Task<ResultadoOperacion> AnularAsync(int eventoId, string motivoAnulacion, int anuladoPorUsuarioId, CancellationToken ct = default);
    Task<SaldoVacacionesDto?> ObtenerSaldoVacacionesAsync(int empleadoId, CancellationToken ct = default);
}
