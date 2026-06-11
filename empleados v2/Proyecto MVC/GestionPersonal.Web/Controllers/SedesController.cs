using GestionPersonal.Application.Interfaces;
using GestionPersonal.Constants;
using GestionPersonal.Models.DTOs.Empleado;
using GestionPersonal.Web.ViewModels.Sedes;
using Microsoft.AspNetCore.Authorization;
using Microsoft.AspNetCore.Mvc;

namespace GestionPersonal.Web.Controllers;

[Authorize(Roles = "Analista")]
public class SedesController : Controller
{
    private readonly ICatalogoService _catalogoService;
    private readonly IEmpleadoService _empleadoService;

    public SedesController(ICatalogoService catalogoService, IEmpleadoService empleadoService)
    {
        _catalogoService = catalogoService;
        _empleadoService = empleadoService;
    }

    [HttpGet]
    public async Task<IActionResult> Index()
    {
        var sedes = await _catalogoService.ObtenerTodasSedesAsync();
        var empleados = await _empleadoService.ObtenerTodosAsync();

        var cards = sedes
            .Select(s =>
            {
                var usuariosSede = empleados.Where(e => e.SedeId == s.Id).ToList();
                var responsable = ObtenerResponsable(usuariosSede);
                return new SedeCardViewModel
                {
                    SedeId = s.Id,
                    Nombre = s.Nombre,
                    Ciudad = s.Ciudad,
                    Direccion = s.Direccion,
                    CantidadUsuarios = usuariosSede.Count,
                    ResponsableNombre = responsable?.NombreCompleto ?? "Sin responsable",
                    ResponsableCargo = responsable?.CargoNombre ?? "Sin responsable",
                    Usuarios = usuariosSede
                };
            })
            .OrderBy(s => s.Nombre)
            .ToList();

        var vm = new SedesIndexViewModel
        {
            Sedes = cards
        };

        ViewData["Title"] = "Sedes";
        ViewData["BreadcrumbCurrent"] = "Sedes";
        return View(vm);
    }

    [HttpGet]
    public async Task<IActionResult> Detalle(
        int id,
        string? buscar = null,
        string? estado = null,
        string? tipoVinculacion = null,
        string? rol = null)
    {
        var sede = (await _catalogoService.ObtenerTodasSedesAsync())
            .FirstOrDefault(s => s.Id == id);
        if (sede is null)
            return NotFound();

        var empleados = (await _empleadoService.ObtenerTodosAsync())
            .Where(e => e.SedeId == id)
            .ToList();

        var responsable = ObtenerResponsable(empleados);
        var query = empleados.AsEnumerable();

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

        if (!string.IsNullOrEmpty(rol))
            query = query.Where(e => e.Rol.Equals(rol, StringComparison.OrdinalIgnoreCase));

        var filtrados = query
            .OrderBy(e => e.NombreCompleto)
            .ToList();

        var vm = new SedeDetalleViewModel
        {
            SedeId = sede.Id,
            Nombre = sede.Nombre,
            Ciudad = sede.Ciudad,
            Direccion = sede.Direccion,
            ResponsableNombre = responsable?.NombreCompleto ?? "Sin responsable",
            ResponsableCargo = responsable?.CargoNombre ?? "Sin responsable",
            TotalUsuarios = empleados.Count,
            Activos = empleados.Count(e => e.Estado == "Activo"),
            NoDisponibles = empleados.Count(e => e.Estado == "NoDisponible"),
            Inactivos = empleados.Count(e => e.Estado == "Inactivo"),
            Usuarios = filtrados,
            Buscar = buscar,
            Estado = estado,
            TipoVinculacion = tipoVinculacion,
            Rol = rol
        };

        ViewData["Title"] = $"Sede {sede.Nombre}";
        ViewData["BreadcrumbParent"] = "Sedes";
        ViewData["BreadcrumbParentUrl"] = Url.Action("Index")!;
        ViewData["BreadcrumbCurrent"] = sede.Nombre;
        return View(vm);
    }

    private static EmpleadoListaDto? ObtenerResponsable(IReadOnlyList<EmpleadoListaDto> usuariosSede)
    {
        var activos = usuariosSede.Where(e => e.Estado == "Activo").ToList();
        var director = activos.FirstOrDefault(e => CargoJefeSede.EsCargoDirector(e.CargoNombre));
        if (director is not null) return director;
        return activos.FirstOrDefault(e => CargoJefeSede.EsCargoRegente(e.CargoNombre));
    }
}
