namespace GestionPersonal.Models.Entities.GestionPersonalEntities;

public class AsignacionTurno
{
    public int Id { get; set; }
    public int EmpleadoId { get; set; }
    public int PlantillaTurnoId { get; set; }
    public DateOnly FechaVigencia { get; set; }
    public int ProgramadoPor { get; set; }
    public DateTime FechaCreacion { get; set; }

    public virtual Empleado Empleado { get; set; } = null!;
    public virtual PlantillaTurno PlantillaTurno { get; set; } = null!;
    public virtual Usuario ProgramadoPorNavigation { get; set; } = null!;
}
