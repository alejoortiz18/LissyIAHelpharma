namespace GestionPersonal.Models.DTOs.EventoLaboral;

/// <summary>DTO con el balance de vacaciones de un empleado.</summary>
public class SaldoVacacionesDto
{
    public int Acumulados { get; init; }
    public int Tomados { get; init; }
    public int Disponibles { get; init; }
}
