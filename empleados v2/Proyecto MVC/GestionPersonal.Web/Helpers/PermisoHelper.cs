using System.Security.Claims;
using GestionPersonal.Constants;

namespace GestionPersonal.Web.Helpers;

public static class PermisoHelper
{
    public static bool TienePermiso(ClaimsPrincipal user, string codigoPermiso)
    {
        if (user?.Identity?.IsAuthenticated != true)
            return false;
        if (SesionHelper.EsUsuarioLissy(user) || user.IsInRole("Analista"))
            return true;
        return user.HasClaim(PermisoClaimTypes.Permiso, codigoPermiso);
    }

    public static bool TieneAlgunPermiso(ClaimsPrincipal user, params string[] codigos)
        => codigos.Any(c => TienePermiso(user, c));
}
