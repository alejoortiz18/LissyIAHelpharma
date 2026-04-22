using GestionPersonal.Application.Interfaces;
using GestionPersonal.Domain.Interfaces;
using GestionPersonal.Models.Entities.GestionPersonalEntities;

namespace GestionPersonal.Application.Services;

public class CatalogoService : ICatalogoService
{
    private readonly ICatalogoRepository _repo;

    public CatalogoService(ICatalogoRepository repo) => _repo = repo;

    public Task<IReadOnlyList<Sede>> ObtenerSedesActivasAsync(CancellationToken ct = default)
        => _repo.ObtenerSedesActivasAsync(ct);

    public Task<IReadOnlyList<Cargo>> ObtenerCargosActivosAsync(CancellationToken ct = default)
        => _repo.ObtenerCargosActivosAsync(ct);

    public Task<IReadOnlyList<EmpresaTemporal>> ObtenerEmpresasTemporalesActivasAsync(CancellationToken ct = default)
        => _repo.ObtenerEmpresasTemporalesActivasAsync(ct);
}
