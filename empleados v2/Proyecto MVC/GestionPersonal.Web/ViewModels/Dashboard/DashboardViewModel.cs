using GestionPersonal.Models.DTOs.Dashboard;

namespace GestionPersonal.Web.ViewModels.Dashboard;

public class DashboardViewModel
{
    public DashboardKpiDto Kpis { get; init; } = new();
    public IReadOnlyList<NovedadHoyDto> NovedadesHoy { get; init; } = [];
    public IReadOnlyList<HoraExtraPendienteDto> HorasExtrasPendientes { get; init; } = [];
}
