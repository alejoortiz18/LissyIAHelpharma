using GestionPersonal.Domain.Interfaces;
using GestionPersonal.Models.Entities.GestionPersonalEntities;
using Microsoft.EntityFrameworkCore;

namespace GestionPersonal.Infrastructure.Repositories;

public class CatalogoRepository : ICatalogoRepository
{
    private readonly AppDbContext _context;

    public CatalogoRepository(AppDbContext context) => _context = context;

    // ── Sedes ──────────────────────────────────────────────────
    public async Task<IReadOnlyList<Sede>> ObtenerSedesActivasAsync(CancellationToken ct = default)
        => await _context.Sedes
            .Where(s => s.Estado == "Activa")
            .AsNoTracking()
            .OrderBy(s => s.Nombre)
            .ToListAsync(ct);

    public async Task<IReadOnlyList<Sede>> ObtenerTodasSedesAsync(CancellationToken ct = default)
        => await _context.Sedes
            .AsNoTracking()
            .OrderBy(s => s.Nombre)
            .ToListAsync(ct);

    public async Task<IReadOnlyList<Sede>> ObtenerSedesParaSelectAsync(int? incluirId, CancellationToken ct = default)
    {
        var activas = await ObtenerSedesActivasAsync(ct);
        if (!incluirId.HasValue || activas.Any(s => s.Id == incluirId.Value))
            return activas;
        var extra = await _context.Sedes.AsNoTracking()
            .FirstOrDefaultAsync(s => s.Id == incluirId.Value, ct);
        if (extra is null) return activas;
        return activas.Append(extra).OrderBy(s => s.Nombre).ToList();
    }

    public async Task<Sede?> ObtenerSedePorIdAsync(int id, CancellationToken ct = default)
        => await _context.Sedes.FirstOrDefaultAsync(s => s.Id == id, ct);

    public async Task<(int Usuarios, int Empleados)> ContarUsoSedeAsync(int sedeId, CancellationToken ct = default)
    {
        var usuarios = await _context.Usuarios.CountAsync(u => u.SedeId == sedeId, ct);
        var empleados = await _context.Empleados.CountAsync(e => e.SedeId == sedeId, ct);
        return (usuarios, empleados);
    }

    // ── Cargos ─────────────────────────────────────────────────
    public async Task<IReadOnlyList<Cargo>> ObtenerCargosActivosAsync(CancellationToken ct = default)
        => await _context.Cargos
            .Where(c => c.Estado == "Activo")
            .AsNoTracking()
            .OrderBy(c => c.Nombre)
            .ToListAsync(ct);

    public async Task<IReadOnlyList<Cargo>> ObtenerTodosCargosAsync(CancellationToken ct = default)
        => await _context.Cargos
            .AsNoTracking()
            .OrderBy(c => c.Nombre)
            .ToListAsync(ct);

    public async Task<IReadOnlyList<Cargo>> ObtenerCargosParaSelectAsync(int? incluirId, CancellationToken ct = default)
    {
        var activos = await ObtenerCargosActivosAsync(ct);
        if (!incluirId.HasValue || activos.Any(c => c.Id == incluirId.Value))
            return activos;
        var extra = await _context.Cargos.AsNoTracking()
            .FirstOrDefaultAsync(c => c.Id == incluirId.Value, ct);
        if (extra is null) return activos;
        return activos.Append(extra).OrderBy(c => c.Nombre).ToList();
    }

    public async Task<Cargo?> ObtenerCargoPorIdAsync(int id, CancellationToken ct = default)
        => await _context.Cargos.FirstOrDefaultAsync(c => c.Id == id, ct);

    public Task<int> ContarUsoCargoAsync(int cargoId, CancellationToken ct = default)
        => _context.Empleados.CountAsync(e => e.CargoId == cargoId, ct);

    // ── Empresas Temporales ────────────────────────────────────
    public async Task<IReadOnlyList<EmpresaTemporal>> ObtenerEmpresasTemporalesActivasAsync(CancellationToken ct = default)
        => await _context.EmpresasTemporales
            .Where(e => e.Estado == "Activa")
            .AsNoTracking()
            .OrderBy(e => e.Nombre)
            .ToListAsync(ct);

    public async Task<IReadOnlyList<EmpresaTemporal>> ObtenerTodasEmpresasTemporalesAsync(CancellationToken ct = default)
        => await _context.EmpresasTemporales
            .AsNoTracking()
            .OrderBy(e => e.Nombre)
            .ToListAsync(ct);

    public async Task<IReadOnlyList<EmpresaTemporal>> ObtenerEmpresasTemporalesParaSelectAsync(int? incluirId, CancellationToken ct = default)
    {
        var activas = await ObtenerEmpresasTemporalesActivasAsync(ct);
        if (!incluirId.HasValue || activas.Any(e => e.Id == incluirId.Value))
            return activas;
        var extra = await _context.EmpresasTemporales.AsNoTracking()
            .FirstOrDefaultAsync(e => e.Id == incluirId.Value, ct);
        if (extra is null) return activas;
        return activas.Append(extra).OrderBy(e => e.Nombre).ToList();
    }

    public async Task<EmpresaTemporal?> ObtenerEmpresaTemporalPorIdAsync(int id, CancellationToken ct = default)
        => await _context.EmpresasTemporales.FirstOrDefaultAsync(e => e.Id == id, ct);

    public Task<int> ContarUsoEmpresaTemporalAsync(int empresaId, CancellationToken ct = default)
        => _context.Empleados.CountAsync(e => e.EmpresaTemporalId == empresaId, ct);

    public Task<int> GuardarCambiosAsync(CancellationToken ct = default)
        => _context.SaveChangesAsync(ct);

    public void AgregarSede(Sede sede) => _context.Sedes.Add(sede);
    public void AgregarCargo(Cargo cargo) => _context.Cargos.Add(cargo);
    public void AgregarEmpresaTemporal(EmpresaTemporal empresa) => _context.EmpresasTemporales.Add(empresa);

    public void EliminarSede(Sede sede) => _context.Sedes.Remove(sede);
    public void EliminarCargo(Cargo cargo) => _context.Cargos.Remove(cargo);
    public void EliminarEmpresaTemporal(EmpresaTemporal empresa) => _context.EmpresasTemporales.Remove(empresa);

    // ── Tipos de solicitud ─────────────────────────────────────
    public async Task<IReadOnlyList<TipoSolicitud>> ObtenerTiposSolicitudActivosAsync(CancellationToken ct = default)
        => await _context.TiposSolicitud
            .Where(t => t.Estado == "Activo")
            .AsNoTracking()
            .OrderBy(t => t.Nombre)
            .ToListAsync(ct);

    public async Task<IReadOnlyList<TipoSolicitud>> ObtenerTodosTiposSolicitudAsync(CancellationToken ct = default)
        => await _context.TiposSolicitud
            .AsNoTracking()
            .OrderBy(t => t.Nombre)
            .ToListAsync(ct);

    public async Task<TipoSolicitud?> ObtenerTipoSolicitudPorIdAsync(int id, CancellationToken ct = default)
        => await _context.TiposSolicitud.FirstOrDefaultAsync(t => t.Id == id, ct);

    public async Task<TipoSolicitud?> ObtenerTipoSolicitudActivoPorCodigoAsync(string codigo, CancellationToken ct = default)
        => await _context.TiposSolicitud
            .AsNoTracking()
            .FirstOrDefaultAsync(
                t => t.Estado == "Activo" && t.Codigo == codigo,
                ct);

    public Task<int> ContarUsoTipoSolicitudAsync(string codigo, CancellationToken ct = default)
        => _context.EventosLaborales.CountAsync(e => e.TipoEvento == codigo, ct);

    public void AgregarTipoSolicitud(TipoSolicitud tipo) => _context.TiposSolicitud.Add(tipo);
    public void EliminarTipoSolicitud(TipoSolicitud tipo) => _context.TiposSolicitud.Remove(tipo);
}
