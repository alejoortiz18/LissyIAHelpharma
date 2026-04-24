namespace GestionPersonal.Models.DTOs.Notificaciones;

public record NotificacionTurnoDto(
    string  TipoEvento,
    string  NombreEmpleado,
    string  CorreoEmpleado,
    string  NombreTurno,
    string? NombreTurnoAnterior,
    string  FechaVigencia,
    string  CorreoJefeEmisor,
    string  NombreJefeEmisor,
    string  NombreQuienGenera);
