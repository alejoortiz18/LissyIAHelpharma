using GestionPersonal.Application.Interfaces;
using GestionPersonal.Models.DTOs.Dashboard;
using GestionPersonal.Web.Helpers;
using GestionPersonal.Web.ViewModels.Dashboard;
using Microsoft.AspNetCore.Authorization;
using Microsoft.AspNetCore.Mvc;

namespace GestionPersonal.Web.Controllers;

[Authorize]
public class DashboardController : Controller
{
    private readonly IDashboardService _dashboardService;

    public DashboardController(IDashboardService dashboardService)
    {
        _dashboardService = dashboardService;
    }

    // GET /Dashboard
    public async Task<IActionResult> Index()
    {
        var sedeId = SesionHelper.GetSedeId(User);
        var kpisResult   = await _dashboardService.ObtenerKpisAsync(sedeId);
        var novedades    = await _dashboardService.ObtenerNovedadesHoyAsync(sedeId);
        var horasExtras  = await _dashboardService.ObtenerHorasExtrasPendientesAsync(sedeId);

        var vm = new DashboardViewModel
        {
            Kpis                  = kpisResult.Exito ? kpisResult.Datos! : new DashboardKpiDto(),
            NovedadesHoy          = novedades,
            HorasExtrasPendientes = horasExtras,
        };

        ViewData["Title"] = "Dashboard";
        ViewData["BreadcrumbCurrent"] = "Dashboard";
        return View(vm);
    }
}
