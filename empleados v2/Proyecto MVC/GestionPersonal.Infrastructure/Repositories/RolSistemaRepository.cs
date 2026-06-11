using GestionPersonal.Constants;
using GestionPersonal.Domain.Interfaces;
using GestionPersonal.Models.Entities.GestionPersonalEntities;
using GestionPersonal.Models.Enums;
using Microsoft.EntityFrameworkCore;

namespace GestionPersonal.Infrastructure.Repositories;

public class RolSistemaRepository : IRolSistemaRepository
{
    private readonly AppDbContext _context;

    public RolSistemaRepository(AppDbContext context) => _context = context;

    public async Task<IReadOnlyList<RolSistema>> ObtenerRolesAsync(bool soloActivos, CancellationToken ct = default)
    {
        var q = _context.RolesSistema.AsNoTracking();
        if (soloActivos)
            q = q.Where(r => r.Estado == "Activo");
        return await q.Include(r => r.Permisos).OrderBy(r => r.Nombre).ToListAsync(ct);
    }

    public async Task<RolSistema?> ObtenerRolPorIdConPermisosAsync(int id, CancellationToken ct = default)
        => await _context.RolesSistema
            .Include(r => r.Permisos)
            .FirstOrDefaultAsync(r => r.Id == id, ct);

    public async Task<RolSistema?> ObtenerRolPorCodigoAsync(string codigo, CancellationToken ct = default)
        => await _context.RolesSistema
            .AsNoTracking()
            .FirstOrDefaultAsync(r => r.Codigo == codigo, ct);

    public async Task<IReadOnlyList<PermisoPlataforma>> ObtenerPermisosAsync(CancellationToken ct = default)
        => await _context.PermisosPlataforma
            .AsNoTracking()
            .OrderBy(p => p.Modulo)
            .ThenBy(p => p.Orden)
            .ThenBy(p => p.Nombre)
            .ToListAsync(ct);

    public async Task<IReadOnlyList<string>> ObtenerCodigosPermisoPorRolCodigoAsync(string codigoRol, CancellationToken ct = default)
        => await _context.RolesSistemaPermisos
            .AsNoTracking()
            .Where(rp => rp.RolSistema.Codigo == codigoRol && rp.RolSistema.Estado == "Activo")
            .Select(rp => rp.Permiso.Codigo)
            .ToListAsync(ct);

    public void AgregarRol(RolSistema rol) => _context.RolesSistema.Add(rol);

    public void EliminarRol(RolSistema rol) => _context.RolesSistema.Remove(rol);

    public async Task<int> ContarUsuariosPorRolCodigoAsync(string codigo, CancellationToken ct = default)
    {
        if (!Enum.TryParse<RolUsuario>(codigo, ignoreCase: true, out var rolEnum))
            return 0;
        return await _context.Usuarios.CountAsync(u => u.Rol == rolEnum, ct);
    }

    public async Task ReemplazarPermisosRolAsync(int rolId, IEnumerable<int> permisoIds, CancellationToken ct = default)
    {
        var existentes = await _context.RolesSistemaPermisos
            .Where(rp => rp.RolSistemaId == rolId)
            .ToListAsync(ct);
        _context.RolesSistemaPermisos.RemoveRange(existentes);

        foreach (var permisoId in permisoIds.Distinct())
        {
            _context.RolesSistemaPermisos.Add(new RolSistemaPermiso
            {
                RolSistemaId = rolId,
                PermisoId = permisoId,
            });
        }
    }

    public Task<int> GuardarCambiosAsync(CancellationToken ct = default)
        => _context.SaveChangesAsync(ct);

    public async Task SincronizarTextosEspanolAsync(CancellationToken ct = default)
    {
        if (!await _context.Database.CanConnectAsync(ct))
            return;

        try
        {
            _ = await _context.PermisosPlataforma.AsNoTracking().AnyAsync(ct);
        }
        catch
        {
            return; // Tablas de roles aún no migradas en este servidor
        }

        foreach (var p in await _context.PermisosPlataforma.ToListAsync(ct))
        {
            if (!PermisosPlataformaTextos.Todos.TryGetValue(p.Codigo, out var t))
                continue;
            p.Modulo = t.Modulo;
            p.Nombre = t.Nombre;
            p.Descripcion = t.Descripcion;
        }

        foreach (var r in await _context.RolesSistema.ToListAsync(ct))
        {
            r.Nombre = RolesSistemaTextos.Nombre(r.Codigo, r.Nombre);
            r.Descripcion = RolesSistemaTextos.Descripcion(r.Codigo, r.Descripcion);
        }

        await _context.SaveChangesAsync(ct);
    }
}
