using GestionPersonal.Models.Entities.GestionPersonalEntities;

namespace GestionPersonal.Domain.Interfaces;

public interface ITurnoRepository
{
    Task<PlantillaTurno?> ObtenerPorIdAsync(int id, CancellationToken ct = default);
    Task<PlantillaTurno?> ObtenerPorIdConDetallesAsync(int id, CancellationToken ct = default);
    Task<IReadOnlyList<PlantillaTurno>> ObtenerActivasAsync(CancellationToken ct = default);
    Task<bool> ExisteNombreAsync(string nombre, int? excluirId = null, CancellationToken ct = default);

    /// <summary>Asignación de turno vigente para un empleado en una fecha dada.</summary>
    Task<AsignacionTurno?> ObtenerAsignacionVigenteAsync(int empleadoId, DateOnly fecha, CancellationToken ct = default);

    Task<IReadOnlyList<AsignacionTurno>> ObtenerAsignacionesActivasPorSedeAsync(int sedeId, CancellationToken ct = default);

    /// <summary>Historial completo de asignaciones de un empleado, orden descendente por fecha.</summary>
    Task<IReadOnlyList<AsignacionTurno>> ObtenerHistorialPorEmpleadoAsync(int empleadoId, CancellationToken ct = default);

    Task<AsignacionTurno?> ObtenerAsignacionPorIdAsync(int id, CancellationToken ct = default);

    void AgregarPlantilla(PlantillaTurno plantilla);
    void EliminarDetalles(IEnumerable<PlantillaTurnoDetalle> detalles);
    void AgregarAsignacion(AsignacionTurno asignacion);

    Task<int> GuardarCambiosAsync(CancellationToken ct = default);
}
