using System.ComponentModel.DataAnnotations;

namespace GestionPersonal.Models.DTOs.Cuenta;

/// <summary>DTO de entrada para el formulario de Login.</summary>
public class LoginDto
{
    [Required(ErrorMessage = "El correo es obligatorio.")]
    [EmailAddress(ErrorMessage = "Ingresa un correo válido.")]
    public string Correo { get; set; } = null!;

    [Required(ErrorMessage = "La contraseña es obligatoria.")]
    public string Password { get; set; } = null!;
}
