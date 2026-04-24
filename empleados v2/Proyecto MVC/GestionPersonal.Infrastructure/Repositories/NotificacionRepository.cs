using GestionPersonal.Domain.Interfaces;
using GestionPersonal.Models.Entities.GestionPersonalEntities;

namespace GestionPersonal.Infrastructure.Repositories;

public class NotificacionRepository : INotificacionRepository
{
    private readonly AppDbContext _context;

    public NotificacionRepository(AppDbContext context) => _context = context;

    public void Agregar(RegistroNotificacion registro)
        => _context.RegistroNotificaciones.Add(registro);

    public Task<int> GuardarCambiosAsync(CancellationToken ct = default)
        => _context.SaveChangesAsync(ct);
}
