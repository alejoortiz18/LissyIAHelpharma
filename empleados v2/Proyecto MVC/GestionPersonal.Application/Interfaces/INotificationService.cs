using GestionPersonal.Models.DTOs.Notificaciones;

namespace GestionPersonal.Application.Interfaces;

/// <summary>
/// Único punto de entrada para todas las notificaciones del sistema.
/// Los servicios de aplicación solo conocen esta interfaz.
/// El transporte, la plantilla y el registro son detalles internos.
/// </summary>
public interface INotificationService
{
    // ── Seguridad ─────────────────────────────────────────────────────────────
    Task NotificarNuevoUsuarioAsync(NotificacionNuevoUsuarioDto datos, CancellationToken ct = default);
    Task NotificarRecuperacionContrasenaAsync(NotificacionRecuperacionDto datos, CancellationToken ct = default);
    Task NotificarCambioContrasenaExitosoAsync(NotificacionCambioContrasenaDto datos, CancellationToken ct = default);

    // ── Solicitudes ───────────────────────────────────────────────────────────
    Task NotificarSolicitudCreadaAsync(NotificacionSolicitudDto datos, CancellationToken ct = default);
    Task NotificarSolicitudAprobadaAsync(NotificacionSolicitudDto datos, CancellationToken ct = default);
    Task NotificarSolicitudRechazadaAsync(NotificacionSolicitudDto datos, CancellationToken ct = default);
    Task NotificarSolicitudDevueltaAsync(NotificacionSolicitudDto datos, CancellationToken ct = default);

    // ── Turnos ────────────────────────────────────────────────────────────────
    Task NotificarAsignacionTurnoAsync(NotificacionTurnoDto datos, CancellationToken ct = default);
    Task NotificarModificacionTurnoAsync(NotificacionTurnoDto datos, CancellationToken ct = default);
    Task NotificarCancelacionTurnoAsync(NotificacionTurnoDto datos, CancellationToken ct = default);

    // ── Cambios de personal ───────────────────────────────────────────────────
    Task NotificarCambioCargoAsync(NotificacionCambioPersonalDto datos, CancellationToken ct = default);
    Task NotificarCambioSedeAsync(NotificacionCambioPersonalDto datos, CancellationToken ct = default);
}
