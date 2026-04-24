namespace GestionPersonal.Models.DTOs.Notificaciones;

public record NotificacionRecuperacionDto(
    string DestinatarioCorreo,
    string NombreEmpleado,
    string Codigo,
    string VigenciaMinutos = "30");
