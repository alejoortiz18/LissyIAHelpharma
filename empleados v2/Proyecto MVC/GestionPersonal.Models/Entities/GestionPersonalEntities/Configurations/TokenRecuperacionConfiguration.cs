using Microsoft.EntityFrameworkCore;
using Microsoft.EntityFrameworkCore.Metadata.Builders;

namespace GestionPersonal.Models.Entities.GestionPersonalEntities.Configurations;

public class TokenRecuperacionConfiguration : IEntityTypeConfiguration<TokenRecuperacion>
{
    public void Configure(EntityTypeBuilder<TokenRecuperacion> builder)
    {
        builder.ToTable("TokensRecuperacion");
        builder.HasKey(e => e.Id);

        builder.HasIndex(e => e.Token)
            .IsUnique()
            .HasDatabaseName("UX_TokensRecuperacion_Token");

        builder.Property(e => e.Token).IsRequired().HasMaxLength(256);
        builder.Property(e => e.FechaExpiracion).HasColumnType("datetime2(0)");
        builder.Property(e => e.Usado).HasDefaultValue(false);
        builder.Property(e => e.FechaCreacion).HasColumnType("datetime2(0)").HasDefaultValueSql("(getutcdate())");

        builder.HasOne(e => e.Usuario)
            .WithMany(u => u.TokensRecuperacion)
            .HasForeignKey(e => e.UsuarioId)
            .OnDelete(DeleteBehavior.Restrict)
            .HasConstraintName("FK_TokensRecuperacion_Usuario");
    }
}
