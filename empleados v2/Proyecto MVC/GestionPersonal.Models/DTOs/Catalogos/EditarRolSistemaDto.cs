using System.ComponentModel.DataAnnotations;

namespace GestionPersonal.Models.DTOs.Catalogos;

public class EditarRolSistemaDto
{
    [Required]
    public int Id { get; set; }

    [Required(ErrorMessage = "El nombre es obligatorio.")]
    [StringLength(200)]
    public string Nombre { get; set; } = string.Empty;

    [StringLength(500)]
    public string? Descripcion { get; set; }

    [Required]
    [RegularExpression("^(Activo|Inactivo)$")]
    public string Estado { get; set; } = "Activo";

    public List<int> PermisoIds { get; set; } = [];
}
