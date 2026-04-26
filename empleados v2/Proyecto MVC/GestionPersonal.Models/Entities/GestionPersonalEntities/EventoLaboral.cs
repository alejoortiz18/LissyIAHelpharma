using GestionPersonal.Models.Enums;

namespace GestionPersonal.Models.Entities.GestionPersonalEntities;

public class EventoLaboral
{
    public int Id { get; set; }
    public int EmpleadoId { get; set; }
    public TipoEvento TipoEvento { get; set; }
    public DateOnly FechaInicio { get; set; }
    public DateOnly FechaFin { get; set; }
    public EstadoEvento Estado { get; set; }

    // Solo para Incapacidad
    public TipoIncapacidad? TipoIncapacidad { get; set; }
    public string? EntidadExpide { get; set; }

    // Solo para Permiso
    public string? Descripcion { get; set; }

    /// <summary>Días explícitamente solicitados para vacaciones. Null para otros tipos de evento.</summary>
    public int? DiasDisfrutar { get; set; }

    public string AutorizadoPor { get; set; } = null!;
    public string? MotivoAnulacion { get; set; }
    public string? RutaDocumento { get; set; }
    public string? NombreDocumento { get; set; }

    public int CreadoPor { get; set; }
    public DateTime FechaCreacion { get; set; }
    public DateTime? FechaModificacion { get; set; }
    public int? AnuladoPor { get; set; }

    public virtual Empleado Empleado { get; set; } = null!;
    public virtual Usuario CreadoPorNavigation { get; set; } = null!;
    public virtual Usuario? AnuladoPorNavigation { get; set; }
}
