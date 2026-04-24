using GestionPersonal.Application.Interfaces;
using GestionPersonal.Application.Services;
using Microsoft.Extensions.DependencyInjection;

namespace GestionPersonal.Application.AccessDependency;

public static class ApplicationAccessDependency
{
    public static IServiceCollection AddApplication(this IServiceCollection services)
    {
        services.AddScoped<ICuentaService, CuentaService>();
        services.AddScoped<IUsuarioService, UsuarioService>();
        services.AddScoped<IEmpleadoService, EmpleadoService>();
        services.AddScoped<IEventoLaboralService, EventoLaboralService>();
        services.AddScoped<IHoraExtraService, HoraExtraService>();
        services.AddScoped<ITurnoService, TurnoService>();
        services.AddScoped<IDashboardService, DashboardService>();
        services.AddScoped<ICatalogoService, CatalogoService>();
        services.AddScoped<IHistorialService, HistorialService>();
        services.AddScoped<INotificationService, NotificationService>();

        return services;
    }
}
