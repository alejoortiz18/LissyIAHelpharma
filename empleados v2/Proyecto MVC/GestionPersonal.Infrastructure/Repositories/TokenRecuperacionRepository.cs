using GestionPersonal.Domain.Interfaces;
using GestionPersonal.Models.Entities.GestionPersonalEntities;
using Microsoft.EntityFrameworkCore;

namespace GestionPersonal.Infrastructure.Repositories;

public class TokenRecuperacionRepository : ITokenRecuperacionRepository
{
    private readonly AppDbContext _context;

    public TokenRecuperacionRepository(AppDbContext context) => _context = context;

    public async Task<TokenRecuperacion?> ObtenerTokenActivoAsync(string token, CancellationToken ct = default)
        => await _context.TokensRecuperacion
            .Include(t => t.Usuario)
            .FirstOrDefaultAsync(
                t => t.Token == token && !t.Usado && t.FechaExpiracion > DateTime.UtcNow, ct);

    public void Agregar(TokenRecuperacion tokenRecuperacion)
        => _context.TokensRecuperacion.Add(tokenRecuperacion);

    public void Actualizar(TokenRecuperacion tokenRecuperacion)
        => _context.TokensRecuperacion.Update(tokenRecuperacion);

    public Task<int> GuardarCambiosAsync(CancellationToken ct = default)
        => _context.SaveChangesAsync(ct);
}
