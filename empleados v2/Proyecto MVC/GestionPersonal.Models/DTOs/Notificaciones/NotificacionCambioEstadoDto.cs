namespace GestionPersonal.Models.DTOs.Notificaciones;

/// <summary>
/// DTO para notificar a los actores involucrados cuando una solicitud laboral cambia de estado.
/// TC-CE-01 a TC-CE-08 (plan-EnvioCorreosCambioEstadoSolicitud.md)
/// </summary>
public record NotificacionCambioEstadoDto(
    string  TipoEvento,             // "Permiso", "Vacaciones", "Incapacidad", etc.
    string  FechaInicio,
    string  FechaFin,
    string? Descripcion,
    string  NuevoEstado,            // "Aprobado", "Rechazado", "Pendiente"
    string  AprobadorNombre,        // Nombre de quien ejecutó la acción
    string  SolicitanteNombre,
    string  SolicitanteCorreo,
    string? JefeAprobadorNombre,    // null si el aprobador no tiene jefe (ej. Analista)
    string? JefeAprobadorCorreo,    // null si el aprobador no tiene jefe
    string? Observacion);
