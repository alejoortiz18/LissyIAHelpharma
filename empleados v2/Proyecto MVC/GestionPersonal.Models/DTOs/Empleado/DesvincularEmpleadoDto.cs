using System.ComponentModel.DataAnnotations;

namespace GestionPersonal.Models.DTOs.Empleado;

/// <summary>DTO para registrar la desvinculación de un empleado.</summary>
public class DesvincularEmpleadoDto
{
    public int EmpleadoId { get; set; }

    [Required(ErrorMessage = "La fecha de desvinculación es obligatoria.")]
    public DateOnly FechaDesvinculacion { get; set; }

    [Required(ErrorMessage = "El motivo de retiro es obligatorio.")]
    [StringLength(500, ErrorMessage = "El motivo no puede superar 500 caracteres.")]
    public string MotivoRetiro { get; set; } = null!;
}
