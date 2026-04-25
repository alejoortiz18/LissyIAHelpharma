using GestionPersonal.Models.DTOs.EventoLaboral;
using GestionPersonal.Models.Enums;
using GestionPersonal.Models.Models;

namespace GestionPersonal.Application.Interfaces;

public interface IEventoLaboralService
{
    Task<IReadOnlyList<EventoLaboralDto>> ObtenerPorSedeAsync(int sedeId, CancellationToken ct = default);

    /// <summary>Todos los eventos de todas las sedes. Solo para el Analista de Servicios Farmacéuticos.</summary>
    Task<IReadOnlyList<EventoLaboralDto>> ObtenerTodosAsync(CancellationToken ct = default);
    Task<IReadOnlyList<EventoLaboralDto>> ObtenerPorEmpleadoAsync(int empleadoId, CancellationToken ct = default);

    /// <summary>Eventos del empleado filtrados opcionalmente por rango de FechaInicio.</summary>
    Task<IReadOnlyList<EventoLaboralDto>> ObtenerPorEmpleadoConFiltroAsync(
        int empleadoId, DateOnly? desde, DateOnly? hasta, CancellationToken ct = default);

    Task<ResultadoOperacion> CrearAsync(CrearEventoLaboralDto dto, int creadoPorUsuarioId, CancellationToken ct = default);
    Task<ResultadoOperacion> AnularAsync(int eventoId, string motivoAnulacion, int anuladoPorUsuarioId, CancellationToken ct = default);

    /// <summary>Obtiene todos los IDs de empleados que forman el árbol descendente de un jefe (BFS recursivo sobre JefeInmediatoId).</summary>
    Task<IReadOnlySet<int>> ObtenerDescendientesAsync(int jefeId, CancellationToken ct = default);

    /// <summary>
    /// Aprueba, rechaza o reversa una solicitud. El nombre del responsable se guarda en AutorizadoPor.
    /// La observación es obligatoria al rechazar o reversar; se persiste en MotivoAnulacion.
    /// </summary>
    Task<ResultadoOperacion> CambiarEstadoAsync(
        int eventoId,
        EstadoEvento nuevoEstado,
        string nombreResponsable,
        string? observacion,
        CancellationToken ct = default);

    Task<SaldoVacacionesDto?> ObtenerSaldoVacacionesAsync(int empleadoId, CancellationToken ct = default);
}
