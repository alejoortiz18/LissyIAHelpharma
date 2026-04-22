using GestionPersonal.Models.Enums;
using Microsoft.EntityFrameworkCore;
using Microsoft.EntityFrameworkCore.Metadata.Builders;

namespace GestionPersonal.Models.Entities.GestionPersonalEntities.Configurations;

public class EmpleadoConfiguration : IEntityTypeConfiguration<Empleado>
{
    public void Configure(EntityTypeBuilder<Empleado> builder)
    {
        builder.ToTable("Empleados");
        builder.HasKey(e => e.Id);

        builder.HasIndex(e => e.Cedula)
            .IsUnique()
            .HasDatabaseName("UX_Empleados_Cedula");

        builder.HasIndex(e => e.CorreoElectronico)
            .IsUnique()
            .HasDatabaseName("UX_Empleados_Correo")
            .HasFilter("[CorreoElectronico] IS NOT NULL");

        builder.HasIndex(e => new { e.SedeId, e.Estado })
            .HasDatabaseName("IX_Empleados_SedeId_Estado");

        builder.HasIndex(e => e.CargoId)
            .HasDatabaseName("IX_Empleados_CargoId");

        builder.HasIndex(e => e.JefeInmediatoId)
            .HasDatabaseName("IX_Empleados_JefeInmediatoId")
            .HasFilter("[JefeInmediatoId] IS NOT NULL");

        // Propiedades básicas
        builder.Property(e => e.NombreCompleto).IsRequired().HasMaxLength(200);
        builder.Property(e => e.Cedula).IsRequired().HasMaxLength(20);
        builder.Property(e => e.FechaNacimiento).HasColumnType("date");
        builder.Property(e => e.Telefono).HasMaxLength(20);
        builder.Property(e => e.CorreoElectronico).HasMaxLength(256);
        builder.Property(e => e.Direccion).HasMaxLength(300);
        builder.Property(e => e.Ciudad).HasMaxLength(100);
        builder.Property(e => e.Departamento).HasMaxLength(100);
        builder.Property(e => e.Eps).HasMaxLength(200);
        builder.Property(e => e.Arl).HasMaxLength(200);

        // Enums → string (nombre del enum coincide con valor en BD)
        builder.Property(e => e.NivelEscolaridad)
            .HasConversion<string>()
            .HasMaxLength(30);

        builder.Property(e => e.TipoVinculacion)
            .HasConversion<string>()
            .IsRequired()
            .HasMaxLength(20);

        builder.Property(e => e.Estado)
            .HasConversion<string>()
            .IsRequired()
            .HasMaxLength(20)
            .HasDefaultValue(EstadoEmpleado.Activo);

        // Fechas
        builder.Property(e => e.FechaIngreso).HasColumnType("date").IsRequired();
        builder.Property(e => e.FechaInicioContrato).HasColumnType("date");
        builder.Property(e => e.FechaFinContrato).HasColumnType("date");
        builder.Property(e => e.DiasVacacionesPrevios).HasPrecision(5, 1).HasDefaultValue(0m);
        builder.Property(e => e.FechaCreacion).HasColumnType("datetime2(0)").HasDefaultValueSql("(getutcdate())");
        builder.Property(e => e.FechaModificacion).HasColumnType("datetime2(0)");

        // Relaciones con DeleteBehavior.Restrict (evitar cascadas)
        builder.HasOne(e => e.Sede)
            .WithMany(s => s.Empleados)
            .HasForeignKey(e => e.SedeId)
            .OnDelete(DeleteBehavior.Restrict)
            .HasConstraintName("FK_Empleados_Sedes");

        builder.HasOne(e => e.Cargo)
            .WithMany(c => c.Empleados)
            .HasForeignKey(e => e.CargoId)
            .OnDelete(DeleteBehavior.Restrict)
            .HasConstraintName("FK_Empleados_Cargos");

        builder.HasOne(e => e.Usuario)
            .WithOne(u => u.Empleado)
            .HasForeignKey<Empleado>(e => e.UsuarioId)
            .OnDelete(DeleteBehavior.Restrict)
            .HasConstraintName("FK_Empleados_Usuarios");

        builder.HasOne(e => e.EmpresaTemporal)
            .WithMany(et => et.Empleados)
            .HasForeignKey(e => e.EmpresaTemporalId)
            .OnDelete(DeleteBehavior.Restrict)
            .HasConstraintName("FK_Empleados_EmpresaTemp");

        // Auto-referencia jerarquía
        builder.HasOne(e => e.JefeInmediato)
            .WithMany(j => j.Subordinados)
            .HasForeignKey(e => e.JefeInmediatoId)
            .OnDelete(DeleteBehavior.Restrict)
            .HasConstraintName("FK_Empleados_JefeInmediato");

        // Auditoría
        builder.HasOne(e => e.CreadoPorNavigation)
            .WithMany(u => u.EmpleadosCreadosPor)
            .HasForeignKey(e => e.CreadoPor)
            .OnDelete(DeleteBehavior.Restrict)
            .HasConstraintName("FK_Empleados_CreadoPor");

        builder.HasOne(e => e.ModificadoPorNavigation)
            .WithMany(u => u.EmpleadosModificadosPor)
            .HasForeignKey(e => e.ModificadoPor)
            .OnDelete(DeleteBehavior.Restrict)
            .HasConstraintName("FK_Empleados_ModificadoPor");
    }
}
