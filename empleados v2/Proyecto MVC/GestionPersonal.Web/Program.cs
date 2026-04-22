using GestionPersonal.Web.DependencyContainer;

var builder = WebApplication.CreateBuilder(args);

builder.Services.DependencyInjection(builder.Configuration);

var app = builder.Build();

if (!app.Environment.IsDevelopment())
{
    app.UseExceptionHandler("/Home/Error");
    app.UseHsts();
}

app.UseHttpsRedirection();
app.UseStaticFiles();
app.UseRouting();
app.UseAuthentication();
app.UseAuthorization();

// Ruta estándar: /Controller/Action/id — permite que /Dashboard resuelva a Dashboard/Index
app.MapControllerRoute(
    name: "standard",
    pattern: "{controller}/{action=Index}/{id?}");

// Ruta raíz: / → CuentaController.Login (página de inicio de sesión por defecto)
app.MapControllerRoute(
    name: "default",
    pattern: "{controller=Cuenta}/{action=Login}/{id?}");

app.Run();
