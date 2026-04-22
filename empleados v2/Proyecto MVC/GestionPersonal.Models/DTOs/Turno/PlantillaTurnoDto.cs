namespace GestionPersonal.Models.DTOs.Turno;

/// <summary>DTO de solo lectura para mostrar una plantilla de turno con sus días.</summary>
public class PlantillaTurnoDto
{
    public int Id { get; init; }
    public string Nombre { get; init; } = null!;
    public string Estado { get; init; } = null!;
    public List<PlantillaTurnoDetalleDto> Detalles { get; init; } = new();
}

public class PlantillaTurnoDetalleDto
{
    public byte DiaSemana { get; init; }    // 1=Lunes … 7=Domingo
    public string? HoraEntrada { get; init; }  // "HH:mm"
    public string? HoraSalida { get; init; }   // "HH:mm"
}
