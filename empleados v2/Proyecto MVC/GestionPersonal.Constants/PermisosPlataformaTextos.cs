namespace GestionPersonal.Constants;

/// <summary>Textos en español (Colombia) para permisos — evita mojibake desde BD.</summary>
public static class PermisosPlataformaTextos
{
    private static readonly Dictionary<string, (string Modulo, string Nombre, string? Descripcion)> PorCodigo =
        new(StringComparer.OrdinalIgnoreCase)
        {
            ["Dashboard.Ver"] = ("Dashboard", "Ver dashboard", "Acceso al panel principal con indicadores"),
            ["Empleados.VerListado"] = ("Empleados", "Ver listado de empleados", "Listado y búsqueda de personal"),
            ["Empleados.VerPerfilPropio"] = ("Empleados", "Ver perfil propio", "Solo el perfil del usuario autenticado"),
            ["Empleados.Crear"] = ("Empleados", "Crear empleados", "Alta de nuevos empleados y usuarios"),
            ["Empleados.Editar"] = ("Empleados", "Editar empleados", "Modificar datos de empleados"),
            ["Empleados.Desvincular"] = ("Empleados", "Desvincular empleados", "Proceso de desvinculación"),
            ["EventosLaborales.Ver"] = ("Eventos laborales", "Ver eventos", "Calendario y listado de novedades"),
            ["EventosLaborales.Crear"] = ("Eventos laborales", "Crear eventos", "Registrar permisos, incapacidades, etc."),
            ["EventosLaborales.Editar"] = ("Eventos laborales", "Editar eventos", "Modificar eventos existentes"),
            ["EventosLaborales.Anular"] = ("Eventos laborales", "Anular eventos", "Anulación de eventos registrados"),
            ["Turnos.Ver"] = ("Turnos", "Ver turnos", "Consultar horarios y asignaciones"),
            ["Turnos.Asignar"] = ("Turnos", "Asignar turnos", "Asignar plantillas a empleados"),
            ["Turnos.Plantillas"] = ("Turnos", "Gestionar plantillas", "Crear y editar plantillas de turno"),
            ["HorasExtras.Ver"] = ("Horas extras", "Ver horas extras", "Consultar registros de horas extras"),
            ["HorasExtras.Crear"] = ("Horas extras", "Crear horas extras", "Registrar horas extras"),
            ["HorasExtras.Aprobar"] = ("Horas extras", "Aprobar horas extras", "Aprobar o rechazar solicitudes"),
            ["Solicitudes.Ver"] = ("Solicitudes", "Ver solicitudes", "Mis solicitudes (operario / direccionador)"),
            ["Solicitudes.Crear"] = ("Solicitudes", "Crear solicitudes", "Enviar solicitudes al área de gestión"),
            ["Catalogos.Ver"] = ("Catálogos", "Ver catálogos", "Sedes, cargos y empresas (Director / Admin)"),
            ["Catalogos.Editar"] = ("Catálogos", "Editar catálogos", "CRUD de catálogos operativos"),
            ["DatosMaestros.Gestionar"] = ("Datos maestros", "Gestionar datos maestros", "Sedes, cargos, empresas y roles (Lissy)"),
            ["RolesSistema.Gestionar"] = ("Roles del sistema", "Gestionar roles y permisos", "Definir qué puede hacer cada rol"),
        };

    public static string Modulo(string codigo) =>
        PorCodigo.TryGetValue(codigo, out var t) ? t.Modulo : codigo;

    public static string Nombre(string codigo) =>
        PorCodigo.TryGetValue(codigo, out var t) ? t.Nombre : codigo;

    public static string? Descripcion(string codigo) =>
        PorCodigo.TryGetValue(codigo, out var t) ? t.Descripcion : null;

    public static IReadOnlyDictionary<string, (string Modulo, string Nombre, string? Descripcion)> Todos => PorCodigo;
}
