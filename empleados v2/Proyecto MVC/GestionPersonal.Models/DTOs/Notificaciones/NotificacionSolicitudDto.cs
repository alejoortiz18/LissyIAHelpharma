namespace GestionPersonal.Models.DTOs.Notificaciones;

public record NotificacionSolicitudDto(
    string  TipoEvento,
    string  TipoSolicitud,
    string  FechaEvento,
    string  NombreEmpleadoSolicitante,
    string  CorreoEmpleadoSolicitante,
    string  NombreJefeInmediato,
    string  CorreoJefeInmediato,
    string? NombreJefeApoyo,
    string? CorreoJefeApoyo,
    string? NombreAprobador,
    string? Observacion,
    string  NombreQuienGenera);
