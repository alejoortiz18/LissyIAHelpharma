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

    // GET /HoraExtra?buscar=&fecha=&estado=&pagina=1
    [HttpGet]
    public async Task<IActionResult> Index(string? buscar, string? fecha, string? estado, int pagina = 1)
    {
        const int tam   = 15;
        var rol         = SesionHelper.GetRol(User);
        var sedeId      = SesionHelper.GetSedeId(User);
        var empId       = SesionHelper.GetEmpleadoId(User);

        var todos = rol == RolUsuario.Operario && empId.HasValue
            ? await _horaExtraService.ObtenerPorEmpleadoAsync(empId.Value)
            : await _horaExtraService.ObtenerPorSedeAsync(sedeId);

        var q = todos.AsEnumerable();
        if (!string.IsNullOrWhiteSpace(buscar))
        {
            var b = buscar.Trim().ToLower();
            q = q.Where(h => h.EmpleadoNombre.ToLower().Contains(b));
        }
        if (!string.IsNullOrEmpty(fecha))
            q = q.Where(h => h.FechaTrabajada.StartsWith(fecha));
        if (!string.IsNullOrEmpty(estado))
            q = q.Where(h => h.Estado.Equals(estado, StringComparison.OrdinalIgnoreCase));

        var lista   = q.ToList();
        var total   = lista.Count;
        var paginas = (int)Math.Ceiling(total / (double)tam);
        pagina      = Math.Clamp(pagina, 1, Math.Max(1, paginas));
        var paginado = lista.Skip((pagina - 1) * tam).Take(tam).ToList();

        var pendientes       = todos.Count(h => h.Estado == "Pendiente");
        var aprobadasEsteMes = todos.Count(h => h.Estado == "Aprobado" &&
            h.FechaAprobacion != null &&
            DateTime.TryParse(h.FechaAprobacion, out var fa) &&
            fa.Month == DateTime.Today.Month && fa.Year == DateTime.Today.Year);
        var totalHoras = todos.Where(h => h.Estado == "Aprobado").Sum(h => h.CantidadHoras);

        var vm = new HorasExtrasViewModel
        {
            HorasExtras          = paginado,
            Pendientes           = pendientes,
            AprobadasEsteMes     = aprobadasEsteMes,
            TotalHorasAprobadas  = totalHoras,
            Buscar               = buscar,
            Fecha                = fecha,
            Estado               = estado,
            Pagina               = pagina,
            TotalPaginas         = paginas,
            TotalRegistros       = total,
        };

        ViewData["Title"] = "Horas extras";
        ViewData["BreadcrumbCurrent"] = "Horas extras";
        return View(vm);
    }

    // GET /HoraExtra/Crear
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

    // POST /HoraExtra/Registrar
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

    // POST /HoraExtra/Aprobar
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

    // POST /HoraExtra/Rechazar
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

    // POST /HoraExtra/Anular
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
