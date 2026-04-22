using GestionPersonal.Domain.Interfaces;
using GestionPersonal.Models.Entities.GestionPersonalEntities;
using Microsoft.EntityFrameworkCore;

namespace GestionPersonal.Infrastructure.Repositories;

public class TurnoRepository : ITurnoRepository
{
    private readonly AppDbContext _context;

    public TurnoRepository(AppDbContext context) => _context = context;

    public async Task<PlantillaTurno?> ObtenerPorIdAsync(int id, CancellationToken ct = default)
        => await _context.PlantillasTurno
            .FirstOrDefaultAsync(p => p.Id == id, ct);

    public async Task<PlantillaTurno?> ObtenerPorIdConDetallesAsync(int id, CancellationToken ct = default)
        => await _context.PlantillasTurno
            .Include(p => p.PlantillaTurnoDetalles)
            .FirstOrDefaultAsync(p => p.Id == id, ct);

    public async Task<IReadOnlyList<PlantillaTurno>> ObtenerActivasAsync(CancellationToken ct = default)
        => await _context.PlantillasTurno
            .Include(p => p.PlantillaTurnoDetalles)
            .Where(p => p.Estado == "Activa")
            .AsNoTracking()
            .OrderBy(p => p.Nombre)
            .ToListAsync(ct);

    public async Task<bool> ExisteNombreAsync(string nombre, int? excluirId = null, CancellationToken ct = default)
        => await _context.PlantillasTurno
            .AnyAsync(p => p.Nombre == nombre && (excluirId == null || p.Id != excluirId), ct);

    public async Task<AsignacionTurno?> ObtenerAsignacionVigenteAsync(
        int empleadoId, DateOnly fecha, CancellationToken ct = default)
        => await _context.AsignacionesTurno
            .Include(a => a.PlantillaTurno)
                .ThenInclude(p => p.PlantillaTurnoDetalles)
            .Where(a => a.EmpleadoId == empleadoId && a.FechaVigencia <= fecha)
            .AsNoTracking()
            .OrderByDescending(a => a.FechaVigencia)
            .FirstOrDefaultAsync(ct);

    public async Task<IReadOnlyList<AsignacionTurno>> ObtenerAsignacionesActivasPorSedeAsync(
        int sedeId, CancellationToken ct = default)
    {
        // Asignaciones vigentes = las más recientes por empleado con sede coincidente
        var hoy = DateOnly.FromDateTime(DateTime.Today);
        return await _context.AsignacionesTurno
            .Include(a => a.Empleado)
                .ThenInclude(emp => emp.Sede)
            .Include(a => a.PlantillaTurno)
            .Include(a => a.ProgramadoPorNavigation)
            .Where(a => a.Empleado.SedeId == sedeId && a.FechaVigencia <= hoy)
            .AsNoTracking()
            .OrderByDescending(a => a.FechaVigencia)
            .ToListAsync(ct);
    }

    public void AgregarPlantilla(PlantillaTurno plantilla) => _context.PlantillasTurno.Add(plantilla);

    public void AgregarAsignacion(AsignacionTurno asignacion) => _context.AsignacionesTurno.Add(asignacion);

    public Task<int> GuardarCambiosAsync(CancellationToken ct = default)
        => _context.SaveChangesAsync(ct);
}
