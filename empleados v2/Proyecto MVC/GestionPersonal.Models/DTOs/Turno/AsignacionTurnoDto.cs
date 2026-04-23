namespace GestionPersonal.Models.DTOs.Turno;

public class AsignacionTurnoDto
{
    public int Id { get; init; }
    public int EmpleadoId { get; init; }
    public string EmpleadoNombre { get; init; } = null!;
    public string SedeNombre { get; init; } = null!;
    public int PlantillaTurnoId { get; init; }
    public string PlantillaNombre { get; init; } = null!;
    public string FechaVigencia { get; init; } = null!;
    public string AsignadoPor { get; init; } = null!;
    public int ProgramadoPorUsuarioId { get; init; }
}
