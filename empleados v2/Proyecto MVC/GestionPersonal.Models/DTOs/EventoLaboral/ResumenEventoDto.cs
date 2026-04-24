namespace GestionPersonal.Models.DTOs.EventoLaboral;

/// <summary>Totalizador de días por tipo de evento (para el resumen del tab Historial).</summary>
public class ResumenEventoDto
{
    public string TipoEvento { get; init; } = null!;
    public int TotalDias { get; init; }
}
