using GestionPersonal.Models.Enums;
using Microsoft.EntityFrameworkCore;
using Microsoft.EntityFrameworkCore.Metadata.Builders;

namespace GestionPersonal.Models.Entities.GestionPersonalEntities.Configurations;

public class EventoLaboralConfiguration : IEntityTypeConfiguration<EventoLaboral>
{
    public void Configure(EntityTypeBuilder<EventoLaboral> builder)
    {
        builder.ToTable("EventosLaborales");
        builder.HasKey(e => e.Id);

        builder.HasIndex(e => new { e.EmpleadoId, e.Estado })
            .HasDatabaseName("IX_EventosLaborales_EmpleadoId_Estado");

        builder.HasIndex(e => new { e.FechaInicio, e.FechaFin, e.Estado })
            .HasDatabaseName("IX_EventosLaborales_Fechas_Estado");

        // Enums → string
        builder.Property(e => e.TipoEvento)
            .HasConversion<string>()
            .IsRequired()
            .HasMaxLength(30);

        builder.Property(e => e.Estado)
            .HasConversion<string>()
            .IsRequired()
            .HasMaxLength(20)
            .HasDefaultValue(EstadoEvento.Activo);

        builder.Property(e => e.TipoIncapacidad)
            .HasConversion<string>()
            .HasMaxLength(50);

        builder.Property(e => e.EntidadExpide).HasMaxLength(200);
        builder.Property(e => e.Descripcion).HasMaxLength(500);
        builder.Property(e => e.AutorizadoPor).IsRequired().HasMaxLength(200);
        builder.Property(e => e.MotivoAnulacion).HasMaxLength(300);
        builder.Property(e => e.RutaDocumento).HasMaxLength(500);
        builder.Property(e => e.NombreDocumento).HasMaxLength(200);
        builder.Property(e => e.FechaInicio).HasColumnType("date");
        builder.Property(e => e.FechaFin).HasColumnType("date");
        builder.Property(e => e.FechaCreacion).HasColumnType("datetime2(0)").HasDefaultValueSql("(getutcdate())");
        builder.Property(e => e.FechaModificacion).HasColumnType("datetime2(0)");

        builder.HasOne(e => e.Empleado)
            .WithMany(emp => emp.EventosLaborales)
            .HasForeignKey(e => e.EmpleadoId)
            .OnDelete(DeleteBehavior.Restrict)
            .HasConstraintName("FK_EventosLaborales_Empleado");

        builder.HasOne(e => e.CreadoPorNavigation)
            .WithMany(u => u.EventosLaboralesCreados)
            .HasForeignKey(e => e.CreadoPor)
            .OnDelete(DeleteBehavior.Restrict)
            .HasConstraintName("FK_EventosLaborales_CreadoPor");

        builder.HasOne(e => e.AnuladoPorNavigation)
            .WithMany(u => u.EventosLaboralesAnulados)
            .HasForeignKey(e => e.AnuladoPor)
            .OnDelete(DeleteBehavior.Restrict)
            .HasConstraintName("FK_EventosLaborales_AnuladoPor");
    }
}
