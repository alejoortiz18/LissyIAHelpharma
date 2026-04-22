using GestionPersonal.Helpers.Email;
using GestionPersonal.Helpers.Security;
using Microsoft.Extensions.DependencyInjection;

namespace GestionPersonal.Helpers.AccessDependency;

public static class HelperAccessDependency
{
    public static IServiceCollection AddHelpers(this IServiceCollection services)
    {
        services.AddScoped<IEmailHelper, EmailHelper>();
        services.AddScoped<ICodigoHelper, CodigoGeneradorHelper>();
        return services;
    }
}
