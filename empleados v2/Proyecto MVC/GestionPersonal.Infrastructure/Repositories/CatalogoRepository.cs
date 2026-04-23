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

    public async Task<Sede?> ObtenerSedePorIdAsync(int id, CancellationToken ct = default)
        => await _context.Sedes
            .FirstOrDefaultAsync(s => s.Id == id, ct);

    // ── Cargos ─────────────────────────────────────────────────
    public async Task<IReadOnlyList<Cargo>> ObtenerCargosActivosAsync(CancellationToken ct = default)
        => await _context.Cargos
            .Where(c => c.Estado == "Activo")
            .AsNoTracking()
            .OrderBy(c => c.Nombre)
            .ToListAsync(ct);

    public async Task<Cargo?> ObtenerCargoPorIdAsync(int id, CancellationToken ct = default)
        => await _context.Cargos
            .FirstOrDefaultAsync(c => c.Id == id, ct);

    // ── Empresas Temporales ────────────────────────────────────
    public async Task<IReadOnlyList<EmpresaTemporal>> ObtenerEmpresasTemporalesActivasAsync(CancellationToken ct = default)
        => await _context.EmpresasTemporales
            .Where(e => e.Estado == "Activa")
            .AsNoTracking()
            .OrderBy(e => e.Nombre)
            .ToListAsync(ct);

    public async Task<EmpresaTemporal?> ObtenerEmpresaTemporalPorIdAsync(int id, CancellationToken ct = default)
        => await _context.EmpresasTemporales
            .FirstOrDefaultAsync(e => e.Id == id, ct);

    public Task<int> GuardarCambiosAsync(CancellationToken ct = default)
        => _context.SaveChangesAsync(ct);

    // ── Creación ───────────────────────────────────────────────
    public void AgregarSede(Sede sede)
        => _context.Sedes.Add(sede);

    public void AgregarCargo(Cargo cargo)
        => _context.Cargos.Add(cargo);

    public void AgregarEmpresaTemporal(EmpresaTemporal empresa)
        => _context.EmpresasTemporales.Add(empresa);
}
