using FluentAssertions;
using GestionPersonal.Models.Enums;
using GestionPersonal.Web.Helpers;

namespace GestionPersonal.Tests.Helpers;

public class EmpleadoAccesoHelperTests
{
    private const int SedeMedellin = 1;
    private const int SedeBogota = 2;

    [Theory]
    [InlineData(RolUsuario.Analista)]
    [InlineData(RolUsuario.Administrador)]
    public void TieneAlcanceMultiSede_RolesGlobales_DevuelveTrue(RolUsuario rol)
    {
        EmpleadoAccesoHelper.TieneAlcanceMultiSede(rol).Should().BeTrue();
    }

    [Theory]
    [InlineData(RolUsuario.DirectorTecnico)]
    [InlineData(RolUsuario.Regente)]
    public void TieneAlcanceMultiSede_RolesPorSede_DevuelveFalse(RolUsuario rol)
    {
        EmpleadoAccesoHelper.TieneAlcanceMultiSede(rol).Should().BeFalse();
    }

    [Fact]
    public void PuedeAccederEmpleado_Analista_CualquierSede()
    {
        EmpleadoAccesoHelper.PuedeAccederEmpleado(RolUsuario.Analista, SedeMedellin, SedeBogota)
            .Should().BeTrue();
    }

    [Fact]
    public void PuedeAccederEmpleado_DirectorTecnico_MismaSede()
    {
        EmpleadoAccesoHelper.PuedeAccederEmpleado(RolUsuario.DirectorTecnico, SedeMedellin, SedeMedellin)
            .Should().BeTrue();
    }

    [Fact]
    public void PuedeAccederEmpleado_DirectorTecnico_OtraSede()
    {
        EmpleadoAccesoHelper.PuedeAccederEmpleado(RolUsuario.DirectorTecnico, SedeMedellin, SedeBogota)
            .Should().BeFalse();
    }
}
