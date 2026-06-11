using System.Security.Claims;
using GestionPersonal.Constants;
using Microsoft.AspNetCore.Mvc;
using Microsoft.AspNetCore.Mvc.Filters;

namespace GestionPersonal.Web.Authorization;

/// <summary>Restringe el acceso al usuario Lissy (por correo de acceso).</summary>
[AttributeUsage(AttributeTargets.Class | AttributeTargets.Method)]
public sealed class SoloLissyAttribute : Attribute, IAuthorizationFilter
{
    public void OnAuthorization(AuthorizationFilterContext context)
    {
        var user = context.HttpContext.User;
        if (user?.Identity?.IsAuthenticated != true)
        {
            context.Result = new ChallengeResult();
            return;
        }

        var correo = user.FindFirstValue(ClaimTypes.Email);
        if (!LissyConstant.EsCorreoLissy(correo))
            context.Result = new RedirectToActionResult("AccesoDenegado", "Cuenta", null);
    }
}
