using GestionPersonal.Models.Enums;
using GestionPersonal.Models.Models;

namespace GestionPersonal.Application.Interfaces;

/// <summary>Gestiona la creación de cuentas de acceso para empleados.</summary>
public interface IUsuarioService
{
    /// <summary>Crea un usuario vinculado al empleado recién creado y envía el correo de bienvenida.</summary>
    Task<ResultadoOperacion<int>> CrearParaEmpleadoAsync(
        string correo, RolUsuario rol, int sedeId, CancellationToken ct = default);
}
