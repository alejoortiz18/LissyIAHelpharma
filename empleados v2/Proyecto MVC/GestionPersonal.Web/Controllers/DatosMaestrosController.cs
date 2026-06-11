using GestionPersonal.Application.Interfaces;
using GestionPersonal.Models.DTOs.Catalogos;
using GestionPersonal.Web.Authorization;
using GestionPersonal.Web.ViewModels.Catalogos;
using Microsoft.AspNetCore.Authorization;
using Microsoft.AspNetCore.Mvc;

namespace GestionPersonal.Web.Controllers;

/// <summary>Gestión de datos maestros (sedes, cargos, empresas temporales) — solo Lissy.</summary>
[Authorize]
[SoloLissy]
public class DatosMaestrosController : Controller
{
    private readonly ICatalogoService _catalogoService;
    private readonly IRolSistemaService _rolSistemaService;

    public DatosMaestrosController(ICatalogoService catalogoService, IRolSistemaService rolSistemaService)
    {
        _catalogoService = catalogoService;
        _rolSistemaService = rolSistemaService;
    }

    [HttpGet]
    public async Task<IActionResult> Index(string tab = "sedes")
    {
        var vm = new CatalogosViewModel
        {
            Sedes              = await _catalogoService.ObtenerTodasSedesAsync(),
            Cargos             = await _catalogoService.ObtenerTodosCargosAsync(),
            EmpresasTemporales = await _catalogoService.ObtenerTodasEmpresasTemporalesAsync(),
            TiposSolicitud     = await _catalogoService.ObtenerTodosTiposSolicitudAsync(),
            RolesSistema       = await _rolSistemaService.ObtenerRolesAsync(),
            PermisosPlataforma = await _rolSistemaService.ObtenerPermisosAsync(),
            Tab                = tab,
        };

        ViewData["Title"] = "Datos maestros";
        ViewData["BreadcrumbCurrent"] = "Datos maestros";
        return View(vm);
    }

    [HttpPost]
    [ValidateAntiForgeryToken]
    public async Task<IActionResult> CrearSedeAjax([FromForm] CrearSedeDto dto)
    {
        if (!ModelState.IsValid)
            return Json(new { exito = false, mensaje = "Datos inválidos. Revisa los campos obligatorios." });

        var resultado = await _catalogoService.CrearSedeAsync(dto);
        return Json(new { exito = resultado.Exito, mensaje = resultado.Mensaje });
    }

    [HttpPost]
    [ValidateAntiForgeryToken]
    public async Task<IActionResult> CrearCargoAjax([FromForm] CrearCargoDto dto)
    {
        if (!ModelState.IsValid)
            return Json(new { exito = false, mensaje = "Datos inválidos. Revisa los campos obligatorios." });

        var resultado = await _catalogoService.CrearCargoAsync(dto);
        return Json(new { exito = resultado.Exito, mensaje = resultado.Mensaje });
    }

    [HttpPost]
    [ValidateAntiForgeryToken]
    public async Task<IActionResult> CrearEmpresaAjax([FromForm] CrearEmpresaTemporalDto dto)
    {
        if (!ModelState.IsValid)
            return Json(new { exito = false, mensaje = "Datos inválidos. Revisa los campos obligatorios." });

        var resultado = await _catalogoService.CrearEmpresaTemporalAsync(dto);
        return Json(new { exito = resultado.Exito, mensaje = resultado.Mensaje });
    }

    [HttpPost]
    [ValidateAntiForgeryToken]
    public async Task<IActionResult> EditarSedeAjax([FromForm] EditarSedeDto dto)
    {
        if (!ModelState.IsValid)
            return Json(new { exito = false, mensaje = "Datos inválidos. Revisa los campos obligatorios." });

        var resultado = await _catalogoService.EditarSedeAsync(dto);
        return Json(new { exito = resultado.Exito, mensaje = resultado.Mensaje });
    }

    [HttpPost]
    [ValidateAntiForgeryToken]
    public async Task<IActionResult> EditarCargoAjax([FromForm] EditarCargoDto dto)
    {
        if (!ModelState.IsValid)
            return Json(new { exito = false, mensaje = "Datos inválidos. Revisa los campos obligatorios." });

        var resultado = await _catalogoService.EditarCargoAsync(dto);
        return Json(new { exito = resultado.Exito, mensaje = resultado.Mensaje });
    }

    [HttpPost]
    [ValidateAntiForgeryToken]
    public async Task<IActionResult> EditarEmpresaAjax([FromForm] EditarEmpresaTemporalDto dto)
    {
        if (!ModelState.IsValid)
            return Json(new { exito = false, mensaje = "Datos inválidos. Revisa los campos obligatorios." });

        var resultado = await _catalogoService.EditarEmpresaTemporalAsync(dto);
        return Json(new { exito = resultado.Exito, mensaje = resultado.Mensaje });
    }

    [HttpGet]
    public async Task<IActionResult> ObtenerRolAjax(int id)
    {
        var detalle = await _rolSistemaService.ObtenerDetalleAsync(id);
        if (detalle is null)
            return Json(new { exito = false, mensaje = "Rol no encontrado." });
        return Json(new { exito = true, datos = detalle });
    }

    [HttpPost]
    [ValidateAntiForgeryToken]
    public async Task<IActionResult> CrearRolAjax([FromForm] CrearRolSistemaDto dto)
    {
        if (!ModelState.IsValid)
            return Json(new { exito = false, mensaje = "Datos inválidos. Revisa código, nombre y permisos." });
        var resultado = await _rolSistemaService.CrearRolAsync(dto);
        return Json(new { exito = resultado.Exito, mensaje = resultado.Mensaje });
    }

    [HttpPost]
    [ValidateAntiForgeryToken]
    public async Task<IActionResult> EditarRolAjax([FromForm] EditarRolSistemaDto dto)
    {
        if (!ModelState.IsValid)
            return Json(new { exito = false, mensaje = "Datos inválidos." });
        var resultado = await _rolSistemaService.EditarRolAsync(dto);
        return Json(new { exito = resultado.Exito, mensaje = resultado.Mensaje });
    }

    [HttpPost]
    [ValidateAntiForgeryToken]
    public async Task<IActionResult> DarDeBajaSedeAjax(int id)
    {
        var resultado = await _catalogoService.DarDeBajaSedeAsync(id);
        return Json(new { exito = resultado.Exito, mensaje = resultado.Mensaje });
    }

    [HttpPost]
    [ValidateAntiForgeryToken]
    public async Task<IActionResult> ActivarSedeAjax(int id)
    {
        var resultado = await _catalogoService.ActivarSedeAsync(id);
        return Json(new { exito = resultado.Exito, mensaje = resultado.Mensaje });
    }

    [HttpPost]
    [ValidateAntiForgeryToken]
    public async Task<IActionResult> DarDeBajaCargoAjax(int id)
    {
        var resultado = await _catalogoService.DarDeBajaCargoAsync(id);
        return Json(new { exito = resultado.Exito, mensaje = resultado.Mensaje });
    }

    [HttpPost]
    [ValidateAntiForgeryToken]
    public async Task<IActionResult> ActivarCargoAjax(int id)
    {
        var resultado = await _catalogoService.ActivarCargoAsync(id);
        return Json(new { exito = resultado.Exito, mensaje = resultado.Mensaje });
    }

    [HttpPost]
    [ValidateAntiForgeryToken]
    public async Task<IActionResult> DarDeBajaEmpresaAjax(int id)
    {
        var resultado = await _catalogoService.DarDeBajaEmpresaTemporalAsync(id);
        return Json(new { exito = resultado.Exito, mensaje = resultado.Mensaje });
    }

    [HttpPost]
    [ValidateAntiForgeryToken]
    public async Task<IActionResult> ActivarEmpresaAjax(int id)
    {
        var resultado = await _catalogoService.ActivarEmpresaTemporalAsync(id);
        return Json(new { exito = resultado.Exito, mensaje = resultado.Mensaje });
    }

    [HttpPost]
    [ValidateAntiForgeryToken]
    public async Task<IActionResult> DarDeBajaRolAjax(int id)
    {
        var resultado = await _rolSistemaService.DarDeBajaRolAsync(id);
        return Json(new { exito = resultado.Exito, mensaje = resultado.Mensaje });
    }

    [HttpPost]
    [ValidateAntiForgeryToken]
    public async Task<IActionResult> ActivarRolAjax(int id)
    {
        var resultado = await _rolSistemaService.ActivarRolAsync(id);
        return Json(new { exito = resultado.Exito, mensaje = resultado.Mensaje });
    }

    [HttpPost]
    [ValidateAntiForgeryToken]
    public async Task<IActionResult> CrearTipoSolicitudAjax([FromForm] CrearTipoSolicitudDto dto)
    {
        if (!ModelState.IsValid)
            return Json(new { exito = false, mensaje = "Datos inválidos. Revisa nombre y código." });

        var resultado = await _catalogoService.CrearTipoSolicitudAsync(dto);
        return Json(new { exito = resultado.Exito, mensaje = resultado.Mensaje });
    }

    [HttpPost]
    [ValidateAntiForgeryToken]
    public async Task<IActionResult> EditarTipoSolicitudAjax([FromForm] EditarTipoSolicitudDto dto)
    {
        if (!ModelState.IsValid)
            return Json(new { exito = false, mensaje = "Datos inválidos." });

        var resultado = await _catalogoService.EditarTipoSolicitudAsync(dto);
        return Json(new { exito = resultado.Exito, mensaje = resultado.Mensaje });
    }

    [HttpPost]
    [ValidateAntiForgeryToken]
    public async Task<IActionResult> DarDeBajaTipoSolicitudAjax(int id)
    {
        var resultado = await _catalogoService.DarDeBajaTipoSolicitudAsync(id);
        return Json(new { exito = resultado.Exito, mensaje = resultado.Mensaje });
    }

    [HttpPost]
    [ValidateAntiForgeryToken]
    public async Task<IActionResult> ActivarTipoSolicitudAjax(int id)
    {
        var resultado = await _catalogoService.ActivarTipoSolicitudAsync(id);
        return Json(new { exito = resultado.Exito, mensaje = resultado.Mensaje });
    }
}
