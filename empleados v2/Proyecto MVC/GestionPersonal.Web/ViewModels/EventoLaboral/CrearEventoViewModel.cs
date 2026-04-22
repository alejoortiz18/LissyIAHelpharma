using GestionPersonal.Models.DTOs.Empleado;
using GestionPersonal.Models.DTOs.EventoLaboral;

namespace GestionPersonal.Web.ViewModels.EventoLaboral;

public class CrearEventoViewModel
{
    public CrearEventoLaboralDto Dto { get; set; } = new();
    public IReadOnlyList<EmpleadoListaDto> Empleados { get; init; } = [];
    /// <summary>Si viene de un perfil de empleado, para pre-seleccionar y volver.</summary>
    public int? EmpleadoPreSeleccionado { get; init; }
}
