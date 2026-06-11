using GestionPersonal.Models.DTOs.Empleado;
using GestionPersonal.Models.DTOs.EventoLaboral;
using GestionPersonal.Models.Entities.GestionPersonalEntities;

namespace GestionPersonal.Web.ViewModels.EventoLaboral;

public class EventosViewModel
{
    public IReadOnlyList<EventoLaboralDto> Eventos { get; init; } = [];
    public IReadOnlyList<EmpleadoListaDto> Empleados { get; init; } = [];
    public IReadOnlyList<TipoSolicitud> TiposSolicitudActivos { get; init; } = [];
    public int? EmpleadoSesionId { get; init; }
    public string? EmpleadoSesionNombre { get; init; }
    public bool FijarEmpleadoSesion { get; init; }

    // Filtros
    public string? Buscar { get; init; }
    public string? Tipo { get; init; }
    public string? Estado { get; init; }
    public string? Desde { get; init; }
    public string? Hasta { get; init; }

    // Paginación
    public int Pagina { get; init; } = 1;
    public int TotalPaginas { get; init; }
    public int TotalRegistros { get; init; }
}
