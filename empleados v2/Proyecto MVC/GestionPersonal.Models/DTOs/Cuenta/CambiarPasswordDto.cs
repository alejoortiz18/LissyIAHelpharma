using System.ComponentModel.DataAnnotations;

namespace GestionPersonal.Models.DTOs.Cuenta;

/// <summary>DTO para que el usuario cambie su contraseña (obligatorio en primer inicio de sesión).</summary>
public class CambiarPasswordDto
{
    [Required(ErrorMessage = "La contraseña actual es obligatoria.")]
    public string PasswordActual { get; set; } = null!;

    [Required(ErrorMessage = "La nueva contraseña es obligatoria.")]
    [StringLength(100, MinimumLength = 8, ErrorMessage = "La contraseña debe tener al menos 8 caracteres.")]
    public string NuevoPassword { get; set; } = null!;

    [Compare("NuevoPassword", ErrorMessage = "Las contraseñas no coinciden.")]
    public string ConfirmarPassword { get; set; } = null!;
}
