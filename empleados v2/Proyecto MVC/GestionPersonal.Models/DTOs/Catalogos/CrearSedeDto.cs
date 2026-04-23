using System.ComponentModel.DataAnnotations;

namespace GestionPersonal.Models.DTOs.Catalogos;

public class CrearSedeDto
{
    [Required(ErrorMessage = "El nombre es obligatorio.")]
    [StringLength(200, ErrorMessage = "El nombre no puede superar 200 caracteres.")]
    public string Nombre { get; set; } = string.Empty;

    [Required(ErrorMessage = "La ciudad es obligatoria.")]
    [StringLength(100, ErrorMessage = "La ciudad no puede superar 100 caracteres.")]
    public string Ciudad { get; set; } = string.Empty;

    [Required(ErrorMessage = "La dirección es obligatoria.")]
    [StringLength(300, ErrorMessage = "La dirección no puede superar 300 caracteres.")]
    public string Direccion { get; set; } = string.Empty;
}
