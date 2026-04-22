namespace GestionPersonal.Constants.Messages;

public static class EmailConstant
{
    #region RESTABLECER CONTRASEÑA

    public const string AsuntoRestablecerContrasena = "Restablecer Contraseña";

    public const string CuerpoRestablecerContrasena = @"
        <p>Estimado usuario,</p>
        <p>Hemos recibido una solicitud para restablecer la contraseña de su cuenta en <strong>GestiónPersonal</strong>.</p>
        <p>Para completar el proceso, utilice el siguiente código:</p>
        <h2 style='color: #1e3a8a;'>{codigo}</h2>
        <p><strong>Este código es de un solo uso y tiene una vigencia de 1 hora.</strong></p>
        <p>Si no solicitó este cambio, ignore este mensaje.</p>
        <p>Atentamente,<br/><strong>Equipo GestiónPersonal</strong></p>";

    #endregion

    #region CREAR USUARIO

    public const string AsuntoUsuarioNuevo = "Bienvenid@ a GestiónPersonal";

    public const string CuerpoCrearUsuario = @"
        <p>Estimado usuario,</p>
        <p>Tu cuenta en <strong>GestiónPersonal</strong> ha sido creada exitosamente.</p>
        <p>Tus credenciales de acceso son:</p>
        <ul>
          <li><strong>Correo:</strong> {correo}</li>
          <li><strong>Contraseña temporal:</strong> {contrasenaTemp}</li>
        </ul>
        <p>Deberás cambiar tu contraseña al iniciar sesión por primera vez.</p>
        <p>Atentamente,<br/><strong>Equipo GestiónPersonal</strong></p>";

    #endregion
}
