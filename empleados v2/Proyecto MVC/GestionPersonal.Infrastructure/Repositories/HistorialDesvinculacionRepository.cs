using GestionPersonal.Domain.Interfaces;
using GestionPersonal.Models.Entities.GestionPersonalEntities;
using Microsoft.EntityFrameworkCore;

namespace GestionPersonal.Infrastructure.Repositories;

public class HistorialDesvinculacionRepository : IHistorialDesvinculacionRepository
{
    private readonly AppDbContext _context;

    public HistorialDesvinculacionRepository(AppDbContext context) => _context = context;

    public async Task<IReadOnlyList<HistorialDesvinculacion>> ObtenerPorEmpleadoAsync(
        int empleadoId, CancellationToken ct = default)
        => await _context.HistorialDesvinculaciones
            .Where(h => h.EmpleadoId == empleadoId)
            .AsNoTracking()
            .OrderByDescending(h => h.FechaDesvinculacion)
            .ToListAsync(ct);

    public void Agregar(HistorialDesvinculacion historial)
        => _context.HistorialDesvinculaciones.Add(historial);

    public Task<int> GuardarCambiosAsync(CancellationToken ct = default)
        => _context.SaveChangesAsync(ct);
}
