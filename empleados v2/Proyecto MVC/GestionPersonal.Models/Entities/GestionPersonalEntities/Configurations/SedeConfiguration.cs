using Microsoft.EntityFrameworkCore;
using Microsoft.EntityFrameworkCore.Metadata.Builders;

namespace GestionPersonal.Models.Entities.GestionPersonalEntities.Configurations;

public class SedeConfiguration : IEntityTypeConfiguration<Sede>
{
    public void Configure(EntityTypeBuilder<Sede> builder)
    {
        builder.ToTable("Sedes");
        builder.HasKey(e => e.Id);

        builder.HasIndex(e => e.Nombre)
            .IsUnique()
            .HasDatabaseName("UX_Sedes_Nombre");

        builder.Property(e => e.Nombre).IsRequired().HasMaxLength(200);
        builder.Property(e => e.Ciudad).IsRequired().HasMaxLength(100);
        builder.Property(e => e.Direccion).IsRequired().HasMaxLength(300);
        builder.Property(e => e.Estado).IsRequired().HasMaxLength(20).HasDefaultValue("Activa");
        builder.Property(e => e.FechaCreacion).HasColumnType("datetime2(0)").HasDefaultValueSql("(getutcdate())");
        builder.Property(e => e.FechaModificacion).HasColumnType("datetime2(0)");
    }
}
