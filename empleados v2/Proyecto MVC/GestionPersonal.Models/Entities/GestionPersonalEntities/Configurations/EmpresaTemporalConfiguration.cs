using Microsoft.EntityFrameworkCore;
using Microsoft.EntityFrameworkCore.Metadata.Builders;

namespace GestionPersonal.Models.Entities.GestionPersonalEntities.Configurations;

public class EmpresaTemporalConfiguration : IEntityTypeConfiguration<EmpresaTemporal>
{
    public void Configure(EntityTypeBuilder<EmpresaTemporal> builder)
    {
        builder.ToTable("EmpresasTemporales");
        builder.HasKey(e => e.Id);

        builder.HasIndex(e => e.Nombre)
            .IsUnique()
            .HasDatabaseName("UX_EmpresasTemporales_Nombre");

        builder.Property(e => e.Nombre).IsRequired().HasMaxLength(200);
        builder.Property(e => e.Estado).IsRequired().HasMaxLength(20).HasDefaultValue("Activa");
        builder.Property(e => e.FechaCreacion).HasColumnType("datetime2(0)").HasDefaultValueSql("(getutcdate())");
        builder.Property(e => e.FechaModificacion).HasColumnType("datetime2(0)");
    }
}
