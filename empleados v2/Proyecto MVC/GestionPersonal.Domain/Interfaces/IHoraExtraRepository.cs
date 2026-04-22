using GestionPersonal.Models.Entities.GestionPersonalEntities;
using GestionPersonal.Models.Enums;

namespace GestionPersonal.Domain.Interfaces;

public interface IHoraExtraRepository
{
    Task<HoraExtra?> ObtenerPorIdAsync(int id, CancellationToken ct = default);
    Task<IReadOnlyList<HoraExtra>> ObtenerPorEmpleadoAsync(int empleadoId, CancellationToken ct = default);
    Task<IReadOnlyList<HoraExtra>> ObtenerPorSedeAsync(int sedeId, CancellationToken ct = default);
    Task<IReadOnlyList<HoraExtra>> ObtenerPendientesPorSedeAsync(int sedeId, CancellationToken ct = default);

    // Dashboard stats
    Task<int> ContarPendientesPorSedeAsync(int sedeId, CancellationToken ct = default);
    Task<int> ContarAprobadasEsteMesPorSedeAsync(int sedeId, int anio, int mes, CancellationToken ct = default);
    Task<decimal> SumarHorasAprobadasEsteMesPorSedeAsync(int sedeId, int anio, int mes, CancellationToken ct = default);

    void Agregar(HoraExtra horaExtra);
    void Actualizar(HoraExtra horaExtra);

    Task<int> GuardarCambiosAsync(CancellationToken ct = default);
}
