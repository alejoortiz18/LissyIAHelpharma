using GestionPersonal.Models.Enums;

namespace GestionPersonal.Models.Entities.GestionPersonalEntities;

public class HoraExtra
{
    public int Id { get; set; }
    public int EmpleadoId { get; set; }
    public DateOnly FechaTrabajada { get; set; }
    public decimal CantidadHoras { get; set; }
    public string Motivo { get; set; } = null!;
    public EstadoHoraExtra Estado { get; set; }

    public int? AprobadoRechazadoPor { get; set; }
    public DateTime? FechaAprobacion { get; set; }
    public string? MotivoRechazo { get; set; }

    public int? AnuladoPor { get; set; }
    public DateTime? FechaAnulacion { get; set; }
    public string? MotivoAnulacion { get; set; }

    public int CreadoPor { get; set; }
    public DateTime FechaCreacion { get; set; }

    public virtual Empleado Empleado { get; set; } = null!;
    public virtual Usuario? AprobadoRechazadoPorNavigation { get; set; }
    public virtual Usuario? AnuladoPorNavigation { get; set; }
    public virtual Usuario CreadoPorNavigation { get; set; } = null!;
}
