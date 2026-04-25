using GestionPersonal.Models.DTOs.EventoLaboral;

namespace GestionPersonal.Web.ViewModels.Solicitud;

public class SolicitudesViewModel
{
    public IReadOnlyList<EventoLaboralDto> Solicitudes { get; init; } = [];

    // Filtros
    public string? Tipo   { get; init; }
    public string? Estado { get; init; }

    // Paginación
    public int Pagina        { get; init; } = 1;
    public int TotalPaginas  { get; init; }
    public int TotalRegistros { get; init; }
}
