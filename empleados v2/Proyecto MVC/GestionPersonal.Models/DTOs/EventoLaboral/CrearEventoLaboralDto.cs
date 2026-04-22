using System.ComponentModel.DataAnnotations;
using GestionPersonal.Models.Enums;

namespace GestionPersonal.Models.DTOs.EventoLaboral;

/// <summary>DTO de entrada para registrar un nuevo evento laboral.</summary>
public class CrearEventoLaboralDto
{
    [Required(ErrorMessage = "El empleado es obligatorio.")]
    [Range(1, int.MaxValue, ErrorMessage = "Selecciona un empleado válido.")]
    public int EmpleadoId { get; set; }

    [Required(ErrorMessage = "El tipo de evento es obligatorio.")]
    public TipoEvento TipoEvento { get; set; }

    [Required(ErrorMessage = "La fecha de inicio es obligatoria.")]
    public DateOnly FechaInicio { get; set; }

    [Required(ErrorMessage = "La fecha de fin es obligatoria.")]
    public DateOnly FechaFin { get; set; }

    // Campos obligatorios solo para Incapacidad
    public TipoIncapacidad? TipoIncapacidad { get; set; }

    [StringLength(200)]
    public string? EntidadExpide { get; set; }

    // Campo obligatorio solo para Permiso
    [StringLength(500)]
    public string? Descripcion { get; set; }

    [Required(ErrorMessage = "El nombre de quien autoriza es obligatorio.")]
    [StringLength(200)]
    public string AutorizadoPor { get; set; } = null!;

    // Documento adjunto (ruta guardada en servidor)
    [StringLength(500)]
    public string? RutaDocumento { get; set; }

    [StringLength(200)]
    public string? NombreDocumento { get; set; }
}
