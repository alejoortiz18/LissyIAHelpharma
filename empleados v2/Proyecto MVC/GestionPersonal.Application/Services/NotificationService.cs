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
               SeguridadEmailTemplate.NuevoUsuario(d.NombreEmpleado, d.CorreoAcceso, d.NombreCreadorEvento),
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

    public Task NotificarSolicitudCreadaAsync(
        NotificacionSolicitudDto d, CancellationToken ct = default)
        => Enviar("SolicitudCreada",
               Asunto($"Nueva {d.TipoSolicitud}", d.NombreEmpleadoSolicitante),
               d.CorreoJefeInmediato, d.CorreoJefeApoyo,
               SolicitudEmailTemplate.SolicitudCreadaParaJefe(
                   d.NombreJefeInmediato, d.NombreEmpleadoSolicitante, d.TipoSolicitud, d.FechaEvento),
               ct);

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

  
    private static string Asunto(string tipo, string quien)
        => string.Format(FormatoAsunto, tipo, quien);

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
}
