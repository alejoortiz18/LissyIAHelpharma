using GestionPersonal.Models.DTOs.Turno;
using GestionPersonal.Models.DTOs.Empleado;

namespace GestionPersonal.Web.ViewModels.Turno;

public class AsignarTurnoViewModel
{
    public AsignarTurnoDto Dto { get; set; } = new();
    public IReadOnlyList<PlantillaTurnoDto> Plantillas { get; init; } = [];
    /// <summary>Si se pre-carga para un empleado específico desde su perfil.</summary>
    public EmpleadoDto? Empleado { get; init; }
}
