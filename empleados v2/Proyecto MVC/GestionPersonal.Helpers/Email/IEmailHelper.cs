namespace GestionPersonal.Helpers.Email;

public interface IEmailHelper
{
    Task EnviarCorreoAsync(string destinatario, string asunto, string cuerpo);
    Task EnviarCorreoConCodigoAsync(string destinatario, string asunto, string plantilla, string codigo);
    Task EnviarCorreoNuevoUsuarioAsync(string destinatario, string asunto, string plantilla, string correo, string contrasenaTemp);
}
