using System.ComponentModel.DataAnnotations;

namespace GestionPersonal.Models.DTOs.Catalogos;

public class EditarCargoDto
{
    [Required]
    [Range(1, int.MaxValue, ErrorMessage = "Id inválido.")]
    public int Id { get; set; }

    [Required(ErrorMessage = "El nombre del cargo es obligatorio.")]
    [StringLength(200, ErrorMessage = "El nombre no puede superar 200 caracteres.")]
    public string Nombre { get; set; } = string.Empty;
}
