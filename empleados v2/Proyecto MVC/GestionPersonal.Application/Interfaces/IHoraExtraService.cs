using GestionPersonal.Models.DTOs.HoraExtra;
using GestionPersonal.Models.Models;

namespace GestionPersonal.Application.Interfaces;

public interface IHoraExtraService
{
    Task<IReadOnlyList<HoraExtraDto>> ObtenerPorSedeAsync(int sedeId, CancellationToken ct = default);
    Task<IReadOnlyList<HoraExtraDto>> ObtenerPorEmpleadoAsync(int empleadoId, CancellationToken ct = default);
    Task<IReadOnlyList<HoraExtraDto>> ObtenerPendientesPorSedeAsync(int sedeId, CancellationToken ct = default);
    Task<ResultadoOperacion> CrearAsync(CrearHoraExtraDto dto, int creadoPorUsuarioId, CancellationToken ct = default);
    Task<ResultadoOperacion> AprobarAsync(int horaExtraId, int aprobadoPorUsuarioId, CancellationToken ct = default);
    Task<ResultadoOperacion> RechazarAsync(int horaExtraId, string motivoRechazo, int rechazadoPorUsuarioId, CancellationToken ct = default);
    Task<ResultadoOperacion> AnularAsync(int horaExtraId, string motivoAnulacion, int anuladoPorUsuarioId, CancellationToken ct = default);
}
