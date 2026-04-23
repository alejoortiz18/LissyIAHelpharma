using GestionPersonal.Application.Interfaces;
using GestionPersonal.Models.Enums;
using GestionPersonal.Web.Helpers;
using GestionPersonal.Web.ViewModels.HoraExtra;
using Microsoft.AspNetCore.Authorization;
using Microsoft.AspNetCore.Mvc;

namespace GestionPersonal.Web.Controllers;

[Authorize]
public class HoraExtraController : Controller
{
    private readonly IHoraExtraService _horaExtraService;
    private readonly IEmpleadoService  _empleadoService;

    public HoraExtraController(IHoraExtraService horaExtraService, IEmpleadoService empleadoService)
    {
        _horaExtraService = horaExtraService;
        _empleadoService  = empleadoService;
    }

    // GET /HoraExtra
    [HttpGet]
    public async Task<IActionResult> Index()
    {
        var rol    = SesionHelper.GetRol(User);
        var sedeId = SesionHelper.GetSedeId(User);
        var empId  = SesionHelper.GetEmpleadoId(User);

        var todos = rol == RolUsuario.Operario && empId.HasValue
            ? await _horaExtraService.ObtenerPorEmpleadoAsync(empId.Value)
            : await _horaExtraService.ObtenerPorSedeAsync(sedeId);

        if ((rol == RolUsuario.Regente || rol == RolUsuario.AuxiliarRegente) && empId.HasValue)
            todos = todos.Where(h => h.EmpleadoId == empId.Value || h.JefeInmediatoId == empId.Value).ToList();

        var pendientes       = todos.Count(h => h.Estado == "Pendiente");
        var aprobadasEsteMes = todos.Count(h => h.Estado == "Aprobado" &&
            h.FechaAprobacion != null &&
            DateTime.TryParse(h.FechaAprobacion, out var fa) &&
            fa.Month == DateTime.Today.Month && fa.Year == DateTime.Today.Year);
        var totalHoras = todos.Where(h => h.Estado == "Aprobado").Sum(h => h.CantidadHoras);

        var empleados = rol != RolUsuario.Operario
            ? await _empleadoService.ObtenerTodosAsync()
            : [];

        var vm = new HorasExtrasViewModel
        {
            HorasExtras         = todos,
            Pendientes          = pendientes,
            AprobadasEsteMes    = aprobadasEsteMes,
            TotalHorasAprobadas = totalHoras,
            TotalRegistros      = todos.Count,
            Empleados           = empleados,
        };

        ViewData["Title"] = "Horas extras";
        ViewData["BreadcrumbCurrent"] = "Horas extras";
        return View(vm);
    }

    // POST /HoraExtra/RegistrarAjax
    [HttpPost]
    [ValidateAntiForgeryToken]
    public async Task<IActionResult> RegistrarAjax([FromForm] GestionPersonal.Models.DTOs.HoraExtra.CrearHoraExtraDto dto)
    {
        if (!ModelState.IsValid)
            return Json(new { exito = false, mensaje = "Datos inválidos. Revisa los campos obligatorios." });

        var usuarioId = SesionHelper.GetUsuarioId(User);
        var resultado = await _horaExtraService.CrearAsync(dto, usuarioId);
        return Json(new { exito = resultado.Exito, mensaje = resultado.Mensaje });
    }

    // POST /HoraExtra/AprobarAjax
    [HttpPost]
    [ValidateAntiForgeryToken]
    public async Task<IActionResult> AprobarAjax([FromForm] int id)
    {
        var rol   = SesionHelper.GetRol(User);
        var empId = SesionHelper.GetEmpleadoId(User);

        if (rol == RolUsuario.Operario)
            return Json(new { exito = false, mensaje = "Sin permisos." });

        if (rol == RolUsuario.Regente || rol == RolUsuario.AuxiliarRegente)
        {
            if (!empId.HasValue) return Json(new { exito = false, mensaje = "Sin permisos." });
            var sedeId = SesionHelper.GetSedeId(User);
            var lista  = await _horaExtraService.ObtenerPorSedeAsync(sedeId);
            var he     = lista.FirstOrDefault(h => h.Id == id);
            if (he is null || he.JefeInmediatoId != empId.Value)
                return Json(new { exito = false, mensaje = "No tienes permisos para gestionar esta hora extra." });
        }

        var usuarioId = SesionHelper.GetUsuarioId(User);
        var resultado = await _horaExtraService.AprobarAsync(id, usuarioId);
        return Json(new { exito = resultado.Exito, mensaje = resultado.Mensaje });
    }

    // POST /HoraExtra/RechazarAjax
    [HttpPost]
    [ValidateAntiForgeryToken]
    public async Task<IActionResult> RechazarAjax([FromForm] int id, [FromForm] string motivoRechazo)
    {
        if (string.IsNullOrWhiteSpace(motivoRechazo))
            return Json(new { exito = false, mensaje = "El motivo de rechazo es obligatorio." });

        var rol   = SesionHelper.GetRol(User);
        var empId = SesionHelper.GetEmpleadoId(User);

        if (rol == RolUsuario.Operario)
            return Json(new { exito = false, mensaje = "Sin permisos." });

        if (rol == RolUsuario.Regente || rol == RolUsuario.AuxiliarRegente)
        {
            if (!empId.HasValue) return Json(new { exito = false, mensaje = "Sin permisos." });
            var sedeId = SesionHelper.GetSedeId(User);
            var lista  = await _horaExtraService.ObtenerPorSedeAsync(sedeId);
            var he     = lista.FirstOrDefault(h => h.Id == id);
            if (he is null || he.JefeInmediatoId != empId.Value)
                return Json(new { exito = false, mensaje = "No tienes permisos para gestionar esta hora extra." });
        }

        var usuarioId = SesionHelper.GetUsuarioId(User);
        var resultado = await _horaExtraService.RechazarAsync(id, motivoRechazo, usuarioId);
        return Json(new { exito = resultado.Exito, mensaje = resultado.Mensaje });
    }

    // POST /HoraExtra/AnularAjax
    [HttpPost]
    [ValidateAntiForgeryToken]
    public async Task<IActionResult> AnularAjax([FromForm] int id, [FromForm] string motivoAnulacion)
    {
        if (string.IsNullOrWhiteSpace(motivoAnulacion))
            return Json(new { exito = false, mensaje = "El motivo de anulación es obligatorio." });

        var usuarioId = SesionHelper.GetUsuarioId(User);
        var resultado = await _horaExtraService.AnularAsync(id, motivoAnulacion, usuarioId);
        return Json(new { exito = resultado.Exito, mensaje = resultado.Mensaje });
    }

    // GET /HoraExtra/Crear  (kept for backwards compatibility)
    [HttpGet]
    public async Task<IActionResult> Crear()
    {
        var empleados = await _empleadoService.ObtenerTodosAsync();
        var vm = new CrearHoraExtraViewModel
        {
            Dto       = new(),
            Empleados = empleados,
        };
        ViewData["Title"] = "Nueva solicitud de hora extra";
        ViewData["BreadcrumbParent"] = "Horas extras";
        ViewData["BreadcrumbParentUrl"] = Url.Action("Index")!;
        ViewData["BreadcrumbCurrent"] = "Nueva solicitud";
        return View(vm);
    }

    // POST /HoraExtra/Registrar  (kept for backwards compatibility)
    [HttpPost]
    [ValidateAntiForgeryToken]
    public async Task<IActionResult> Registrar(CrearHoraExtraViewModel vm)
    {
        if (!ModelState.IsValid)
        {
            var empleadosRecarga = await _empleadoService.ObtenerTodosAsync();
            return View("Crear", new CrearHoraExtraViewModel { Dto = vm.Dto, Empleados = empleadosRecarga });
        }

        var usuarioId = SesionHelper.GetUsuarioId(User);
        var resultado = await _horaExtraService.CrearAsync(vm.Dto, usuarioId);

        if (!resultado.Exito)
        {
            ModelState.AddModelError(string.Empty, resultado.Mensaje ?? "No se pudo registrar la solicitud.");
            var empleadosRecarga2 = await _empleadoService.ObtenerTodosAsync();
            return View("Crear", new CrearHoraExtraViewModel { Dto = vm.Dto, Empleados = empleadosRecarga2 });
        }

        TempData["Exito"] = "Solicitud de hora extra registrada correctamente.";
        return RedirectToAction("Index");
    }

    // POST /HoraExtra/Aprobar  (kept for backwards compatibility)
    [HttpPost]
    [ValidateAntiForgeryToken]
    public async Task<IActionResult> Aprobar(int id)
    {
        var usuarioId = SesionHelper.GetUsuarioId(User);
        var resultado = await _horaExtraService.AprobarAsync(id, usuarioId);
        TempData[resultado.Exito ? "Exito" : "Error"] =
            resultado.Exito ? "Hora extra aprobada." : resultado.Mensaje;
        return RedirectToAction("Index");
    }

    // POST /HoraExtra/Rechazar  (kept for backwards compatibility)
    [HttpPost]
    [ValidateAntiForgeryToken]
    public async Task<IActionResult> Rechazar(int id, string motivoRechazo)
    {
        if (string.IsNullOrWhiteSpace(motivoRechazo))
        {
            TempData["Error"] = "Debe indicar el motivo de rechazo.";
            return RedirectToAction("Index");
        }

        var usuarioId = SesionHelper.GetUsuarioId(User);
        var resultado = await _horaExtraService.RechazarAsync(id, motivoRechazo, usuarioId);
        TempData[resultado.Exito ? "Exito" : "Error"] =
            resultado.Exito ? "Hora extra rechazada." : resultado.Mensaje;
        return RedirectToAction("Index");
    }

    // POST /HoraExtra/Anular  (kept for backwards compatibility)
    [HttpPost]
    [ValidateAntiForgeryToken]
    public async Task<IActionResult> Anular(int id, string motivoAnulacion)
    {
        if (string.IsNullOrWhiteSpace(motivoAnulacion))
        {
            TempData["Error"] = "Debe indicar el motivo de anulación.";
            return RedirectToAction("Index");
        }

        var usuarioId = SesionHelper.GetUsuarioId(User);
        var resultado = await _horaExtraService.AnularAsync(id, motivoAnulacion, usuarioId);
        TempData[resultado.Exito ? "Exito" : "Error"] =
            resultado.Exito ? "Hora extra anulada." : resultado.Mensaje;
        return RedirectToAction("Index");
    }
}
