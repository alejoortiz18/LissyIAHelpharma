using GestionPersonal.Domain.Interfaces;
using GestionPersonal.Models.Entities.GestionPersonalEntities;
using GestionPersonal.Models.Enums;
using Microsoft.EntityFrameworkCore;

namespace GestionPersonal.Infrastructure.Repositories;

public class HoraExtraRepository : IHoraExtraRepository
{
    private readonly AppDbContext _context;

    public HoraExtraRepository(AppDbContext context) => _context = context;

    public async Task<HoraExtra?> ObtenerPorIdAsync(int id, CancellationToken ct = default)
        => await _context.HorasExtras
            .Include(h => h.Empleado)
                .ThenInclude(emp => emp.Sede)
            .FirstOrDefaultAsync(h => h.Id == id, ct);

    public async Task<IReadOnlyList<HoraExtra>> ObtenerPorEmpleadoAsync(int empleadoId, CancellationToken ct = default)
        => await _context.HorasExtras
            .Where(h => h.EmpleadoId == empleadoId)
            .AsNoTracking()
            .OrderByDescending(h => h.FechaTrabajada)
            .ToListAsync(ct);

    public async Task<IReadOnlyList<HoraExtra>> ObtenerPorSedeAsync(int sedeId, CancellationToken ct = default)
        => await _context.HorasExtras
            .Include(h => h.Empleado)
                .ThenInclude(emp => emp.Sede)
            .Where(h => h.Empleado.SedeId == sedeId)
            .AsNoTracking()
            .OrderByDescending(h => h.FechaTrabajada)
            .ToListAsync(ct);

    public async Task<IReadOnlyList<HoraExtra>> ObtenerPendientesPorSedeAsync(int sedeId, CancellationToken ct = default)
        => await _context.HorasExtras
            .Include(h => h.Empleado)
                .ThenInclude(emp => emp.Sede)
            .Where(h => h.Empleado.SedeId == sedeId && h.Estado == EstadoHoraExtra.Pendiente)
            .AsNoTracking()
            .OrderBy(h => h.FechaTrabajada)
            .ToListAsync(ct);

    public async Task<int> ContarPendientesPorSedeAsync(int sedeId, CancellationToken ct = default)
        => await _context.HorasExtras
            .CountAsync(h => h.Empleado.SedeId == sedeId && h.Estado == EstadoHoraExtra.Pendiente, ct);

    public async Task<int> ContarAprobadasEsteMesPorSedeAsync(int sedeId, int anio, int mes, CancellationToken ct = default)
    {
        var desde = new DateOnly(anio, mes, 1);
        var hasta = desde.AddMonths(1).AddDays(-1);
        return await _context.HorasExtras
            .CountAsync(h => h.Empleado.SedeId == sedeId
                          && h.Estado == EstadoHoraExtra.Aprobado
                          && h.FechaTrabajada >= desde
                          && h.FechaTrabajada <= hasta, ct);
    }

    public async Task<decimal> SumarHorasAprobadasEsteMesPorSedeAsync(int sedeId, int anio, int mes, CancellationToken ct = default)
    {
        var desde = new DateOnly(anio, mes, 1);
        var hasta = desde.AddMonths(1).AddDays(-1);
        return await _context.HorasExtras
            .Where(h => h.Empleado.SedeId == sedeId
                     && h.Estado == EstadoHoraExtra.Aprobado
                     && h.FechaTrabajada >= desde
                     && h.FechaTrabajada <= hasta)
            .SumAsync(h => h.CantidadHoras, ct);
    }

    public void Agregar(HoraExtra horaExtra) => _context.HorasExtras.Add(horaExtra);

    public void Actualizar(HoraExtra horaExtra) => _context.HorasExtras.Update(horaExtra);

    public Task<int> GuardarCambiosAsync(CancellationToken ct = default)
        => _context.SaveChangesAsync(ct);
}
