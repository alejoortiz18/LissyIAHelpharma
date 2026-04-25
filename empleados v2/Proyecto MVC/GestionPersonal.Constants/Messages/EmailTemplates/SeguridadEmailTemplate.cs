namespace GestionPersonal.Constants.Messages.EmailTemplates;

/// <summary>
/// Plantillas de correo para eventos de seguridad y acceso al sistema.
/// Todos los métodos son funciones puras — sin estado, sin IO, testeables directamente.
/// EVT-01: Nuevo usuario creado.
/// EVT-02: Recuperación de contraseña.
/// EVT-03: Cambio de contraseña exitoso.
/// </summary>
public static class SeguridadEmailTemplate
{
    // ── EVT-01: Nuevo usuario ─────────────────────────────────────────────────

    /// <summary>
    /// Correo de bienvenida al crear una cuenta nueva.
    /// NO incluye contraseña — el usuario la establece al primer inicio de sesión.
    /// </summary>
    public static string NuevoUsuario(
        string nombreEmpleado,
        string correoAcceso,
        string nombreCreador)
    {
        var cuerpo = $"""
            <p style="margin:0 0 20px;font-size:15px;color:#1e293b;line-height:1.7;">
              Hola <strong>{EmailBase.EscapeHtml(nombreEmpleado)}</strong>,
            </p>
            <p style="margin:0 0 20px;font-size:14px;color:#475569;line-height:1.7;">
              Tu cuenta en <strong>GestionPersonal</strong> ha sido creada. A continuación tu correo de acceso:
            </p>

            {EmailBase.TablaInfo(
                EmailBase.FilaDato("Correo de acceso", correoAcceso, false) +
                EmailBase.FilaDato("Estado de la cuenta", "Activa — primer acceso pendiente", true)
            )}

            {EmailBase.Banner(
                "Por seguridad no enviamos contraseñas por correo. Al ingresar por primera vez el sistema te pedirá crear tu propia contraseña.",
                "info")}

            <p style="margin:24px 0 0;font-size:14px;color:#475569;line-height:1.7;">
              Si tienes dificultades para acceder, comunícate con
              <strong>{EmailBase.EscapeHtml(nombreCreador)}</strong>, quien creó tu cuenta.
            </p>
            """;

        return EmailBase.Construir(
            tituloVentana   : "Bienvenido a GestionPersonal",
            badgeColor      : "Cuenta nueva",
            badgeTexto      : "Sistema de Gestión de Personal",
            tituloPrincipal : $"Bienvenido, {nombreEmpleado}",
            cuerpoHtml      : cuerpo,
            generadoPor     : nombreCreador,
            tipoEvento      : "Creación de Usuario");
    }

    // ── EVT-02: Recuperación de contraseña ───────────────────────────────────

    /// <summary>
    /// Correo con el código de recuperación de contraseña.
    /// <paramref name="codigo"/> es el código PLANO. El hash SHA-256 se almacena en BD.
    /// </summary>
    public static string RecuperacionContrasena(
        string nombreEmpleado,
        string correoAcceso,
        string codigo,
        string vigenciaMinutos = "30",
        string? urlRestablecimiento = null)
    {
        // Botón CTA: se incluye solo cuando se provee la URL
        var botonCta = urlRestablecimiento is not null
            ? $"""

            <div style="text-align:center;margin:28px 0 8px;">
              <a href="{EmailBase.EscapeHtml(urlRestablecimiento)}"
                 style="display:inline-block;background-color:#3b5bdb;color:#ffffff;text-decoration:none;
                        font-weight:700;font-size:15px;padding:14px 40px;border-radius:8px;letter-spacing:.4px;">
                Restablecer contraseña
              </a>
            </div>
            <p style="text-align:center;font-size:12px;color:#94a3b8;margin:0 0 24px;">
              ¿No funciona el botón? Copia y pega este enlace en tu navegador:<br/>
              <span style="color:#3b5bdb;word-break:break-all;">{EmailBase.EscapeHtml(urlRestablecimiento)}</span>
            </p>
            """
            : string.Empty;

        var cuerpo = $"""
            <p style="margin:0 0 20px;font-size:15px;color:#1e293b;line-height:1.7;">
              Hola <strong>{EmailBase.EscapeHtml(nombreEmpleado)}</strong>,
            </p>
            <p style="margin:0 0 20px;font-size:14px;color:#475569;line-height:1.7;">
              Recibimos una solicitud para restablecer la contraseña de
              <strong>{EmailBase.EscapeHtml(correoAcceso)}</strong>.
              Usa el siguiente código de verificación:
            </p>

            <div style="text-align:center;margin:28px 0;">
              <div style="display:inline-block;background-color:#f0f4ff;border:2px dashed #3b5bdb;border-radius:12px;padding:20px 40px;">
                <p style="margin:0 0 6px;font-size:11px;font-weight:700;letter-spacing:2px;text-transform:uppercase;color:#3b5bdb;">Código de verificación</p>
                <p style="margin:0;font-size:32px;font-weight:900;letter-spacing:8px;color:#1e3a8a;font-family:'Courier New',monospace;">{EmailBase.EscapeHtml(codigo)}</p>
                <p style="margin:8px 0 0;font-size:12px;color:#64748b;">
                  Válido por <strong>{EmailBase.EscapeHtml(vigenciaMinutos)} minutos</strong>
                </p>
              </div>
            </div>

            {botonCta}
            {EmailBase.Banner(
                $"Este código expira en {vigenciaMinutos} minutos y solo puede usarse una vez. Si no solicitaste este cambio, ignora este correo.",
                "advertencia")}

            <p style="margin:20px 0 0;font-size:13px;color:#94a3b8;line-height:1.6;">
              Por tu seguridad, nunca compartas este código con nadie, incluyendo personal de soporte.
            </p>
            """;

        return EmailBase.Construir(
            tituloVentana   : "Código de recuperación de contraseña",
            badgeColor      : "Seguridad",
            badgeTexto      : "Solicitud de restablecimiento",
            tituloPrincipal : "Recuperación de contraseña",
            cuerpoHtml      : cuerpo,
            generadoPor     : correoAcceso,
            tipoEvento      : "Recuperación de Contraseña");
    }

    // ── EVT-03: Cambio de contraseña exitoso ─────────────────────────────────

    /// <summary>Confirmación de que la contraseña fue cambiada exitosamente.</summary>
    public static string CambioContrasenaExitoso(
        string nombreEmpleado,
        string correoAcceso)
    {
        var cuerpo = $"""
            <p style="margin:0 0 20px;font-size:15px;color:#1e293b;line-height:1.7;">
              Hola <strong>{EmailBase.EscapeHtml(nombreEmpleado)}</strong>,
            </p>

            {EmailBase.Banner(
                "Tu contraseña fue cambiada exitosamente. Si realizaste este cambio, no es necesario que hagas nada más.",
                "exito")}

            <p style="margin:20px 0;font-size:14px;color:#475569;line-height:1.7;">
              Si <strong>no realizaste este cambio</strong>, tu cuenta puede estar comprometida.
              Contacta inmediatamente a tu administrador del sistema.
            </p>

            {EmailBase.TablaInfo(
                EmailBase.FilaDato("Cuenta afectada", correoAcceso, false) +
                EmailBase.FilaDato("Acción", "Cambio de contraseña", true) +
                EmailBase.FilaDato("Fecha", DateTime.Now.ToString("dd/MM/yyyy HH:mm"), false)
            )}
            """;

        return EmailBase.Construir(
            tituloVentana   : "Contraseña actualizada",
            badgeColor      : "Confirmación",
            badgeTexto      : "Seguridad de la cuenta",
            tituloPrincipal : "Contraseña actualizada",
            cuerpoHtml      : cuerpo,
            generadoPor     : correoAcceso,
            tipoEvento      : "Cambio de Contraseña");
    }
}
