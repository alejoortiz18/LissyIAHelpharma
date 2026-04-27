namespace GestionPersonal.Constants.Messages.EmailTemplates;

/// <summary>
/// Plantillas para notificaciones de cambio de estado de solicitudes laborales.
/// TC-CE-01 a TC-CE-08 (plan-EnvioCorreosCambioEstadoSolicitud.md)
///
/// ParaSolicitante  → siempre se envía al empleado que creó la solicitud.
/// ParaJefeAprobador → se envía al jefe del aprobador SOLO cuando el nuevo estado es Aprobado.
/// </summary>
public static class CambioEstadoEmailTemplate
{
    // ── Correo al solicitante ─────────────────────────────────────────────────

    public static string ParaSolicitante(
        string nombreSolicitante,
        string tipoEvento,
        string fechaInicio,
        string fechaFin,
        string? descripcion,
        string nuevoEstado,          // "Aprobado" | "Rechazado" | "Pendiente"
        string aprobadorNombre,
        string? observacion = null)
    {
        var filaObs = string.IsNullOrWhiteSpace(observacion)
            ? ""
            : EmailBase.FilaDato("Observación", observacion, true);

        var filaDescripcion = string.IsNullOrWhiteSpace(descripcion)
            ? ""
            : EmailBase.FilaDato("Descripción", descripcion, false);

        var (bannerTipo, badgeColor, badgeTexto, tituloPrincipal, accion) = nuevoEstado switch
        {
            "Aprobado"  => ("exito",       "Aprobada",         "Resultado de tu solicitud",   "Tu solicitud fue aprobada",        "aprobada"),
            "Rechazado" => ("peligro",     "Rechazada",        "Resultado de tu solicitud",   "Tu solicitud fue rechazada",       "rechazada"),
            _           => ("advertencia", "En revisión",      "Solicitud devuelta a revisión","Tu solicitud fue devuelta",        "devuelta a revisión"),
        };

        var cuerpo = $"""
            <p style="margin:0 0 20px;font-size:15px;color:#1e293b;line-height:1.7;">
              Hola <strong>{EmailBase.EscapeHtml(nombreSolicitante)}</strong>,
            </p>

            {EmailBase.Banner($"Tu solicitud de {EmailBase.EscapeHtml(tipoEvento)} fue {accion} por {EmailBase.EscapeHtml(aprobadorNombre)}.", bannerTipo)}

            {EmailBase.TablaInfo(
                EmailBase.FilaDato("Tipo de solicitud", tipoEvento,       false) +
                EmailBase.FilaDato("Fecha inicio",      fechaInicio,      true)  +
                EmailBase.FilaDato("Fecha fin",         fechaFin,         false) +
                filaDescripcion                                                    +
                EmailBase.FilaDato("Gestionada por",    aprobadorNombre,  true)  +
                filaObs
            )}

            <p style="margin:20px 0 0;font-size:14px;color:#475569;line-height:1.7;">
              Puedes consultar el estado de todas tus solicitudes ingresando al sistema.
            </p>
            """;

        return EmailBase.Construir(
            tituloVentana   : $"Solicitud de {tipoEvento} {accion}",
            badgeColor      : badgeColor,
            badgeTexto      : badgeTexto,
            tituloPrincipal : tituloPrincipal,
            cuerpoHtml      : cuerpo,
            generadoPor     : aprobadorNombre,
            tipoEvento      : "Cambio de estado — Solicitud");
    }

    // ── Correo informativo a jefe inmediato o aprobador (cualquier estado) ──

    public static string ParaJefeNotificado(
        string nombreJefe,
        string aprobadorNombre,
        string solicitanteNombre,
        string tipoEvento,
        string fechaInicio,
        string fechaFin,
        string? descripcion,
        string nuevoEstado,
        string? observacion = null)
    {
        var filaObs = string.IsNullOrWhiteSpace(observacion)
            ? ""
            : EmailBase.FilaDato("Observación", observacion, true);

        var filaDescripcion = string.IsNullOrWhiteSpace(descripcion)
            ? ""
            : EmailBase.FilaDato("Descripción", descripcion, false);

        var (bannerTipo, accion) = nuevoEstado switch
        {
            "Aprobado"  => ("exito",       "aprobada"),
            "Rechazado" => ("peligro",     "rechazada"),
            _           => ("advertencia", "devuelta a revisión"),
        };

        var cuerpo = $"""
            <p style="margin:0 0 20px;font-size:15px;color:#1e293b;line-height:1.7;">
              Hola <strong>{EmailBase.EscapeHtml(nombreJefe)}</strong>,
            </p>

            {EmailBase.Banner($"La solicitud de {EmailBase.EscapeHtml(solicitanteNombre)} fue {accion} por {EmailBase.EscapeHtml(aprobadorNombre)}.", bannerTipo)}

            {EmailBase.TablaInfo(
                EmailBase.FilaDato("Gestionada por",   aprobadorNombre,    false) +
                EmailBase.FilaDato("Empleado",         solicitanteNombre,  true)  +
                EmailBase.FilaDato("Tipo",             tipoEvento,         false) +
                EmailBase.FilaDato("Fecha inicio",     fechaInicio,        true)  +
                EmailBase.FilaDato("Fecha fin",        fechaFin,           false) +
                filaDescripcion                                                    +
                filaObs
            )}

            {EmailBase.Banner("Este correo es solo informativo. No se requiere acción de tu parte.", "info")}
            """;

        return EmailBase.Construir(
            tituloVentana   : $"Solicitud de {tipoEvento} {accion}",
            badgeColor      : "Informativo",
            badgeTexto      : $"Solicitud {nuevoEstado}",
            tituloPrincipal : $"Solicitud de {EmailBase.EscapeHtml(solicitanteNombre)} {accion}",
            cuerpoHtml      : cuerpo,
            generadoPor     : aprobadorNombre,
            tipoEvento      : "Cambio de estado — Solicitud");
    }

    // ── Correo al jefe del aprobador (solo en aprobación) ────────────────────

    public static string ParaJefeAprobador(
        string nombreJefe,
        string aprobadorNombre,
        string solicitanteNombre,
        string tipoEvento,
        string fechaInicio,
        string fechaFin,
        string? descripcion,
        string? observacion = null)
    {
        var filaObs = string.IsNullOrWhiteSpace(observacion)
            ? ""
            : EmailBase.FilaDato("Observación", observacion, true);

        var filaDescripcion = string.IsNullOrWhiteSpace(descripcion)
            ? ""
            : EmailBase.FilaDato("Descripción", descripcion, false);

        var cuerpo = $"""
            <p style="margin:0 0 20px;font-size:15px;color:#1e293b;line-height:1.7;">
              Hola <strong>{EmailBase.EscapeHtml(nombreJefe)}</strong>,
            </p>
            <p style="margin:0 0 20px;font-size:14px;color:#475569;line-height:1.7;">
              Una solicitud fue aprobada bajo tu línea de autoridad.
            </p>

            {EmailBase.TablaInfo(
                EmailBase.FilaDato("Aprobado por",     aprobadorNombre,    false) +
                EmailBase.FilaDato("Empleado",         solicitanteNombre,  true)  +
                EmailBase.FilaDato("Tipo",             tipoEvento,         false) +
                EmailBase.FilaDato("Fecha inicio",     fechaInicio,        true)  +
                EmailBase.FilaDato("Fecha fin",        fechaFin,           false) +
                filaDescripcion                                                    +
                filaObs
            )}

            {EmailBase.Banner("Este correo es solo informativo. No se requiere acción de tu parte.", "info")}
            """;

        return EmailBase.Construir(
            tituloVentana   : $"{aprobadorNombre} aprobó solicitud de {solicitanteNombre}",
            badgeColor      : "Informativo",
            badgeTexto      : "Aprobación bajo tu autoridad",
            tituloPrincipal : $"{EmailBase.EscapeHtml(aprobadorNombre)} aprobó una solicitud",
            cuerpoHtml      : cuerpo,
            generadoPor     : aprobadorNombre,
            tipoEvento      : "Cambio de estado — Solicitud");
    }
}
