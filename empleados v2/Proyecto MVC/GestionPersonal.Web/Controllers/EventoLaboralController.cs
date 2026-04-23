using GestionPersonal.Application.Interfaces;
using GestionPersonal.Models.DTOs.EventoLaboral;
using GestionPersonal.Models.Enums;
using GestionPersonal.Web.Helpers;
using GestionPersonal.Web.ViewModels.EventoLaboral;
using Microsoft.AspNetCore.Authorization;
using Microsoft.AspNetCore.Mvc;

namespace GestionPersonal.Web.Controllers;

[Authorize]
public class EventoLaboralController : Controller
{
    private readonly IEventoLaboralService _eventoService;
    private readonly IEmpleadoService      _empleadoService;

    public EventoLaboralController(
        IEventoLaboralService eventoService,
        IEmpleadoService      empleadoService)
    {
        _eventoService   = eventoService;
        _empleadoService = empleadoService;
    }

    // GET /EventoLaboral?buscar=&tipo=&estado=&desde=&hasta=
    [HttpGet]
    public async Task<IActionResult> Index(
        string? buscar, string? tipo, string? estado,
        string? desde, string? hasta, int pagina = 1)
    {
        const int tam = 15;
        var rol    = SesionHelper.GetRol(User);
        var sedeId = SesionHelper.GetSedeId(User);

        // Sequential awaits — EF Core DbContext is not thread-safe; Task.WhenAll is not allowed
        var todos = await _eventoService.ObtenerPorSedeAsync(sedeId);
        var empleadosList = rol == RolUsuario.Jefe || rol == RolUsuario.Administrador
            ? await _empleadoService.ObtenerTodosAsync()
            : await _empleadoService.ObtenerPorSedeAsync(sedeId);

        var q = todos.AsEnumerable();
        if (!string.IsNullOrWhiteSpace(buscar))
        {
            var b = buscar.Trim().ToLower();
            q = q.Where(e => e.EmpleadoNombre.ToLower().Contains(b));
        }
        if (!string.IsNullOrEmpty(tipo))
            q = q.Where(e => e.TipoEvento.Equals(tipo, StringComparison.OrdinalIgnoreCase));
        if (!string.IsNullOrEmpty(estado))
            q = q.Where(e => e.Estado.Equals(estado, StringComparison.OrdinalIgnoreCase));
        if (!string.IsNullOrEmpty(desde) && DateOnly.TryParse(desde, out var d))
            q = q.Where(e => DateOnly.TryParse(e.FechaInicio, out var fi) && fi >= d);
        if (!string.IsNullOrEmpty(hasta) && DateOnly.TryParse(hasta, out var h))
            q = q.Where(e => DateOnly.TryParse(e.FechaFin, out var ff) && ff <= h);

        var lista   = q.ToList();
        var total   = lista.Count;
        var paginas = (int)Math.Ceiling(total / (double)tam);
        pagina      = Math.Clamp(pagina, 1, Math.Max(1, paginas));
        var paginado = lista.Skip((pagina - 1) * tam).Take(tam).ToList();

        var vm = new EventosViewModel
        {
            Eventos        = paginado,
            Empleados      = empleadosList.Where(e => e.Estado == "Activo").ToList(),
            Buscar         = buscar,
            Tipo           = tipo,
            Estado         = estado,
            Desde          = desde,
            Hasta          = hasta,
            Pagina         = pagina,
            TotalPaginas   = paginas,
            TotalRegistros = total,
        };

        ViewData["Title"] = "Eventos laborales";
        ViewData["BreadcrumbCurrent"] = "Eventos laborales";
        return View(vm);
    }

    // GET /EventoLaboral/SaldoVacaciones?empleadoId=
    [HttpGet]
    public async Task<IActionResult> SaldoVacaciones(int empleadoId)
    {
        var saldo = await _eventoService.ObtenerSaldoVacacionesAsync(empleadoId);
        if (saldo is null) return NotFound();
        return Json(saldo);
    }

    // POST /EventoLaboral/RegistrarAjax  (called by modal)
    [HttpPost]
    [ValidateAntiForgeryToken]
    public async Task<IActionResult> RegistrarAjax([FromForm] CrearEventoLaboralDto dto)
    {
        if (!ModelState.IsValid)
        {
            var errores = ModelState.Values
                .SelectMany(v => v.Errors)
                .Select(e => e.ErrorMessage)
                .ToList();
            return Json(new { exito = false, mensaje = string.Join(" ", errores) });
        }

        var usuarioId = SesionHelper.GetUsuarioId(User);
        var resultado = await _eventoService.CrearAsync(dto, usuarioId);

        return Json(new { exito = resultado.Exito, mensaje = resultado.Mensaje });
    }

    // POST /EventoLaboral/AnularAjax  (called by anular modal)
    [HttpPost]
    [ValidateAntiForgeryToken]
    public async Task<IActionResult> AnularAjax([FromForm] int id, [FromForm] string motivoAnulacion)
    {
        if (string.IsNullOrWhiteSpace(motivoAnulacion))
            return Json(new { exito = false, mensaje = "El motivo de anulación es obligatorio." });

        var usuarioId = SesionHelper.GetUsuarioId(User);
        var resultado = await _eventoService.AnularAsync(id, motivoAnulacion, usuarioId);

        return Json(new { exito = resultado.Exito, mensaje = resultado.Mensaje });
    }

    // GET /EventoLaboral/Crear?empleadoId=   (kept for use from employee profile)
    [HttpGet]
    public async Task<IActionResult> Crear(int? empleadoId)
    {
        var empleados = await _empleadoService.ObtenerTodosAsync();
        var vm = new CrearEventoViewModel
        {
            Dto                  = new() { EmpleadoId = empleadoId ?? 0 },
            Empleados            = empleados,
            EmpleadoPreSeleccionado = empleadoId,
        };
        ViewData["Title"] = "Registrar evento laboral";
        ViewData["BreadcrumbParent"] = "Eventos laborales";
        ViewData["BreadcrumbParentUrl"] = Url.Action("Index")!;
        ViewData["BreadcrumbCurrent"] = "Registrar evento";
        return View(vm);
    }

    // POST /EventoLaboral/Registrar  (kept for Crear.cshtml form submit)
    [HttpPost]
    [ValidateAntiForgeryToken]
    public async Task<IActionResult> Registrar(CrearEventoViewModel vm)
    {
        if (!ModelState.IsValid)
        {
            var empleadosRecarga = await _empleadoService.ObtenerTodosAsync();
            var vmRecarga = new CrearEventoViewModel
            {
                Dto                     = vm.Dto,
                Empleados               = empleadosRecarga,
                EmpleadoPreSeleccionado = vm.EmpleadoPreSeleccionado,
            };
            return View("Crear", vmRecarga);
        }

        var usuarioId = SesionHelper.GetUsuarioId(User);
        var resultado = await _eventoService.CrearAsync(vm.Dto, usuarioId);

        if (!resultado.Exito)
        {
            var empleadosRecarga2 = await _empleadoService.ObtenerTodosAsync();
            var vmRecarga2 = new CrearEventoViewModel
            {
                Dto                     = vm.Dto,
                Empleados               = empleadosRecarga2,
                EmpleadoPreSeleccionado = vm.EmpleadoPreSeleccionado,
            };
            ModelState.AddModelError(string.Empty, resultado.Mensaje ?? "No se pudo registrar el evento.");
            return View("Crear", vmRecarga2);
        }

        TempData["Exito"] = "Evento registrado correctamente.";
        return RedirectToAction("Index");
    }

    // POST /EventoLaboral/Anular
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
        var resultado = await _eventoService.AnularAsync(id, motivoAnulacion, usuarioId);

        TempData[resultado.Exito ? "Exito" : "Error"] =
            resultado.Exito ? "Evento anulado correctamente." : resultado.Mensaje;

        return RedirectToAction("Index");
    }
}
