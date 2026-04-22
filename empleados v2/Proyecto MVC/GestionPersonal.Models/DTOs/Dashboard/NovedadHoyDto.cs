namespace GestionPersonal.Models.DTOs.Dashboard;

/// <summary>DTO para la fila de "Empleados no disponibles hoy" en el dashboard.</summary>
public class NovedadHoyDto
{
    public int EmpleadoId { get; init; }
    public string EmpleadoNombre { get; init; } = null!;
    public string SedeNombre { get; init; } = null!;
    public string TipoNovedad { get; init; } = null!;
    public string Periodo { get; init; } = null!;    // "01/abr – 05/abr"
    public string Estado { get; init; } = null!;
}
