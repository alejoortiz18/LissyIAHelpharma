using GestionPersonal.Application.Interfaces;
using GestionPersonal.Constants.Messages;
using GestionPersonal.Domain.Interfaces;
using GestionPersonal.Helpers.Email;
using GestionPersonal.Helpers.Security;
using GestionPersonal.Models.DTOs.Cuenta;
using GestionPersonal.Models.Models;

namespace GestionPersonal.Application.Services;

public class CuentaService : ICuentaService
{
    private readonly IUsuarioRepository _usuarioRepo;
    private readonly ITokenRecuperacionRepository _tokenRepo;
    private readonly ICodigoHelper _codigoHelper;
    private readonly IEmailHelper _emailHelper;

    public CuentaService(
        IUsuarioRepository usuarioRepo,
        ITokenRecuperacionRepository tokenRepo,
        ICodigoHelper codigoHelper,
        IEmailHelper emailHelper)
    {
        _usuarioRepo  = usuarioRepo;
        _tokenRepo    = tokenRepo;
        _codigoHelper = codigoHelper;
        _emailHelper  = emailHelper;
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
            EmpleadoId         = usuario.Empleado?.Id
        };

        return ResultadoOperacion<UsuarioSesionDto>.Ok(sesion, InicioSesionConstant.UsuarioBienvenido);
    }

    public async Task<ResultadoOperacion> SolicitarRecuperacionAsync(SolicitarRecuperacionDto dto, CancellationToken ct = default)
    {
        var usuario = await _usuarioRepo.ObtenerPorCorreoAsync(dto.Correo, ct);

        // Siempre devolver Ok para no revelar si el correo existe
        if (usuario is null)
            return ResultadoOperacion.Ok();

        var token = new GestionPersonal.Models.Entities.GestionPersonalEntities.TokenRecuperacion
        {
            UsuarioId       = usuario.Id,
            Token           = _codigoHelper.GenerarCodigoUnico(),
            FechaExpiracion = DateTime.UtcNow.AddHours(1),
            Usado           = false,
            FechaCreacion   = DateTime.UtcNow
        };

        _tokenRepo.Agregar(token);
        await _tokenRepo.GuardarCambiosAsync(ct);

        var cuerpo = EmailConstant.CuerpoRestablecerContrasena.Replace("{codigo}", token.Token);
        await _emailHelper.EnviarCorreoConCodigoAsync(
            dto.Correo,
            EmailConstant.AsuntoRestablecerContrasena,
            EmailConstant.CuerpoRestablecerContrasena,
            token.Token);

        return ResultadoOperacion.Ok();
    }

    public async Task<ResultadoOperacion> RestablecerPasswordAsync(RestablecerPasswordDto dto, CancellationToken ct = default)
    {
        var tokenEntidad = await _tokenRepo.ObtenerTokenActivoAsync(dto.Token, ct);

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
}
