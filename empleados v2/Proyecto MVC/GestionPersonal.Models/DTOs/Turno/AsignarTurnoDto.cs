using System.ComponentModel.DataAnnotations;

namespace GestionPersonal.Models.DTOs.Turno;

/// <summary>DTO para asignar una plantilla de turno a un empleado.</summary>
public class AsignarTurnoDto
{
    [Required(ErrorMessage = "El empleado es obligatorio.")]
    [Range(1, int.MaxValue, ErrorMessage = "Selecciona un empleado válido.")]
    public int EmpleadoId { get; set; }

    [Required(ErrorMessage = "La plantilla de turno es obligatoria.")]
    [Range(1, int.MaxValue, ErrorMessage = "Selecciona una plantilla válida.")]
    public int PlantillaTurnoId { get; set; }

    [Required(ErrorMessage = "La fecha de vigencia es obligatoria.")]
    public DateOnly FechaVigencia { get; set; }
}
