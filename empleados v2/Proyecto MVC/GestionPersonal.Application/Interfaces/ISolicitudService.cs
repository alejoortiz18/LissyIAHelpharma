using GestionPersonal.Models.DTOs.EventoLaboral;
using GestionPersonal.Models.Models;

namespace GestionPersonal.Application.Interfaces;

/// <summary>
/// Servicio de autogestión de solicitudes para Operario y Direccionador.
/// Solo opera sobre los eventos propios del empleado autenticado.
/// </summary>
public interface ISolicitudService
{
    /// <summary>Devuelve todas las solicitudes del empleado, sin exponer registros de otros.</summary>
    Task<IReadOnlyList<EventoLaboralDto>> ObtenerPropiosAsync(int empleadoId, CancellationToken ct = default);

    /// <summary>Registra una nueva solicitud. EmpleadoId y AutorizadoPor se resuelven en servicio.</summary>
    Task<ResultadoOperacion> CrearSolicitudAsync(CrearEventoLaboralDto dto, int creadoPorUsuarioId, CancellationToken ct = default);
}
