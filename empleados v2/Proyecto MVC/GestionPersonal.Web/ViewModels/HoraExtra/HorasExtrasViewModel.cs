using GestionPersonal.Models.DTOs.Empleado;
using GestionPersonal.Models.DTOs.HoraExtra;

namespace GestionPersonal.Web.ViewModels.HoraExtra;

public class HorasExtrasViewModel
{
    public IReadOnlyList<HoraExtraDto> HorasExtras { get; init; } = [];

    // Stats
    public int Pendientes { get; init; }
    public int AprobadasEsteMes { get; init; }
    public decimal TotalHorasAprobadas { get; init; }

    // Filtros
    public string? Buscar { get; init; }
    public string? Fecha { get; init; }
    public string? Estado { get; init; }

    // Paginación
    public int Pagina { get; init; } = 1;
    public int TotalPaginas { get; init; }
    public int TotalRegistros { get; init; }
}
