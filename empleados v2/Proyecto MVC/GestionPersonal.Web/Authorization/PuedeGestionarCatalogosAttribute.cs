using GestionPersonal.Constants;
using GestionPersonal.Web.Helpers;
using Microsoft.AspNetCore.Mvc;
using Microsoft.AspNetCore.Mvc.Filters;

namespace GestionPersonal.Web.Authorization;

/// <summary>Acceso a catálogos / datos maestros operativos (sedes, cargos, tipos de solicitud).</summary>
[AttributeUsage(AttributeTargets.Class | AttributeTargets.Method)]
public sealed class PuedeGestionarCatalogosAttribute : Attribute, IAuthorizationFilter
{
    public void OnAuthorization(AuthorizationFilterContext context)
    {
        var user = context.HttpContext.User;
        if (user?.Identity?.IsAuthenticated != true)
        {
            context.Result = new ChallengeResult();
            return;
        }

        if (user.IsInRole("Analista") || SesionHelper.EsUsuarioLissy(user))
            return;

        context.Result = new RedirectToActionResult("AccesoDenegado", "Cuenta", null);
    }
}
