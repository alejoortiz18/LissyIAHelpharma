using GestionPersonal.Models.Entities.GestionPersonalEntities;
using GestionPersonal.Models.Enums;

namespace GestionPersonal.Domain.Interfaces;

public interface IEventoLaboralRepository
{
    Task<EventoLaboral?> ObtenerPorIdAsync(int id, CancellationToken ct = default);
    Task<IReadOnlyList<EventoLaboral>> ObtenerPorEmpleadoAsync(int empleadoId, CancellationToken ct = default);
    Task<IReadOnlyList<EventoLaboral>> ObtenerPorSedeAsync(int sedeId, CancellationToken ct = default);

    /// <summary>Todos los eventos de todas las sedes (para el Analista de Servicios Farmacéuticos).</summary>
    Task<IReadOnlyList<EventoLaboral>> ObtenerTodosAsync(CancellationToken ct = default);

    /// <summary>Eventos activos (estado Activo) cuyo rango cubre la fecha indicada. Para detectar solapamientos.</summary>
    Task<IReadOnlyList<EventoLaboral>> ObtenerActivosEnFechaAsync(int empleadoId, DateOnly fecha, CancellationToken ct = default);

    /// <summary>Eventos activos o finalizados del empleado por tipo (para calcular saldo vacaciones).</summary>
    Task<IReadOnlyList<EventoLaboral>> ObtenerPorEmpleadoYTipoAsync(int empleadoId, TipoEvento tipo, CancellationToken ct = default);

    /// <summary>Eventos del empleado filtrados por rango de FechaInicio (ambos extremos opcionales e inclusivos).</summary>
    Task<IReadOnlyList<EventoLaboral>> ObtenerPorEmpleadoConFiltroAsync(
        int empleadoId, DateOnly? desde, DateOnly? hasta, CancellationToken ct = default);

    // Dashboard: eventos activos hoy
    Task<IReadOnlyList<EventoLaboral>> ObtenerActivosHoyPorSedeAsync(int sedeId, DateOnly hoy, CancellationToken ct = default);

    /// <summary>Dashboard Analista: eventos activos hoy en todas las sedes.</summary>
    Task<IReadOnlyList<EventoLaboral>> ObtenerActivosHoyGlobalAsync(DateOnly hoy, CancellationToken ct = default);

    /// <summary>Dashboard: cuenta eventos con estado Pendiente en el conjunto de empleados dado (null = todos).</summary>
    Task<int> ContarPendientesAsync(IReadOnlySet<int>? empleadoIds, CancellationToken ct = default);

    void Agregar(EventoLaboral evento);
    void Actualizar(EventoLaboral evento);

    Task<int> GuardarCambiosAsync(CancellationToken ct = default);
}
