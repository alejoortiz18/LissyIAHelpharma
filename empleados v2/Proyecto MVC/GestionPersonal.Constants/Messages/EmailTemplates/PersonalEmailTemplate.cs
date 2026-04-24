namespace GestionPersonal.Constants.Messages.EmailTemplates;

/// <summary>
/// Plantillas para cambios en la información personal del empleado.
/// EVT-11: Cambio de cargo.
/// EVT-12: Cambio de sede.
/// </summary>
public static class PersonalEmailTemplate
{
    // ── EVT-11: Cambio de cargo ───────────────────────────────────────────────

    public static string CambioCargo(
        string nombreEmpleado,
        string cargoAnterior,
        string cargoNuevo,
        string nombreResponsable)
    {
        var cuerpo = $"""
            <p style="margin:0 0 20px;font-size:15px;color:#1e293b;line-height:1.7;">
              Hola <strong>{EmailBase.EscapeHtml(nombreEmpleado)}</strong>,
            </p>
            <p style="margin:0 0 20px;font-size:14px;color:#475569;line-height:1.7;">
              Se ha registrado un cambio en tu cargo dentro de la organización:
            </p>

            {EmailBase.TablaInfo(
                EmailBase.FilaDato("Cargo anterior",    cargoAnterior,     false) +
                EmailBase.FilaDato("Cargo nuevo",       cargoNuevo,        true)  +
                EmailBase.FilaDato("Registrado por",    nombreResponsable, false) +
                EmailBase.FilaDato("Fecha de cambio",   DateTime.Now.ToString("dd/MM/yyyy"), true)
            )}

            {EmailBase.Banner("Si tienes dudas sobre este cambio, comunícate con Recursos Humanos.", "info")}
            """;

        return EmailBase.Construir(
            tituloVentana   : "Cambio de cargo",
            badgeColor      : "Cambio registrado",
            badgeTexto      : "Actualización de personal",
            tituloPrincipal : "Cambio de cargo",
            cuerpoHtml      : cuerpo,
            generadoPor     : nombreResponsable,
            tipoEvento      : "Cambio de Cargo");
    }

    // ── EVT-12: Cambio de sede ────────────────────────────────────────────────

    public static string CambioSede(
        string nombreEmpleado,
        string sedeAnterior,
        string sedeNueva,
        string nombreResponsable)
    {
        var cuerpo = $"""
            <p style="margin:0 0 20px;font-size:15px;color:#1e293b;line-height:1.7;">
              Hola <strong>{EmailBase.EscapeHtml(nombreEmpleado)}</strong>,
            </p>
            <p style="margin:0 0 20px;font-size:14px;color:#475569;line-height:1.7;">
              Se ha registrado un traslado de sede en tu perfil:
            </p>

            {EmailBase.TablaInfo(
                EmailBase.FilaDato("Sede anterior",     sedeAnterior,      false) +
                EmailBase.FilaDato("Sede nueva",        sedeNueva,         true)  +
                EmailBase.FilaDato("Registrado por",    nombreResponsable, false) +
                EmailBase.FilaDato("Fecha de traslado", DateTime.Now.ToString("dd/MM/yyyy"), true)
            )}

            {EmailBase.Banner("Si tienes dudas sobre este traslado, comunícate con Recursos Humanos.", "info")}
            """;

        return EmailBase.Construir(
            tituloVentana   : "Traslado de sede",
            badgeColor      : "Traslado registrado",
            badgeTexto      : "Actualización de personal",
            tituloPrincipal : "Traslado de sede",
            cuerpoHtml      : cuerpo,
            generadoPor     : nombreResponsable,
            tipoEvento      : "Cambio de Sede");
    }
}
