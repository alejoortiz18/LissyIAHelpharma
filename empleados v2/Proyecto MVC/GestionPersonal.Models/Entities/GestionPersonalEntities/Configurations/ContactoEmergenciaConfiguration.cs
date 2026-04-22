using Microsoft.EntityFrameworkCore;
using Microsoft.EntityFrameworkCore.Metadata.Builders;

namespace GestionPersonal.Models.Entities.GestionPersonalEntities.Configurations;

public class ContactoEmergenciaConfiguration : IEntityTypeConfiguration<ContactoEmergencia>
{
    public void Configure(EntityTypeBuilder<ContactoEmergencia> builder)
    {
        builder.ToTable("ContactosEmergencia");
        builder.HasKey(e => e.Id);

        builder.HasIndex(e => e.EmpleadoId)
            .HasDatabaseName("IX_ContactosEmergencia_EmpleadoId");

        builder.Property(e => e.NombreContacto).IsRequired().HasMaxLength(200);
        builder.Property(e => e.TelefonoContacto).IsRequired().HasMaxLength(20);

        builder.HasOne(e => e.Empleado)
            .WithOne(emp => emp.ContactoEmergencia)
            .HasForeignKey<ContactoEmergencia>(e => e.EmpleadoId)
            .OnDelete(DeleteBehavior.Restrict)
            .HasConstraintName("FK_ContactosEmergencia_Empleado");
    }
}
