namespace GestionPersonal.Models.Entities.GestionPersonalEntities;

public class PlantillaTurno
{
    public int Id { get; set; }
    public string Nombre { get; set; } = null!;
    public string Estado { get; set; } = null!;
    public DateTime FechaCreacion { get; set; }
    public DateTime? FechaModificacion { get; set; }

    /// <summary>Empleado (jefe) que creó la plantilla. Determina la visibilidad y asignación jerárquica.</summary>
    public int? CreadoPorId { get; set; }

    public virtual Empleado? CreadoPor { get; set; }
    public virtual ICollection<PlantillaTurnoDetalle> PlantillaTurnoDetalles { get; set; } = new List<PlantillaTurnoDetalle>();
    public virtual ICollection<AsignacionTurno> AsignacionesTurno { get; set; } = new List<AsignacionTurno>();
}
