using GestionPersonal.Models.Entities.GestionPersonalEntities;

namespace GestionPersonal.Domain.Interfaces;

public interface IHistorialDesvinculacionRepository
{
    Task<IReadOnlyList<HistorialDesvinculacion>> ObtenerPorEmpleadoAsync(int empleadoId, CancellationToken ct = default);

    void Agregar(HistorialDesvinculacion historial);

    Task<int> GuardarCambiosAsync(CancellationToken ct = default);
}
