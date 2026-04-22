using Microsoft.EntityFrameworkCore;
using Microsoft.EntityFrameworkCore.Metadata.Builders;

namespace GestionPersonal.Models.Entities.GestionPersonalEntities.Configurations;

public class AsignacionTurnoConfiguration : IEntityTypeConfiguration<AsignacionTurno>
{
    public void Configure(EntityTypeBuilder<AsignacionTurno> builder)
    {
        builder.ToTable("AsignacionesTurno");
        builder.HasKey(e => e.Id);

        builder.HasIndex(e => new { e.EmpleadoId, e.FechaVigencia })
            .HasDatabaseName("IX_AsignacionesTurno_EmpleadoId_Vigencia")
            .IsDescending(false, true);

        builder.Property(e => e.FechaVigencia).HasColumnType("date").IsRequired();
        builder.Property(e => e.FechaCreacion).HasColumnType("datetime2(0)").HasDefaultValueSql("(getutcdate())");

        builder.HasOne(e => e.Empleado)
            .WithMany(emp => emp.AsignacionesTurno)
            .HasForeignKey(e => e.EmpleadoId)
            .OnDelete(DeleteBehavior.Restrict)
            .HasConstraintName("FK_AsignacionesTurno_Empleado");

        builder.HasOne(e => e.PlantillaTurno)
            .WithMany(p => p.AsignacionesTurno)
            .HasForeignKey(e => e.PlantillaTurnoId)
            .OnDelete(DeleteBehavior.Restrict)
            .HasConstraintName("FK_AsignacionesTurno_Plantilla");

        builder.HasOne(e => e.ProgramadoPorNavigation)
            .WithMany(u => u.AsignacionesTurnoProgramadas)
            .HasForeignKey(e => e.ProgramadoPor)
            .OnDelete(DeleteBehavior.Restrict)
            .HasConstraintName("FK_AsignacionesTurno_ProgramadoPor");
    }
}
