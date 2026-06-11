using System.Text.RegularExpressions;

namespace GestionPersonal.Constants;

/// <summary>
/// Reglas de jerarquía basadas en el cargo del empleado (no en el rol del sistema).
/// </summary>
public static partial class CargoJefeSede
{
    [GeneratedRegex(@"\bDirector\b", RegexOptions.IgnoreCase | RegexOptions.CultureInvariant)]
    private static partial Regex DirectorPattern();

    [GeneratedRegex(@"\bRegente\b", RegexOptions.IgnoreCase | RegexOptions.CultureInvariant)]
    private static partial Regex RegentePattern();
    
    [GeneratedRegex(@"\bAnalista\b", RegexOptions.IgnoreCase | RegexOptions.CultureInvariant)]
    private static partial Regex AnalistaPattern();

    [GeneratedRegex(@"farmac", RegexOptions.IgnoreCase | RegexOptions.CultureInvariant)]
    private static partial Regex FarmaceuticoPattern();

    public static bool EsCargoDirector(string? cargoNombre)
    {
        if (string.IsNullOrWhiteSpace(cargoNombre)) return false;
        if (cargoNombre.Contains("auxiliar", StringComparison.OrdinalIgnoreCase)) return false;
        return DirectorPattern().IsMatch(cargoNombre);
    }

    public static bool EsCargoRegente(string? cargoNombre)
    {
        if (string.IsNullOrWhiteSpace(cargoNombre)) return false;
        if (cargoNombre.Contains("auxiliar", StringComparison.OrdinalIgnoreCase)) return false;
        return RegentePattern().IsMatch(cargoNombre);
    }

    public static bool EsCargoAnalistaServiciosFarmaceuticos(string? cargoNombre)
    {
        if (string.IsNullOrWhiteSpace(cargoNombre)) return false;
        return AnalistaPattern().IsMatch(cargoNombre) && FarmaceuticoPattern().IsMatch(cargoNombre);
    }

    public static bool PuedeSerJefePotencial(string? cargoNombre)
        => EsCargoDirector(cargoNombre)
        || EsCargoRegente(cargoNombre)
        || EsCargoAnalistaServiciosFarmaceuticos(cargoNombre);

    /// <summary>Cargos que pueden tener personal a cargo en su jerarquía descendente.</summary>
    public static bool PuedeTenerPersonalACargo(string? cargoNombre)
        => PuedeSerJefePotencial(cargoNombre);
}
