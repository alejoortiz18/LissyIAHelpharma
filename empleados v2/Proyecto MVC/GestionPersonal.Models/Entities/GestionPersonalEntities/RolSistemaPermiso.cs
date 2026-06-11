namespace GestionPersonal.Models.Entities.GestionPersonalEntities;

public class RolSistemaPermiso
{
    public int RolSistemaId { get; set; }
    public int PermisoId { get; set; }

    public virtual RolSistema RolSistema { get; set; } = null!;
    public virtual PermisoPlataforma Permiso { get; set; } = null!;
}
