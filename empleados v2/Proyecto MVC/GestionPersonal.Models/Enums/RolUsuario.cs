namespace GestionPersonal.Models.Enums;

public enum RolUsuario
{
    Administrador,    // Rol técnico de plataforma — superusuario sin restricciones
    DirectorTecnico,  // Renombrado desde: Jefe
    Regente,
    Operario,
    AuxiliarRegente,
    Analista,         // Nuevo — autoridad superior, acceso total multi-sede
    Direccionador     // Nuevo — operativo, solo información propia
}
