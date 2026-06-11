namespace GestionPersonal.Constants;

/// <summary>Nombres y descripciones en español (Colombia) para roles del sistema.</summary>
public static class RolesSistemaTextos
{
    private static readonly Dictionary<string, (string Nombre, string Descripcion)> PorCodigo =
        new(StringComparer.OrdinalIgnoreCase)
        {
            ["Administrador"] = ("Administrador", "Rol técnico con acceso amplio a la plataforma"),
            ["Analista"] = ("Analista", "Autoridad superior, visión multi-sede"),
            ["DirectorTecnico"] = ("Director Técnico", "Jefe de área / supervisión técnica"),
            ["Regente"] = ("Regente", "Responsable de sede / farmacia"),
            ["AuxiliarRegente"] = ("Auxiliar de Regente", "Apoyo al regente en operación de sede"),
            ["Operario"] = ("Operario", "Personal operativo — perfil y solicitudes"),
            ["Direccionador"] = ("Direccionador", "Personal operativo con enfoque en dirección"),
        };

    public static string Nombre(string codigo, string? fallback = null) =>
        PorCodigo.TryGetValue(codigo, out var t) ? t.Nombre : (fallback ?? codigo);

    public static string Descripcion(string codigo, string? fallback = null) =>
        PorCodigo.TryGetValue(codigo, out var t) ? t.Descripcion : (fallback ?? string.Empty);
}
