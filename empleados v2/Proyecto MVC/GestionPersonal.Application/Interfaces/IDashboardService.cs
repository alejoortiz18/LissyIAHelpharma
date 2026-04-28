using GestionPersonal.Models.DTOs.Dashboard;
using GestionPersonal.Models.Models;

namespace GestionPersonal.Application.Interfaces;

public interface IDashboardService
{
    /// <summary>
    /// Calcula los KPIs del dashboard.
    /// <para>Si <paramref name="filtrarPorJefeId"/> es <c>null</c>, devuelve datos globales (Analista).</para>
    /// <para>Si se especifica un empleadoId, filtra a la línea jerárquica descendente de ese jefe.</para>
    /// </summary>
    Task<ResultadoOperacion<DashboardKpiDto>> ObtenerKpisAsync(int? filtrarPorJefeId, CancellationToken ct = default);

    Task<IReadOnlyList<NovedadHoyDto>> ObtenerNovedadesHoyAsync(int? filtrarPorJefeId, CancellationToken ct = default);
    Task<IReadOnlyList<HoraExtraPendienteDto>> ObtenerHorasExtrasPendientesAsync(int? filtrarPorJefeId, CancellationToken ct = default);
}
