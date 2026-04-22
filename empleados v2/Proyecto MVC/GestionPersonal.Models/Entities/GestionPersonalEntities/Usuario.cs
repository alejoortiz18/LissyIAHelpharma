using GestionPersonal.Models.Enums;

namespace GestionPersonal.Models.Entities.GestionPersonalEntities;

public class Usuario
{
    public int Id { get; set; }
    public string CorreoAcceso { get; set; } = null!;
    public byte[] PasswordHash { get; set; } = null!;
    public byte[] PasswordSalt { get; set; } = null!;
    public RolUsuario Rol { get; set; }
    public int SedeId { get; set; }
    public bool DebecambiarPassword { get; set; }
    public string Estado { get; set; } = null!;
    public DateTime FechaCreacion { get; set; }
    public DateTime? FechaModificacion { get; set; }
    public DateTime? UltimoAcceso { get; set; }

    public virtual Sede Sede { get; set; } = null!;
    public virtual Empleado? Empleado { get; set; }
    public virtual ICollection<TokenRecuperacion> TokensRecuperacion { get; set; } = new List<TokenRecuperacion>();
    public virtual ICollection<AsignacionTurno> AsignacionesTurnoProgramadas { get; set; } = new List<AsignacionTurno>();
    public virtual ICollection<EventoLaboral> EventosLaboralesCreados { get; set; } = new List<EventoLaboral>();
    public virtual ICollection<EventoLaboral> EventosLaboralesAnulados { get; set; } = new List<EventoLaboral>();
    public virtual ICollection<HoraExtra> HorasExtrasCreadas { get; set; } = new List<HoraExtra>();
    public virtual ICollection<HoraExtra> HorasExtrasAprobadas { get; set; } = new List<HoraExtra>();
    public virtual ICollection<HoraExtra> HorasExtrasAnuladas { get; set; } = new List<HoraExtra>();
    public virtual ICollection<HistorialDesvinculacion> HistorialDesvinculacionesRegistrados { get; set; } = new List<HistorialDesvinculacion>();
    public virtual ICollection<Empleado> EmpleadosCreadosPor { get; set; } = new List<Empleado>();
    public virtual ICollection<Empleado> EmpleadosModificadosPor { get; set; } = new List<Empleado>();
}
