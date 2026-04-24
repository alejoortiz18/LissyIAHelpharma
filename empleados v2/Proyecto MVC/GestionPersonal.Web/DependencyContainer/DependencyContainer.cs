using AutoMapper;
using GestionPersonal.Application.AccessDependency;
using GestionPersonal.Helpers.AccessDependency;
using GestionPersonal.Infrastructure.AccessDependency;
using GestionPersonal.Models.Models.Email;
using GestionPersonal.Web.AutoMapper;
using Microsoft.AspNetCore.Authentication.Cookies;
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

        services.AddAuthentication(CookieAuthenticationDefaults.AuthenticationScheme)
            .AddCookie(options =>
            {
                options.LoginPath         = "/Cuenta/Login";
                options.LogoutPath        = "/Cuenta/Logout";
                options.AccessDeniedPath  = "/Cuenta/Acceso-Denegado";
                options.ExpireTimeSpan    = TimeSpan.FromMinutes(30);
                options.SlidingExpiration = true;
                options.Cookie.HttpOnly   = true;
                options.Cookie.SecurePolicy = CookieSecurePolicy.Always;
                options.Cookie.SameSite   = SameSiteMode.Strict;
            });

        services.AddAuthorization();

        services.AddControllersWithViews(options =>
            options.Filters.Add(new ResponseCacheAttribute
            {
                NoStore  = true,
                Location = ResponseCacheLocation.None
            }));

        return services;
    }
}
