using GestionPersonal.Application.Interfaces;
using GestionPersonal.Constants.Messages.EmailTemplates;
using GestionPersonal.Domain.Interfaces;
using GestionPersonal.Helpers.Email;
using GestionPersonal.Models.DTOs.Notificaciones;
using GestionPersonal.Models.Entities.GestionPersonalEntities;
using Microsoft.Extensions.Logging;

namespace GestionPersonal.Application.Services;

/// <summary>
/// Módulo profundo de notificaciones.
/// Interfaz: INotificationService (12 métodos semánticos).
/// Implementación oculta: selección de plantilla, formato de asunto,
/// lógica de CC, envío por MailKit y auditoría en BD.
/// Las excepciones de transporte no interrumpen el flujo del negocio;
/// el error queda registrado en RegistroNotificaciones.
/// </summary>
public class NotificationService : INotificationService
{
    private const string FormatoAsunto = "[{0}] - [{1}]";

    private readonly IEmailHelper                 _email;
    private readonly INotificacionRepository      _notificacionRepo;
    private readonly ILogger<NotificationService> _logger;

    public NotificationService(
        IEmailHelper email,
        INotificacionRepository notificacionRepo,
        ILogger<NotificationService> logger)
    {
        _email            = email;
        _notificacionRepo = notificacionRepo;
        _logger           = logger;
    }


    public Task NotificarNuevoUsuarioAsync(
        NotificacionNuevoUsuarioDto d, CancellationToken ct = default)
        => Enviar("NuevoUsuario",
               Asunto("Nuevo Usuario", d.NombreCreadorEvento),
               d.DestinatarioCorreo, null,
               SeguridadEmailTemplate.NuevoUsuario(d.NombreEmpleado, d.CorreoAcceso, d.NombreCreadorEvento, d.UrlRestablecimiento),
               ct);

    public Task NotificarRecuperacionContrasenaAsync(
        NotificacionRecuperacionDto d, CancellationToken ct = default)
        => Enviar("RecuperacionContrasena",
               Asunto("Recuperación de Contraseña", d.DestinatarioCorreo),
               d.DestinatarioCorreo, null,
               SeguridadEmailTemplate.RecuperacionContrasena(
                   d.NombreEmpleado, d.DestinatarioCorreo, d.Codigo,
                   d.VigenciaMinutos, d.UrlRestablecimiento),
               ct);

    public Task NotificarCambioContrasenaExitosoAsync(
        NotificacionCambioContrasenaDto d, CancellationToken ct = default)
        => Enviar("CambioContrasenaExitoso",
               Asunto("Cambio de Contraseña", d.DestinatarioCorreo),
               d.DestinatarioCorreo, null,
               SeguridadEmailTemplate.CambioContrasenaExitoso(d.NombreEmpleado, d.DestinatarioCorreo),
               ct);

    public async Task NotificarSolicitudCreadaAsync(
        NotificacionSolicitudDto d, CancellationToken ct = default)
    {
        var asunto = Asunto($"Nueva {d.TipoSolicitud}", d.NombreEmpleadoSolicitante);

        var destinatariosJerarquia = d.DestinatariosJerarquia?.ToList()
            ?? ConstruirDestinatariosJerarquiaLegado(d);

        if (destinatariosJerarquia.Count == 0)
            return;

        bool tieneAdjunto = !string.IsNullOrWhiteSpace(d.RutaDocumentoAdjunto)
                         && !string.IsNullOrWhiteSpace(d.NombreDocumentoAdjunto)
                         && File.Exists(d.RutaDocumentoAdjunto);

        var nombreJefeInm = d.NombreJefeInmediato;

        foreach (var dest in destinatariosJerarquia)
        {
            var cuerpo = ConstruirCuerpoSolicitudCreada(d, dest, nombreJefeInm);

            if (tieneAdjunto)
            {
                await EnviarConAdjunto("SolicitudCreada", asunto,
                    dest.Correo, cuerpo,
                    d.RutaDocumentoAdjunto!, d.NombreDocumentoAdjunto!, ct);
            }
            else
            {
                await Enviar("SolicitudCreada", asunto,
                    dest.Correo, null, cuerpo, ct);
            }
        }
    }

    private static List<DestinatarioJerarquiaSolicitud> ConstruirDestinatariosJerarquiaLegado(
        NotificacionSolicitudDto d)
    {
        var lista = new List<DestinatarioJerarquiaSolicitud>();
        var correosVistos = new HashSet<string>(StringComparer.OrdinalIgnoreCase);

        void Agregar(string? correo, string nombre, bool esJefeInmediato)
        {
            if (string.IsNullOrWhiteSpace(correo) || !correosVistos.Add(correo))
                return;
            lista.Add(new DestinatarioJerarquiaSolicitud(correo, nombre, esJefeInmediato, false));
        }

        Agregar(d.CorreoJefeInmediato, d.NombreJefeInmediato, esJefeInmediato: true);
        Agregar(d.CorreoJefeApoyo, d.NombreJefeApoyo ?? "Jefe de apoyo", esJefeInmediato: false);

        if (d.CorreosLineaJerarquica is not null)
        {
            foreach (var correo in d.CorreosLineaJerarquica)
                Agregar(correo, d.NombreJefeInmediato, esJefeInmediato: false);
        }

        return lista;
    }

    private static string ConstruirCuerpoSolicitudCreada(
        NotificacionSolicitudDto d,
        DestinatarioJerarquiaSolicitud dest,
        string nombreJefeInmediatoDelSolicitante)
    {
        if (dest.EsAnalistaServiciosFarmaceuticos)
        {
            return SolicitudEmailTemplate.SolicitudCreadaParaAnalista(
                nombreJefeInmediatoDelSolicitante,
                d.NombreEmpleadoSolicitante,
                d.TipoSolicitud,
                d.FechaEvento,
                d.FechaFin ?? "",
                d.Descripcion,
                jefeInmediatoEsElAnalista: dest.EsJefeInmediatoDelSolicitante);
        }

        if (dest.EsJefeInmediatoDelSolicitante)
        {
            return SolicitudEmailTemplate.SolicitudCreadaParaJefe(
                dest.Nombre,
                d.NombreEmpleadoSolicitante,
                d.TipoSolicitud,
                d.FechaEvento,
                d.FechaFin ?? "",
                d.Descripcion);
        }

        return SolicitudEmailTemplate.SolicitudCreadaParaSuperiorEnJerarquia(
            dest.Nombre,
            nombreJefeInmediatoDelSolicitante,
            d.NombreEmpleadoSolicitante,
            d.TipoSolicitud,
            d.FechaEvento,
            d.FechaFin ?? "",
            d.Descripcion);
    }

    public Task NotificarSolicitudAprobadaAsync(
        NotificacionSolicitudDto d, CancellationToken ct = default)
        => Enviar("SolicitudAprobada",
               Asunto($"{d.TipoSolicitud} Aprobada", d.NombreAprobador ?? d.NombreJefeInmediato),
               d.CorreoEmpleadoSolicitante, null,
               SolicitudEmailTemplate.SolicitudAprobada(
                   d.NombreEmpleadoSolicitante, d.TipoSolicitud, d.FechaEvento,
                   d.NombreAprobador ?? d.NombreJefeInmediato, d.Observacion ?? ""),
               ct);

   
    public Task NotificarSolicitudRechazadaAsync(
        NotificacionSolicitudDto d, CancellationToken ct = default)
        => Enviar("SolicitudRechazada",
               Asunto($"{d.TipoSolicitud} Rechazada", d.NombreAprobador ?? d.NombreJefeInmediato),
               d.CorreoEmpleadoSolicitante, null,
               SolicitudEmailTemplate.SolicitudRechazada(
                   d.NombreEmpleadoSolicitante, d.TipoSolicitud, d.FechaEvento,
                   d.NombreAprobador ?? d.NombreJefeInmediato, d.Observacion ?? ""),
               ct);


    public Task NotificarSolicitudDevueltaAsync(
        NotificacionSolicitudDto d, CancellationToken ct = default)
        => Enviar("SolicitudDevuelta",
               Asunto($"{d.TipoSolicitud} Devuelta", d.NombreAprobador ?? d.NombreJefeInmediato),
               d.CorreoEmpleadoSolicitante, null,
               SolicitudEmailTemplate.SolicitudDevuelta(
                   d.NombreEmpleadoSolicitante, d.TipoSolicitud, d.FechaEvento,
                   d.NombreAprobador ?? d.NombreJefeInmediato,
                   d.Observacion ?? "Sin comentario"),
               ct);

 
    public Task NotificarAsignacionTurnoAsync(
        NotificacionTurnoDto d, CancellationToken ct = default)
        => Enviar("AsignacionTurno",
               Asunto("Asignación de Turno", d.NombreJefeEmisor),
               d.CorreoEmpleado, d.CorreoJefeEmisor,
               TurnoEmailTemplate.TurnoAsignado(
                   d.NombreEmpleado, d.NombreTurno, d.FechaVigencia, d.NombreJefeEmisor),
               ct);

    public Task NotificarModificacionTurnoAsync(
        NotificacionTurnoDto d, CancellationToken ct = default)
        => Enviar("ModificacionTurno",
               Asunto("Cambio de Turno", d.NombreJefeEmisor),
               d.CorreoEmpleado, d.CorreoJefeEmisor,
               TurnoEmailTemplate.TurnoModificado(
                   d.NombreEmpleado, d.NombreTurnoAnterior ?? "—",
                   d.NombreTurno, d.FechaVigencia, d.NombreJefeEmisor),
               ct);

    public Task NotificarCancelacionTurnoAsync(
        NotificacionTurnoDto d, CancellationToken ct = default)
        => Enviar("CancelacionTurno",
               Asunto("Turno Cancelado", d.NombreJefeEmisor),
               d.CorreoEmpleado, null,
               TurnoEmailTemplate.TurnoCancelado(
                   d.NombreEmpleado, d.NombreTurno, d.FechaVigencia, d.NombreJefeEmisor),
               ct);

    public Task NotificarCambioCargoAsync(
        NotificacionCambioPersonalDto d, CancellationToken ct = default)
        => Enviar("CambioCargo",
               Asunto("Cambio de Cargo", d.NombreQuienGenera),
               d.CorreoEmpleado, d.CorreoRRHH,
               PersonalEmailTemplate.CambioCargo(
                   d.NombreEmpleado, d.ValorAnterior, d.ValorNuevo, d.NombreQuienGenera),
               ct);


    public Task NotificarCambioSedeAsync(
        NotificacionCambioPersonalDto d, CancellationToken ct = default)
        => Enviar("CambioSede",
               Asunto("Traslado de Sede", d.NombreQuienGenera),
               d.CorreoEmpleado, d.CorreoRRHH,
               PersonalEmailTemplate.CambioSede(
                   d.NombreEmpleado, d.ValorAnterior, d.ValorNuevo, d.NombreQuienGenera),
               ct);

    public async Task NotificarCambioEstadoSolicitudAsync(
        NotificacionCambioEstadoDto d, CancellationToken ct = default)
    {
        // 1. Siempre: correo al solicitante
        await Enviar("CambioEstadoSolicitud",
               Asunto($"Solicitud {d.NuevoEstado}", d.AprobadorNombre),
               d.SolicitanteCorreo, null,
               CambioEstadoEmailTemplate.ParaSolicitante(
                   d.SolicitanteNombre, d.TipoEvento, d.FechaInicio, d.FechaFin,
                   d.Descripcion, d.NuevoEstado, d.AprobadorNombre, d.Observacion),
               ct);

        // 2. Correo al jefe inmediato del solicitante cuando NO es quien aprobó
        //    (evita auto-notificación cuando el jefe inmediato es el propio aprobador)
        bool notificarJefeInm =
            !string.IsNullOrWhiteSpace(d.JefeInmediatoDeSolicitanteCorreo) &&
            d.JefeInmediatoDeSolicitanteCorreo != d.SolicitanteCorreo &&
            d.JefeInmediatoDeSolicitanteCorreo != d.AprobadorCorreo;

        if (notificarJefeInm)
        {
            await Enviar("CambioEstadoSolicitudJefeInmediato",
                   Asunto($"Solicitud {d.NuevoEstado}", d.AprobadorNombre),
                   d.JefeInmediatoDeSolicitanteCorreo!, null,
                   CambioEstadoEmailTemplate.ParaJefeNotificado(
                       d.JefeInmediatoDeSolicitanteNombre!, d.AprobadorNombre, d.SolicitanteNombre,
                       d.TipoEvento, d.FechaInicio, d.FechaFin, d.Descripcion, d.NuevoEstado, d.Observacion),
                   ct);
        }

        // 3. Confirmación al aprobador cuando es distinto al jefe inmediato del solicitante
        //    (cubre el caso en que el jefe principal cambia el estado)
        bool notificarAprobador =
            !string.IsNullOrWhiteSpace(d.AprobadorCorreo) &&
            d.AprobadorCorreo != d.SolicitanteCorreo &&
            d.AprobadorCorreo != d.JefeInmediatoDeSolicitanteCorreo;

        if (notificarAprobador)
        {
            await Enviar("CambioEstadoSolicitudAprobador",
                   Asunto($"Solicitud {d.NuevoEstado}", d.AprobadorNombre),
                   d.AprobadorCorreo!, null,
                   CambioEstadoEmailTemplate.ParaJefeNotificado(
                       d.AprobadorNombre, d.AprobadorNombre, d.SolicitanteNombre,
                       d.TipoEvento, d.FechaInicio, d.FechaFin, d.Descripcion, d.NuevoEstado, d.Observacion),
                   ct);
        }

        // 4. Solo en aprobación con jefe por encima del aprobador (lógica existente)
        if (d.NuevoEstado == "Aprobado" && !string.IsNullOrWhiteSpace(d.JefeAprobadorCorreo))
        {
            await Enviar("CambioEstadoSolicitudJefeAprobador",
                   Asunto("Aprobación bajo tu autoridad", d.AprobadorNombre),
                   d.JefeAprobadorCorreo, null,
                   CambioEstadoEmailTemplate.ParaJefeAprobador(
                       d.JefeAprobadorNombre!, d.AprobadorNombre, d.SolicitanteNombre,
                       d.TipoEvento, d.FechaInicio, d.FechaFin, d.Descripcion, d.Observacion),
                   ct);
        }
    }

  
    private static string Asunto(string tipo, string quien)
        => string.Format(FormatoAsunto, tipo, quien);

    private static void AgregarDestinatario(List<string> destinatarios, string? correo)
    {
        if (string.IsNullOrWhiteSpace(correo))
            return;
        if (destinatarios.Any(x => x.Equals(correo, StringComparison.OrdinalIgnoreCase)))
            return;
        destinatarios.Add(correo.Trim());
    }

    private async Task Enviar(
        string tipoEvento, string asunto,
        string destinatario, string? copia,
        string html, CancellationToken ct)
    {
        var reg = new RegistroNotificacion
        {
            TipoEvento   = tipoEvento,
            Destinatario = destinatario,
            Copia        = copia,
            Asunto       = asunto,
            FechaIntento = DateTime.UtcNow,
            Exitoso      = false
        };

        try
        {
            if (!string.IsNullOrWhiteSpace(copia))
                await _email.EnviarConCopiaAsync(destinatario, copia, asunto, html, ct);
            else
                await _email.EnviarAsync(destinatario, asunto, html, ct);

            reg.Exitoso = true;
        }
        catch (Exception ex)
        {
            reg.ErrorMensaje = ex.Message.Length > 950 ? ex.Message[..950] : ex.Message;
            _logger.LogError(ex,
                "Fallo al enviar notificación {TipoEvento} a {Destinatario}", tipoEvento, destinatario);
        }
        finally
        {
            _notificacionRepo.Agregar(reg);
            await _notificacionRepo.GuardarCambiosAsync(ct);
        }
    }

    private async Task EnviarConAdjunto(
        string tipoEvento, string asunto,
        string destinatario, string html,
        string rutaAdjunto, string nombreAdjunto,
        CancellationToken ct)
    {
        var reg = new RegistroNotificacion
        {
            TipoEvento   = tipoEvento,
            Destinatario = destinatario,
            Copia        = null,
            Asunto       = asunto,
            FechaIntento = DateTime.UtcNow,
            Exitoso      = false
        };

        try
        {
            await _email.EnviarConAdjuntoAsync(destinatario, asunto, html, rutaAdjunto, nombreAdjunto, ct);
            reg.Exitoso = true;
        }
        catch (Exception ex)
        {
            reg.ErrorMensaje = ex.Message.Length > 950 ? ex.Message[..950] : ex.Message;
            _logger.LogError(ex,
                "Fallo al enviar notificación {TipoEvento} con adjunto a {Destinatario}", tipoEvento, destinatario);
        }
        finally
        {
            _notificacionRepo.Agregar(reg);
            await _notificacionRepo.GuardarCambiosAsync(ct);
        }
    }
}
