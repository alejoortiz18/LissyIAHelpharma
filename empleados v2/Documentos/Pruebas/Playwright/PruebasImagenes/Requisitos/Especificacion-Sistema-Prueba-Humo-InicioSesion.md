# Especificación para el sistema — Prueba de humo · Inicio de sesión

> **Audiencia:** agente de IA / ejecutor automatizado en Cursor.  
> **Pitch Shape Up:** `Pitch-Humo-InicioSesion-ShapeUp.md`  
> **Salida obligatoria:** `../Resultados/InicioSesionIMG.md`

---

## 1. Objetivo

Ejecutar una **prueba de humo** del inicio de sesión en **GestionPersonal** (`GestiónRH`), levantando la aplicación en **Google Chrome en modo visible (headed)**, usando **Playwright con TypeScript**, y generar un informe markdown con texto explicativo, usuarios utilizados, mensajes de error en fallo e **imágenes** de cada paso.

---

## 2. Precondiciones

1. **Base de datos:** aplicar `Documentos/BD/Seeding_Completo.sql` si no se ha hecho en la sesión.
2. **Aplicación web** en ejecución:

```powershell
cd "c:\Users\alejandro.ortiz\Documents\helpharma\Desarrollos\lissy\IA\LissyIAHelpharma\empleados v2\Proyecto MVC"
dotnet run --project GestionPersonal.Web/GestionPersonal.Web.csproj --launch-profile http
```

3. Confirmar: `http://localhost:5002` responde (HTTP 200 en `/Cuenta/Login`).
4. **Stack de automatización:** Node.js + `@playwright/test` en esta carpeta (`PruebasImagenes`).

---

## 3. Configuración Playwright (obligatoria)

| Parámetro | Valor |
|-----------|--------|
| Navegador | **Google Chrome** (`channel: 'chrome'`) |
| Modo | **Headed** (`headless: false`) |
| `slowMo` | 500–1000 ms (observabilidad) |
| `baseURL` | `http://localhost:5002` |
| Test | `tests/smoke-inicio-sesion.spec.ts` |

```powershell
cd "...\Documentos\Pruebas\Playwright\PruebasImagenes"
npm install
npx playwright install chrome
npx playwright test tests/smoke-inicio-sesion.spec.ts --headed --project=chrome
```

---

## 4. Escenarios a ejecutar

### 4.1 Caso exitoso (must-have)

| Campo | Valor |
|-------|--------|
| Correo | `carlos.rodriguez@yopmail.com` |
| Contraseña | `Usuario1` |
| Selectores | `#CorreoAcceso`, `#inputPassword`, `button[type=submit]` |
| Resultado esperado | URL contiene `/Dashboard` **o** `/Cuenta/CambiarPassword` |
| Capturas | `paso-01-login-vacio.png`, `paso-02-formulario-lleno-exito.png`, `paso-03-post-login-exito.png` |

### 4.2 Caso fallo — contraseña incorrecta (must-have)

| Campo | Valor |
|-------|--------|
| Correo | `carlos.rodriguez@yopmail.com` |
| Contraseña | `WrongPass123` |
| Resultado esperado | Permanece en `/Cuenta/Login`; mensaje visible en `.form-error` (típicamente *"Datos incorrectos"*) |
| Capturas | `paso-04-formulario-fallo.png`, `paso-05-mensaje-error-fallo.png` |

---

## 5. Estructura del informe `InicioSesionIMG.md`

Guardar en: `Resultados/InicioSesionIMG.md`

El informe **debe** incluir:

1. **Encabezado:** título, fecha/hora (ISO), entorno (`localhost:5002`), resultado global (PASS/FAIL/BLOCKED).
2. **Resumen ejecutivo** (3–5 líneas): qué se probó y conclusión.
3. **Usuarios utilizados:** tabla con correo, rol y propósito (éxito vs fallo).
4. **Alcance Shape Up:** appetite, must-haves cubiertos, no-gos respetados (referencia al pitch).
5. **Pasos ejecutados:** lista numerada; cada paso con:
   - Descripción de la acción
   - Resultado observado (URL, assertions)
   - Imagen embebida: `![descripción](../Resultados/capturas/inicio-sesion/<archivo>.png)`
6. **Mensajes en caso de fallo de inicio de sesión:** texto literal del DOM (`.form-error`) o mensaje de excepción Playwright si la app no respondió.
7. **Evidencia de fallo técnico** (si aplica): stack trace resumido, captura del estado de la pantalla.
8. **Comandos ejecutados** (bloque de código) para reproducir.

---

## 6. Rutas de archivos

| Artefacto | Ruta relativa a `PruebasImagenes/` |
|-----------|--------------------------------------|
| Requisitos (este doc) | `Requisitos/Especificacion-Sistema-Prueba-Humo-InicioSesion.md` |
| Pitch Shape Up | `Requisitos/Pitch-Humo-InicioSesion-ShapeUp.md` |
| Capturas | `Resultados/capturas/inicio-sesion/*.png` |
| Informe final | `Resultados/InicioSesionIMG.md` |

---

## 7. Criterios de aceptación

- [ ] Chrome abierto y visible durante la ejecución
- [ ] Login exitoso documentado con al menos 3 capturas
- [ ] Login fallido documentado con mensaje de error textual
- [ ] `InicioSesionIMG.md` creado en `Resultados/`
- [ ] No se ejecutó TC-05 ni flujos que modifiquen `DebeCambiarPassword` más allá del login estándar del Jefe

---

## 8. Instrucción resumida para el agente

```text
Lee Pitch-Humo-InicioSesion-ShapeUp.md y esta especificación.
Asegura que la app corre en http://localhost:5002.
Ejecuta tests/smoke-inicio-sesion.spec.ts con Playwright (Chrome, headed).
Genera Resultados/InicioSesionIMG.md con narrativa, usuarios, mensajes de error e imágenes embebidas.
```
