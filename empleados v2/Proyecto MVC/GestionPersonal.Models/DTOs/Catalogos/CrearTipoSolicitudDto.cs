using System.ComponentModel.DataAnnotations;

namespace GestionPersonal.Models.DTOs.Catalogos;

public class CrearTipoSolicitudDto
{
    [Required(ErrorMessage = "El nombre es obligatorio.")]
    [StringLength(200)]
    public string Nombre { get; set; } = string.Empty;

    [Required(ErrorMessage = "El código es obligatorio.")]
    [StringLength(50)]
    [RegularExpression(@"^[A-Za-z0-9_]+$", ErrorMessage = "El código solo puede contener letras, números y guión bajo.")]
    public string Codigo { get; set; } = string.Empty;

    public bool EsVacaciones { get; set; }
}
