using GestionPersonal.Domain.Interfaces;
using GestionPersonal.Models.Entities.GestionPersonalEntities;
using GestionPersonal.Models.Enums;
using Microsoft.EntityFrameworkCore;

namespace GestionPersonal.Infrastructure.Repositories;

public class EmpleadoRepository : IEmpleadoRepository
{
    private readonly AppDbContext _context;

    public EmpleadoRepository(AppDbContext context) => _context = context;

    public async Task<Empleado?> ObtenerPorIdAsync(int id, CancellationToken ct = default)
        => await _context.Empleados
            .FirstOrDefaultAsync(e => e.Id == id, ct);

    public async Task<Empleado?> ObtenerPorIdConDetallesAsync(int id, CancellationToken ct = default)
        => await _context.Empleados
            .Include(e => e.Sede)
            .Include(e => e.Cargo)
            .Include(e => e.Usuario)
            .Include(e => e.EmpresaTemporal)
            .Include(e => e.JefeInmediato)
            .Include(e => e.ContactoEmergencia)
            .FirstOrDefaultAsync(e => e.Id == id, ct);

    public async Task<IReadOnlyList<Empleado>> ObtenerPorSedeAsync(int sedeId, CancellationToken ct = default)
        => await _context.Empleados
            .Include(e => e.Cargo)
            .Include(e => e.Usuario)
            .Where(e => e.SedeId == sedeId)
            .AsNoTracking()
            .ToListAsync(ct);

    public async Task<IReadOnlyList<Empleado>> ObtenerTodosAsync(CancellationToken ct = default)
        => await _context.Empleados
            .Include(e => e.Sede)
            .Include(e => e.Cargo)
            .Include(e => e.Usuario)
            .AsNoTracking()
            .ToListAsync(ct);

    public async Task<bool> ExisteCedulaAsync(string cedula, int? excluirId = null, CancellationToken ct = default)
        => await _context.Empleados
            .AnyAsync(e => e.Cedula == cedula && (excluirId == null || e.Id != excluirId), ct);

    public async Task<bool> ExisteCorreoAsync(string correo, int? excluirId = null, CancellationToken ct = default)
        => await _context.Empleados
            .AnyAsync(e => e.CorreoElectronico == correo && (excluirId == null || e.Id != excluirId), ct);

    public async Task<int> ContarActivosPorSedeAsync(int sedeId, CancellationToken ct = default)
        => await _context.Empleados
            .CountAsync(e => e.SedeId == sedeId && e.Estado == EstadoEmpleado.Activo, ct);

    public async Task<int> ContarTotalesPorEstadoAsync(EstadoEmpleado estado, CancellationToken ct = default)
        => await _context.Empleados
            .CountAsync(e => e.Estado == estado, ct);

    public void Agregar(Empleado empleado) => _context.Empleados.Add(empleado);

    public void Actualizar(Empleado empleado) => _context.Empleados.Update(empleado);

    public Task<int> GuardarCambiosAsync(CancellationToken ct = default)
        => _context.SaveChangesAsync(ct);
}
