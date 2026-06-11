using AutoMapper;
using GestionPersonal.Helpers;
using GestionPersonal.Models.DTOs.Empleado;
using GestionPersonal.Models.Enums;

namespace GestionPersonal.Web.AutoMapper;

public class AutoMapperURT : Profile
{
    public AutoMapperURT()
    {
        CreateMap<EmpleadoDto, EditarEmpleadoDto>()
            .ForMember(dest => dest.FechaNacimiento, opt => opt.MapFrom(src =>
                DateParseHelper.ParseFlexible(src.FechaNacimiento)))
            .ForMember(dest => dest.NivelEscolaridad, opt => opt.MapFrom(src =>
                string.IsNullOrEmpty(src.NivelEscolaridad)
                    ? (NivelEscolaridad?)null
                    : Enum.Parse<NivelEscolaridad>(src.NivelEscolaridad)))
            .ForMember(dest => dest.FechaInicioContrato, opt => opt.MapFrom(src =>
                DateParseHelper.ParseFlexible(src.FechaInicioContrato)))
            .ForMember(dest => dest.FechaFinContrato, opt => opt.MapFrom(src =>
                DateParseHelper.ParseFlexible(src.FechaFinContrato)))
            .ForMember(dest => dest.Rol, opt => opt.MapFrom(src => src.Rol));
    }
}

