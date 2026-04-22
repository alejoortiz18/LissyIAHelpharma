using GestionPersonal.Application.Interfaces;
using GestionPersonal.Models.DTOs.Turno;
using GestionPersonal.Models.Enums;
using GestionPersonal.Web.Helpers;
using GestionPersonal.Web.ViewModels.Turno;
using Microsoft.AspNetCore.Authorization;
using Microsoft.AspNetCore.Mvc;

namespace GestionPersonal.Web.Controllers;

[Authorize]
public class TurnoController : Controller
{
    private readonly ITurnoService   _turnoService;
    private readonly IEmpleadoService _empleadoService;

    public TurnoController(ITurnoService turnoService, IEmpleadoService empleadoService)
    {
        _turnoService    = turnoService;
        _empleadoService = empleadoService;
    }

    // GET /Turno
    [HttpGet]
    public async Task<IActionResult> Index()
    {
        var plantillas = await _turnoService.ObtenerPlantillasActivasAsync();

        var vm = new TurnosViewModel
        {
            Plantillas   = plantillas,
            Asignaciones = [],   // se muestra en el perfil del empleado
        };

        ViewData["Title"] = "Horarios y turnos";
        ViewData["BreadcrumbCurrent"] = "Horarios";
        return View(vm);
    }

    // GET /Turno/CrearPlantilla
    [HttpGet]
    public IActionResult CrearPlantilla()
    {
        // Inicializar con 7 días vacíos
        var dto = new CrearPlantillaTurnoDto
        {
            Detalles = Enumerable.Range(1, 7)
                .Select(d => new CrearPlantillaTurnoDetalleDto { DiaSemana = (byte)d })
                .ToList()
        };

        var vm = new CrearPlantillaViewModel { Dto = dto };
        ViewData["Title"] = "Nueva plantilla de turno";
        ViewData["BreadcrumbParent"] = "Horarios";
        ViewData["BreadcrumbParentUrl"] = Url.Action("Index")!;
        ViewData["BreadcrumbCurrent"] = "Nueva plantilla";
        return View(vm);
    }

    // POST /Turno/CrearPlantilla
    [HttpPost]
    [ValidateAntiForgeryToken]
    public async Task<IActionResult> CrearPlantilla(CrearPlantillaViewModel vm)
    {
        if (!ModelState.IsValid)
            return View(vm);

        var usuarioId = SesionHelper.GetUsuarioId(User);
        var resultado = await _turnoService.CrearPlantillaAsync(vm.Dto);

        if (!resultado.Exito)
        {
            ModelState.AddModelError(string.Empty, resultado.Mensaje ?? "No se pudo crear la plantilla.");
            return View(vm);
        }

        TempData["Exito"] = "Plantilla de turno creada correctamente.";
        return RedirectToAction("Index");
    }

    // GET /Turno/AsignarTurno?empleadoId=
    [HttpGet]
    public async Task<IActionResult> AsignarTurno(int empleadoId)
    {
        var plantillas = await _turnoService.ObtenerPlantillasActivasAsync();
        var empResult  = await _empleadoService.ObtenerPerfilAsync(empleadoId);

        var vm = new AsignarTurnoViewModel
        {
            Dto = new() { EmpleadoId = empleadoId, FechaVigencia = DateOnly.FromDateTime(DateTime.Today) },
            Plantillas = plantillas,
            Empleado   = empResult.Exito ? empResult.Datos : null,
        };

        ViewData["Title"] = "Asignar turno";
        ViewData["BreadcrumbParent"] = empResult.Datos?.NombreCompleto ?? "Empleado";
        ViewData["BreadcrumbParentUrl"] = Url.Action("Perfil", "Empleado", new { id = empleadoId, tab = "horario" })!;
        ViewData["BreadcrumbCurrent"] = "Asignar turno";
        return View(vm);
    }

    // POST /Turno/AsignarTurno
    [HttpPost]
    [ValidateAntiForgeryToken]
    public async Task<IActionResult> AsignarTurno(AsignarTurnoViewModel vm)
    {
        if (!ModelState.IsValid)
        {
            var plantillasRecarga = await _turnoService.ObtenerPlantillasActivasAsync();
            var empR = await _empleadoService.ObtenerPerfilAsync(vm.Dto.EmpleadoId);
            var vmRecarga = new AsignarTurnoViewModel
            {
                Dto        = vm.Dto,
                Plantillas = plantillasRecarga,
                Empleado   = empR.Exito ? empR.Datos : null,
            };
            return View(vmRecarga);
        }

        var usuarioId = SesionHelper.GetUsuarioId(User);
        var resultado = await _turnoService.AsignarTurnoAsync(vm.Dto, usuarioId);

        if (!resultado.Exito)
        {
            ModelState.AddModelError(string.Empty, resultado.Mensaje ?? "No se pudo asignar el turno.");
            var plantillasRecarga = await _turnoService.ObtenerPlantillasActivasAsync();
            var empR = await _empleadoService.ObtenerPerfilAsync(vm.Dto.EmpleadoId);
            var vmRecarga = new AsignarTurnoViewModel
            {
                Dto        = vm.Dto,
                Plantillas = plantillasRecarga,
                Empleado   = empR.Exito ? empR.Datos : null,
            };
            return View(vmRecarga);
        }

        TempData["Exito"] = "Turno asignado correctamente.";
        return RedirectToAction("Perfil", "Empleado", new { id = vm.Dto.EmpleadoId, tab = "horario" });
    }
}
