using Microsoft.Extensions.Configuration;
using Microsoft.Extensions.DependencyInjection;
using Microsoft.EntityFrameworkCore;
using GestionPersonal.Domain.Interfaces;
using GestionPersonal.Infrastructure.Repositories;
using GestionPersonal.Models.Entities.GestionPersonalEntities;

namespace GestionPersonal.Infrastructure.AccessDependency;

public static class InfrastructureAccessDependency
{
    public static IServiceCollection AddInfrastructure(
        this IServiceCollection services, IConfiguration configuration)
    {
        // AppDbContext vive en GestionPersonal.Models; las Migrations se almacenan aquí
        services.AddDbContext<AppDbContext>(options =>
            options.UseSqlServer(
                configuration.GetConnectionString("Default"),
                sql => sql.MigrationsAssembly("GestionPersonal.Infrastructure")));

        // Repositorios
        services.AddScoped<IEmpleadoRepository, EmpleadoRepository>();
        services.AddScoped<IUsuarioRepository, UsuarioRepository>();
        services.AddScoped<ITokenRecuperacionRepository, TokenRecuperacionRepository>();
        services.AddScoped<IEventoLaboralRepository, EventoLaboralRepository>();
        services.AddScoped<IHoraExtraRepository, HoraExtraRepository>();
        services.AddScoped<ITurnoRepository, TurnoRepository>();
        services.AddScoped<ICatalogoRepository, CatalogoRepository>();
        services.AddScoped<IHistorialDesvinculacionRepository, HistorialDesvinculacionRepository>();

        return services;
    }
}
