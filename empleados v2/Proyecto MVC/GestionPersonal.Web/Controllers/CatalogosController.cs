using GestionPersonal.Application.Interfaces;
using GestionPersonal.Models.DTOs.Catalogos;
using GestionPersonal.Web.ViewModels.Catalogos;
using Microsoft.AspNetCore.Authorization;
using Microsoft.AspNetCore.Mvc;

namespace GestionPersonal.Web.Controllers;

[Authorize(Roles = "Jefe,Administrador")]
public class CatalogosController : Controller
{
    private readonly ICatalogoService _catalogoService;

    public CatalogosController(ICatalogoService catalogoService)
    {
        _catalogoService = catalogoService;
    }

    // GET /Catalogos?tab=sedes
    [HttpGet]
    public async Task<IActionResult> Index(string tab = "sedes")
    {
        var sedes    = await _catalogoService.ObtenerSedesActivasAsync();
        var cargos   = await _catalogoService.ObtenerCargosActivosAsync();
        var empresas = await _catalogoService.ObtenerEmpresasTemporalesActivasAsync();

        var vm = new CatalogosViewModel
        {
            Sedes              = sedes,
            Cargos             = cargos,
            EmpresasTemporales = empresas,
            Tab                = tab,
        };

        ViewData["Title"] = "Catálogos";
        ViewData["BreadcrumbCurrent"] = "Catálogos";
        return View(vm);
    }

    // POST /Catalogos/CrearSedeAjax
    [HttpPost]
    [ValidateAntiForgeryToken]
    public async Task<IActionResult> CrearSedeAjax([FromForm] CrearSedeDto dto)
    {
        if (!ModelState.IsValid)
            return Json(new { exito = false, mensaje = "Datos inválidos. Revisa los campos obligatorios." });

        var resultado = await _catalogoService.CrearSedeAsync(dto);
        return Json(new { exito = resultado.Exito, mensaje = resultado.Mensaje });
    }

    // POST /Catalogos/CrearCargoAjax
    [HttpPost]
    [ValidateAntiForgeryToken]
    public async Task<IActionResult> CrearCargoAjax([FromForm] CrearCargoDto dto)
    {
        if (!ModelState.IsValid)
            return Json(new { exito = false, mensaje = "Datos inválidos. Revisa los campos obligatorios." });

        var resultado = await _catalogoService.CrearCargoAsync(dto);
        return Json(new { exito = resultado.Exito, mensaje = resultado.Mensaje });
    }

    // POST /Catalogos/CrearEmpresaAjax
    [HttpPost]
    [ValidateAntiForgeryToken]
    public async Task<IActionResult> CrearEmpresaAjax([FromForm] CrearEmpresaTemporalDto dto)
    {
        if (!ModelState.IsValid)
            return Json(new { exito = false, mensaje = "Datos inválidos. Revisa los campos obligatorios." });

        var resultado = await _catalogoService.CrearEmpresaTemporalAsync(dto);
        return Json(new { exito = resultado.Exito, mensaje = resultado.Mensaje });
    }

    // POST /Catalogos/EditarSedeAjax
    [HttpPost]
    [ValidateAntiForgeryToken]
    public async Task<IActionResult> EditarSedeAjax([FromForm] EditarSedeDto dto)
    {
        if (!ModelState.IsValid)
            return Json(new { exito = false, mensaje = "Datos inválidos. Revisa los campos obligatorios." });

        var resultado = await _catalogoService.EditarSedeAsync(dto);
        return Json(new { exito = resultado.Exito, mensaje = resultado.Mensaje });
    }

    // POST /Catalogos/EditarCargoAjax
    [HttpPost]
    [ValidateAntiForgeryToken]
    public async Task<IActionResult> EditarCargoAjax([FromForm] EditarCargoDto dto)
    {
        if (!ModelState.IsValid)
            return Json(new { exito = false, mensaje = "Datos inválidos. Revisa los campos obligatorios." });

        var resultado = await _catalogoService.EditarCargoAsync(dto);
        return Json(new { exito = resultado.Exito, mensaje = resultado.Mensaje });
    }

    // POST /Catalogos/EditarEmpresaAjax
    [HttpPost]
    [ValidateAntiForgeryToken]
    public async Task<IActionResult> EditarEmpresaAjax([FromForm] EditarEmpresaTemporalDto dto)
    {
        if (!ModelState.IsValid)
            return Json(new { exito = false, mensaje = "Datos inválidos. Revisa los campos obligatorios." });

        var resultado = await _catalogoService.EditarEmpresaTemporalAsync(dto);
        return Json(new { exito = resultado.Exito, mensaje = resultado.Mensaje });
    }
}
