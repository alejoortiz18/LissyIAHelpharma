using System.Numerics;

namespace GestionPersonal.Helpers.Security;

public class CodigoGeneradorHelper : ICodigoHelper
{
    public string GenerarCodigoUnico()
    {
        BigInteger bigInt = new BigInteger(Guid.NewGuid().ToByteArray());
        if (bigInt < 0) bigInt = -bigInt;
        return Base36Encode(bigInt)[..8].ToUpper();
    }

    private static string Base36Encode(BigInteger value)
    {
        const string Caracteres = "0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZ";
        var resultado = new System.Text.StringBuilder();

        do
        {
            resultado.Insert(0, Caracteres[(int)(value % 36)]);
            value /= 36;
        }
        while (value > 0);

        return resultado.ToString();
    }
}
