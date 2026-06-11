using GestionPersonal.Models.Entities.GestionPersonalEntities;

namespace GestionPersonal.Web.ViewModels.Catalogos;

public class CatalogosViewModel
{
    public IReadOnlyList<Sede> Sedes { get; init; } = [];
    public IReadOnlyList<Cargo> Cargos { get; init; } = [];
    public IReadOnlyList<EmpresaTemporal> EmpresasTemporales { get; init; } = [];
    public IReadOnlyList<TipoSolicitud> TiposSolicitud { get; init; } = [];
    public IReadOnlyList<RolSistema> RolesSistema { get; init; } = [];
    public IReadOnlyList<PermisoPlataforma> PermisosPlataforma { get; init; } = [];

    /// <summary>Tab activo: sedes | cargos | empresas | tipos-solicitud | roles</summary>
    public string Tab { get; init; } = "sedes";
}
