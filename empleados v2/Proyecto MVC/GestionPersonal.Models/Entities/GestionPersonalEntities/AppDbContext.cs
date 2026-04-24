using Microsoft.EntityFrameworkCore;

namespace GestionPersonal.Models.Entities.GestionPersonalEntities;

public class AppDbContext : DbContext
{
    public AppDbContext(DbContextOptions<AppDbContext> options) : base(options) { }

    // ── Catálogos maestros ───────────────────────────────────
    public DbSet<Sede> Sedes => Set<Sede>();
    public DbSet<Cargo> Cargos => Set<Cargo>();
    public DbSet<EmpresaTemporal> EmpresasTemporales => Set<EmpresaTemporal>();

    // ── Turnos ──────────────────────────────────────────────
    public DbSet<PlantillaTurno> PlantillasTurno => Set<PlantillaTurno>();
    public DbSet<PlantillaTurnoDetalle> PlantillasTurnoDetalle => Set<PlantillaTurnoDetalle>();

    // ── Usuarios y seguridad ────────────────────────────────
    public DbSet<Usuario> Usuarios => Set<Usuario>();
    public DbSet<TokenRecuperacion> TokensRecuperacion => Set<TokenRecuperacion>();

    // ── Empleados ───────────────────────────────────────────
    public DbSet<Empleado> Empleados => Set<Empleado>();
    public DbSet<ContactoEmergencia> ContactosEmergencia => Set<ContactoEmergencia>();
    public DbSet<HistorialDesvinculacion> HistorialDesvinculaciones => Set<HistorialDesvinculacion>();
    public DbSet<AsignacionTurno> AsignacionesTurno => Set<AsignacionTurno>();

    // ── Novedades ───────────────────────────────────────────
    public DbSet<EventoLaboral> EventosLaborales => Set<EventoLaboral>();
    public DbSet<HoraExtra> HorasExtras => Set<HoraExtra>();

    // ── Auditoría de notificaciones ─────────────────────────
    public DbSet<RegistroNotificacion> RegistroNotificaciones => Set<RegistroNotificacion>();

    protected override void OnModelCreating(ModelBuilder modelBuilder)
    {
        // Carga todas las IEntityTypeConfiguration<T> del mismo ensamblado
        modelBuilder.ApplyConfigurationsFromAssembly(typeof(AppDbContext).Assembly);
    }
}
