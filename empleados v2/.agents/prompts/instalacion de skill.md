# SKILL: dotnet-layered-architecture (Operational Enterprise)

## 🎯 OBJETIVO
Este skill define EXACTAMENTE qué debe generar Copilot en cada capa de un proyecto ASP.NET Core MVC con SQL Server.

Copilot debe seguir estas reglas SIN EXCEPCIÓN.

---

# 🧱 ESTRUCTURA DE CAPAS

El sistema se divide en:

- Constants
- Helpers
- Domain
- Application
- Infrastructure
- Web

---

# 📦 CONSTANTS (OBLIGATORIO)

## Qué generar
- Clases estáticas
- Mensajes del sistema
- Plantillas de correo
- Enums

## Qué NO hacer
- ❌ No lógica
- ❌ No dependencias

## Ejemplo esperado

```csharp
public static class UsuarioConstant
{
    public const string UsuarioNoExiste = "Usuario no encontrado";
}

HELPERS (OBLIGATORIO)
Qué generar
Clases reutilizables con interfaz
Implementaciones desacopladas
Helpers obligatorios
EmailHelper
PasswordHelper
CodigoHelper
📧 EmailHelper (OBLIGATORIO)

Copilot debe:

Leer SMTP desde appsettings
Enviar correo async
Soportar HTML
Manejar errores

Ejemplo:

public interface IEmailHelper
{
    Task SendAsync(string to, string subject, string body);
}
🔐 PasswordHelper (OBLIGATORIO)

Copilot debe:

Generar Hash + Salt
Usar PBKDF2
Implementar método Verify

Ejemplo:

public static class PasswordHelper
{
    public static (byte[] Hash, byte[] Salt) CrearHash(string password)
    {
        byte[] salt = RandomNumberGenerator.GetBytes(16);
        using var pbkdf2 = new Rfc2898DeriveBytes(password, salt, 10000, HashAlgorithmName.SHA256);
        return (pbkdf2.GetBytes(32), salt);
    }

    public static bool Verificar(string password, byte[] hash, byte[] salt)
    {
        using var pbkdf2 = new Rfc2898DeriveBytes(password, salt, 10000, HashAlgorithmName.SHA256);
        return pbkdf2.GetBytes(32).SequenceEqual(hash);
    }
}
🔑 CodigoHelper

Copilot debe:

Generar códigos únicos
Usar GUID/Base36

Ejemplo:

public interface ICodigoHelper
{
    string Generar();
}
🧠 DOMAIN (OBLIGATORIO)
Qué generar
Entidades puras
Propiedades
Relaciones
Qué NO hacer
❌ No DbContext
❌ No lógica de negocio compleja

Ejemplo:

public class Empleado
{
    public int Id { get; set; }
    public string Nombre { get; set; }
}
⚙️ APPLICATION (CRÍTICO)
Copilot DEBE generar:
1. Interfaces
public interface IEmpleadoService
{
    Task CrearAsync(Empleado empleado);
}
2. Implementaciones
public class EmpleadoService : IEmpleadoService
{
    public async Task CrearAsync(Empleado empleado)
    {
        if (string.IsNullOrEmpty(empleado.Nombre))
            throw new Exception("Nombre requerido");

        await Task.CompletedTask;
    }
}
RESPONSABILIDADES
Validaciones de negocio
Reglas del sistema
Orquestación
Llamado a repositorios
VALIDACIONES OBLIGATORIAS

Copilot debe validar:

Datos requeridos
Reglas del negocio
Estados del sistema
PROHIBIDO
❌ Acceso directo a DB
❌ Código en Controllers
🗄️ INFRASTRUCTURE
Copilot DEBE generar:
DbContext
Configuración EF Core
Repositorios
RESPONSABILIDADES
Acceso a datos
Queries
Persistencia
REGLAS
Usar async/await
Usar LINQ optimizado
Usar AsNoTracking cuando aplique
🌐 WEB
Copilot DEBE generar:
Controllers
ViewModels
Vistas
RESPONSABILIDADES
Recibir request
Llamar services
Retornar vistas
PROHIBIDO
❌ Lógica de negocio
❌ Acceso a DB
🔌 DEPENDENCY INJECTION (OBLIGATORIO)

Cada capa DEBE tener:

public static class AccessDependency
{
    public static IServiceCollection AddXDependency(this IServiceCollection services)
    {
        return services;
    }
}
🔐 SEGURIDAD (CRÍTICO)
Contraseñas

Copilot DEBE:

Usar Hash + Salt
No guardar texto plano
Cookies

Copilot DEBE:

Configurar autenticación por cookies
Evitar acceso con botón atrás

Ejemplo:

[ResponseCache(NoStore = true, Location = ResponseCacheLocation.None)]
🔄 MAPPING (OBLIGATORIO)

Copilot debe:

Crear DTOs
Crear métodos de conversión

Ejemplo:

public static EmpleadoDto ToDto(this Empleado entity)
🧠 VALIDACIONES (OBLIGATORIO)

Copilot debe usar:

DataAnnotations
IValidatableObject
Validaciones en Services
📧 EMAIL (OBLIGATORIO)

Copilot debe:

Usar templates de Constants
Reemplazar variables
Enviar por SMTP
🗄️ BASE DE DATOS
Flujo obligatorio
Crear DB en SQL Server
Ejecutar:
dotnet ef dbcontext scaffold "connection_string" Microsoft.EntityFrameworkCore.SqlServer -o Entities --context AppDbContext --force
Usar entidades generadas
⚠️ REGLAS CRÍTICAS

Copilot NUNCA debe:

❌ Poner lógica en Controllers
❌ Acceder DB desde Web
❌ Guardar contraseñas sin hash
❌ Hardcodear credenciales

Copilot SIEMPRE debe:

✅ Usar Services
✅ Usar interfaces
✅ Validar datos
✅ Usar async/await
🚀 INSTRUCCIÓN FINAL PARA COPILOT

Cuando generes código:

Identifica la capa correcta
Genera interfaces + implementación
Aplica validaciones
Usa DI
Respeta TODAS las reglas anteriores

Si necesitas generar código para una nueva funcionalidad, sigue esta estructura y reglas al pie de la letra.