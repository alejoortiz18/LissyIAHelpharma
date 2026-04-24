namespace GestionPersonal.Models.Models.Email;

/// <summary>
/// Configuración de correo. La contraseña se lee desde user-secrets o variable de entorno.
/// Nunca debe estar en appsettings.json comiteado.
/// </summary>
public class EmailSettings
{
    public const string SectionName = "EmailSettings";

    public string       Provider { get; set; } = "Smtp";  // "Smtp" | "Graph"
    public SmtpSettings Smtp     { get; set; } = new();
}

public class SmtpSettings
{
    public string Host        { get; set; } = string.Empty;
    public int    Port        { get; set; } = 587;
    public bool   UseSsl      { get; set; } = false;
    public bool   UseStartTls { get; set; } = true;
    public string Username    { get; set; } = string.Empty;
    public string Password    { get; set; } = string.Empty;
    public string FromAddress { get; set; } = string.Empty;
    public string FromName    { get; set; } = string.Empty;
}
