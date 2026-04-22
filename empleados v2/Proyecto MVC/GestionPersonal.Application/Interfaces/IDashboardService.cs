using GestionPersonal.Models.DTOs.Dashboard;
using GestionPersonal.Models.Models;

namespace GestionPersonal.Application.Interfaces;

public interface IDashboardService
{
    Task<ResultadoOperacion<DashboardKpiDto>> ObtenerKpisAsync(int sedeId, CancellationToken ct = default);
    Task<IReadOnlyList<NovedadHoyDto>> ObtenerNovedadesHoyAsync(int sedeId, CancellationToken ct = default);
    Task<IReadOnlyList<HoraExtraPendienteDto>> ObtenerHorasExtrasPendientesAsync(int sedeId, CancellationToken ct = default);
}
