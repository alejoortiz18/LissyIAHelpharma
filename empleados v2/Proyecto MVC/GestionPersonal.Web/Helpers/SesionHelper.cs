using System.Security.Claims;
using GestionPersonal.Models.Enums;

namespace GestionPersonal.Web.Helpers;

/// <summary>Lee los claims del usuario autenticado de forma centralizada.</summary>
public static class SesionHelper
{
    public static int GetUsuarioId(ClaimsPrincipal user) =>
        int.Parse(user.FindFirstValue(ClaimTypes.NameIdentifier)!);

    public static string GetCorreo(ClaimsPrincipal user) =>
        user.FindFirstValue(ClaimTypes.Email) ?? string.Empty;

    public static RolUsuario GetRol(ClaimsPrincipal user) =>
        Enum.Parse<RolUsuario>(user.FindFirstValue(ClaimTypes.Role)!);

    public static int GetSedeId(ClaimsPrincipal user) =>
        int.Parse(user.FindFirstValue("SedeId")!);

    public static string GetSedeNombre(ClaimsPrincipal user) =>
        user.FindFirstValue("SedeNombre") ?? string.Empty;

    public static bool GetDebeCambiarPassword(ClaimsPrincipal user) =>
        bool.Parse(user.FindFirstValue("DebeCambiarPassword") ?? "false");

    public static int? GetEmpleadoId(ClaimsPrincipal user)
    {
        var val = user.FindFirstValue("EmpleadoId");
        return string.IsNullOrEmpty(val) ? null : int.Parse(val);
    }
}
