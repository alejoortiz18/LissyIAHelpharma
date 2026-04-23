using System.ComponentModel.DataAnnotations;

namespace GestionPersonal.Models.DTOs.Catalogos;

public class CrearCargoDto
{
    [Required(ErrorMessage = "El nombre del cargo es obligatorio.")]
    [StringLength(200, ErrorMessage = "El nombre no puede superar 200 caracteres.")]
    public string Nombre { get; set; } = string.Empty;
}
