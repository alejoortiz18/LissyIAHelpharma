namespace GestionPersonal.Models.Entities.GestionPersonalEntities;

public class Sede
{
    public int Id { get; set; }
    public string Nombre { get; set; } = null!;
    public string Ciudad { get; set; } = null!;
    public string Direccion { get; set; } = null!;
    public string Estado { get; set; } = null!;
    public DateTime FechaCreacion { get; set; }
    public DateTime? FechaModificacion { get; set; }

    public virtual ICollection<Usuario> Usuarios { get; set; } = new List<Usuario>();
    public virtual ICollection<Empleado> Empleados { get; set; } = new List<Empleado>();
}
