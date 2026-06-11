using GestionPersonal.Application.Interfaces;
using GestionPersonal.Domain.Interfaces;
using GestionPersonal.Helpers.Security;
using GestionPersonal.Models.DTOs.Notificaciones;
using GestionPersonal.Models.Entities.GestionPersonalEntities;
using GestionPersonal.Models.Enums;
using GestionPersonal.Models.Models;

namespace GestionPersonal.Application.Services;

public class UsuarioService : IUsuarioService
{
    private readonly IUsuarioRepository    _repo;
    private readonly INotificationService  _notificationService;

    public UsuarioService(IUsuarioRepository repo, INotificationService notificationService)
    {
        _repo                = repo;
        _notificationService = notificationService;
    }

    public async Task<ResultadoOperacion<int>> CrearParaEmpleadoAsync(
        string correo, RolUsuario rol, int sedeId, string? urlRestablecimiento = null, CancellationToken ct = default)
    {
        if (await _repo.ExisteCorreoAsync(correo, ct: ct))
            return new ResultadoOperacion<int> { Exito = false, Mensaje = "Ya existe un usuario con ese correo." };

        var contrasenaTemp = PasswordHelper.GenerarContrasenaTemp();
        var (hash, salt)   = PasswordHelper.CrearHash(contrasenaTemp);

        var usuario = new Usuario
        {
            CorreoAcceso        = correo,
            PasswordHash        = hash,
            PasswordSalt        = salt,
            Rol                 = rol,
            SedeId              = sedeId,
            DebecambiarPassword  = true,
            Estado              = "Activo",
            FechaCreacion       = DateTime.UtcNow
        };

        _repo.Agregar(usuario);
        await _repo.GuardarCambiosAsync(ct);

        // Enviar correo de bienvenida (NO se envía contraseña — OWASP A02)
        await _notificationService.NotificarNuevoUsuarioAsync(
            new NotificacionNuevoUsuarioDto(
                DestinatarioCorreo  : correo,
                NombreEmpleado      : correo,
                CorreoAcceso        : correo,
                NombreCreadorEvento : "Sistema",
                UrlRestablecimiento : urlRestablecimiento),
            ct);

        return ResultadoOperacion<int>.Ok(usuario.Id);
    }

    public async Task<ResultadoOperacion> ActualizarParaEmpleadoAsync(
        int usuarioId, string correo, string rolCodigo, int sedeId, CancellationToken ct = default)
    {
        var usuario = await _repo.ObtenerPorIdAsync(usuarioId, ct);
        if (usuario is null)
            return ResultadoOperacion.Fail("Usuario de acceso no encontrado.");

        correo = correo.Trim();
        if (await _repo.ExisteCorreoAsync(correo, usuarioId, ct))
            return ResultadoOperacion.Fail("Ya existe otro usuario con ese correo electrónico.");

        if (!Enum.TryParse<RolUsuario>(rolCodigo, ignoreCase: true, out var rol))
            return ResultadoOperacion.Fail("El rol del sistema no es válido. Selecciona un rol de la lista.");

        usuario.CorreoAcceso        = correo;
        usuario.Rol                 = rol;
        usuario.SedeId              = sedeId;
        usuario.FechaModificacion   = DateTime.UtcNow;

        _repo.Actualizar(usuario);
        await _repo.GuardarCambiosAsync(ct);

        return ResultadoOperacion.Ok("Datos de acceso actualizados.");
    }
}
