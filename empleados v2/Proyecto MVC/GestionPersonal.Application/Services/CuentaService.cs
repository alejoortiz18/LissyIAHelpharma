using System.Security.Cryptography;
using System.Text;
using GestionPersonal.Application.Interfaces;
using GestionPersonal.Constants.Messages;
using GestionPersonal.Domain.Interfaces;
using GestionPersonal.Helpers.Security;
using GestionPersonal.Models.DTOs.Cuenta;
using GestionPersonal.Models.DTOs.Notificaciones;
using GestionPersonal.Models.Models;
using System.Security.Cryptography;
using System.Text;

namespace GestionPersonal.Application.Services;

public class CuentaService : ICuentaService
{
    private readonly IUsuarioRepository _usuarioRepo;
    private readonly ITokenRecuperacionRepository _tokenRepo;
    private readonly ICodigoHelper _codigoHelper;
    private readonly INotificationService _notificationService;

    public CuentaService(
        IUsuarioRepository usuarioRepo,
        ITokenRecuperacionRepository tokenRepo,
        ICodigoHelper codigoHelper,
        INotificationService notificationService)
    {
        _usuarioRepo         = usuarioRepo;
        _tokenRepo           = tokenRepo;
        _codigoHelper        = codigoHelper;
        _notificationService = notificationService;
    }

    public async Task<ResultadoOperacion<UsuarioSesionDto>> LoginAsync(LoginDto dto, CancellationToken ct = default)
    {
        var usuario = await _usuarioRepo.ObtenerPorCorreoAsync(dto.Correo, ct);

        if (usuario is null || !PasswordHelper.VerificarPassword(dto.Password, usuario.PasswordHash, usuario.PasswordSalt))
            return new ResultadoOperacion<UsuarioSesionDto> { Exito = false, Mensaje = InicioSesionConstant.UsuarioIncorrecto };

        if (usuario.Estado != "Activo")
            return new ResultadoOperacion<UsuarioSesionDto> { Exito = false, Mensaje = InicioSesionConstant.UsuarioInactivo };

        // Actualizar último acceso
        usuario.UltimoAcceso = DateTime.UtcNow;
        _usuarioRepo.Actualizar(usuario);
        await _usuarioRepo.GuardarCambiosAsync(ct);

        var sesion = new UsuarioSesionDto
        {
            Id                 = usuario.Id,
            CorreoAcceso       = usuario.CorreoAcceso,
            Rol                = usuario.Rol,
            SedeId             = usuario.SedeId,
            SedeNombre         = usuario.Sede?.Nombre ?? string.Empty,
            DebeCambiarPassword = usuario.DebecambiarPassword,
            EmpleadoId         = usuario.Empleado?.Id,
            NombreCompleto     = usuario.Empleado?.NombreCompleto ?? usuario.CorreoAcceso
        };

        return ResultadoOperacion<UsuarioSesionDto>.Ok(sesion, InicioSesionConstant.UsuarioBienvenido);
    }

    public async Task<ResultadoOperacion> SolicitarRecuperacionAsync(SolicitarRecuperacionDto dto, CancellationToken ct = default)
    {
        var usuario = await _usuarioRepo.ObtenerPorCorreoAsync(dto.Correo, ct);

        // Siempre devolver Ok para no revelar si el correo existe
        if (usuario is null)
            return ResultadoOperacion.Ok();

        var codigoPlano = GenerarCodigoSeguro();
        var token = new GestionPersonal.Models.Entities.GestionPersonalEntities.TokenRecuperacion
        {
            UsuarioId       = usuario.Id,
            Token           = ComputarHashSha256(codigoPlano),
            FechaExpiracion = DateTime.UtcNow.AddMinutes(30),
            Usado           = false,
            FechaCreacion   = DateTime.UtcNow
        };

        _tokenRepo.Agregar(token);
        await _tokenRepo.GuardarCambiosAsync(ct);

        await _notificationService.NotificarRecuperacionContrasenaAsync(
            new NotificacionRecuperacionDto(
                DestinatarioCorreo  : dto.Correo,
                NombreEmpleado      : usuario.CorreoAcceso,
                Codigo              : codigoPlano,
                UrlRestablecimiento : dto.UrlBaseRestablecimiento is not null
                    ? $"{dto.UrlBaseRestablecimiento}?token={Uri.EscapeDataString(codigoPlano)}"
                    : null),
            ct);

        return ResultadoOperacion.Ok();
    }

    public async Task<ResultadoOperacion> RestablecerPasswordAsync(RestablecerPasswordDto dto, CancellationToken ct = default)
    {
        var tokenEntidad = await _tokenRepo.ObtenerTokenActivoAsync(ComputarHashSha256(dto.Token), ct);

        if (tokenEntidad is null)
            return ResultadoOperacion.Fail("El código es inválido o ha expirado.");

        var usuario = await _usuarioRepo.ObtenerPorIdAsync(tokenEntidad.UsuarioId, ct);
        if (usuario is null)
            return ResultadoOperacion.Fail(InicioSesionConstant.UsuarioIncorrecto);

        var (hash, salt) = PasswordHelper.CrearHash(dto.NuevoPassword);
        usuario.PasswordHash       = hash;
        usuario.PasswordSalt       = salt;
        usuario.DebecambiarPassword = false;
        usuario.FechaModificacion  = DateTime.UtcNow;

        tokenEntidad.Usado = true;

        _usuarioRepo.Actualizar(usuario);
        _tokenRepo.Actualizar(tokenEntidad);
        await _usuarioRepo.GuardarCambiosAsync(ct);

        await _notificationService.NotificarCambioContrasenaExitosoAsync(
            new NotificacionCambioContrasenaDto(
                DestinatarioCorreo : usuario.CorreoAcceso,
                NombreEmpleado     : usuario.Empleado?.NombreCompleto ?? usuario.CorreoAcceso
            ), ct);

        return ResultadoOperacion.Ok("Contraseña restablecida exitosamente.");
    }

    public async Task<ResultadoOperacion> CambiarPasswordAsync(int usuarioId, CambiarPasswordDto dto, CancellationToken ct = default)
    {
        var usuario = await _usuarioRepo.ObtenerPorIdAsync(usuarioId, ct);
        if (usuario is null)
            return ResultadoOperacion.Fail(InicioSesionConstant.UsuarioIncorrecto);

        if (!PasswordHelper.VerificarPassword(dto.PasswordActual, usuario.PasswordHash, usuario.PasswordSalt))
            return ResultadoOperacion.Fail("La contraseña actual es incorrecta.");

        var (hash, salt) = PasswordHelper.CrearHash(dto.NuevoPassword);
        usuario.PasswordHash        = hash;
        usuario.PasswordSalt        = salt;
        usuario.DebecambiarPassword  = false;
        usuario.FechaModificacion   = DateTime.UtcNow;

        _usuarioRepo.Actualizar(usuario);
        await _usuarioRepo.GuardarCambiosAsync(ct);

        return ResultadoOperacion.Ok("Contraseña actualizada exitosamente.");
    }

    private static string GenerarCodigoSeguro()
    {
        const string chars = "ABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789";
        var bytes = RandomNumberGenerator.GetBytes(12);
        return new string(bytes.Select(b => chars[b % chars.Length]).ToArray());
    }

    private static string ComputarHashSha256(string entrada)
    {
        var bytes = SHA256.HashData(Encoding.UTF8.GetBytes(entrada));
        return Convert.ToHexString(bytes).ToLowerInvariant();
    }
}
