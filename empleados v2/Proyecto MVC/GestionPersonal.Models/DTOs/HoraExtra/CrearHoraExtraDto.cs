using System.ComponentModel.DataAnnotations;

namespace GestionPersonal.Models.DTOs.HoraExtra;

/// <summary>DTO de entrada para registrar una solicitud de hora extra.</summary>
public class CrearHoraExtraDto
{
    [Required(ErrorMessage = "El empleado es obligatorio.")]
    [Range(1, int.MaxValue, ErrorMessage = "Selecciona un empleado válido.")]
    public int EmpleadoId { get; set; }

    [Required(ErrorMessage = "La fecha es obligatoria.")]
    public DateOnly FechaTrabajada { get; set; }

    [Required(ErrorMessage = "Las horas extras son obligatorias.")]
    [Range(1, 24, ErrorMessage = "El valor debe estar entre 1 y 24 horas.")]
    public decimal CantidadHoras { get; set; }

    [Required(ErrorMessage = "El motivo es obligatorio.")]
    [StringLength(500, ErrorMessage = "El motivo no puede superar 500 caracteres.")]
    public string Motivo { get; set; } = null!;
}
