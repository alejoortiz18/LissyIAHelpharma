using GestionPersonal.Models.Enums;
using Microsoft.EntityFrameworkCore;
using Microsoft.EntityFrameworkCore.Metadata.Builders;

namespace GestionPersonal.Models.Entities.GestionPersonalEntities.Configurations;

public class UsuarioConfiguration : IEntityTypeConfiguration<Usuario>
{
    public void Configure(EntityTypeBuilder<Usuario> builder)
    {
        builder.ToTable("Usuarios");
        builder.HasKey(e => e.Id);

        builder.HasIndex(e => e.CorreoAcceso)
            .IsUnique()
            .HasDatabaseName("UX_Usuarios_Correo");

        builder.HasIndex(e => e.SedeId)
            .HasDatabaseName("IX_Usuarios_SedeId");

        builder.Property(e => e.CorreoAcceso).IsRequired().HasMaxLength(256);
        builder.Property(e => e.PasswordHash).IsRequired().HasMaxLength(256);
        builder.Property(e => e.PasswordSalt).IsRequired().HasMaxLength(256);

        builder.Property(e => e.Rol)
            .HasConversion<string>()
            .IsRequired()
            .HasMaxLength(30);

        builder.Property(e => e.Estado).IsRequired().HasMaxLength(20).HasDefaultValue("Activo");
        builder.Property(e => e.DebecambiarPassword).HasDefaultValue(true);
        builder.Property(e => e.FechaCreacion).HasColumnType("datetime2(0)").HasDefaultValueSql("(getutcdate())");
        builder.Property(e => e.FechaModificacion).HasColumnType("datetime2(0)");
        builder.Property(e => e.UltimoAcceso).HasColumnType("datetime2(0)");

        builder.HasOne(e => e.Sede)
            .WithMany(s => s.Usuarios)
            .HasForeignKey(e => e.SedeId)
            .OnDelete(DeleteBehavior.Restrict)
            .HasConstraintName("FK_Usuarios_Sedes");
    }
}
