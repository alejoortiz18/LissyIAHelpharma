using GestionPersonal.Application.Interfaces;
using GestionPersonal.Domain.Interfaces;
using GestionPersonal.Models.DTOs.Catalogos;
using GestionPersonal.Models.Entities.GestionPersonalEntities;
using GestionPersonal.Models.Models;

namespace GestionPersonal.Application.Services;

public class RolSistemaService : IRolSistemaService
{
    private readonly IRolSistemaRepository _repo;

    public RolSistemaService(IRolSistemaRepository repo) => _repo = repo;

    public Task<IReadOnlyList<RolSistema>> ObtenerRolesAsync(CancellationToken ct = default)
        => _repo.ObtenerRolesAsync(soloActivos: false, ct);

    public Task<IReadOnlyList<RolSistema>> ObtenerRolesActivosAsync(CancellationToken ct = default)
        => _repo.ObtenerRolesAsync(soloActivos: true, ct);

    public async Task<IReadOnlyList<RolSistema>> ObtenerRolesParaSelectAsync(string? codigoIncluir, CancellationToken ct = default)
    {
        var activos = await _repo.ObtenerRolesAsync(soloActivos: true, ct);
        if (string.IsNullOrWhiteSpace(codigoIncluir) || activos.Any(r => r.Codigo == codigoIncluir))
            return activos;
        var extra = await _repo.ObtenerRolPorCodigoAsync(codigoIncluir, ct);
        if (extra is null) return activos;
        return activos.Append(extra).OrderBy(r => r.Nombre).ToList();
    }

    public Task<IReadOnlyList<PermisoPlataforma>> ObtenerPermisosAsync(CancellationToken ct = default)
        => _repo.ObtenerPermisosAsync(ct);

    public async Task<RolSistemaDetalleDto?> ObtenerDetalleAsync(int id, CancellationToken ct = default)
    {
        var rol = await _repo.ObtenerRolPorIdConPermisosAsync(id, ct);
        if (rol is null) return null;
        return new RolSistemaDetalleDto
        {
            Id = rol.Id,
            Codigo = rol.Codigo,
            Nombre = rol.Nombre,
            Descripcion = rol.Descripcion,
            EsRolSistema = rol.EsRolSistema,
            Estado = rol.Estado,
            PermisoIds = rol.Permisos.Select(p => p.PermisoId).ToList(),
        };
    }

    public Task<IReadOnlyList<string>> ObtenerCodigosPermisoPorRolAsync(string codigoRol, CancellationToken ct = default)
        => _repo.ObtenerCodigosPermisoPorRolCodigoAsync(codigoRol, ct);

    public async Task<ResultadoOperacion> CrearRolAsync(CrearRolSistemaDto dto)
    {
        if (await _repo.ObtenerRolPorCodigoAsync(dto.Codigo.Trim()) is not null)
            return ResultadoOperacion.Fail("Ya existe un rol con ese código.");

        if (dto.PermisoIds.Count == 0)
            return ResultadoOperacion.Fail("Selecciona al menos un permiso para el rol.");

        try
        {
            var rol = new RolSistema
            {
                Codigo = dto.Codigo.Trim(),
                Nombre = dto.Nombre.Trim(),
                Descripcion = string.IsNullOrWhiteSpace(dto.Descripcion) ? null : dto.Descripcion.Trim(),
                EsRolSistema = false,
                Estado = "Activo",
                FechaCreacion = DateTime.UtcNow,
            };
            _repo.AgregarRol(rol);
            await _repo.GuardarCambiosAsync();

            await _repo.ReemplazarPermisosRolAsync(rol.Id, dto.PermisoIds);
            await _repo.GuardarCambiosAsync();
            return ResultadoOperacion.Ok("Rol creado correctamente.");
        }
        catch
        {
            return ResultadoOperacion.Fail("No se pudo crear el rol. Verifique los datos.");
        }
    }

    public async Task<ResultadoOperacion> EditarRolAsync(EditarRolSistemaDto dto)
    {
        var rol = await _repo.ObtenerRolPorIdConPermisosAsync(dto.Id);
        if (rol is null)
            return ResultadoOperacion.Fail("Rol no encontrado.");

        if (dto.PermisoIds.Count == 0)
            return ResultadoOperacion.Fail("Selecciona al menos un permiso para el rol.");

        try
        {
            rol.Nombre = dto.Nombre.Trim();
            rol.Descripcion = string.IsNullOrWhiteSpace(dto.Descripcion) ? null : dto.Descripcion.Trim();
            rol.Estado = dto.Estado;
            rol.FechaModificacion = DateTime.UtcNow;

            await _repo.ReemplazarPermisosRolAsync(rol.Id, dto.PermisoIds);
            await _repo.GuardarCambiosAsync();
            return ResultadoOperacion.Ok("Rol actualizado correctamente.");
        }
        catch
        {
            return ResultadoOperacion.Fail("No se pudo actualizar el rol.");
        }
    }

    public async Task<ResultadoOperacion> DarDeBajaRolAsync(int id)
    {
        var rol = await _repo.ObtenerRolPorIdConPermisosAsync(id);
        if (rol is null)
            return ResultadoOperacion.Fail("Rol no encontrado.");
        if (rol.Estado == "Inactivo")
            return ResultadoOperacion.Fail("El rol ya está inactivo.");
        var enUso = await _repo.ContarUsuariosPorRolCodigoAsync(rol.Codigo);
        if (!rol.EsRolSistema && enUso == 0)
        {
            _repo.EliminarRol(rol);
            await _repo.GuardarCambiosAsync();
            return ResultadoOperacion.Ok("Rol eliminado correctamente.");
        }

        rol.Estado = "Inactivo";
        rol.FechaModificacion = DateTime.UtcNow;
        await _repo.GuardarCambiosAsync();
        if (rol.EsRolSistema)
            return ResultadoOperacion.Ok("Rol del sistema inactivado. Ya no aparecerá al asignar roles nuevos.");
        return ResultadoOperacion.Ok(
            enUso > 0
                ? $"El rol está asignado a {enUso} usuario(s). Se inactivó y ya no aparecerá al asignar roles."
                : "Rol inactivado correctamente.");
    }

    public async Task<ResultadoOperacion> ActivarRolAsync(int id)
    {
        var rol = await _repo.ObtenerRolPorIdConPermisosAsync(id);
        if (rol is null)
            return ResultadoOperacion.Fail("Rol no encontrado.");
        rol.Estado = "Activo";
        rol.FechaModificacion = DateTime.UtcNow;
        await _repo.GuardarCambiosAsync();
        return ResultadoOperacion.Ok("Rol activado correctamente.");
    }

    public Task SincronizarTextosEspanolAsync(CancellationToken ct = default)
        => _repo.SincronizarTextosEspanolAsync(ct);
}
