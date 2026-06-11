using GestionPersonal.Models.DTOs.EventoLaboral;
using GestionPersonal.Models.Entities.GestionPersonalEntities;

namespace GestionPersonal.Web.ViewModels.Solicitud;

public class SolicitudesViewModel
{
    public IReadOnlyList<EventoLaboralDto> Solicitudes { get; init; } = [];
    public IReadOnlyList<TipoSolicitud> TiposSolicitudActivos { get; init; } = [];

    // Filtros
    public string? Tipo   { get; init; }
    public string? Estado { get; init; }

    // Paginación
    public int Pagina        { get; init; } = 1;
    public int TotalPaginas  { get; init; }
    public int TotalRegistros { get; init; }
}
