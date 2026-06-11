import { test, expect } from '@playwright/test';
import fs from 'fs';
import path from 'path';

const CAPTURAS = path.join(__dirname, '..', 'Resultados', 'capturas', 'inicio-sesion');
const CORREO_JEFE = 'carlos.rodriguez@yopmail.com';
const PASSWORD_OK = 'Usuario1';
const PASSWORD_FAIL = 'WrongPass123';

fs.mkdirSync(CAPTURAS, { recursive: true });

async function captura(page: import('@playwright/test').Page, nombre: string) {
  await page.screenshot({ path: path.join(CAPTURAS, nombre), fullPage: true });
}

async function textoError(page: import('@playwright/test').Page): Promise<string> {
  const resumen = page.locator('.form-error[role="alert"], .alert[role="alert"]');
  const textos: string[] = [];
  for (const el of await resumen.all()) {
    const t = (await el.innerText()).trim();
    if (t) textos.push(t);
  }
  return textos.join(' | ');
}

async function llenarLogin(page: import('@playwright/test').Page, correo: string, password: string) {
  await page.getByLabel(/correo electrónico/i).fill(correo);
  const pwd = page.locator('#inputPassword');
  await pwd.click();
  await pwd.fill(password);
  await expect(pwd).toHaveValue(password);
}

test.describe('Humo — Inicio de sesión', () => {
  test.setTimeout(120_000);

  test('éxito y fallo con evidencia gráfica', async ({ page }) => {
    const meta: Record<string, string> = {
      inicio: new Date().toISOString(),
      resultado: 'FAIL',
    };

    // —— Paso 1: pantalla login ——
    await page.goto('/Cuenta/Login');
    await page.waitForLoadState('networkidle');
    await captura(page, 'paso-01-login-vacio.png');

    // —— Paso 2–3: login exitoso ——
    await llenarLogin(page, CORREO_JEFE, PASSWORD_OK);
    await captura(page, 'paso-02-formulario-lleno-exito.png');
    await page.getByRole('button', { name: /iniciar sesión/i }).click();
    await Promise.race([
      page.getByRole('navigation', { name: /menú principal/i }).waitFor({ state: 'visible', timeout: 25_000 }),
      page.waitForURL(/CambiarPassword/, { timeout: 25_000 }),
    ]);
    meta.urlExito = page.url();
    await captura(page, 'paso-03-post-login-exito.png');

    expect(meta.urlExito).toMatch(/Dashboard|CambiarPassword/);

    // —— Paso 4–5: login fallido (cerrar sesión y volver al login) ——
    await page.goto('/Cuenta/Logout');
    await page.waitForLoadState('networkidle');
    await page.goto('/Cuenta/Login');
    await page.waitForLoadState('networkidle');
    await llenarLogin(page, CORREO_JEFE, PASSWORD_FAIL);
    await captura(page, 'paso-04-formulario-fallo.png');
    await page.getByRole('button', { name: /iniciar sesión/i }).click();
    await page.waitForLoadState('networkidle');
    meta.urlFallo = page.url();
    meta.mensajeError =
      (await textoError(page)) ||
      (await page.locator('.alert, [role="alert"]').first().innerText().catch(() => ''));
    await captura(page, 'paso-05-mensaje-error-fallo.png');

    expect(meta.urlFallo).toMatch(/\/Cuenta\/Login|\/$/);
    expect(meta.mensajeError.length).toBeGreaterThan(0);
    expect(meta.mensajeError.toLowerCase()).toContain('datos incorrectos');

    fs.writeFileSync(
      path.join(CAPTURAS, 'meta-ejecucion.json'),
      JSON.stringify(
        {
          ...meta,
          usuarios: {
            exito: { correo: CORREO_JEFE, password: PASSWORD_OK, rol: 'Jefe — Carlos Rodríguez' },
            fallo: { correo: CORREO_JEFE, password: PASSWORD_FAIL, rol: 'Misma cuenta — contraseña inválida' },
          },
          resultado: 'PASS',
        },
        null,
        2
      ),
      'utf-8'
    );
    meta.resultado = 'PASS';
  });
});
