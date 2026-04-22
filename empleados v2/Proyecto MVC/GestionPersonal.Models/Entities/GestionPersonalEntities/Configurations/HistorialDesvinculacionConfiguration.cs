using Microsoft.EntityFrameworkCore;
using Microsoft.EntityFrameworkCore.Metadata.Builders;

namespace GestionPersonal.Models.Entities.GestionPersonalEntities.Configurations;

public class HistorialDesvinculacionConfiguration : IEntityTypeConfiguration<HistorialDesvinculacion>
{
    public void Configure(EntityTypeBuilder<HistorialDesvinculacion> builder)
    {
        builder.ToTable("HistorialDesvinculaciones");
        builder.HasKey(e => e.Id);

        builder.HasIndex(e => e.EmpleadoId)
            .HasDatabaseName("IX_HistorialDesvinc_EmpleadoId");

        builder.Property(e => e.MotivoRetiro).IsRequired().HasMaxLength(500);
        builder.Property(e => e.FechaDesvinculacion).HasColumnType("date");
        builder.Property(e => e.FechaCreacion).HasColumnType("datetime2(0)").HasDefaultValueSql("(getutcdate())");

        builder.HasOne(e => e.Empleado)
            .WithMany(emp => emp.HistorialDesvinculaciones)
            .HasForeignKey(e => e.EmpleadoId)
            .OnDelete(DeleteBehavior.Restrict)
            .HasConstraintName("FK_HistorialDesvinc_Empleado");

        builder.HasOne(e => e.RegistradoPorNavigation)
            .WithMany(u => u.HistorialDesvinculacionesRegistrados)
            .HasForeignKey(e => e.RegistradoPor)
            .OnDelete(DeleteBehavior.Restrict)
            .HasConstraintName("FK_HistorialDesvinc_RegistradoPor");
    }
}
