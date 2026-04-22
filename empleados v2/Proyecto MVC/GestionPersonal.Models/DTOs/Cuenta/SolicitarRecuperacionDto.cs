using System.ComponentModel.DataAnnotations;

namespace GestionPersonal.Models.DTOs.Cuenta;

/// <summary>DTO para solicitar la recuperación de contraseña (ingreso del correo).</summary>
public class SolicitarRecuperacionDto
{
    [Required(ErrorMessage = "El correo es obligatorio.")]
    [EmailAddress(ErrorMessage = "Ingresa un correo válido.")]
    public string Correo { get; set; } = null!;
}
