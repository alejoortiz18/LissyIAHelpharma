using GestionPersonal.Models.Enums;

namespace GestionPersonal.Models.DTOs.EventoLaboral;

/// <summary>DTO de solo lectura para la tabla de eventos laborales.</summary>
public class EventoLaboralDto
{
    public int Id { get; init; }
    public int EmpleadoId { get; init; }
    public int? JefeInmediatoId { get; init; }
    public string EmpleadoNombre { get; init; } = null!;
    public string SedeNombre { get; init; } = null!;
    public string TipoEvento { get; init; } = null!;
    public string FechaInicio { get; init; } = null!;
    public string FechaFin { get; init; } = null!;
    public int DiasSolicitados { get; init; }
    public string? TipoIncapacidad { get; init; }
    public string? EntidadExpide { get; init; }
    public string? Descripcion { get; init; }
    public string AutorizadoPor { get; init; } = null!;
    public string Estado { get; init; } = null!;
    public string? MotivoAnulacion { get; init; }
    public string? RutaDocumento { get; init; }
    public string? NombreDocumento { get; init; }
}
