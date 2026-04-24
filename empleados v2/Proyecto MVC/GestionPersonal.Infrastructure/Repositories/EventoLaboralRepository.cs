using GestionPersonal.Domain.Interfaces;
using GestionPersonal.Models.Entities.GestionPersonalEntities;
using GestionPersonal.Models.Enums;
using Microsoft.EntityFrameworkCore;

namespace GestionPersonal.Infrastructure.Repositories;

public class EventoLaboralRepository : IEventoLaboralRepository
{
    private readonly AppDbContext _context;

    public EventoLaboralRepository(AppDbContext context) => _context = context;

    public async Task<EventoLaboral?> ObtenerPorIdAsync(int id, CancellationToken ct = default)
        => await _context.EventosLaborales
            .Include(e => e.Empleado)
                .ThenInclude(emp => emp.Sede)
            .FirstOrDefaultAsync(e => e.Id == id, ct);

    public async Task<IReadOnlyList<EventoLaboral>> ObtenerPorEmpleadoAsync(int empleadoId, CancellationToken ct = default)
        => await _context.EventosLaborales
            .Where(e => e.EmpleadoId == empleadoId)
            .AsNoTracking()
            .OrderByDescending(e => e.FechaInicio)
            .ToListAsync(ct);

    public async Task<IReadOnlyList<EventoLaboral>> ObtenerPorSedeAsync(int sedeId, CancellationToken ct = default)
        => await _context.EventosLaborales
            .Include(e => e.Empleado)
                .ThenInclude(emp => emp.Sede)
            .Where(e => e.Empleado.SedeId == sedeId)
            .AsNoTracking()
            .OrderByDescending(e => e.FechaInicio)
            .ToListAsync(ct);

    public async Task<IReadOnlyList<EventoLaboral>> ObtenerActivosEnFechaAsync(
        int empleadoId, DateOnly fecha, CancellationToken ct = default)
        => await _context.EventosLaborales
            .Where(e => e.EmpleadoId == empleadoId
                     && e.Estado != EstadoEvento.Anulado
                     && e.FechaInicio <= fecha
                     && e.FechaFin >= fecha)
            .AsNoTracking()
            .ToListAsync(ct);

    public async Task<IReadOnlyList<EventoLaboral>> ObtenerPorEmpleadoYTipoAsync(
        int empleadoId, TipoEvento tipo, CancellationToken ct = default)
        => await _context.EventosLaborales
            .Where(e => e.EmpleadoId == empleadoId
                     && e.TipoEvento == tipo
                     && e.Estado != EstadoEvento.Anulado)
            .AsNoTracking()
            .ToListAsync(ct);

    public async Task<IReadOnlyList<EventoLaboral>> ObtenerActivosHoyPorSedeAsync(
        int sedeId, DateOnly hoy, CancellationToken ct = default)
        => await _context.EventosLaborales
            .Include(e => e.Empleado)
                .ThenInclude(emp => emp.Sede)
            .Where(e => e.Empleado.SedeId == sedeId
                     && e.Estado == EstadoEvento.Activo
                     && e.FechaInicio <= hoy
                     && e.FechaFin >= hoy)
            .AsNoTracking()
            .ToListAsync(ct);

    public async Task<IReadOnlyList<EventoLaboral>> ObtenerPorEmpleadoConFiltroAsync(
        int empleadoId, DateOnly? desde, DateOnly? hasta, CancellationToken ct = default)
        => await _context.EventosLaborales
            .Where(e => e.EmpleadoId == empleadoId
                     && (desde == null || e.FechaInicio >= desde)
                     && (hasta == null || e.FechaInicio <= hasta))
            .AsNoTracking()
            .OrderByDescending(e => e.FechaInicio)
            .ToListAsync(ct);

    public void Agregar(EventoLaboral evento) => _context.EventosLaborales.Add(evento);

    public void Actualizar(EventoLaboral evento) => _context.EventosLaborales.Update(evento);

    public Task<int> GuardarCambiosAsync(CancellationToken ct = default)
        => _context.SaveChangesAsync(ct);
}
