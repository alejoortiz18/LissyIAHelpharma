namespace GestionPersonal.Models.Entities.GestionPersonalEntities;

public class HistorialDesvinculacion
{
    public int Id { get; set; }
    public int EmpleadoId { get; set; }
    public string MotivoRetiro { get; set; } = null!;
    public DateOnly FechaDesvinculacion { get; set; }
    public int RegistradoPor { get; set; }
    public DateTime FechaCreacion { get; set; }

    public virtual Empleado Empleado { get; set; } = null!;
    public virtual Usuario RegistradoPorNavigation { get; set; } = null!;
}
