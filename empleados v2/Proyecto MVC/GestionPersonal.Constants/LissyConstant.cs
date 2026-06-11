namespace GestionPersonal.Constants;

/// <summary>Usuario administrador de datos maestros (Lissy).</summary>
public static class LissyConstant
{
    public const string CorreoProduccion = "lissy.gallego@zentria.com.co";

    private static readonly string[] CorreosPermitidos =
    [
        CorreoProduccion,
    ];

    public static bool EsCorreoLissy(string? correoAcceso) =>
        !string.IsNullOrWhiteSpace(correoAcceso)
        && CorreosPermitidos.Contains(correoAcceso.Trim(), StringComparer.OrdinalIgnoreCase);
}
