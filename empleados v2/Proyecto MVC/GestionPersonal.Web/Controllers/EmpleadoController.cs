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

        // Operario solo ve su perfil
        if (rol == RolUsuario.Operario)
        {
            var empId = SesionHelper.GetEmpleadoId(User);
            if (empId.HasValue)
                return RedirectToAction("Perfil", new { id = empId.Value });
            return RedirectToAction("Index", "Dashboard");
        }

        IReadOnlyList<EmpleadoListaDto> todos;
        if (rol == RolUsuario.Jefe || rol == RolUsuario.Administrador)
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
        if (rol == RolUsuario.Operario)
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
        if (rol == RolUsuario.Operario)
            return Forbid();

        if (!ModelState.IsValid)
        {
            var refreshed = await ConstruirNuevoVm(vm.Dto);
            return View("Nuevo", refreshed);
        }

        var usuarioId = SesionHelper.GetUsuarioId(User);
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

    // GET /Empleado/Perfil/{id}?tab=datos
    [HttpGet]
    public async Task<IActionResult> Perfil(int id, string tab = "datos")
    {
        var rol     = SesionHelper.GetRol(User);
        var empId   = SesionHelper.GetEmpleadoId(User);
        var miSede  = SesionHelper.GetSedeId(User);

        // Operario solo puede ver su propio perfil
        if (rol == RolUsuario.Operario && empId.HasValue && empId.Value != id)
            return Forbid();

        var empleadoResult = await _empleadoService.ObtenerPerfilAsync(id);
        if (!empleadoResult.Exito || empleadoResult.Datos is null)
            return NotFound();
        var empleado = empleadoResult.Datos;

        // El DTO del empleado incluye el nombre del turno actual si existe
        // Para el detalle del turno (detalles por día), buscamos en las plantillas activas
        var todasPlantillas = await _turnoService.ObtenerPlantillasActivasAsync();
        PlantillaTurnoDto? turnoActual = null;
        if (!string.IsNullOrEmpty(empleado.PlantillaTurnoActualNombre))
        {
            var match = todasPlantillas.FirstOrDefault(p =>
                p.Nombre.Equals(empleado.PlantillaTurnoActualNombre, StringComparison.OrdinalIgnoreCase));
            if (match != null)
            {
                var detalle = await _turnoService.ObtenerPlantillaConDetallesAsync(match.Id);
                if (detalle.Exito)
                    turnoActual = detalle.Datos;
            }
        }

        var eventos    = await ObtenerEventosAsync(id);
        var horasExtras = await ObtenerHorasExtrasAsync(id);
        var historialTurnos = await _turnoService.ObtenerHistorialPorEmpleadoAsync(id);

        var vm = new PerfilEmpleadoViewModel
        {
            Empleado        = empleado,
            Eventos         = eventos,
            HorasExtras     = horasExtras,
            TurnoActual     = turnoActual,
            Plantillas      = todasPlantillas,
            HistorialTurnos = historialTurnos,
            Tab             = tab,
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
        if (rolCheck != RolUsuario.Jefe && rolCheck != RolUsuario.Administrador)
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
        if (rol != RolUsuario.Jefe && rol != RolUsuario.Administrador)
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
        var jefes     = todosEmps.Where(e => e.Rol == RolUsuario.Jefe.ToString()
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
        var jefes     = todosEmps.Where(e => e.Rol == RolUsuario.Jefe.ToString()
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
