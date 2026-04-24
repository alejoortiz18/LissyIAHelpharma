namespace GestionPersonal.Constants.Messages.EmailTemplates;

/// <summary>
/// Plantillas para el ciclo de vida de solicitudes laborales
/// (Horas Extra, Vacaciones, Permisos, Incapacidades).
/// EVT-04: Solicitud creada → notifica al jefe inmediato.
/// EVT-05: Aprobada → notifica al solicitante.
/// EVT-06: Rechazada → notifica al solicitante.
/// EVT-07: Devuelta para corrección → notifica al solicitante.
/// </summary>
public static class SolicitudEmailTemplate
{
    // ── EVT-04: Solicitud creada ──────────────────────────────────────────────

    public static string SolicitudCreadaParaJefe(
        string nombreJefe,
        string nombreSolicitante,
        string tipoSolicitud,
        string fechaEvento,
        string detalle = "")
    {
        var filaDetalle = string.IsNullOrWhiteSpace(detalle)
            ? ""
            : EmailBase.FilaDato("Detalle", detalle, true);

        var cuerpo = $"""
            <p style="margin:0 0 20px;font-size:15px;color:#1e293b;line-height:1.7;">
              Hola <strong>{EmailBase.EscapeHtml(nombreJefe)}</strong>,
            </p>
            <p style="margin:0 0 20px;font-size:14px;color:#475569;line-height:1.7;">
              Se ha registrado una nueva solicitud de <strong>{EmailBase.EscapeHtml(tipoSolicitud)}</strong>
              que requiere tu revisión:
            </p>

            {EmailBase.TablaInfo(
                EmailBase.FilaDato("Solicitante", nombreSolicitante, false) +
                EmailBase.FilaDato("Tipo",        tipoSolicitud,     true)  +
                EmailBase.FilaDato("Fecha",       fechaEvento,       false) +
                filaDetalle
            )}

            {EmailBase.Banner("Esta solicitud está pendiente de tu aprobación. Ingresa al sistema para revisarla.", "info")}
            """;

        return EmailBase.Construir(
            tituloVentana   : $"Nueva solicitud de {tipoSolicitud}",
            badgeColor      : "Pendiente",
            badgeTexto      : "Solicitud en espera de aprobación",
            tituloPrincipal : $"Nueva solicitud — {tipoSolicitud}",
            cuerpoHtml      : cuerpo,
            generadoPor     : nombreSolicitante,
            tipoEvento      : "Solicitud Creada");
    }

    // ── EVT-05: Solicitud aprobada ────────────────────────────────────────────

    public static string SolicitudAprobada(
        string nombreSolicitante,
        string tipoSolicitud,
        string fechaEvento,
        string nombreAprobador,
        string observacion = "")
    {
        var filaObs = string.IsNullOrWhiteSpace(observacion)
            ? ""
            : EmailBase.FilaDato("Observación", observacion, true);

        var cuerpo = $"""
            <p style="margin:0 0 20px;font-size:15px;color:#1e293b;line-height:1.7;">
              Hola <strong>{EmailBase.EscapeHtml(nombreSolicitante)}</strong>,
            </p>

            {EmailBase.Banner($"Tu solicitud de {tipoSolicitud} fue aprobada por {nombreAprobador}.", "exito")}

            {EmailBase.TablaInfo(
                EmailBase.FilaDato("Tipo de solicitud", tipoSolicitud,   false) +
                EmailBase.FilaDato("Fecha",             fechaEvento,     true)  +
                EmailBase.FilaDato("Aprobado por",      nombreAprobador, false) +
                filaObs
            )}

            <p style="margin:20px 0 0;font-size:14px;color:#475569;line-height:1.7;">
              Si tienes alguna consulta sobre esta aprobación, comunícate con
              <strong>{EmailBase.EscapeHtml(nombreAprobador)}</strong>.
            </p>
            """;

        return EmailBase.Construir(
            tituloVentana   : $"Solicitud de {tipoSolicitud} aprobada",
            badgeColor      : "Aprobada",
            badgeTexto      : "Resultado de tu solicitud",
            tituloPrincipal : "Tu solicitud fue aprobada",
            cuerpoHtml      : cuerpo,
            generadoPor     : nombreAprobador,
            tipoEvento      : "Solicitud Aprobada");
    }

    // ── EVT-06: Solicitud rechazada ───────────────────────────────────────────

    public static string SolicitudRechazada(
        string nombreSolicitante,
        string tipoSolicitud,
        string fechaEvento,
        string nombreRevisor,
        string motivoRechazo = "")
    {
        var filaMotivo = string.IsNullOrWhiteSpace(motivoRechazo)
            ? ""
            : EmailBase.FilaDato("Motivo", motivoRechazo, true);

        var cuerpo = $"""
            <p style="margin:0 0 20px;font-size:15px;color:#1e293b;line-height:1.7;">
              Hola <strong>{EmailBase.EscapeHtml(nombreSolicitante)}</strong>,
            </p>

            {EmailBase.Banner($"Tu solicitud de {tipoSolicitud} no fue aprobada.", "peligro")}

            {EmailBase.TablaInfo(
                EmailBase.FilaDato("Tipo de solicitud", tipoSolicitud, false) +
                EmailBase.FilaDato("Fecha",             fechaEvento,   true)  +
                EmailBase.FilaDato("Revisado por",      nombreRevisor, false) +
                filaMotivo
            )}

            <p style="margin:20px 0 0;font-size:14px;color:#475569;line-height:1.7;">
              Si consideras que esta decisión es incorrecta, comunícate con
              <strong>{EmailBase.EscapeHtml(nombreRevisor)}</strong>.
            </p>
            """;

        return EmailBase.Construir(
            tituloVentana   : $"Solicitud de {tipoSolicitud} rechazada",
            badgeColor      : "Rechazada",
            badgeTexto      : "Resultado de tu solicitud",
            tituloPrincipal : "Tu solicitud fue rechazada",
            cuerpoHtml      : cuerpo,
            generadoPor     : nombreRevisor,
            tipoEvento      : "Solicitud Rechazada");
    }

    // ── EVT-07: Solicitud devuelta para corrección ────────────────────────────

    public static string SolicitudDevuelta(
        string nombreSolicitante,
        string tipoSolicitud,
        string fechaEvento,
        string nombreRevisor,
        string comentario)
    {
        var cuerpo = $"""
            <p style="margin:0 0 20px;font-size:15px;color:#1e293b;line-height:1.7;">
              Hola <strong>{EmailBase.EscapeHtml(nombreSolicitante)}</strong>,
            </p>

            {EmailBase.Banner($"Tu solicitud de {tipoSolicitud} fue devuelta para corrección.", "advertencia")}

            {EmailBase.TablaInfo(
                EmailBase.FilaDato("Tipo de solicitud", tipoSolicitud, false) +
                EmailBase.FilaDato("Fecha",             fechaEvento,   true)  +
                EmailBase.FilaDato("Devuelta por",      nombreRevisor, false) +
                EmailBase.FilaDato("Comentario",        comentario,    true)
            )}

            <p style="margin:20px 0 0;font-size:14px;color:#475569;line-height:1.7;">
              Ingresa al sistema, corrige los campos indicados y vuelve a enviar la solicitud.
            </p>
            """;

        return EmailBase.Construir(
            tituloVentana   : $"Solicitud de {tipoSolicitud} devuelta",
            badgeColor      : "Requiere corrección",
            badgeTexto      : "Solicitud pendiente de ajuste",
            tituloPrincipal : "Tu solicitud requiere corrección",
            cuerpoHtml      : cuerpo,
            generadoPor     : nombreRevisor,
            tipoEvento      : "Solicitud Devuelta");
    }
}
