namespace GestionPersonal.Helpers.Email;

/// <summary>
/// Contrato de transporte de correo. Solo responsable del envío.
/// No conoce plantillas ni lógica de negocio.
/// </summary>
public interface IEmailHelper
{
    Task EnviarAsync(
        string destinatario,
        string asunto,
        string cuerpoHtml,
        CancellationToken ct = default);

    Task EnviarConCopiaAsync(
        string destinatario,
        string copia,
        string asunto,
        string cuerpoHtml,
        CancellationToken ct = default);

    /// <summary>Envía un correo con un archivo adjunto.</summary>
    Task EnviarConAdjuntoAsync(
        string destinatario,
        string asunto,
        string cuerpoHtml,
        string rutaAdjunto,
        string nombreAdjunto,
        CancellationToken ct = default);
}
