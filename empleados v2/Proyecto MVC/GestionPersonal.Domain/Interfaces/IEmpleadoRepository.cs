using GestionPersonal.Models.Entities.GestionPersonalEntities;
using GestionPersonal.Models.Enums;

namespace GestionPersonal.Domain.Interfaces;

public interface IEmpleadoRepository
{
    // Consultas
    Task<Empleado?> ObtenerPorIdAsync(int id, CancellationToken ct = default);
    Task<Empleado?> ObtenerPorIdConDetallesAsync(int id, CancellationToken ct = default);
    Task<IReadOnlyList<Empleado>> ObtenerPorSedeAsync(int sedeId, CancellationToken ct = default);
    Task<IReadOnlyList<Empleado>> ObtenerTodosAsync(CancellationToken ct = default);
    Task<bool> ExisteCedulaAsync(string cedula, int? excluirId = null, CancellationToken ct = default);
    Task<bool> ExisteCorreoAsync(string correo, int? excluirId = null, CancellationToken ct = default);

    /// <summary>Devuelve true si <paramref name="empleadoId"/> está en la jerarquía descendente del jefe indicado (directo o indirecto).</summary>
    Task<bool> EsSubordinadoTransitivoAsync(int empleadoId, int jefeEmpleadoId, CancellationToken ct = default);

    // Conteos para dashboard
    Task<int> ContarActivosPorSedeAsync(int sedeId, CancellationToken ct = default);
    Task<int> ContarTotalesPorEstadoAsync(EstadoEmpleado estado, CancellationToken ct = default);

    // Escritura
    void Agregar(Empleado empleado);
    void Actualizar(Empleado empleado);

    Task<int> GuardarCambiosAsync(CancellationToken ct = default);
}
