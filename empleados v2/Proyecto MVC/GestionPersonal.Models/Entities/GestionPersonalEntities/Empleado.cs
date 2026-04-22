using GestionPersonal.Models.Enums;

namespace GestionPersonal.Models.Entities.GestionPersonalEntities;

public class Empleado
{
    public int Id { get; set; }

    // Datos personales
    public string NombreCompleto { get; set; } = null!;
    public string Cedula { get; set; } = null!;
    public DateOnly? FechaNacimiento { get; set; }
    public string? Telefono { get; set; }
    public string? CorreoElectronico { get; set; }

    // Residencia
    public string? Direccion { get; set; }
    public string? Ciudad { get; set; }
    public string? Departamento { get; set; }

    // Formacion
    public NivelEscolaridad? NivelEscolaridad { get; set; }

    // Seguridad social
    public string? Eps { get; set; }
    public string? Arl { get; set; }

    // Vinculacion laboral
    public int SedeId { get; set; }
    public int CargoId { get; set; }
    public int? UsuarioId { get; set; }
    public int? JefeInmediatoId { get; set; }
    public TipoVinculacion TipoVinculacion { get; set; }
    public DateOnly FechaIngreso { get; set; }

    // Contrato temporal
    public int? EmpresaTemporalId { get; set; }
    public DateOnly? FechaInicioContrato { get; set; }
    public DateOnly? FechaFinContrato { get; set; }

    // Estado y vacaciones
    public EstadoEmpleado Estado { get; set; }
    public decimal DiasVacacionesPrevios { get; set; }

    // Auditoria
    public DateTime FechaCreacion { get; set; }
    public int? CreadoPor { get; set; }
    public DateTime? FechaModificacion { get; set; }
    public int? ModificadoPor { get; set; }

    // Navegacion
    public virtual Sede Sede { get; set; } = null!;
    public virtual Cargo Cargo { get; set; } = null!;
    public virtual Usuario? Usuario { get; set; }
    public virtual EmpresaTemporal? EmpresaTemporal { get; set; }
    public virtual Empleado? JefeInmediato { get; set; }
    public virtual ICollection<Empleado> Subordinados { get; set; } = new List<Empleado>();
    public virtual Usuario? CreadoPorNavigation { get; set; }
    public virtual Usuario? ModificadoPorNavigation { get; set; }
    public virtual ContactoEmergencia? ContactoEmergencia { get; set; }
    public virtual ICollection<AsignacionTurno> AsignacionesTurno { get; set; } = new List<AsignacionTurno>();
    public virtual ICollection<EventoLaboral> EventosLaborales { get; set; } = new List<EventoLaboral>();
    public virtual ICollection<HoraExtra> HorasExtras { get; set; } = new List<HoraExtra>();
    public virtual ICollection<HistorialDesvinculacion> HistorialDesvinculaciones { get; set; } = new List<HistorialDesvinculacion>();
}
