using GestionPersonal.Application.Interfaces;

using GestionPersonal.Constants;

using GestionPersonal.Models.Enums;

using GestionPersonal.Web.Authorization;

using GestionPersonal.Web.Helpers;

using GestionPersonal.Web.ViewModels.HoraExtra;

using Microsoft.AspNetCore.Authorization;

using Microsoft.AspNetCore.Mvc;



namespace GestionPersonal.Web.Controllers;



[Authorize]

[RequierePermiso(PermisosCodigo.HorasExtrasVer)]

public class HoraExtraController : Controller

{

    private readonly IHoraExtraService _horaExtraService;

    private readonly IEmpleadoService  _empleadoService;

    private readonly IEventoLaboralService _eventoLaboralService;



    public HoraExtraController(
        IHoraExtraService horaExtraService,
        IEmpleadoService empleadoService,
        IEventoLaboralService eventoLaboralService)

    {

        _horaExtraService   = horaExtraService;

        _empleadoService    = empleadoService;

        _eventoLaboralService = eventoLaboralService;

    }



    // GET /HoraExtra

    [HttpGet]

    public async Task<IActionResult> Index()

    {

        var puedeCrear   = PermisoHelper.TienePermiso(User, PermisosCodigo.HorasExtrasCrear);

        var puedeAprobar = PermisoHelper.TienePermiso(User, PermisosCodigo.HorasExtrasAprobar);

        var sedeId       = SesionHelper.GetSedeId(User);

        var empId        = SesionHelper.GetEmpleadoId(User);

        var rol          = SesionHelper.GetRol(User);



        IReadOnlyList<GestionPersonal.Models.DTOs.HoraExtra.HoraExtraDto> todos;

        if (!puedeAprobar && empId.HasValue)

            todos = await _horaExtraService.ObtenerPorEmpleadoAsync(empId.Value);

        else if (rol == RolUsuario.Analista)

            todos = await _horaExtraService.ObtenerTodosAsync();

        else if (rol == RolUsuario.DirectorTecnico && empId.HasValue)

        {

            var descendientes = await _eventoLaboralService.ObtenerDescendientesAsync(empId.Value);

            var todas = await _horaExtraService.ObtenerTodosAsync();

            todos = todas

                .Where(h => h.EmpleadoId == empId.Value || descendientes.Contains(h.EmpleadoId))

                .ToList();

        }

        else

        {

            todos = await _horaExtraService.ObtenerPorSedeAsync(sedeId);

            if (empId.HasValue &&

                (rol == RolUsuario.Regente || rol == RolUsuario.AuxiliarRegente))

            {

                var descendientes = await _eventoLaboralService.ObtenerDescendientesAsync(empId.Value);

                todos = todos

                    .Where(h => h.EmpleadoId == empId.Value || descendientes.Contains(h.EmpleadoId))

                    .ToList();

            }

        }



        var pendientes       = todos.Count(h => h.Estado == "Pendiente");

        var aprobadasEsteMes = todos.Count(h => h.Estado == "Aprobado" &&

            h.FechaAprobacion != null &&

            DateTime.TryParse(h.FechaAprobacion, out var fa) &&

            fa.Month == DateTime.Today.Month && fa.Year == DateTime.Today.Year);

        var totalHoras = todos.Where(h => h.Estado == "Aprobado").Sum(h => h.CantidadHoras);



        IReadOnlyList<GestionPersonal.Models.DTOs.Empleado.EmpleadoListaDto> empleados = [];
        if (puedeCrear && puedeAprobar)
            empleados = await _empleadoService.ObtenerTodosAsync();
        else if (puedeCrear && !puedeAprobar && empId.HasValue
                 && (rol == RolUsuario.Regente || rol == RolUsuario.AuxiliarRegente))
        {
            var porSede = await _empleadoService.ObtenerPorSedeAsync(sedeId);
            var descendientes = await _eventoLaboralService.ObtenerDescendientesAsync(empId.Value);
            empleados = porSede
                .Where(e => e.Id == empId.Value || descendientes.Contains(e.Id))
                .ToList();
        }
        else if (puedeCrear && puedeAprobar == false
                 && rol is RolUsuario.DirectorTecnico or RolUsuario.Administrador or RolUsuario.Analista)
            empleados = await _empleadoService.ObtenerTodosAsync();



        var vm = new HorasExtrasViewModel

        {

            HorasExtras         = todos,

            Pendientes          = pendientes,

            AprobadasEsteMes    = aprobadasEsteMes,

            TotalHorasAprobadas = totalHoras,

            TotalRegistros      = todos.Count,

            Empleados           = empleados,

            PuedeCrear          = puedeCrear,

            PuedeAprobar        = puedeAprobar,

            CrearSoloPropias    = puedeCrear && !puedeAprobar,

            EmpleadoIdSesion    = empId,

        };



        ViewData["Title"] = "Horas extras";

        ViewData["BreadcrumbCurrent"] = "Horas extras";

        return View(vm);

    }



    // POST /HoraExtra/RegistrarAjax

    [HttpPost]

    [ValidateAntiForgeryToken]

    [RequierePermiso(PermisosCodigo.HorasExtrasCrear)]

    public async Task<IActionResult> RegistrarAjax([FromForm] GestionPersonal.Models.DTOs.HoraExtra.CrearHoraExtraDto dto)

    {

        if (!ModelState.IsValid)

            return Json(new { exito = false, mensaje = "Datos inválidos. Revisa los campos obligatorios." });



        if (!PermisoHelper.TienePermiso(User, PermisosCodigo.HorasExtrasAprobar))

        {

            var empId = SesionHelper.GetEmpleadoId(User);

            if (!empId.HasValue)

                return Json(new { exito = false, mensaje = "Tu usuario no tiene empleado vinculado." });

            dto.EmpleadoId = empId.Value;

        }



        var usuarioId = SesionHelper.GetUsuarioId(User);

        var resultado = await _horaExtraService.CrearAsync(dto, usuarioId);

        return Json(new { exito = resultado.Exito, mensaje = resultado.Mensaje });

    }



    // POST /HoraExtra/AprobarAjax

    [HttpPost]

    [ValidateAntiForgeryToken]

    [RequierePermiso(PermisosCodigo.HorasExtrasAprobar)]

    public async Task<IActionResult> AprobarAjax([FromForm] int id)

    {

        var rol   = SesionHelper.GetRol(User);

        var empId = SesionHelper.GetEmpleadoId(User);



        var errorJerarquia = await ValidarGestionJerarquiaAsync(id, rol, empId);

        if (errorJerarquia is not null)

            return Json(new { exito = false, mensaje = errorJerarquia });



        var usuarioId = SesionHelper.GetUsuarioId(User);

        var resultado = await _horaExtraService.AprobarAsync(id, usuarioId);

        return Json(new { exito = resultado.Exito, mensaje = resultado.Mensaje });

    }



    // POST /HoraExtra/RechazarAjax

    [HttpPost]

    [ValidateAntiForgeryToken]

    [RequierePermiso(PermisosCodigo.HorasExtrasAprobar)]

    public async Task<IActionResult> RechazarAjax([FromForm] int id, [FromForm] string motivoRechazo)

    {

        if (string.IsNullOrWhiteSpace(motivoRechazo))

            return Json(new { exito = false, mensaje = "El motivo de rechazo es obligatorio." });



        var rol   = SesionHelper.GetRol(User);

        var empId = SesionHelper.GetEmpleadoId(User);



        var errorJerarquia = await ValidarGestionJerarquiaAsync(id, rol, empId);

        if (errorJerarquia is not null)

            return Json(new { exito = false, mensaje = errorJerarquia });



        var usuarioId = SesionHelper.GetUsuarioId(User);

        var resultado = await _horaExtraService.RechazarAsync(id, motivoRechazo, usuarioId);

        return Json(new { exito = resultado.Exito, mensaje = resultado.Mensaje });

    }



    // POST /HoraExtra/AnularAjax

    [HttpPost]

    [ValidateAntiForgeryToken]

    [RequierePermiso(PermisosCodigo.HorasExtrasAprobar)]

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

    [RequierePermiso(PermisosCodigo.HorasExtrasCrear)]

    public async Task<IActionResult> Crear()

    {

        var empleados = PermisoHelper.TienePermiso(User, PermisosCodigo.HorasExtrasAprobar)

            ? await _empleadoService.ObtenerTodosAsync()

            : [];

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

    [RequierePermiso(PermisosCodigo.HorasExtrasCrear)]

    public async Task<IActionResult> Registrar(CrearHoraExtraViewModel vm)

    {

        if (!PermisoHelper.TienePermiso(User, PermisosCodigo.HorasExtrasAprobar))

        {

            var empId = SesionHelper.GetEmpleadoId(User);

            if (empId.HasValue)

                vm.Dto.EmpleadoId = empId.Value;

        }



        if (!ModelState.IsValid)

        {

            var empleadosRecarga = PermisoHelper.TienePermiso(User, PermisosCodigo.HorasExtrasAprobar)

                ? await _empleadoService.ObtenerTodosAsync()

                : [];

            return View("Crear", new CrearHoraExtraViewModel { Dto = vm.Dto, Empleados = empleadosRecarga });

        }



        var usuarioId = SesionHelper.GetUsuarioId(User);

        var resultado = await _horaExtraService.CrearAsync(vm.Dto, usuarioId);



        if (!resultado.Exito)

        {

            ModelState.AddModelError(string.Empty, resultado.Mensaje ?? "No se pudo registrar la solicitud.");

            var empleadosRecarga2 = PermisoHelper.TienePermiso(User, PermisosCodigo.HorasExtrasAprobar)

                ? await _empleadoService.ObtenerTodosAsync()

                : [];

            return View("Crear", new CrearHoraExtraViewModel { Dto = vm.Dto, Empleados = empleadosRecarga2 });

        }



        TempData["Exito"] = "Solicitud de hora extra registrada correctamente.";

        return RedirectToAction("Index");

    }



    [HttpPost]

    [ValidateAntiForgeryToken]

    [RequierePermiso(PermisosCodigo.HorasExtrasAprobar)]

    public async Task<IActionResult> Aprobar(int id)

    {

        var usuarioId = SesionHelper.GetUsuarioId(User);

        var resultado = await _horaExtraService.AprobarAsync(id, usuarioId);

        TempData[resultado.Exito ? "Exito" : "Error"] =

            resultado.Exito ? "Hora extra aprobada." : resultado.Mensaje;

        return RedirectToAction("Index");

    }



    [HttpPost]

    [ValidateAntiForgeryToken]

    [RequierePermiso(PermisosCodigo.HorasExtrasAprobar)]

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



    [HttpPost]

    [ValidateAntiForgeryToken]

    [RequierePermiso(PermisosCodigo.HorasExtrasAprobar)]

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



    /// <summary>
    /// Regente/Auxiliar solo gestionan horas extra de su árbol jerárquico descendente.
    /// Analista y Director técnico sin restricción adicional aquí.
    /// </summary>
    private async Task<string?> ValidarGestionJerarquiaAsync(int horaExtraId, RolUsuario rol, int? empId)
    {
        if (rol != RolUsuario.Regente && rol != RolUsuario.AuxiliarRegente)
            return null;

        if (!empId.HasValue)
            return "Sin permisos.";

        var sedeId = SesionHelper.GetSedeId(User);
        var lista  = await _horaExtraService.ObtenerPorSedeAsync(sedeId);
        var he     = lista.FirstOrDefault(h => h.Id == horaExtraId);
        if (he is null)
            return "Hora extra no encontrada.";

        var descendientes = await _eventoLaboralService.ObtenerDescendientesAsync(empId.Value);
        if (!descendientes.Contains(he.EmpleadoId))
            return "Solo puedes gestionar horas extra de tu línea jerárquica.";

        return null;
    }

}

