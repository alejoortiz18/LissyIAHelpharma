using GestionPersonal.Models.DTOs.Empleado;
using GestionPersonal.Models.DTOs.HoraExtra;

namespace GestionPersonal.Web.ViewModels.HoraExtra;

public class CrearHoraExtraViewModel
{
    public CrearHoraExtraDto Dto { get; set; } = new();
    public IReadOnlyList<EmpleadoListaDto> Empleados { get; init; } = [];
}
