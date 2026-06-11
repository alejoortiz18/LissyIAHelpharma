using GestionPersonal.Web.Helpers;
using Microsoft.AspNetCore.Mvc;
using Microsoft.AspNetCore.Mvc.Filters;

namespace GestionPersonal.Web.Authorization;

/// <summary>Exige al menos uno de los permisos indicados (claims de sesión).</summary>
[AttributeUsage(AttributeTargets.Class | AttributeTargets.Method, AllowMultiple = true)]
public sealed class RequierePermisoAttribute : Attribute, IAuthorizationFilter
{
    private readonly string[] _codigos;

    public RequierePermisoAttribute(params string[] codigos)
    {
        _codigos = codigos.Length > 0 ? codigos : throw new ArgumentException("Indica al menos un código de permiso.");
    }

    public void OnAuthorization(AuthorizationFilterContext context)
    {
        var user = context.HttpContext.User;
        if (user?.Identity?.IsAuthenticated != true)
        {
            context.Result = new ChallengeResult();
            return;
        }

        if (PermisoHelper.TieneAlgunPermiso(user, _codigos))
            return;

        context.Result = new RedirectToActionResult("AccesoDenegado", "Cuenta", null);
    }
}
