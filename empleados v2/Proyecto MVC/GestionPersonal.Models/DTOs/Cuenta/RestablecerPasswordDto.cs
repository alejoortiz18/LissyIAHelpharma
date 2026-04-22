using System.ComponentModel.DataAnnotations;

namespace GestionPersonal.Models.DTOs.Cuenta;

/// <summary>DTO para restablecer la contraseña con el token de recuperación.</summary>
public class RestablecerPasswordDto
{
    [Required]
    public string Token { get; set; } = null!;

    [Required(ErrorMessage = "La nueva contraseña es obligatoria.")]
    [StringLength(100, MinimumLength = 8, ErrorMessage = "La contraseña debe tener al menos 8 caracteres.")]
    public string NuevoPassword { get; set; } = null!;

    [Compare("NuevoPassword", ErrorMessage = "Las contraseñas no coinciden.")]
    public string ConfirmarPassword { get; set; } = null!;
}
