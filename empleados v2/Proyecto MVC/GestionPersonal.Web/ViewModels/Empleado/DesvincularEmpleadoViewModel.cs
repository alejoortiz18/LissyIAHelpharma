using GestionPersonal.Models.DTOs.Empleado;

namespace GestionPersonal.Web.ViewModels.Empleado;

public class DesvincularEmpleadoViewModel
{
    public DesvincularEmpleadoDto Dto { get; set; } = new();
    public EmpleadoDto Empleado { get; init; } = null!;
}
