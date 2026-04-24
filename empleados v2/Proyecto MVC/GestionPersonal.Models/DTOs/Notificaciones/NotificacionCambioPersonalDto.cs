namespace GestionPersonal.Models.DTOs.Notificaciones;

public record NotificacionCambioPersonalDto(
    string TipoEvento,
    string NombreEmpleado,
    string CorreoEmpleado,
    string ValorAnterior,
    string ValorNuevo,
    string CorreoRRHH,
    string NombreQuienGenera);
