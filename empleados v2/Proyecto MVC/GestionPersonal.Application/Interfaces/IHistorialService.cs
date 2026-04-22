using GestionPersonal.Models.Entities.GestionPersonalEntities;

namespace GestionPersonal.Application.Interfaces;

public interface IHistorialService
{
    Task<IReadOnlyList<HistorialDesvinculacion>> ObtenerPorEmpleadoAsync(int empleadoId, CancellationToken ct = default);
}
