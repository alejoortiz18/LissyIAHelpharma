using AutoMapper;
using GestionPersonal.Application.AccessDependency;
using GestionPersonal.Helpers.AccessDependency;
using GestionPersonal.Infrastructure.AccessDependency;
using GestionPersonal.Models.Models.Email;
using GestionPersonal.Web.AutoMapper;
using Microsoft.AspNetCore.Authentication.Cookies;
using Microsoft.AspNetCore.Http;
using Microsoft.AspNetCore.Mvc;
using Microsoft.Extensions.Configuration;
using Microsoft.Extensions.DependencyInjection;

namespace GestionPersonal.Web.DependencyContainer;

public static class DependencyContainer
{
    public static IServiceCollection DependencyInjection(
        this IServiceCollection services, IConfiguration configuration)
    {
        services.Configure<EmailSettings>(configuration.GetSection(EmailSettings.SectionName));
        services.AddInfrastructure(configuration);
        services.AddApplication();
        services.AddHelpers();

        services.AddAutoMapper(cfg => cfg.AddProfile<AutoMapperURT>());

        var environmentName =
            Environment.GetEnvironmentVariable("ASPNETCORE_ENVIRONMENT")
            ?? Environment.GetEnvironmentVariable("DOTNET_ENVIRONMENT")
            ?? configuration["ASPNETCORE_ENVIRONMENT"]
            ?? configuration["DOTNET_ENVIRONMENT"];

        var esDesarrollo = string.Equals(
            environmentName, "Development",
            StringComparison.OrdinalIgnoreCase);

        services.AddAuthentication(CookieAuthenticationDefaults.AuthenticationScheme)
            .AddCookie(options =>
            {
                options.LoginPath         = "/Cuenta/Login";
                options.LogoutPath        = "/Cuenta/Logout";
                options.AccessDeniedPath  = "/Cuenta/Acceso-Denegado";
                options.ExpireTimeSpan    = TimeSpan.FromMinutes(30);
                options.SlidingExpiration = true;
                options.Cookie.HttpOnly   = true;
                // En Development (HTTP local) permitir cookie; en producción exige HTTPS.
                options.Cookie.SecurePolicy = esDesarrollo
                    ? CookieSecurePolicy.SameAsRequest
                    : CookieSecurePolicy.Always;
                options.Cookie.SameSite   = SameSiteMode.Strict;
            });

        services.AddAuthorization();

        // SameAsRequest: en HTTP local (p. ej. IIS con Production) la cookie sí se envía; en HTTPS prod sigue siendo Secure.
        services.AddAntiforgery(options =>
        {
            options.Cookie.SecurePolicy = CookieSecurePolicy.SameAsRequest;
            options.Cookie.HttpOnly     = true;
            options.Cookie.SameSite     = SameSiteMode.Lax;
        });

        services.AddControllersWithViews(options =>
            options.Filters.Add(new ResponseCacheAttribute
            {
                NoStore  = true,
                Location = ResponseCacheLocation.None
            }));

        return services;
    }
}
