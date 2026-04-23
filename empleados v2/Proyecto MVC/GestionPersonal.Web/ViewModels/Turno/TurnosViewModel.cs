using GestionPersonal.Models.DTOs.Turno;

namespace GestionPersonal.Web.ViewModels.Turno;

public class TurnosViewModel
{
    public IReadOnlyList<PlantillaTurnoDto> Plantillas { get; init; } = [];
    public IReadOnlyList<AsignacionTurnoDto> Asignaciones { get; init; } = [];
}
