using GestionPersonal.Models.DTOs.Empleado;
using GestionPersonal.Models.DTOs.EventoLaboral;
using GestionPersonal.Models.DTOs.HoraExtra;
using GestionPersonal.Models.DTOs.Turno;

namespace GestionPersonal.Web.ViewModels.Empleado;

public class PerfilEmpleadoViewModel
{
    public EmpleadoDto Empleado { get; init; } = null!;
    public IReadOnlyList<EventoLaboralDto> Eventos { get; init; } = [];
    public IReadOnlyList<HoraExtraDto> HorasExtras { get; init; } = [];
    public PlantillaTurnoDto? TurnoActual { get; init; }
    public IReadOnlyList<PlantillaTurnoDto> Plantillas { get; init; } = [];
    public IReadOnlyList<AsignacionTurnoDto> HistorialTurnos { get; init; } = [];

    /// <summary>Tab activo: "datos" | "historial" | "horario"</summary>
    public string Tab { get; init; } = "datos";
}
