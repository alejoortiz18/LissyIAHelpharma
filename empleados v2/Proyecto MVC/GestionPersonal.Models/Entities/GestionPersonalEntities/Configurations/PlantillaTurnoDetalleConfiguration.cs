using Microsoft.EntityFrameworkCore;
using Microsoft.EntityFrameworkCore.Metadata.Builders;

namespace GestionPersonal.Models.Entities.GestionPersonalEntities.Configurations;

public class PlantillaTurnoDetalleConfiguration : IEntityTypeConfiguration<PlantillaTurnoDetalle>
{
    public void Configure(EntityTypeBuilder<PlantillaTurnoDetalle> builder)
    {
        builder.ToTable("PlantillasTurnoDetalle");
        builder.HasKey(e => e.Id);

        builder.HasIndex(e => new { e.PlantillaTurnoId, e.DiaSemana })
            .IsUnique()
            .HasDatabaseName("UX_PlantillasTurnoDetalle_Dia");

        builder.Property(e => e.DiaSemana).IsRequired();
        builder.Property(e => e.HoraEntrada).HasColumnType("time(0)");
        builder.Property(e => e.HoraSalida).HasColumnType("time(0)");

        builder.HasOne(e => e.PlantillaTurno)
            .WithMany(p => p.PlantillaTurnoDetalles)
            .HasForeignKey(e => e.PlantillaTurnoId)
            .OnDelete(DeleteBehavior.Restrict)
            .HasConstraintName("FK_PlantillasTurnoDetalle_Plantilla");
    }
}
