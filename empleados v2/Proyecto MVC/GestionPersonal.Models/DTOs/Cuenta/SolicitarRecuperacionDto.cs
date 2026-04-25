using System.ComponentModel.DataAnnotations;

namespace GestionPersonal.Models.DTOs.Cuenta;

/// <summary>DTO para solicitar la recuperación de contraseña (ingreso del correo).</summary>
public class SolicitarRecuperacionDto
{
    [Required(ErrorMessage = "El correo es obligatorio.")]
    [EmailAddress(ErrorMessage = "Ingresa un correo válido.")]
    public string Correo { get; set; } = null!;

    /// <summary>
    /// URL base de la página de restablecimiento (sin el token).
    /// Ej: https://app.empresa.com/Cuenta/RestablecerPassword
    /// El servicio agrega ?token=CODIGO al construir el enlace del correo.
    /// </summary>
    public string? UrlBaseRestablecimiento { get; set; }
}
