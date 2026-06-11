using System.Globalization;

namespace GestionPersonal.Helpers;

public static class DateParseHelper
{
    private static readonly string[] Formatos =
        ["yyyy-MM-dd", "dd/MM/yyyy", "d/M/yyyy"];

    public static DateOnly? ParseFlexible(string? valor)
    {
        if (string.IsNullOrWhiteSpace(valor))
            return null;

        if (DateOnly.TryParseExact(valor.Trim(), Formatos, CultureInfo.InvariantCulture,
                DateTimeStyles.None, out var fecha))
            return fecha;

        return DateOnly.TryParse(valor, CultureInfo.InvariantCulture, DateTimeStyles.None, out fecha)
            ? fecha
            : null;
    }
}
