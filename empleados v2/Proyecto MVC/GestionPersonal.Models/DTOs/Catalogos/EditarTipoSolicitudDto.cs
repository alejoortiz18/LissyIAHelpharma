using System.ComponentModel.DataAnnotations;

namespace GestionPersonal.Models.DTOs.Catalogos;

public class EditarTipoSolicitudDto
{
    [Range(1, int.MaxValue)]
    public int Id { get; set; }

    [Required(ErrorMessage = "El nombre es obligatorio.")]
    [StringLength(200)]
    public string Nombre { get; set; } = string.Empty;

    public bool EsVacaciones { get; set; }
}
