namespace GestionPersonal.Models.Entities.GestionPersonalEntities;

public class RolSistema
{
    public int Id { get; set; }
    public string Codigo { get; set; } = null!;
    public string Nombre { get; set; } = null!;
    public string? Descripcion { get; set; }
    public bool EsRolSistema { get; set; }
    public string Estado { get; set; } = null!;
    public DateTime FechaCreacion { get; set; }
    public DateTime? FechaModificacion { get; set; }

    public virtual ICollection<RolSistemaPermiso> Permisos { get; set; } = new List<RolSistemaPermiso>();
}
