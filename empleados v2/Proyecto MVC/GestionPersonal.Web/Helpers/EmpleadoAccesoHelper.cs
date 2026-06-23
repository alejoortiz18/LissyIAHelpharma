using GestionPersonal.Models.Enums;

namespace GestionPersonal.Web.Helpers;

/// <summary>Reglas de alcance por sede en el módulo de empleados.</summary>
public static class EmpleadoAccesoHelper
{
    /// <summary>Analista y Administrador ven personal de todas las sedes.</summary>
    public static bool TieneAlcanceMultiSede(RolUsuario rol) =>
        rol is RolUsuario.Administrador or RolUsuario.Analista;

    /// <summary>Director técnico solo accede a empleados cuyo SedeId coincide con su sede de sesión.</summary>
    public static bool PuedeAccederEmpleado(RolUsuario rol, int miSede, int empleadoSedeId) =>
        TieneAlcanceMultiSede(rol) || empleadoSedeId == miSede;
}
