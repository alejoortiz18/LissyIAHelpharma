using GestionPersonal.Models.DTOs.Empleado;
using GestionPersonal.Models.DTOs.Turno;
using GestionPersonal.Models.Entities.GestionPersonalEntities;

namespace GestionPersonal.Web.ViewModels.Turno;

public class TurnosViewModel
{
    public IReadOnlyList<PlantillaTurnoDto> Plantillas { get; init; } = [];
    public IReadOnlyList<AsignacionTurnoRow> Asignaciones { get; init; } = [];
}

public class AsignacionTurnoRow
{
    public int EmpleadoId { get; init; }
    public string EmpleadoNombre { get; init; } = null!;
    public string SedeNombre { get; init; } = null!;
    public string PlantillaNombre { get; init; } = null!;
    public string FechaVigencia { get; init; } = null!;
    public string AsignadoPor { get; init; } = null!;
}
