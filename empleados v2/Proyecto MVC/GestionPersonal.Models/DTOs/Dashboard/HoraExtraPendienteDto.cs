namespace GestionPersonal.Models.DTOs.Dashboard;

/// <summary>DTO para la fila de "Horas extras pendientes" en el dashboard.</summary>
public class HoraExtraPendienteDto
{
    public int Id { get; init; }
    public int EmpleadoId { get; init; }
    public string EmpleadoNombre { get; init; } = null!;
    public string FechaTrabajada { get; init; } = null!;
    public decimal CantidadHoras { get; init; }
    public string Motivo { get; init; } = null!;
}
