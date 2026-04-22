namespace GestionPersonal.Models.Models;

public class ResultadoOperacion
{
    public bool   Exito   { get; init; }
    public string Mensaje { get; init; } = string.Empty;

    public static ResultadoOperacion Ok(string mensaje = "")
        => new() { Exito = true, Mensaje = mensaje };

    public static ResultadoOperacion Fail(string mensaje)
        => new() { Exito = false, Mensaje = mensaje };
}

public class ResultadoOperacion<T> : ResultadoOperacion
{
    public T? Datos { get; init; }

    public static ResultadoOperacion<T> Ok(T datos, string mensaje = "")
        => new() { Exito = true, Datos = datos, Mensaje = mensaje };
}
