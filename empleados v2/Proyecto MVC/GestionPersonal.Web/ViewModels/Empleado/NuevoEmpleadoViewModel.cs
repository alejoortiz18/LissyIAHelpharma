using GestionPersonal.Models.DTOs.Empleado;
using GestionPersonal.Models.Entities.GestionPersonalEntities;

namespace GestionPersonal.Web.ViewModels.Empleado;

public class NuevoEmpleadoViewModel
{
    public CrearEmpleadoDto Dto { get; set; } = new();

    // Catálogos para selects
    public IReadOnlyList<Sede> Sedes { get; init; } = [];
    public IReadOnlyList<Cargo> Cargos { get; init; } = [];
    public IReadOnlyList<EmpresaTemporal> EmpresasTemporales { get; init; } = [];
    public IReadOnlyList<EmpleadoListaDto> Jefes { get; init; } = [];
}
