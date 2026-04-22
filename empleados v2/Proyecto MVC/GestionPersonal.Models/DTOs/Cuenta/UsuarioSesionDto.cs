using GestionPersonal.Models.Enums;

namespace GestionPersonal.Models.DTOs.Cuenta;

/// <summary>DTO que se almacena en los Claims de la cookie de autenticación.</summary>
public class UsuarioSesionDto
{
    public int Id { get; init; }
    public string CorreoAcceso { get; init; } = null!;
    public RolUsuario Rol { get; init; }
    public int SedeId { get; init; }
    public string SedeNombre { get; init; } = null!;
    public bool DebeCambiarPassword { get; init; }
    public int? EmpleadoId { get; init; }
}
