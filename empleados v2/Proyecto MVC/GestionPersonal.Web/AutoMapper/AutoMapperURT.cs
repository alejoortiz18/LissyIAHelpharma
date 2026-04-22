using AutoMapper;
using GestionPersonal.Models.DTOs.Empleado;
using GestionPersonal.Models.Enums;

namespace GestionPersonal.Web.AutoMapper;

public class AutoMapperURT : Profile
{
    public AutoMapperURT()
    {
        CreateMap<EmpleadoDto, EditarEmpleadoDto>()
            .ForMember(dest => dest.FechaNacimiento, opt => opt.MapFrom(src =>
                string.IsNullOrEmpty(src.FechaNacimiento) ? DateOnly.MinValue : DateOnly.Parse(src.FechaNacimiento)))
            .ForMember(dest => dest.NivelEscolaridad, opt => opt.MapFrom(src =>
                string.IsNullOrEmpty(src.NivelEscolaridad)
                    ? NivelEscolaridad.Bachillerato
                    : Enum.Parse<NivelEscolaridad>(src.NivelEscolaridad)))
            .ForMember(dest => dest.FechaInicioContrato, opt => opt.MapFrom(src =>
                string.IsNullOrEmpty(src.FechaInicioContrato) ? (DateOnly?)null : DateOnly.Parse(src.FechaInicioContrato)))
            .ForMember(dest => dest.FechaFinContrato, opt => opt.MapFrom(src =>
                string.IsNullOrEmpty(src.FechaFinContrato) ? (DateOnly?)null : DateOnly.Parse(src.FechaFinContrato)))
            .ForMember(dest => dest.EmpresaTemporalId, opt => opt.Ignore());
    }
}

