namespace GestionPersonal.Helpers.Security;

public static class PasswordHelper
{
    private const int Iteraciones  = 10000;
    private const int TamanioHash  = 32; // 256 bits

    public static (byte[] Hash, byte[] Salt) CrearHash(string password)
    {
        byte[] salt = new byte[16];
        using (var rng = System.Security.Cryptography.RandomNumberGenerator.Create())
            rng.GetBytes(salt);

        using var pbkdf2 = new System.Security.Cryptography.Rfc2898DeriveBytes(
            password, salt, Iteraciones, System.Security.Cryptography.HashAlgorithmName.SHA256);

        return (pbkdf2.GetBytes(TamanioHash), salt);
    }

    public static bool VerificarPassword(string password, byte[] hashGuardado, byte[] saltGuardado)
    {
        using var pbkdf2 = new System.Security.Cryptography.Rfc2898DeriveBytes(
            password, saltGuardado, Iteraciones, System.Security.Cryptography.HashAlgorithmName.SHA256);

        byte[] hashComparar = pbkdf2.GetBytes(TamanioHash);
        return hashComparar.SequenceEqual(hashGuardado);
    }

    public static string GenerarContrasenaTemp(int longitud = 10)
    {
        const string chars = "abcdefghijkmnopqrstuvwxyzABCDEFGHJKLMNPQRSTUVWXYZ23456789!@#";
        var random = System.Security.Cryptography.RandomNumberGenerator.GetBytes(longitud);
        return new string(random.Select(b => chars[b % chars.Length]).ToArray());
    }
}
