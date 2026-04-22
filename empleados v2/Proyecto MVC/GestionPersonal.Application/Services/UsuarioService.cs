using GestionPersonal.Application.Interfaces;
using GestionPersonal.Constants.Messages;
using GestionPersonal.Domain.Interfaces;
using GestionPersonal.Helpers.Email;
using GestionPersonal.Helpers.Security;
using GestionPersonal.Models.Entities.GestionPersonalEntities;
using GestionPersonal.Models.Enums;
using GestionPersonal.Models.Models;

namespace GestionPersonal.Application.Services;

public class UsuarioService : IUsuarioService
{
    private readonly IUsuarioRepository _repo;
    private readonly IEmailHelper _emailHelper;

    public UsuarioService(IUsuarioRepository repo, IEmailHelper emailHelper)
    {
        _repo         = repo;
        _emailHelper  = emailHelper;
    }

    public async Task<ResultadoOperacion<int>> CrearParaEmpleadoAsync(
        string correo, RolUsuario rol, int sedeId, CancellationToken ct = default)
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

        // Enviar correo de bienvenida
        await _emailHelper.EnviarCorreoNuevoUsuarioAsync(
            correo,
            EmailConstant.AsuntoUsuarioNuevo,
            EmailConstant.CuerpoCrearUsuario,
            correo,
            contrasenaTemp);

        return ResultadoOperacion<int>.Ok(usuario.Id);
    }
}
