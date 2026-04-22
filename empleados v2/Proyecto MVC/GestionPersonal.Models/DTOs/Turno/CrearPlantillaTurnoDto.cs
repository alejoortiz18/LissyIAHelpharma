using System.ComponentModel.DataAnnotations;

namespace GestionPersonal.Models.DTOs.Turno;

/// <summary>DTO de entrada para crear o editar una plantilla de turno.</summary>
public class CrearPlantillaTurnoDto
{
    [Required(ErrorMessage = "El nombre de la plantilla es obligatorio.")]
    [StringLength(200, ErrorMessage = "El nombre no puede superar 200 caracteres.")]
    public string Nombre { get; set; } = null!;

    /// <summary>7 detalles, uno por día (DiaSemana 1=Lunes..7=Domingo). HoraEntrada/HoraSalida null = no labora.</summary>
    [Required]
    [MinLength(7, ErrorMessage = "Deben enviarse los 7 días de la semana.")]
    [MaxLength(7, ErrorMessage = "Deben enviarse exactamente los 7 días de la semana.")]
    public List<CrearPlantillaTurnoDetalleDto> Detalles { get; set; } = new();
}

public class CrearPlantillaTurnoDetalleDto
{
    [Range(1, 7)]
    public byte DiaSemana { get; set; }
    public TimeOnly? HoraEntrada { get; set; }
    public TimeOnly? HoraSalida { get; set; }
}
