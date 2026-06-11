using FluentAssertions;
using GestionPersonal.Helpers;

namespace GestionPersonal.Tests.Helpers;

public class DateParseHelperTests
{
    [Theory]
    [InlineData("22/05/1990", 1990, 5, 22)]
    [InlineData("1990-05-22", 1990, 5, 22)]
    [InlineData("1/3/2024", 2024, 3, 1)]
    public void ParseFlexible_AceptaFormatosComunes(string input, int y, int m, int d)
    {
        var result = DateParseHelper.ParseFlexible(input);
        result.Should().Be(new DateOnly(y, m, d));
    }

    [Theory]
    [InlineData(null)]
    [InlineData("")]
    [InlineData("   ")]
    public void ParseFlexible_VacioRetornaNull(string? input)
    {
        DateParseHelper.ParseFlexible(input).Should().BeNull();
    }

    [Fact]
    public void ParseFlexible_TextoInvalidoRetornaNull()
    {
        DateParseHelper.ParseFlexible("no-es-fecha").Should().BeNull();
    }
}
