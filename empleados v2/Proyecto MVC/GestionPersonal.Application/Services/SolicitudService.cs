using GestionPersonal.Application.Interfaces;
using GestionPersonal.Models.DTOs.EventoLaboral;
using GestionPersonal.Models.Enums;
using GestionPersonal.Models.Models;

namespace GestionPersonal.Application.Services;

public class SolicitudService : ISolicitudService
{
    private readonly IEventoLaboralService _eventoService;

    public SolicitudService(IEventoLaboralService eventoService)
    {
        _eventoService = eventoService;
    }

    public async Task<IReadOnlyList<EventoLaboralDto>> ObtenerPropiosAsync(
        int empleadoId, CancellationToken ct = default)
    {
        return await _eventoService.ObtenerPorEmpleadoAsync(empleadoId, ct);
    }

    public async Task<ResultadoOperacion> CrearSolicitudAsync(
        CrearEventoLaboralDto dto, int creadoPorUsuarioId, CancellationToken ct = default)
    {
        // El EmpleadoId viene del claim de sesión (no del body del request).
        // Se fuerza el estado inicial y el campo AutorizadoPor.
        dto.EstadoInicial = EstadoEvento.Pendiente;
        dto.AutorizadoPor = "Pendiente de aprobación";

        return await _eventoService.CrearAsync(dto, creadoPorUsuarioId, ct);
    }
}
