---
name: dotnet-testing
description: |
  Pruebas unitarias para proyectos ASP.NET Core MVC con C# usando xUnit, Moq y FluentAssertions.
  Úsalo cuando escribas tests para Services, Repositories, Helpers o Controllers del proyecto GestionPersonal.
  Cubre: configuración del proyecto de pruebas, patrones AAA (Arrange/Act/Assert), mock de interfaces
  con Moq, afirmaciones legibles con FluentAssertions, y pruebas de ResultadoOperacion<T>.
  Triggers: "escribir prueba", "unit test", "test unitario", "probar servicio", "mockear repositorio",
  "xUnit", "Moq", "FluentAssertions", "pruebas C#", "test EmpleadoService", "test CuentaService".
metadata:
  author: custom
  version: "1.0.0"
---

# Testing Unitario – ASP.NET Core MVC (.NET)

Guía para escribir pruebas unitarias en el proyecto **GestionPersonal** usando xUnit + Moq + FluentAssertions.

## Configuración del Proyecto de Pruebas

### Crear el proyecto

```bash
dotnet new xunit -n GestionPersonal.Tests
dotnet sln GestionPersonal.slnx add GestionPersonal.Tests/GestionPersonal.Tests.csproj
```

### Paquetes NuGet requeridos

```xml
<!-- GestionPersonal.Tests/GestionPersonal.Tests.csproj -->
<ItemGroup>
  <PackageReference Include="Microsoft.NET.Test.Sdk"      Version="17.*" />
  <PackageReference Include="xunit"                       Version="2.*" />
  <PackageReference Include="xunit.runner.visualstudio"   Version="2.*" />
  <PackageReference Include="Moq"                         Version="4.*" />
  <PackageReference Include="FluentAssertions"            Version="6.*" />
  <PackageReference Include="coverlet.collector"          Version="6.*" />
</ItemGroup>

<!-- Referencias a proyectos del dominio -->
<ItemGroup>
  <ProjectReference Include="..\GestionPersonal.Application\GestionPersonal.Application.csproj" />
  <ProjectReference Include="..\GestionPersonal.Domain\GestionPersonal.Domain.csproj" />
  <ProjectReference Include="..\GestionPersonal.Models\GestionPersonal.Models.csproj" />
  <ProjectReference Include="..\GestionPersonal.Helpers\GestionPersonal.Helpers.csproj" />
  <ProjectReference Include="..\GestionPersonal.Constants\GestionPersonal.Constants.csproj" />
</ItemGroup>
```

### Estructura de carpetas del proyecto de pruebas

```
GestionPersonal.Tests/
├── Services/
│   ├── EmpleadoServiceTests.cs
│   ├── CuentaServiceTests.cs
│   └── EventoLaboralServiceTests.cs
├── Helpers/
│   ├── PasswordHelperTests.cs
│   └── CodigoHelperTests.cs
└── Builders/                      ← Objetos de prueba reutilizables (opcional)
    ├── EmpleadoBuilder.cs
    └── UsuarioBuilder.cs
```

## Patrón AAA (Arrange / Act / Assert)

Siempre estructura cada test con tres secciones bien delimitadas:

```csharp
[Fact]
public async Task MiMetodo_Escenario_ResultadoEsperado()
{
    // Arrange – preparar datos y mocks
    var repo = new Mock<IEmpleadoRepository>();
    repo.Setup(...).ReturnsAsync(...);

    var sut = new EmpleadoService(repo.Object, ...);

    // Act – ejecutar el método bajo prueba
    var resultado = await sut.ObtenerPerfilAsync(1);

    // Assert – verificar el resultado
    resultado.Exito.Should().BeTrue();
    resultado.Datos.Should().NotBeNull();
}
```

## Nombramiento de Tests

Usa el patrón: **`Metodo_Escenario_ResultadoEsperado`**

```
ObtenerPerfilAsync_EmpleadoExiste_RetornaExito
ObtenerPerfilAsync_EmpleadoNoExiste_RetornaFallo
CrearAsync_CedulaDuplicada_RetornaFallo
LoginAsync_CredencialesCorrectas_RetornaUsuarioSesion
LoginAsync_PasswordIncorrecto_RetornaFallo
```

## Ejemplo Completo: EmpleadoService

```csharp
using FluentAssertions;
using GestionPersonal.Application.Interfaces;
using GestionPersonal.Application.Services;
using GestionPersonal.Constants.Messages;
using GestionPersonal.Domain.Interfaces;
using GestionPersonal.Models.DTOs.Empleado;
using GestionPersonal.Models.Entities.GestionPersonalEntities;
using GestionPersonal.Models.Enums;
using Moq;

namespace GestionPersonal.Tests.Services;

public class EmpleadoServiceTests
{
    // ── Mocks compartidos ─────────────────────────────────────────────
    private readonly Mock<IEmpleadoRepository>              _repoMock        = new();
    private readonly Mock<IUsuarioService>                  _usuarioSvcMock  = new();
    private readonly Mock<IHistorialDesvinculacionRepository> _historialMock  = new();

    private EmpleadoService CrearSut() =>
        new(_repoMock.Object, _usuarioSvcMock.Object, _historialMock.Object);

    // ── ObtenerPerfilAsync ────────────────────────────────────────────

    [Fact]
    public async Task ObtenerPerfilAsync_EmpleadoExiste_RetornaExito()
    {
        // Arrange
        var empleado = new Empleado
        {
            Id            = 1,
            NombreCompleto = "Ana García",
            Cedula        = "1234567890",
            Estado        = "Activo"
        };
        _repoMock.Setup(r => r.ObtenerPorIdConDetallesAsync(1, default))
                 .ReturnsAsync(empleado);

        var sut = CrearSut();

        // Act
        var resultado = await sut.ObtenerPerfilAsync(1);

        // Assert
        resultado.Exito.Should().BeTrue();
        resultado.Datos.Should().NotBeNull();
        resultado.Datos!.NombreCompleto.Should().Be("Ana García");
    }

    [Fact]
    public async Task ObtenerPerfilAsync_EmpleadoNoExiste_RetornaFallo()
    {
        // Arrange
        _repoMock.Setup(r => r.ObtenerPorIdConDetallesAsync(99, default))
                 .ReturnsAsync((Empleado?)null);

        var sut = CrearSut();

        // Act
        var resultado = await sut.ObtenerPerfilAsync(99);

        // Assert
        resultado.Exito.Should().BeFalse();
        resultado.Mensaje.Should().Be(EmpleadoConstant.EmpleadoNoEncontrado);
    }

    [Fact]
    public async Task CrearAsync_CedulaDuplicada_RetornaFallo()
    {
        // Arrange
        var dto = new CrearEmpleadoDto { Cedula = "1234567890" };
        _repoMock.Setup(r => r.ExisteCedulaAsync(dto.Cedula, null, default))
                 .ReturnsAsync(true);

        var sut = CrearSut();

        // Act
        var resultado = await sut.CrearAsync(dto, creadoPorUsuarioId: 1);

        // Assert
        resultado.Exito.Should().BeFalse();
        resultado.Mensaje.Should().Be(EmpleadoConstant.CedulaDuplicada);
        _repoMock.Verify(r => r.Agregar(It.IsAny<Empleado>()), Times.Never);
    }
}
```

## Ejemplo Completo: CuentaService

```csharp
using FluentAssertions;
using GestionPersonal.Application.Services;
using GestionPersonal.Constants.Messages;
using GestionPersonal.Domain.Interfaces;
using GestionPersonal.Helpers.Security;
using GestionPersonal.Models.DTOs.Cuenta;
using GestionPersonal.Models.Entities.GestionPersonalEntities;
using Moq;

namespace GestionPersonal.Tests.Services;

public class CuentaServiceTests
{
    private readonly Mock<IUsuarioRepository>          _usuarioRepoMock = new();
    private readonly Mock<ITokenRecuperacionRepository> _tokenRepoMock  = new();
    private readonly Mock<ICodigoHelper>               _codigoMock     = new();
    private readonly Mock<INotificationService>        _notifMock      = new();

    private CuentaService CrearSut() =>
        new(_usuarioRepoMock.Object, _tokenRepoMock.Object,
            _codigoMock.Object, _notifMock.Object);

    [Fact]
    public async Task LoginAsync_UsuarioNoExiste_RetornaFallo()
    {
        // Arrange
        var dto = new LoginDto { Correo = "noexiste@test.com", Password = "pass123" };
        _usuarioRepoMock.Setup(r => r.ObtenerPorCorreoAsync(dto.Correo, default))
                        .ReturnsAsync((Usuario?)null);

        var sut = CrearSut();

        // Act
        var resultado = await sut.LoginAsync(dto);

        // Assert
        resultado.Exito.Should().BeFalse();
        resultado.Mensaje.Should().Be(InicioSesionConstant.UsuarioIncorrecto);
    }

    [Fact]
    public async Task LoginAsync_UsuarioInactivo_RetornaFallo()
    {
        // Arrange
        var dto     = new LoginDto { Correo = "user@test.com", Password = "pass123" };
        var hashSalt = PasswordHelper.HashPassword(dto.Password);
        var usuario = new Usuario
        {
            Correo       = dto.Correo,
            Estado       = "Inactivo",
            PasswordHash = hashSalt.Hash,
            PasswordSalt = hashSalt.Salt
        };
        _usuarioRepoMock.Setup(r => r.ObtenerPorCorreoAsync(dto.Correo, default))
                        .ReturnsAsync(usuario);

        var sut = CrearSut();

        // Act
        var resultado = await sut.LoginAsync(dto);

        // Assert
        resultado.Exito.Should().BeFalse();
        resultado.Mensaje.Should().Be(InicioSesionConstant.UsuarioInactivo);
    }
}
```

## Afirmaciones con FluentAssertions

### ResultadoOperacion

```csharp
// Verificar éxito
resultado.Exito.Should().BeTrue();
resultado.Datos.Should().NotBeNull();
resultado.Datos!.Id.Should().Be(1);

// Verificar fallo con mensaje específico
resultado.Exito.Should().BeFalse();
resultado.Mensaje.Should().Be(EmpleadoConstant.CedulaDuplicada);

// Verificar lista
lista.Should().NotBeEmpty();
lista.Should().HaveCount(3);
lista.Should().ContainSingle(e => e.Estado == "Activo");
```

### Verificar llamadas a mocks (Moq)

```csharp
// El método fue llamado exactamente una vez
_repoMock.Verify(r => r.Agregar(It.IsAny<Empleado>()), Times.Once);

// El método nunca fue llamado
_repoMock.Verify(r => r.Agregar(It.IsAny<Empleado>()), Times.Never);

// GuardarCambios fue llamado
_repoMock.Verify(r => r.GuardarCambiosAsync(It.IsAny<CancellationToken>()), Times.Once);
```

## Tests Parametrizados con `[Theory]`

```csharp
[Theory]
[InlineData("")]
[InlineData(" ")]
[InlineData(null)]
public async Task CrearAsync_CorrienteVacio_RetornaFallo(string? correo)
{
    var dto = new CrearEmpleadoDto { Correo = correo! };

    var resultado = await CrearSut().CrearAsync(dto, creadoPorUsuarioId: 1);

    resultado.Exito.Should().BeFalse();
}
```

## Builders para Objetos de Prueba

Usa builders cuando necesites crear el mismo objeto con variaciones:

```csharp
// Tests/Builders/EmpleadoBuilder.cs
public class EmpleadoBuilder
{
    private readonly Empleado _empleado = new()
    {
        Id            = 1,
        NombreCompleto = "Empleado Test",
        Cedula        = "1111111111",
        Estado        = "Activo"
    };

    public EmpleadoBuilder ConId(int id)         { _empleado.Id = id; return this; }
    public EmpleadoBuilder Inactivo()             { _empleado.Estado = "Inactivo"; return this; }
    public EmpleadoBuilder ConCedula(string c)   { _empleado.Cedula = c; return this; }
    public Empleado Build() => _empleado;
}

// Uso en test:
var empleado = new EmpleadoBuilder().ConId(5).Inactivo().Build();
```

## Ejecutar las Pruebas

```bash
# Desde la raíz del proyecto MVC
dotnet test GestionPersonal.Tests/GestionPersonal.Tests.csproj

# Con cobertura de código
dotnet test --collect:"XPlat Code Coverage"

# Filtrar por nombre
dotnet test --filter "FullyQualifiedName~EmpleadoService"
```

## Qué NO Probar en Unit Tests

| ❌ Evitar | ✅ Alternativa |
|---|---|
| Acceso real a base de datos | Mock del repositorio |
| Envío real de correo | Mock de `INotificationService` |
| Lectura de `appsettings.json` | Pasar opciones como parámetro |
| Pruebas de Controllers con HTTP real | Usar Playwright para E2E o WebApplicationFactory |

## Convenciones del Proyecto

- Un archivo de test por clase de servicio: `{Nombre}ServiceTests.cs`
- Mocks declarados como campos privados de la clase de test
- Método `CrearSut()` privado que instancia el servicio bajo prueba
- Constantes de mensajes tomadas de `GestionPersonal.Constants` (nunca strings literales)
- No usar `[SetUp]`/`[TearDown]` de NUnit — xUnit usa constructor/`IDisposable`
