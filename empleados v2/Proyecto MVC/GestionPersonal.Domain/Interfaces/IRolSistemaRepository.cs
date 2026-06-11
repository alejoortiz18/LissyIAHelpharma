using GestionPersonal.Models.Entities.GestionPersonalEntities;

namespace GestionPersonal.Domain.Interfaces;

public interface IRolSistemaRepository
{
    Task<IReadOnlyList<RolSistema>> ObtenerRolesAsync(bool soloActivos, CancellationToken ct = default);
    Task<RolSistema?> ObtenerRolPorIdConPermisosAsync(int id, CancellationToken ct = default);
    Task<RolSistema?> ObtenerRolPorCodigoAsync(string codigo, CancellationToken ct = default);
    Task<IReadOnlyList<PermisoPlataforma>> ObtenerPermisosAsync(CancellationToken ct = default);
    Task<IReadOnlyList<string>> ObtenerCodigosPermisoPorRolCodigoAsync(string codigoRol, CancellationToken ct = default);
    void AgregarRol(RolSistema rol);
    void EliminarRol(RolSistema rol);
    Task<int> ContarUsuariosPorRolCodigoAsync(string codigo, CancellationToken ct = default);
    Task ReemplazarPermisosRolAsync(int rolId, IEnumerable<int> permisoIds, CancellationToken ct = default);
    Task<int> GuardarCambiosAsync(CancellationToken ct = default);
    Task SincronizarTextosEspanolAsync(CancellationToken ct = default);
}
