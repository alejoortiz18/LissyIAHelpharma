using GestionPersonal.Application.Interfaces;
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
            Sedes            = sedes,
            Cargos           = cargos,
            EmpresasTemporales = empresas,
            Tab              = tab,
        };

        ViewData["Title"] = "Catálogos";
        ViewData["BreadcrumbCurrent"] = "Catálogos";
        return View(vm);
    }
}
