using GestionPersonal.Models.DTOs.Catalogos;
using GestionPersonal.Models.Entities.GestionPersonalEntities;
using GestionPersonal.Models.Models;

namespace GestionPersonal.Application.Interfaces;

public interface IRolSistemaService
{
    Task<IReadOnlyList<RolSistema>> ObtenerRolesAsync(CancellationToken ct = default);
    Task<IReadOnlyList<RolSistema>> ObtenerRolesActivosAsync(CancellationToken ct = default);
    Task<IReadOnlyList<RolSistema>> ObtenerRolesParaSelectAsync(string? codigoIncluir, CancellationToken ct = default);
    Task<IReadOnlyList<PermisoPlataforma>> ObtenerPermisosAsync(CancellationToken ct = default);
    Task<RolSistemaDetalleDto?> ObtenerDetalleAsync(int id, CancellationToken ct = default);
    Task<IReadOnlyList<string>> ObtenerCodigosPermisoPorRolAsync(string codigoRol, CancellationToken ct = default);
    Task<ResultadoOperacion> CrearRolAsync(CrearRolSistemaDto dto);
    Task<ResultadoOperacion> EditarRolAsync(EditarRolSistemaDto dto);
    Task<ResultadoOperacion> DarDeBajaRolAsync(int id);
    Task<ResultadoOperacion> ActivarRolAsync(int id);
    Task SincronizarTextosEspanolAsync(CancellationToken ct = default);
}
