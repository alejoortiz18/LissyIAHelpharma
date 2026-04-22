using System.ComponentModel.DataAnnotations;

namespace GestionPersonal.Web.ViewModels.Cuenta;

public class RestablecerPasswordViewModel
{
    [Required]
    public string Token { get; set; } = null!;

    [Required(ErrorMessage = "La nueva contraseña es obligatoria.")]
    [StringLength(100, MinimumLength = 8, ErrorMessage = "La contraseña debe tener al menos 8 caracteres.")]
    public string NuevoPassword { get; set; } = null!;

    [Compare("NuevoPassword", ErrorMessage = "Las contraseñas no coinciden.")]
    public string ConfirmarPassword { get; set; } = null!;
}
