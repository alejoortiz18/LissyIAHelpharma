namespace GestionPersonal.Models.DTOs.Notificaciones;

public record NotificacionNuevoUsuarioDto(
    string DestinatarioCorreo,
    string NombreEmpleado,
    string CorreoAcceso,
    string NombreCreadorEvento);
