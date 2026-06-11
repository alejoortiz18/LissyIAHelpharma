using Microsoft.EntityFrameworkCore;
using Microsoft.EntityFrameworkCore.Metadata.Builders;

namespace GestionPersonal.Models.Entities.GestionPersonalEntities.Configurations;

public class TipoSolicitudConfiguration : IEntityTypeConfiguration<TipoSolicitud>
{
    public void Configure(EntityTypeBuilder<TipoSolicitud> builder)
    {
        builder.ToTable("TiposSolicitud");
        builder.HasKey(e => e.Id);

        builder.HasIndex(e => e.Codigo)
            .IsUnique()
            .HasDatabaseName("UX_TiposSolicitud_Codigo");

        builder.Property(e => e.Nombre).IsRequired().HasMaxLength(200);
        builder.Property(e => e.Codigo).IsRequired().HasMaxLength(50);
        builder.Property(e => e.EsVacaciones).HasDefaultValue(false);
        builder.Property(e => e.Estado).IsRequired().HasMaxLength(20).HasDefaultValue("Activo");
        builder.Property(e => e.FechaCreacion).HasColumnType("datetime2(0)").HasDefaultValueSql("(getutcdate())");
        builder.Property(e => e.FechaModificacion).HasColumnType("datetime2(0)");
    }
}
