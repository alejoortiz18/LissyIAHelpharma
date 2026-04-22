using GestionPersonal.Domain.Interfaces;
using GestionPersonal.Models.Entities.GestionPersonalEntities;
using Microsoft.EntityFrameworkCore;

namespace GestionPersonal.Infrastructure.Repositories;

public class UsuarioRepository : IUsuarioRepository
{
    private readonly AppDbContext _context;

    public UsuarioRepository(AppDbContext context) => _context = context;

    public async Task<Usuario?> ObtenerPorIdAsync(int id, CancellationToken ct = default)
        => await _context.Usuarios
            .Include(u => u.Sede)
            .FirstOrDefaultAsync(u => u.Id == id, ct);

    public async Task<Usuario?> ObtenerPorCorreoAsync(string correo, CancellationToken ct = default)
        => await _context.Usuarios
            .Include(u => u.Sede)
            .Include(u => u.Empleado)
            .FirstOrDefaultAsync(u => u.CorreoAcceso == correo, ct);

    public async Task<bool> ExisteCorreoAsync(string correo, int? excluirId = null, CancellationToken ct = default)
        => await _context.Usuarios
            .AnyAsync(u => u.CorreoAcceso == correo && (excluirId == null || u.Id != excluirId), ct);

    public void Agregar(Usuario usuario) => _context.Usuarios.Add(usuario);

    public void Actualizar(Usuario usuario) => _context.Usuarios.Update(usuario);

    public Task<int> GuardarCambiosAsync(CancellationToken ct = default)
        => _context.SaveChangesAsync(ct);
}
