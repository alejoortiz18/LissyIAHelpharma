using System.Net;
using System.Net.Mail;
using Microsoft.Extensions.Configuration;

namespace GestionPersonal.Helpers.Email;

public class EmailHelper : IEmailHelper
{
    private readonly IConfiguration _config;

    public EmailHelper(IConfiguration config)
    {
        _config = config;
    }

    private SmtpClient CrearCliente()
    {
        return new SmtpClient
        {
            Host                  = _config["Email:Host"]!,
            Port                  = int.Parse(_config["Email:Port"]!),
            EnableSsl             = true,
            UseDefaultCredentials = false,
            Credentials           = new NetworkCredential(
                _config["Email:Remitente"],
                _config["Email:Contrasena"])
        };
    }

    public async Task EnviarCorreoAsync(string destinatario, string asunto, string cuerpo)
    {
        using var smtp    = CrearCliente();
        using var mensaje = new MailMessage(_config["Email:Remitente"]!, destinatario)
        {
            Subject    = asunto,
            Body       = cuerpo,
            IsBodyHtml = true
        };
        await smtp.SendMailAsync(mensaje);
    }

    public async Task EnviarCorreoConCodigoAsync(
        string destinatario, string asunto, string plantilla, string codigo)
    {
        string cuerpo = plantilla.Replace("{codigo}", codigo);
        await EnviarCorreoAsync(destinatario, asunto, cuerpo);
    }

    public async Task EnviarCorreoNuevoUsuarioAsync(
        string destinatario, string asunto, string plantilla, string correo, string contrasenaTemp)
    {
        string cuerpo = plantilla
            .Replace("{correo}", correo)
            .Replace("{contrasenaTemp}", contrasenaTemp);
        await EnviarCorreoAsync(destinatario, asunto, cuerpo);
    }
}
