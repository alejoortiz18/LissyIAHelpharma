using System.ComponentModel.DataAnnotations;

namespace GestionPersonal.Models.DTOs.Catalogos;

public class CrearRolSistemaDto
{
    [Required(ErrorMessage = "El código es obligatorio.")]
    [StringLength(50, MinimumLength = 2)]
    [RegularExpression(@"^[A-Za-z][A-Za-z0-9_]*$", ErrorMessage = "Código alfanumérico sin espacios (ej. CoordinadorRH).")]
    public string Codigo { get; set; } = string.Empty;

    [Required(ErrorMessage = "El nombre es obligatorio.")]
    [StringLength(200)]
    public string Nombre { get; set; } = string.Empty;

    [StringLength(500)]
    public string? Descripcion { get; set; }

    public List<int> PermisoIds { get; set; } = [];
}
