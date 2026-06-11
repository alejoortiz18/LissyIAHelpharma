using GestionPersonal.Application.Interfaces;
using GestionPersonal.Web.DependencyContainer;

var builder = WebApplication.CreateBuilder(args);

// IIS: asegurar que la variable de entorno gana sobre JSON vacío (si se define en el servidor).
var smtpPasswordEnv = Environment.GetEnvironmentVariable("EmailSettings__Smtp__Password");
if (!string.IsNullOrWhiteSpace(smtpPasswordEnv))
{
    builder.Configuration.AddInMemoryCollection(new Dictionary<string, string?>
    {
        ["EmailSettings:Smtp:Password"] = smtpPasswordEnv.Trim()
    });
}

builder.Services.DependencyInjection(builder.Configuration);

var app = builder.Build();

var smtpUser = builder.Configuration["EmailSettings:Smtp:Username"];
var smtpPassword = builder.Configuration["EmailSettings:Smtp:Password"];
var smtpFrom = builder.Configuration["EmailSettings:Smtp:FromAddress"];
if (string.IsNullOrWhiteSpace(smtpPassword))
{
    app.Logger.LogWarning(
        "EmailSettings:Smtp:Password está vacío. Configure Password en appsettings.Production.json " +
        "o EmailSettings__Smtp__Password en el servidor.");
}
else if (!app.Environment.IsDevelopment())
{
    app.Logger.LogInformation(
        "SMTP configurado: Host={Host}, User={User}, From={From}, PasswordLength={Len}",
        builder.Configuration["EmailSettings:Smtp:Host"],
        smtpUser,
        smtpFrom,
        smtpPassword.Length);
}

// Solo en local: sincroniza textos de roles. En IIS no debe tumbar el arranque si falta migración o BD.
if (app.Environment.IsDevelopment())
{
    try
    {
        using var scope = app.Services.CreateScope();
        await scope.ServiceProvider
            .GetRequiredService<IRolSistemaService>()
            .SincronizarTextosEspanolAsync();
    }
    catch (Exception ex)
    {
        app.Logger.LogWarning(ex, "Sincronización de textos de roles omitida al iniciar.");
    }
}

if (!app.Environment.IsDevelopment())
{
    app.UseExceptionHandler("/Home/Error");
    app.UseHsts();
}

if (!app.Environment.IsDevelopment())
    app.UseHttpsRedirection();
app.UseStaticFiles();

app.UseRouting();

app.UseAuthentication();
app.UseAuthorization();

app.MapControllerRoute(
    name: "default",
    pattern: "{controller=Cuenta}/{action=Login}/{id?}");

app.Run();
