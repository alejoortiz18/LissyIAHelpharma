namespace GestionPersonal.Models.Entities.GestionPersonalEntities;

public class PermisoPlataforma
{
    public int Id { get; set; }
    public string Codigo { get; set; } = null!;
    public string Modulo { get; set; } = null!;
    public string Nombre { get; set; } = null!;
    public string? Descripcion { get; set; }
    public int Orden { get; set; }

    public virtual ICollection<RolSistemaPermiso> RolesPermisos { get; set; } = new List<RolSistemaPermiso>();
}
