using GestionPersonal.Models.Enums;
using Microsoft.EntityFrameworkCore;
using Microsoft.EntityFrameworkCore.Metadata.Builders;

namespace GestionPersonal.Models.Entities.GestionPersonalEntities.Configurations;

public class HoraExtraConfiguration : IEntityTypeConfiguration<HoraExtra>
{
    public void Configure(EntityTypeBuilder<HoraExtra> builder)
    {
        builder.ToTable("HorasExtras");
        builder.HasKey(e => e.Id);

        builder.HasIndex(e => new { e.EmpleadoId, e.FechaTrabajada })
            .IsUnique()
            .HasDatabaseName("UX_HorasExtras_Empleado_Fecha_Activa");

        builder.HasIndex(e => new { e.EmpleadoId, e.Estado })
            .HasDatabaseName("IX_HorasExtras_EmpleadoId_Estado");

        builder.HasIndex(e => new { e.FechaTrabajada, e.Estado })
            .HasDatabaseName("IX_HorasExtras_FechaTrabajada");

        builder.Property(e => e.FechaTrabajada).HasColumnType("date").IsRequired();
        builder.Property(e => e.CantidadHoras).HasPrecision(5, 1).IsRequired();
        builder.Property(e => e.Motivo).IsRequired().HasMaxLength(500);
        builder.Property(e => e.MotivoRechazo).HasMaxLength(300);
        builder.Property(e => e.MotivoAnulacion).HasMaxLength(300);
        builder.Property(e => e.FechaAprobacion).HasColumnType("datetime2(0)");
        builder.Property(e => e.FechaAnulacion).HasColumnType("datetime2(0)");
        builder.Property(e => e.FechaCreacion).HasColumnType("datetime2(0)").HasDefaultValueSql("(getutcdate())");

        builder.Property(e => e.Estado)
            .HasConversion<string>()
            .IsRequired()
            .HasMaxLength(20)
            .HasDefaultValue(EstadoHoraExtra.Pendiente);

        builder.HasOne(e => e.Empleado)
            .WithMany(emp => emp.HorasExtras)
            .HasForeignKey(e => e.EmpleadoId)
            .OnDelete(DeleteBehavior.Restrict)
            .HasConstraintName("FK_HorasExtras_Empleado");

        builder.HasOne(e => e.CreadoPorNavigation)
            .WithMany(u => u.HorasExtrasCreadas)
            .HasForeignKey(e => e.CreadoPor)
            .OnDelete(DeleteBehavior.Restrict)
            .HasConstraintName("FK_HorasExtras_CreadoPor");

        builder.HasOne(e => e.AprobadoRechazadoPorNavigation)
            .WithMany(u => u.HorasExtrasAprobadas)
            .HasForeignKey(e => e.AprobadoRechazadoPor)
            .OnDelete(DeleteBehavior.Restrict)
            .HasConstraintName("FK_HorasExtras_AprobadoPor");

        builder.HasOne(e => e.AnuladoPorNavigation)
            .WithMany(u => u.HorasExtrasAnuladas)
            .HasForeignKey(e => e.AnuladoPor)
            .OnDelete(DeleteBehavior.Restrict)
            .HasConstraintName("FK_HorasExtras_AnuladoPor");
    }
}
