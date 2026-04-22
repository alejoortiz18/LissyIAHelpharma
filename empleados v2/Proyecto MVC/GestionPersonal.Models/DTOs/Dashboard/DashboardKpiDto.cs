namespace GestionPersonal.Models.DTOs.Dashboard;

/// <summary>DTO con los KPIs del dashboard principal.</summary>
public class DashboardKpiDto
{
    // Empleados
    public int TotalEmpleados { get; init; }
    public int EmpleadosActivos { get; init; }
    public int EmpleadosInactivos { get; init; }
    public int EmpleadosDirectos { get; init; }
    public int EmpleadosTemporales { get; init; }

    // Novedades hoy
    public int EmpleadosConNovedad { get; init; }
    public int EnVacaciones { get; init; }
    public int ConIncapacidad { get; init; }
    public int ConPermiso { get; init; }

    // Horas extras
    public int HorasExtrasPendientes { get; init; }
    public int HorasExtrasAprobadasEsteMes { get; init; }
    public decimal TotalHorasAprobadasEsteMes { get; init; }
}
