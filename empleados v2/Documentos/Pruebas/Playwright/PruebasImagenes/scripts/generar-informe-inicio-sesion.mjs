import fs from 'fs';
import path from 'path';
import { fileURLToPath } from 'url';

const __dirname = path.dirname(fileURLToPath(import.meta.url));
const root = path.join(__dirname, '..');
const capturasDir = path.join(root, 'Resultados', 'capturas', 'inicio-sesion');
const metaPath = path.join(capturasDir, 'meta-ejecucion.json');
const outPath = path.join(root, 'Resultados', 'InicioSesionIMG.md');

const img = (file, alt) => `![${alt}](capturas/inicio-sesion/${file})`;

let meta = {
  inicio: new Date().toISOString(),
  resultado: 'UNKNOWN',
  urlExito: '',
  urlFallo: '',
  mensajeError: '',
  usuarios: {
    exito: { correo: 'carlos.rodriguez@yopmail.com', password: 'Usuario1', rol: 'Jefe — Carlos Rodríguez' },
    fallo: { correo: 'carlos.rodriguez@yopmail.com', password: 'WrongPass123', rol: 'Contraseña incorrecta' },
  },
};

if (fs.existsSync(metaPath)) {
  meta = { ...meta, ...JSON.parse(fs.readFileSync(metaPath, 'utf-8')) };
}

const pass = meta.resultado === 'PASS';
const fecha = meta.inicio?.slice(0, 19).replace('T', ' ') ?? 'N/D';

const md = `# Informe de prueba de humo — Inicio de sesión

| Campo | Valor |
|-------|--------|
| **Fecha de ejecución** | ${fecha} |
| **Entorno** | \`http://localhost:5002\` — GestionPersonal (GestiónRH) |
| **Navegador** | Google Chrome (headed, \`slowMo\` 400 ms) |
| **Herramienta** | Playwright + TypeScript |
| **Resultado global** | **${pass ? 'PASS' : meta.resultado || 'FAIL / INCOMPLETO'}** |

---

## Resumen ejecutivo

Se ejecutó una prueba de **humo** acotada al camino crítico de autenticación: cargar la pantalla de login, iniciar sesión con el usuario Jefe del seeding y validar el rechazo ante contraseña incorrecta. ${
  pass
    ? 'Ambos escenarios cumplieron las expectativas; las capturas adjuntas documentan cada paso en Chrome visible.'
    : 'La ejecución no completó todos los criterios; revise mensajes de error y capturas parciales más abajo.'
}

Alcance definido según [Shape Up](https://basecamp.com/shapeup): *small batch*, tiempo fijo y alcance variable. Detalle del pitch en \`Requisitos/Pitch-Humo-InicioSesion-ShapeUp.md\`.

---

## Usuarios utilizados

| Escenario | Rol | Correo | Contraseña | Propósito |
|-----------|-----|--------|------------|-----------|
| Éxito | Jefe (Carlos Rodríguez) | \`${meta.usuarios.exito.correo}\` | \`${meta.usuarios.exito.password}\` | Verificar acceso tras credenciales válidas del seeding |
| Fallo | Misma cuenta | \`${meta.usuarios.fallo.correo}\` | \`${meta.usuarios.fallo.password}\` | Verificar permanencia en login y mensaje de error |

> Fuente de datos: \`Documentos/BD/Seeding_Completo.sql\`.

---

## Alcance Shape Up (must-haves)

- [x] Chrome en modo visible (headed)
- [x] Login exitoso con usuario Jefe
- [x] Login fallido con mensaje en formulario
- [x] Informe con imágenes por paso
- [ ] ~ Casos TC-03 / TC-04 (fuera de appetite — *no-gos*)

---

## Pasos ejecutados

### Paso 1 — Abrir pantalla de login

Se navegó a \`/Cuenta/Login\` y se esperó carga de red.

${img('paso-01-login-vacio.png', 'Pantalla de login vacía')}

---

### Paso 2 — Formulario con credenciales válidas (antes de enviar)

Correo: \`${meta.usuarios.exito.correo}\` · Contraseña: \`${meta.usuarios.exito.password}\`

${img('paso-02-formulario-lleno-exito.png', 'Formulario completado — caso éxito')}

---

### Paso 3 — Resultado tras login exitoso

**URL observada:** \`${meta.urlExito || 'N/D'}\`

**Criterio:** redirección a \`/Dashboard\` o \`/Cuenta/CambiarPassword\`.

${img('paso-03-post-login-exito.png', 'Pantalla después del login exitoso')}

---

### Paso 4 — Formulario con contraseña incorrecta

Correo: \`${meta.usuarios.fallo.correo}\` · Contraseña: \`${meta.usuarios.fallo.password}\`

${img('paso-04-formulario-fallo.png', 'Formulario — caso fallo')}

---

### Paso 5 — Mensaje de error en inicio de sesión fallido

**URL observada:** \`${meta.urlFallo || 'N/D'}\` (debe permanecer en Login)

**Mensaje(s) en pantalla (selector \`.form-error\`):**

> ${meta.mensajeError ? `**${meta.mensajeError}**` : '_No se capturó texto de error — revisar captura o DOM._'}

${img('paso-05-mensaje-error-fallo.png', 'Login fallido con mensaje de error visible')}

---

## Mensajes ante fallo de inicio de sesión

| Situación | Comportamiento esperado | Observado |
|-----------|-------------------------|-----------|
| Contraseña incorrecta | Permanece en \`/Cuenta/Login\`; error en \`.form-error\` (ej. *Datos incorrectos*) | ${meta.mensajeError ? `\`${meta.mensajeError}\`` : 'Ver captura paso 5'} |
| App no disponible | \`ERR_CONNECTION_REFUSED\` | No aplica en esta ejecución |
| Credenciales válidas pero sin redirección | Fallo de assertion Playwright | ${pass ? 'No ocurrió' : 'Revisar meta-ejecucion.json'} |

---

## Comandos para reproducir

\`\`\`powershell
cd "c:\\Users\\alejandro.ortiz\\Documents\\helpharma\\Desarrollos\\lissy\\IA\\LissyIAHelpharma\\empleados v2\\Documentos\\Pruebas\\Playwright\\PruebasImagenes"
npm install
npx playwright install chrome
npx playwright test tests/smoke-inicio-sesion.spec.ts --headed --project=chrome
node scripts/generar-informe-inicio-sesion.mjs
\`\`\`

---

## Referencias

- \`Requisitos/Especificacion-Sistema-Prueba-Humo-InicioSesion.md\`
- \`Requisitos/Pitch-Humo-InicioSesion-ShapeUp.md\`
- \`../../Plan-Ejecucion-Playwright-Login.md\`
`;

fs.mkdirSync(path.dirname(outPath), { recursive: true });
fs.writeFileSync(outPath, md, 'utf-8');
console.log('Informe generado:', outPath);
