using MailKit.Net.Smtp;
using MailKit.Security;
using Microsoft.Extensions.Options;
using MimeKit;
using GestionPersonal.Models.Models.Email;

namespace GestionPersonal.Helpers.Email;

/// <summary>
/// Implementación SMTP con MailKit + STARTTLS.
/// Envía como buzón compartido (notificacion.sf@zentria.com.co)
/// autenticándose con la cuenta de servicio (sistemas.helpharma@zentria.com.co).
/// Requiere permiso "Send As" configurado en Exchange Online.
/// </summary>
public class EmailHelper : IEmailHelper
{
    private readonly SmtpSettings _settings;

    public EmailHelper(IOptions<EmailSettings> options)
        => _settings = options.Value.Smtp;

    public Task EnviarAsync(
        string destinatario, string asunto, string cuerpoHtml,
        CancellationToken ct = default)
        => EnviarInternoAsync(
               ConstruirMensaje([destinatario], null, asunto, cuerpoHtml), ct);

    public Task EnviarConCopiaAsync(
        string destinatario, string copia, string asunto, string cuerpoHtml,
        CancellationToken ct = default)
        => EnviarInternoAsync(
               ConstruirMensaje([destinatario], copia, asunto, cuerpoHtml), ct);

    // ── Privados ────────────────────────────────────────────────────────────────────

    private MimeMessage ConstruirMensaje(
        IEnumerable<string> destinatarios, string? copia,
        string asunto, string cuerpoHtml)
    {
        var msg = new MimeMessage();
        msg.From.Add(new MailboxAddress(_settings.FromName, _settings.FromAddress));

        foreach (var d in destinatarios)
            msg.To.Add(MailboxAddress.Parse(d));

        if (!string.IsNullOrWhiteSpace(copia))
            msg.Cc.Add(MailboxAddress.Parse(copia));

        msg.Subject = asunto;
        msg.Body    = new TextPart("html") { Text = cuerpoHtml };
        return msg;
    }

    private async Task EnviarInternoAsync(MimeMessage mensaje, CancellationToken ct)
    {
        using var smtp = new SmtpClient();
        await smtp.ConnectAsync(_settings.Host, _settings.Port,
                                 SecureSocketOptions.StartTls, ct);
        await smtp.AuthenticateAsync(_settings.Username, _settings.Password, ct);
        await smtp.SendAsync(mensaje, ct);
        await smtp.DisconnectAsync(quit: true, ct);
    }
}
