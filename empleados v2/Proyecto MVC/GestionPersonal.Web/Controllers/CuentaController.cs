using System.Security.Claims;
using GestionPersonal.Application.Interfaces;
using GestionPersonal.Models.DTOs.Cuenta;
using GestionPersonal.Web.Helpers;
using GestionPersonal.Web.ViewModels.Cuenta;
using Microsoft.AspNetCore.Authentication;
using Microsoft.AspNetCore.Authentication.Cookies;
using Microsoft.AspNetCore.Authorization;
using Microsoft.AspNetCore.Mvc;

namespace GestionPersonal.Web.Controllers;

public class CuentaController : Controller
{
    private readonly ICuentaService _cuentaService;

    public CuentaController(ICuentaService cuentaService)
    {
        _cuentaService = cuentaService;
    }

    // GET /Cuenta/Login
    [HttpGet]
    public IActionResult Login()
    {
        if (User.Identity?.IsAuthenticated == true)
            return RedirectToAction("Index", "Dashboard");
        return View(new LoginViewModel());
    }

    // POST /Cuenta/Login
    [HttpPost]
    [ValidateAntiForgeryToken]
    public async Task<IActionResult> Login(LoginViewModel vm)
    {

        if (!ModelState.IsValid)
            return View(vm);

        var dto = new LoginDto { Correo = vm.CorreoAcceso, Password = vm.Password };
        var resultado = await _cuentaService.LoginAsync(dto);

        if (!resultado.Exito)
        {
            ModelState.AddModelError(string.Empty, resultado.Mensaje ?? "Credenciales inválidas.");
            return View(vm);
        }

        var sesion = resultado.Datos!;
        var claims = new List<Claim>
        {
            new(ClaimTypes.NameIdentifier, sesion.Id.ToString()),
            new(ClaimTypes.Email,          sesion.CorreoAcceso),
            new(ClaimTypes.Role,           sesion.Rol.ToString()),
            new("SedeId",                  sesion.SedeId.ToString()),
            new("SedeNombre",              sesion.SedeNombre),
            new("DebeCambiarPassword",     sesion.DebeCambiarPassword.ToString()),
        };
        if (sesion.EmpleadoId.HasValue)
            claims.Add(new Claim("EmpleadoId", sesion.EmpleadoId.Value.ToString()));

        var identity  = new ClaimsIdentity(claims, CookieAuthenticationDefaults.AuthenticationScheme);
        var principal = new ClaimsPrincipal(identity);
        await HttpContext.SignInAsync(CookieAuthenticationDefaults.AuthenticationScheme, principal);

        if (sesion.DebeCambiarPassword)
            return RedirectToAction("CambiarPassword");

        return RedirectToAction("Index", "Dashboard");
    }

    // GET /Cuenta/Logout
    [Authorize]
    public async Task<IActionResult> Logout()
    {
        await HttpContext.SignOutAsync(CookieAuthenticationDefaults.AuthenticationScheme);
        return RedirectToAction("Login");
    }

    // GET /Cuenta/RecuperarPassword
    [HttpGet]
    public IActionResult RecuperarPassword() => View(new RecuperarPasswordViewModel());

    // POST /Cuenta/RecuperarPassword
    [HttpPost]
    [ValidateAntiForgeryToken]
    public async Task<IActionResult> RecuperarPassword(RecuperarPasswordViewModel vm)
    {
        if (!ModelState.IsValid) return View(vm);

        var dto = new SolicitarRecuperacionDto { Correo = vm.CorreoAcceso };
        await _cuentaService.SolicitarRecuperacionAsync(dto);

        TempData["Info"] = "Si el correo está registrado, recibirás las instrucciones de recuperación.";
        return RedirectToAction("Login");
    }

    // GET /Cuenta/RestablecerPassword?token=xxx
    [HttpGet]
    public IActionResult RestablecerPassword(string token)
    {
        if (string.IsNullOrEmpty(token))
            return RedirectToAction("Login");
        return View(new RestablecerPasswordViewModel { Token = token });
    }

    // POST /Cuenta/RestablecerPassword
    [HttpPost]
    [ValidateAntiForgeryToken]
    public async Task<IActionResult> RestablecerPassword(RestablecerPasswordViewModel vm)
    {
        if (!ModelState.IsValid) return View(vm);

        var dto = new RestablecerPasswordDto { Token = vm.Token, NuevoPassword = vm.NuevoPassword };
        var resultado = await _cuentaService.RestablecerPasswordAsync(dto);

        if (!resultado.Exito)
        {
            ModelState.AddModelError(string.Empty, resultado.Mensaje ?? "No se pudo restablecer la contraseña.");
            return View(vm);
        }

        TempData["Exito"] = "Contraseña restablecida correctamente. Inicia sesión.";
        return RedirectToAction("Login");
    }

    // GET /Cuenta/CambiarPassword
    [Authorize]
    [HttpGet]
    public IActionResult CambiarPassword() => View(new CambiarPasswordViewModel());

    // POST /Cuenta/CambiarPassword
    [Authorize]
    [HttpPost]
    [ValidateAntiForgeryToken]
    public async Task<IActionResult> CambiarPassword(CambiarPasswordViewModel vm)
    {
        if (!ModelState.IsValid) return View(vm);

        var usuarioId = SesionHelper.GetUsuarioId(User);
        var resultado = await _cuentaService.CambiarPasswordAsync(usuarioId, vm.Dto);

        if (!resultado.Exito)
        {
            ModelState.AddModelError(string.Empty, resultado.Mensaje ?? "No se pudo cambiar la contraseña.");
            return View(vm);
        }

        // Re-issue cookie with DebeCambiarPassword=false
        var claims = User.Claims
            .Where(c => c.Type != "DebeCambiarPassword")
            .Append(new Claim("DebeCambiarPassword", "False"))
            .ToList();

        await HttpContext.SignOutAsync(CookieAuthenticationDefaults.AuthenticationScheme);
        var identity  = new ClaimsIdentity(claims, CookieAuthenticationDefaults.AuthenticationScheme);
        var principal = new ClaimsPrincipal(identity);
        await HttpContext.SignInAsync(CookieAuthenticationDefaults.AuthenticationScheme, principal);

        TempData["Exito"] = "Contraseña actualizada correctamente.";
        return RedirectToAction("Index", "Dashboard");
    }
}
