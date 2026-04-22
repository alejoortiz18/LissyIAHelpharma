using System.ComponentModel.DataAnnotations;

namespace GestionPersonal.Web.ViewModels.Cuenta;

public class RecuperarPasswordViewModel
{
    [Required(ErrorMessage = "El correo es obligatorio.")]
    [EmailAddress(ErrorMessage = "Correo no válido.")]
    public string CorreoAcceso { get; set; } = null!;
}
