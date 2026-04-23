using GestionPersonal.Models.Enums;

namespace GestionPersonal.Models.DTOs.HoraExtra;

/// <summary>DTO de solo lectura para la tabla de horas extras.</summary>
public class HoraExtraDto
{
    public int Id { get; init; }
    public int EmpleadoId { get; init; }
    public int? JefeInmediatoId { get; init; }
    public string EmpleadoNombre { get; init; } = null!;
    public string SedeNombre { get; init; } = null!;
    public string FechaTrabajada { get; init; } = null!;
    public decimal CantidadHoras { get; init; }
    public string Motivo { get; init; } = null!;
    public string Estado { get; init; } = null!;
    public string? MotivoRechazo { get; init; }
    public string? MotivoAnulacion { get; init; }
    public string? FechaAprobacion { get; init; }
}
