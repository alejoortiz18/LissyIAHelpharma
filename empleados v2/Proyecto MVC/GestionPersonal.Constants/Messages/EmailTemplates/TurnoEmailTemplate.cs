namespace GestionPersonal.Constants.Messages.EmailTemplates;

/// <summary>
/// Plantillas para eventos de asignación y gestión de turnos.
/// EVT-08: Turno asignado.
/// EVT-09: Turno modificado.
/// EVT-10: Turno cancelado.
/// </summary>
public static class TurnoEmailTemplate
{
    // ── EVT-08: Turno asignado ────────────────────────────────────────────────

    public static string TurnoAsignado(
        string nombreEmpleado,
        string nombreTurno,
        string fechaVigencia,
        string nombreJefe)
    {
        var cuerpo = $"""
            <p style="margin:0 0 20px;font-size:15px;color:#1e293b;line-height:1.7;">
              Hola <strong>{EmailBase.EscapeHtml(nombreEmpleado)}</strong>,
            </p>
            <p style="margin:0 0 20px;font-size:14px;color:#475569;line-height:1.7;">
              Se te ha asignado un turno de trabajo. Revisa los detalles a continuación:
            </p>

            {EmailBase.TablaInfo(
                EmailBase.FilaDato("Turno asignado", nombreTurno,   false) +
                EmailBase.FilaDato("Vigencia desde", fechaVigencia, true)  +
                EmailBase.FilaDato("Asignado por",   nombreJefe,    false)
            )}

            {EmailBase.Banner("Ingresa al sistema para ver el detalle completo de tu horario.", "info")}
            """;

        return EmailBase.Construir(
            tituloVentana   : "Asignación de turno",
            badgeColor      : "Turno asignado",
            badgeTexto      : "Gestión de horarios",
            tituloPrincipal : "Nuevo turno asignado",
            cuerpoHtml      : cuerpo,
            generadoPor     : nombreJefe,
            tipoEvento      : "Asignación de Turno");
    }

    // ── EVT-09: Turno modificado ──────────────────────────────────────────────

    public static string TurnoModificado(
        string nombreEmpleado,
        string nombreTurnoAnterior,
        string nombreTurnoNuevo,
        string fechaVigencia,
        string nombreJefe)
    {
        var cuerpo = $"""
            <p style="margin:0 0 20px;font-size:15px;color:#1e293b;line-height:1.7;">
              Hola <strong>{EmailBase.EscapeHtml(nombreEmpleado)}</strong>,
            </p>
            <p style="margin:0 0 20px;font-size:14px;color:#475569;line-height:1.7;">
              Tu turno de trabajo ha sido modificado:
            </p>

            {EmailBase.TablaInfo(
                EmailBase.FilaDato("Turno anterior", nombreTurnoAnterior, false) +
                EmailBase.FilaDato("Turno nuevo",    nombreTurnoNuevo,    true)  +
                EmailBase.FilaDato("Vigencia desde", fechaVigencia,       false) +
                EmailBase.FilaDato("Modificado por", nombreJefe,          true)
            )}

            {EmailBase.Banner("Verifica tu nuevo horario en el sistema.", "advertencia")}
            """;

        return EmailBase.Construir(
            tituloVentana   : "Cambio de turno",
            badgeColor      : "Turno modificado",
            badgeTexto      : "Gestión de horarios",
            tituloPrincipal : "Tu turno fue modificado",
            cuerpoHtml      : cuerpo,
            generadoPor     : nombreJefe,
            tipoEvento      : "Modificación de Turno");
    }

    // ── EVT-10: Turno cancelado ───────────────────────────────────────────────

    public static string TurnoCancelado(
        string nombreEmpleado,
        string nombreTurno,
        string fechaVigencia,
        string nombreJefe)
    {
        var cuerpo = $"""
            <p style="margin:0 0 20px;font-size:15px;color:#1e293b;line-height:1.7;">
              Hola <strong>{EmailBase.EscapeHtml(nombreEmpleado)}</strong>,
            </p>

            {EmailBase.Banner($"El turno '{nombreTurno}' con vigencia desde {fechaVigencia} ha sido cancelado.", "peligro")}

            {EmailBase.TablaInfo(
                EmailBase.FilaDato("Turno cancelado", nombreTurno,   false) +
                EmailBase.FilaDato("Vigencia desde",  fechaVigencia, true)  +
                EmailBase.FilaDato("Cancelado por",   nombreJefe,    false)
            )}

            <p style="margin:20px 0 0;font-size:14px;color:#475569;line-height:1.7;">
              Comunícate con <strong>{EmailBase.EscapeHtml(nombreJefe)}</strong>
              para más información sobre tu nueva asignación.
            </p>
            """;

        return EmailBase.Construir(
            tituloVentana   : "Turno cancelado",
            badgeColor      : "Turno cancelado",
            badgeTexto      : "Gestión de horarios",
            tituloPrincipal : "Turno cancelado",
            cuerpoHtml      : cuerpo,
            generadoPor     : nombreJefe,
            tipoEvento      : "Cancelación de Turno");
    }
}
