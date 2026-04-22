using GestionPersonal.Application.Interfaces;
using GestionPersonal.Domain.Interfaces;
using GestionPersonal.Models.Entities.GestionPersonalEntities;

namespace GestionPersonal.Application.Services;

public class HistorialService : IHistorialService
{
    private readonly IHistorialDesvinculacionRepository _repo;

    public HistorialService(IHistorialDesvinculacionRepository repo) => _repo = repo;

    public Task<IReadOnlyList<HistorialDesvinculacion>> ObtenerPorEmpleadoAsync(int empleadoId, CancellationToken ct = default)
        => _repo.ObtenerPorEmpleadoAsync(empleadoId, ct);
}
