using AutoMapper;
using GestionPersonal.Application.Interfaces;
using GestionPersonal.Models.DTOs.Empleado;
using GestionPersonal.Models.DTOs.EventoLaboral;
using GestionPersonal.Models.DTOs.HoraExtra;
using GestionPersonal.Models.DTOs.Turno;
using GestionPersonal.Models.Entities.GestionPersonalEntities;
using GestionPersonal.Models.Enums;
using GestionPersonal.Web.Helpers;
using GestionPersonal.Web.ViewModels.Empleado;
using GestionPersonal.Web.ViewModels.Turno;
using Microsoft.AspNetCore.Authorization;
using Microsoft.AspNetCore.Mvc;

namespace GestionPersonal.Web.Controllers;

[Authorize]
public class EmpleadoController : Controller
{
    private readonly IEmpleadoService _empleadoService;
    private readonly ICatalogoService _catalogoService;
    private readonly ITurnoService    _turnoService;
    private readonly IMapper          _mapper;

    public EmpleadoController(
        IEmpleadoService empleadoService,
        ICatalogoService catalogoService,
        ITurnoService    turnoService,
        IMapper          mapper)
    {
        _empleadoService = empleadoService;
        _catalogoService = catalogoService;
        _turnoService    = turnoService;
        _mapper          = mapper;
    }

    // GET /Empleado?buscar=&sedeId=&cargoId=&estado=&tipoVinculacion=&pagina=1
    [HttpGet]
    public async Task<IActionResult> Index(
        string? buscar, int? sedeId, int? cargoId,
        string? estado, string? tipoVinculacion, int pagina = 1)
    {
        const int tamanioPagina = 15;
        var rol    = SesionHelper.GetRol(User);
        var miSede = SesionHelper.GetSedeId(User);

        // Operario y Direccionador solo ven su propio perfil
        if (rol == RolUsuario.Operario || rol == RolUsuario.Direccionador)
        {
            var empId = SesionHelper.GetEmpleadoId(User);
            if (empId.HasValue)
                return RedirectToAction("Perfil", new { id = empId.Value });
            return RedirectToAction("Index", "Dashboard");
        }

        IReadOnlyList<EmpleadoListaDto> todos;
        // Administrador, Analista y DirectorTecnico: acceso total sin filtro de sede
        if (rol == RolUsuario.Administrador || rol == RolUsuario.Analista || rol == RolUsuario.DirectorTecnico)
            todos = await _empleadoService.ObtenerTodosAsync();
        else
            todos = await _empleadoService.ObtenerPorSedeAsync(miSede);

        // Filtros en memoria
        var query = todos.AsEnumerable();

        // Regente / AuxiliarRegente: solo ve a sí mismo + sus subordinados directos
        if (rol == RolUsuario.Regente || rol == RolUsuario.AuxiliarRegente)
        {
            var miEmpleadoId = SesionHelper.GetEmpleadoId(User);
            if (miEmpleadoId.HasValue)
                query = query.Where(e => e.Id == miEmpleadoId.Value || e.JefeInmediatoId == miEmpleadoId.Value);
        }

        if (!string.IsNullOrWhiteSpace(buscar))
        {
            var b = buscar.Trim().ToLower();
            query = query.Where(e =>
                e.NombreCompleto.ToLower().Contains(b) ||
                e.Cedula.Contains(b));
        }
        if (!string.IsNullOrEmpty(estado))
            query = query.Where(e => e.Estado.Equals(estado, StringComparison.OrdinalIgnoreCase));
        if (!string.IsNullOrEmpty(tipoVinculacion))
            query = query.Where(e => e.TipoVinculacion.Equals(tipoVinculacion, StringComparison.OrdinalIgnoreCase));

        var lista    = query.ToList();
        var total    = lista.Count;
        var paginas  = (int)Math.Ceiling(total / (double)tamanioPagina);
        pagina       = Math.Clamp(pagina, 1, Math.Max(1, paginas));
        var paginated = lista.Skip((pagina - 1) * tamanioPagina).Take(tamanioPagina).ToList();

        var sedes  = await _catalogoService.ObtenerSedesActivasAsync();
        var cargos = await _catalogoService.ObtenerCargosActivosAsync();

        var vm = new EmpleadosViewModel
        {
            Empleados      = paginated,
            Sedes          = sedes,
            Cargos         = cargos,
            Buscar         = buscar,
            SedeId         = sedeId,
            CargoId        = cargoId,
            Estado         = estado,
            TipoVinculacion = tipoVinculacion,
            Pagina         = pagina,
            TotalPaginas   = paginas,
            TotalRegistros = total,
            TamanioPagina  = tamanioPagina,
        };

        ViewData["Title"] = "Empleados";
        ViewData["BreadcrumbCurrent"] = "Empleados";
        return View(vm);
    }

    // GET /Empleado/Nuevo
    [HttpGet]
    public async Task<IActionResult> Nuevo()
    {
        var rol = SesionHelper.GetRol(User);
        if (rol == RolUsuario.Operario || rol == RolUsuario.Direccionador
            || rol == RolUsuario.Regente || rol == RolUsuario.AuxiliarRegente)
            return Forbid();

        var vm = await ConstruirNuevoVm(new CrearEmpleadoDto());
        ViewData["Title"] = "Nuevo empleado";
        ViewData["BreadcrumbParent"] = "Empleados";
        ViewData["BreadcrumbParentUrl"] = Url.Action("Index")!;
        ViewData["BreadcrumbCurrent"] = "Nuevo empleado";
        return View(vm);
    }

    // POST /Empleado/Crear
    [HttpPost]
    [ValidateAntiForgeryToken]
    public async Task<IActionResult> Crear(NuevoEmpleadoViewModel vm)
    {
        var rol = SesionHelper.GetRol(User);
        if (rol == RolUsuario.Operario || rol == RolUsuario.Direccionador
            || rol == RolUsuario.Regente || rol == RolUsuario.AuxiliarRegente)
            return Forbid();

        if (!ModelState.IsValid)
        {
            var refreshed = await ConstruirNuevoVm(vm.Dto);
            return View("Nuevo", refreshed);
        }

        var usuarioId = SesionHelper.GetUsuarioId(User);

        vm.Dto.UrlBaseRestablecimiento = Url.Action(
            "RecuperarPassword", "Cuenta", values: null, protocol: Request.Scheme);

        var resultado = await _empleadoService.CrearAsync(vm.Dto, usuarioId);

        if (!resultado.Exito)
        {
            ModelState.AddModelError(string.Empty, resultado.Mensaje ?? "No se pudo crear el empleado.");
            var refreshed = await ConstruirNuevoVm(vm.Dto);
            return View("Nuevo", refreshed);
        }

        TempData["Exito"] = "Empleado registrado correctamente.";
        return RedirectToAction("Index");
    }

    // GET /Empleado/Editar/{id}
    [HttpGet]
    public async Task<IActionResult> Editar(int id)
    {
        var rol = SesionHelper.GetRol(User);
        if (rol == RolUsuario.Operario)
            return Forbid();

        if (rol == RolUsuario.Regente || rol == RolUsuario.AuxiliarRegente)
        {
            var miEmpId = SesionHelper.GetEmpleadoId(User);
            if (!miEmpId.HasValue) return Forbid();
            var objetivo = await _empleadoService.ObtenerPerfilAsync(id);
            if (!objetivo.Exito || objetivo.Datos is null) return NotFound();
            var esPropio      = objetivo.Datos.Id == miEmpId.Value;
            var esSubordinado = objetivo.Datos.JefeInmediatoId == miEmpId.Value;
            if (!esPropio && !esSubordinado)
                return Forbid();
        }

        var resultadoEditar = await _empleadoService.ObtenerParaEditarAsync(id);
        if (!resultadoEditar.Exito || resultadoEditar.Datos is null)
            return NotFound();

        var editarDto = _mapper.Map<EditarEmpleadoDto>(resultadoEditar.Datos);
        var vm = await ConstruirEditarVm(editarDto);
        ViewData["Title"] = "Editar empleado";
        ViewData["BreadcrumbParent"] = "Empleados";
        ViewData["BreadcrumbParentUrl"] = Url.Action("Index")!;
        ViewData["BreadcrumbCurrent"] = "Editar empleado";
        return View(vm);
    }

    // POST /Empleado/Actualizar
    [HttpPost]
    [ValidateAntiForgeryToken]
    public async Task<IActionResult> Actualizar(EditarEmpleadoViewModel vm)
    {
        var rol = SesionHelper.GetRol(User);
        if (rol == RolUsuario.Operario)
            return Forbid();

        if (rol == RolUsuario.Regente || rol == RolUsuario.AuxiliarRegente)
        {
            var miEmpId = SesionHelper.GetEmpleadoId(User);
            if (!miEmpId.HasValue) return Forbid();
            var objetivo = await _empleadoService.ObtenerPerfilAsync(vm.Dto.Id);
            if (!objetivo.Exito || objetivo.Datos is null) return NotFound();
            var esPropio      = objetivo.Datos.Id == miEmpId.Value;
            var esSubordinado = objetivo.Datos.JefeInmediatoId == miEmpId.Value;
            if (!esPropio && !esSubordinado)
                return Forbid();
        }

        if (!ModelState.IsValid)
        {
            var refreshed = await ConstruirEditarVm(vm.Dto);
            return View("Editar", refreshed);
        }

        var usuarioId = SesionHelper.GetUsuarioId(User);
        var resultado = await _empleadoService.EditarAsync(vm.Dto, usuarioId);

        if (!resultado.Exito)
        {
            ModelState.AddModelError(string.Empty, resultado.Mensaje ?? "No se pudo actualizar el empleado.");
            var refreshed = await ConstruirEditarVm(vm.Dto);
            return View("Editar", refreshed);
        }

        TempData["Exito"] = "Empleado actualizado correctamente.";
        return RedirectToAction("Perfil", new { id = vm.Dto.Id });
    }

    // GET /Empleado/Perfil/{id}?tab=datos&desde=2026-01-01&hasta=2026-04-30
    [HttpGet]
    public async Task<IActionResult> Perfil(int id, string tab = "datos",
        DateOnly? desde = null, DateOnly? hasta = null)
    {
        var rol     = SesionHelper.GetRol(User);
        var empId   = SesionHelper.GetEmpleadoId(User);
        var miSede  = SesionHelper.GetSedeId(User);

        // Operario y Direccionador solo pueden ver su propio perfil
        if ((rol == RolUsuario.Operario || rol == RolUsuario.Direccionador) && empId.HasValue && empId.Value != id)
            return Forbid();

        // Regente / AuxiliarRegente: solo puede ver su perfil o el de subordinados
        if (rol == RolUsuario.Regente || rol == RolUsuario.AuxiliarRegente)
        {
            if (!empId.HasValue) return Forbid();
            var objPerfil = await _empleadoService.ObtenerPerfilAsync(id);
            if (!objPerfil.Exito || objPerfil.Datos is null) return NotFound();
            var esPropio      = objPerfil.Datos.Id == empId.Value;
            var esSubordinado = objPerfil.Datos.JefeInmediatoId == empId.Value;
            if (!esPropio && !esSubordinado)
                return Forbid();
        }

        var empleadoResult = await _empleadoService.ObtenerPerfilAsync(id);
        if (!empleadoResult.Exito || empleadoResult.Datos is null)
            return NotFound();
        var empleado = empleadoResult.Datos;

        // El DTO del empleado incluye el nombre del turno actual si existe
        // Para el detalle del turno (detalles por día), buscamos en las plantillas activas
        var todasPlantillas = await _turnoService.ObtenerPlantillasActivasAsync();
        var historialTurnos = await _turnoService.ObtenerHistorialPorEmpleadoAsync(id);

        PlantillaTurnoDto? turnoActual = null;
        var today = DateOnly.FromDateTime(DateTime.Today);
        var vigente = historialTurnos.FirstOrDefault(h =>
            DateOnly.TryParseExact(h.FechaVigencia, "dd/MM/yyyy",
                System.Globalization.CultureInfo.InvariantCulture,
                System.Globalization.DateTimeStyles.None, out var d) && d <= today);
        if (vigente != null)
        {
            var detalle = await _turnoService.ObtenerPlantillaConDetallesAsync(vigente.PlantillaTurnoId);
            if (detalle.Exito)
                turnoActual = detalle.Datos;
        }

        // Eventos con filtro opcional por rango de FechaInicio
        var eventoSvc = HttpContext.RequestServices.GetRequiredService<IEventoLaboralService>();
        var eventos   = await eventoSvc.ObtenerPorEmpleadoConFiltroAsync(id, desde, hasta);

        // Resumen totalizado por tipo (solo eventos no anulados)
        var resumen = eventos
            .Where(ev => ev.Estado != "Anulado")
            .GroupBy(ev => ev.TipoEvento)
            .Select(g => new GestionPersonal.Models.DTOs.EventoLaboral.ResumenEventoDto
            {
                TipoEvento = g.Key,
                TotalDias  = g.Sum(e => e.DiasSolicitados)
            })
            .OrderByDescending(r => r.TotalDias)
            .ToList();

        // Cálculo de vacaciones disponibles basado en FechaInicioContrato × 1.25 por mes
        decimal? vacacionesDisponibles = null;
        if (empleado.FechaInicioContrato is not null &&
            System.DateOnly.TryParseExact(empleado.FechaInicioContrato, "dd/MM/yyyy",
                System.Globalization.CultureInfo.InvariantCulture,
                System.Globalization.DateTimeStyles.None, out var inicioContrato))
        {
            var hoy   = DateOnly.FromDateTime(DateTime.Today);
            var meses = ((hoy.Year - inicioContrato.Year) * 12) + hoy.Month - inicioContrato.Month;
            if (hoy.Day < inicioContrato.Day) meses--;
            if (meses < 0) meses = 0;
            var causadas = meses * 1.25m;

            // Descuenta TODOS los eventos de vacaciones (sin filtro de fecha) con inicio >= FechaInicioContrato
            var todosEventos = desde.HasValue || hasta.HasValue
                ? await eventoSvc.ObtenerPorEmpleadoConFiltroAsync(id, null, null)
                : eventos;
            var disfrutadas = todosEventos
                .Where(ev => ev.TipoEvento == TipoEvento.Vacaciones.ToString() &&
                             ev.Estado     != "Anulado" &&
                             System.DateOnly.TryParseExact(ev.FechaInicio, "dd/MM/yyyy",
                                 System.Globalization.CultureInfo.InvariantCulture,
                                 System.Globalization.DateTimeStyles.None, out var fi) &&
                             fi >= inicioContrato)
                .Sum(ev => ev.DiasSolicitados);

            vacacionesDisponibles = Math.Max(0m, causadas - disfrutadas);
        }

        var horasExtras = await ObtenerHorasExtrasAsync(id);

        var vm = new PerfilEmpleadoViewModel
        {
            Empleado              = empleado,
            Eventos               = eventos,
            HorasExtras           = horasExtras,
            TurnoActual           = turnoActual,
            Plantillas            = todasPlantillas,
            HistorialTurnos       = historialTurnos,
            Tab                   = tab,
            ResumenEventos        = resumen,
            VacacionesDisponibles = vacacionesDisponibles,
            FiltroDesde           = desde?.ToString("yyyy-MM-dd"),
            FiltroHasta           = hasta?.ToString("yyyy-MM-dd"),
        };

        ViewData["Title"] = empleado.NombreCompleto;
        ViewData["BreadcrumbParent"] = "Empleados";
        ViewData["BreadcrumbParentUrl"] = Url.Action("Index")!;
        ViewData["BreadcrumbCurrent"] = empleado.NombreCompleto;
        return View(vm);
    }

    // GET /Empleado/Desvincular/{id}
    [HttpGet]
    public async Task<IActionResult> Desvincular(int id)
    {
        var rolCheck = SesionHelper.GetRol(User);
        if (rolCheck != RolUsuario.DirectorTecnico && rolCheck != RolUsuario.Administrador
            && rolCheck != RolUsuario.Analista)
            return Forbid();

        var empResult = await _empleadoService.ObtenerPerfilAsync(id);
        if (!empResult.Exito || empResult.Datos is null)
            return NotFound();
        var empleado = empResult.Datos;

        var vm = new DesvincularEmpleadoViewModel
        {
            Empleado = empleado,
            Dto      = new DesvincularEmpleadoDto { EmpleadoId = id },
        };

        ViewData["Title"] = "Desvincular empleado";
        ViewData["BreadcrumbParent"] = empleado.NombreCompleto;
        ViewData["BreadcrumbParentUrl"] = Url.Action("Perfil", new { id })!;
        ViewData["BreadcrumbCurrent"] = "Desvincular";
        return View(vm);
    }

    // POST /Empleado/Desvincular
    [HttpPost]
    [ValidateAntiForgeryToken]
    public async Task<IActionResult> Desvincular(DesvincularEmpleadoViewModel vm)
    {
        var rol = SesionHelper.GetRol(User);
        if (rol != RolUsuario.DirectorTecnico && rol != RolUsuario.Administrador
            && rol != RolUsuario.Analista)
            return Forbid();

        if (!ModelState.IsValid)
        {
            var empR = await _empleadoService.ObtenerPerfilAsync(vm.Dto.EmpleadoId);
            var vmRecarga = new DesvincularEmpleadoViewModel { Dto = vm.Dto, Empleado = empR.Datos! };
            return View(vmRecarga);
        }

        var usuarioId = SesionHelper.GetUsuarioId(User);
        var resultado = await _empleadoService.DesvincularAsync(vm.Dto, usuarioId);

        if (!resultado.Exito)
        {
            ModelState.AddModelError(string.Empty, resultado.Mensaje ?? "No se pudo desvincular el empleado.");
            var empR2 = await _empleadoService.ObtenerPerfilAsync(vm.Dto.EmpleadoId);
            var vmRecarga2 = new DesvincularEmpleadoViewModel { Dto = vm.Dto, Empleado = empR2.Datos! };
            return View(vmRecarga2);
        }

        TempData["Exito"] = "Empleado desvinculado correctamente.";
        return RedirectToAction("Index");
    }

    // ── Private helpers ─────────────────────────────────────────────────

    private async Task<NuevoEmpleadoViewModel> ConstruirNuevoVm(CrearEmpleadoDto dto)
    {
        var sedes     = await _catalogoService.ObtenerSedesActivasAsync();
        var cargos    = await _catalogoService.ObtenerCargosActivosAsync();
        var empresas  = await _catalogoService.ObtenerEmpresasTemporalesActivasAsync();
        var todosEmps = await _empleadoService.ObtenerTodosAsync();
        var jefes     = todosEmps.Where(e => e.Rol == RolUsuario.DirectorTecnico.ToString()
                                          && e.Estado == "Activo").ToList();
        return new NuevoEmpleadoViewModel
        {
            Dto               = dto,
            Sedes             = sedes,
            Cargos            = cargos,
            EmpresasTemporales = empresas,
            Jefes             = jefes,
        };
    }

    private async Task<EditarEmpleadoViewModel> ConstruirEditarVm(EditarEmpleadoDto dto)
    {
        var sedes     = await _catalogoService.ObtenerSedesActivasAsync();
        var cargos    = await _catalogoService.ObtenerCargosActivosAsync();
        var empresas  = await _catalogoService.ObtenerEmpresasTemporalesActivasAsync();
        var todosEmps = await _empleadoService.ObtenerTodosAsync();
        var jefes     = todosEmps.Where(e => e.Rol == RolUsuario.DirectorTecnico.ToString()
                                          && e.Estado == "Activo").ToList();
        return new EditarEmpleadoViewModel
        {
            Dto               = dto,
            Sedes             = sedes,
            Cargos            = cargos,
            EmpresasTemporales = empresas,
            Jefes             = jefes,
        };
    }

    private async Task<IReadOnlyList<EventoLaboralDto>> ObtenerEventosAsync(int empleadoId)
    {
        // Lazy-loaded via service - avoiding circular injection; resolved directly from service locator pattern via DI
        var svc = HttpContext.RequestServices.GetRequiredService<IEventoLaboralService>();
        return await svc.ObtenerPorEmpleadoAsync(empleadoId);
    }

    private async Task<IReadOnlyList<HoraExtraDto>> ObtenerHorasExtrasAsync(int empleadoId)
    {
        var svc = HttpContext.RequestServices.GetRequiredService<IHoraExtraService>();
        return await svc.ObtenerPorEmpleadoAsync(empleadoId);
    }
}
