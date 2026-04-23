using System.ComponentModel.DataAnnotations;

namespace GestionPersonal.Models.DTOs.Turno;

/// <summary>DTO para editar una asignación de turno existente.</summary>
public class EditarAsignacionDto
{
    [Required]
    [Range(1, int.MaxValue, ErrorMessage = "Id de asignación inválido.")]
    public int Id { get; set; }

    [Required(ErrorMessage = "La plantilla de turno es obligatoria.")]
    [Range(1, int.MaxValue, ErrorMessage = "Selecciona una plantilla válida.")]
    public int PlantillaTurnoId { get; set; }

    [Required(ErrorMessage = "La fecha de vigencia es obligatoria.")]
    public DateOnly FechaVigencia { get; set; }
}
