using Microsoft.EntityFrameworkCore;
using Microsoft.EntityFrameworkCore.Metadata.Builders;

namespace GestionPersonal.Models.Entities.GestionPersonalEntities.Configurations;

public class RolSistemaConfiguration : IEntityTypeConfiguration<RolSistema>
{
    public void Configure(EntityTypeBuilder<RolSistema> builder)
    {
        builder.ToTable("RolesSistema");
        builder.HasKey(e => e.Id);
        builder.HasIndex(e => e.Codigo).IsUnique().HasDatabaseName("UX_RolesSistema_Codigo");
        builder.Property(e => e.Codigo).IsRequired().HasMaxLength(50);
        builder.Property(e => e.Nombre).IsRequired().HasMaxLength(200);
        builder.Property(e => e.Descripcion).HasMaxLength(500);
        builder.Property(e => e.Estado).IsRequired().HasMaxLength(20).HasDefaultValue("Activo");
        builder.Property(e => e.FechaCreacion).HasColumnType("datetime2(0)").HasDefaultValueSql("(getutcdate())");
        builder.Property(e => e.FechaModificacion).HasColumnType("datetime2(0)");
    }
}

public class PermisoPlataformaConfiguration : IEntityTypeConfiguration<PermisoPlataforma>
{
    public void Configure(EntityTypeBuilder<PermisoPlataforma> builder)
    {
        builder.ToTable("PermisosPlataforma");
        builder.HasKey(e => e.Id);
        builder.HasIndex(e => e.Codigo).IsUnique().HasDatabaseName("UX_PermisosPlataforma_Codigo");
        builder.Property(e => e.Codigo).IsRequired().HasMaxLength(80);
        builder.Property(e => e.Modulo).IsRequired().HasMaxLength(50);
        builder.Property(e => e.Nombre).IsRequired().HasMaxLength(200);
        builder.Property(e => e.Descripcion).HasMaxLength(500);
    }
}

public class RolSistemaPermisoConfiguration : IEntityTypeConfiguration<RolSistemaPermiso>
{
    public void Configure(EntityTypeBuilder<RolSistemaPermiso> builder)
    {
        builder.ToTable("RolesSistemaPermisos");
        builder.HasKey(e => new { e.RolSistemaId, e.PermisoId });
        builder.HasOne(e => e.RolSistema)
            .WithMany(r => r.Permisos)
            .HasForeignKey(e => e.RolSistemaId)
            .OnDelete(DeleteBehavior.Cascade);
        builder.HasOne(e => e.Permiso)
            .WithMany(p => p.RolesPermisos)
            .HasForeignKey(e => e.PermisoId)
            .OnDelete(DeleteBehavior.Cascade);
    }
}
