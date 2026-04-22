using GestionPersonal.Models.DTOs.Empleado;
using GestionPersonal.Models.Entities.GestionPersonalEntities;

namespace GestionPersonal.Web.ViewModels.Empleado;

public class EmpleadosViewModel
{
    public IReadOnlyList<EmpleadoListaDto> Empleados { get; init; } = [];
    public IReadOnlyList<Sede> Sedes { get; init; } = [];
    public IReadOnlyList<Cargo> Cargos { get; init; } = [];

    // Filtros activos
    public string? Buscar { get; init; }
    public int? SedeId { get; init; }
    public int? CargoId { get; init; }
    public string? Estado { get; init; }
    public string? TipoVinculacion { get; init; }

    // Paginación
    public int Pagina { get; init; } = 1;
    public int TotalPaginas { get; init; }
    public int TotalRegistros { get; init; }
    public int TamanioPagina { get; init; } = 15;
}
