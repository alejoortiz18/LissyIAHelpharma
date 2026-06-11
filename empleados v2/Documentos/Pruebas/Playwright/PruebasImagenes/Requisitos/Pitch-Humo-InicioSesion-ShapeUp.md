# Pitch — Prueba de humo: inicio de sesión

> Refinamiento con metodología [Shape Up](https://basecamp.com/shapeup) (Basecamp / 37signals).  
> Documento de **shaping**: define el trabajo antes de ejecutarlo. No es el informe de ejecución.

---

## Ingrediente 1 — Problema

Antes de ampliar la suite E2E de login (TC-01 a TC-07), necesitamos **evidencia rápida y compartible** de que el camino crítico de autenticación sigue operativo: la aplicación responde, el formulario de login acepta credenciales válidas del seeding y rechaza credenciales inválidas con mensajes visibles al usuario.

Sin esta verificación, el equipo puede invertir tiempo en pruebas profundas sobre una base rota (app caída, BD desactualizada o regresión en `/Cuenta/Login`).

**Baseline (sin la prueba):** se asume que el entorno local en `http://localhost:5002` está levantado y que `Seeding_Completo.sql` fue aplicado recientemente.

---

## Ingrediente 2 — Appetite (tiempo fijo, alcance variable)

| Concepto Shape Up | Decisión |
|-------------------|----------|
| **Appetite** | **Small batch** — una sesión corta (≈ 30–45 min), no un ciclo de seis semanas |
| **Time horizon** | Mismo día: levantar app → ejecutar humo → publicar informe |
| **Fixed time, variable scope** | Si algo falla, se documenta y se corta alcance; no se extiende la apuesta |

**Definición de “hecho” (done):** existe `Resultados/InicioSesionIMG.md` con narrativa, usuarios usados, mensajes de error capturados y capturas de pantalla de cada paso acordado.

---

## Ingrediente 3 — Solución (elementos acotados)

### Alcance — un “slice” vertical (Shape Up: *Get one piece done*)

Un único flujo en **Chrome visible** (headed), automatizado con **Playwright (TypeScript)**:

| Paso | Acción | Evidencia |
|------|--------|-----------|
| 1 | Abrir `http://localhost:5002/Cuenta/Login` | Captura: pantalla de login |
| 2 | Login exitoso con usuario Jefe del seeding | Captura: URL post-login (`/Dashboard` o `/Cuenta/CambiarPassword`) |
| 3 | Login fallido (contraseña incorrecta) | Captura: permanece en Login + mensaje `.form-error` |

### Usuarios (datos de prueba)

| Rol | Correo | Contraseña | Uso en humo |
|-----|--------|------------|-------------|
| Jefe (Carlos Rodríguez) | `carlos.rodriguez@yopmail.com` | `Usuario1` | Caso **éxito** |
| Misma cuenta | `carlos.rodriguez@yopmail.com` | `WrongPass123` | Caso **fallo** |

> Fuente: `Documentos/BD/Seeding_Completo.sql` y `Plan-Ejecucion-Playwright-Login.md`.

### Hill chart (estado esperado del trabajo)

```text
        unknown          known              done
           │                │                 │
Humo login ├────────────────┼─────────────────┤
           │  App + BD OK   │  Playwright OK  │  InicioSesionIMG.md
```

- **Uphill:** app no responde, seeding desactualizado, selectores rotos.
- **Downhill:** capturas generadas y markdown publicado.

### Must-haves vs nice-to-haves

| Must-have | Nice-to-have (`~`) |
|-----------|-------------------|
| Chrome headed | Video/trace completo |
| 2 escenarios (éxito + fallo) | TC-03 correo inexistente |
| `InicioSesionIMG.md` con imágenes | TC-04 campos vacíos |
| Mensaje de error textual en fallo | Integración CI |

---

## Ingrediente 4 — Rabbit holes (riesgos)

| Riesgo | Mitigación |
|--------|------------|
| App no levantada (`ERR_CONNECTION_REFUSED`) | Verificar `http://localhost:5002` antes de Playwright; documentar en informe |
| `DebeCambiarPassword` distinto al esperado | Aceptar redirección a Dashboard **o** CambiarPassword como éxito (ambos válidos según seeding) |
| Flaky por animaciones / `networkidle` | `slowMo` en headed; reintentos máx. 1 |
| Mezclar humo con suite completa TC-01–TC-07 | **No** ejecutar TC-05 en humo (modifica BD) |

---

## Ingrediente 5 — No-gos

- No automatizar cambio de contraseña (TC-05) en esta apuesta.
- No pruebas de carga ni seguridad (pentest).
- No sustituir la suite regression completa de login.
- No ejecutar en headless para este informe (requiere **Chrome visible** para evidencia humana).
- No incluir credenciales distintas del seeding documentado sin actualizar este pitch.

---

## Apuesta (bet)

**Compromiso:** una ejecución de humo de inicio de sesión con Playwright + Chrome visible, informe `InicioSesionIMG.md` en `Resultados/`, acotada al appetite anterior.

**Circuit breaker:** si en 15 minutos la app no está disponible o el login exitoso falla dos veces seguidas, se detiene, se registra el bloqueo y no se amplía alcance.

---

## QA en los bordes (Shape Up, cap. 14)

Esta prueba es **humo en el borde crítico** del producto: autenticación. La calidad profunda (rutas protegidas, logout, primer ingreso) queda para scopes posteriores (TC-06, TC-07, TC-05) fuera de esta apuesta.

---

## Referencias internas

- `../Plan-Ejecucion-Playwright-Login.md`
- `Especificacion-Sistema-Prueba-Humo-InicioSesion.md` (instrucciones operativas para el agente)
- Skills del proyecto: `run-smoke-tests`, `playwright-best-practices`, `e2e-testing-patterns`
