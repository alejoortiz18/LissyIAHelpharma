namespace GestionPersonal.Models.Entities.GestionPersonalEntities;

/// <summary>
/// Auditoría de todos los intentos de envío de correo del sistema.
/// Se inserta una fila por cada llamada a INotificationService.
/// </summary>
public class RegistroNotificacion
{
    public int      Id           { get; set; }
    public string   TipoEvento   { get; set; } = string.Empty;
    public string   Destinatario { get; set; } = string.Empty;
    public string?  Copia        { get; set; }
    public string   Asunto       { get; set; } = string.Empty;
    public bool     Exitoso      { get; set; }
    public string?  ErrorMensaje { get; set; }
    public DateTime FechaIntento { get; set; } = DateTime.UtcNow;
}
