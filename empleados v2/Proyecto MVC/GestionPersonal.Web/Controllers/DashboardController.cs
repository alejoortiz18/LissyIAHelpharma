using GestionPersonal.Application.Interfaces;
using GestionPersonal.Models.DTOs.Dashboard;
using GestionPersonal.Models.Enums;
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
        var rol = SesionHelper.GetRol(User);

        // Analista y Administrador ven datos globales (null = sin filtro de jerarquía).
        // Todos los demás roles ven únicamente su propia línea jerárquica.
        int? filtrarPorJefeId = rol is RolUsuario.Analista or RolUsuario.Administrador
            ? null
            : SesionHelper.GetEmpleadoId(User);

        var kpisResult   = await _dashboardService.ObtenerKpisAsync(filtrarPorJefeId);
        var novedades    = await _dashboardService.ObtenerNovedadesHoyAsync(filtrarPorJefeId);
        var horasExtras  = await _dashboardService.ObtenerHorasExtrasPendientesAsync(filtrarPorJefeId);

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
