using System.Security.Claims;
using GestionPersonal.Constants;
using Microsoft.AspNetCore.Mvc;

namespace GestionPersonal.Web.Helpers;

public static class NavegacionHelper
{
    /// <summary>Redirige al primer módulo permitido según permisos de sesión.</summary>
    public static IActionResult RedirigirInicio(Controller controller, ClaimsPrincipal user)
    {
        if (PermisoHelper.TienePermiso(user, PermisosCodigo.DashboardVer))
            return controller.RedirectToAction("Index", "Dashboard");

        if (PermisoHelper.TienePermiso(user, PermisosCodigo.EmpleadosVerListado))
            return controller.RedirectToAction("Index", "Empleado");

        var empId = SesionHelper.GetEmpleadoId(user);
        if (PermisoHelper.TienePermiso(user, PermisosCodigo.EmpleadosVerPerfilPropio) && empId.HasValue)
            return controller.RedirectToAction("Perfil", "Empleado", new { id = empId.Value });

        if (PermisoHelper.TienePermiso(user, PermisosCodigo.SolicitudesVer))
            return controller.RedirectToAction("Index", "Solicitud");

        if (PermisoHelper.TienePermiso(user, PermisosCodigo.EventosLaboralesVer))
            return controller.RedirectToAction("Index", "EventoLaboral");

        if (PermisoHelper.TienePermiso(user, PermisosCodigo.TurnosVer))
            return controller.RedirectToAction("Index", "Turno");

        if (PermisoHelper.TienePermiso(user, PermisosCodigo.HorasExtrasVer))
            return controller.RedirectToAction("Index", "HoraExtra");

        if (user.IsInRole("Analista"))
            return controller.RedirectToAction("Index", "Catalogos");

        return controller.RedirectToAction("AccesoDenegado", "Cuenta");
    }
}
