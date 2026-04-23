using GestionPersonal.Models.DTOs.Empleado;
using GestionPersonal.Models.DTOs.EventoLaboral;

namespace GestionPersonal.Web.ViewModels.EventoLaboral;

public class EventosViewModel
{
    public IReadOnlyList<EventoLaboralDto> Eventos { get; init; } = [];
    public IReadOnlyList<EmpleadoListaDto> Empleados { get; init; } = [];

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
