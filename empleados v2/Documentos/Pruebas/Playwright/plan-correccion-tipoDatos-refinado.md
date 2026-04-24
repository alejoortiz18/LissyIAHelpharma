# Shape Up Pitch: Corrección Masiva de Codificación en Base de Datos

> Metodología: [Shape Up by Basecamp](https://basecamp.com/shapeup)

---

## Problema

La base de datos del sistema **GestionPersonal** contiene registros con caracteres corruptos producto de errores de encoding UTF-8/ANSI/Latin1 en importaciones o cargas de datos anteriores. Estos caracteres aparecen en formularios, reportes y consultas, afectando la credibilidad del sistema ante los usuarios finales.

**Historia concreta:** Un jefe de recursos humanos abre el catálogo de cargos y ve `FarmacÃ©utico` en lugar de `Farmacéutico`. Al imprimir el directorio de empleados, los nombres de ciudad como `MedellÃ­n` aparecen corruptos. Esto genera desconfianza inmediata y fuerza correcciones manuales registro por registro, sin garantía de cobertura total.

El problema no es visible en código fuente ni en la aplicación MVC — vive únicamente en los datos almacenados. Cualquier reporte, exportación a Excel o documento impreso hereda el dato corrupto sin advertencia.

---

## Appetite

**Small Batch — 1 semana**

Esta corrección no requiere cambios de modelo de datos, de interfaces de usuario ni de lógica de negocio. Es trabajo acotado de base de datos: detectar, corregir y validar. Una semana es suficiente para construir los scripts, ejecutarlos en un ambiente QA, validar los resultados por muestra y aplicarlos en producción con respaldo previo.

Si al explorar el volumen de datos afectados se descubre que supera las expectativas, el alcance se reduce: primero se corrigen las tablas maestras y catálogos (alta visibilidad), y en un segundo ciclo las tablas transaccionales e históricas.

---

## Solución

Un único script SQL dinámico ejecuta las cuatro fases de forma controlada y genera una bitácora al finalizar.

### Flujo general

```
INFORMATION_SCHEMA.COLUMNS
         ↓
  Cursor por tabla / columna texto
         ↓
  ¿Contiene patrones corruptos? ──── NO ──→ siguiente columna
         ↓ SÍ
  UPDATE con REPLACE encadenado
         ↓
  INSERT en #BitacoraCorreccion
         ↓
  Reporte final: tabla | columna | filas_corregidas
```

---

### Fase 1 — Inventario automático de columnas texto

Se consulta `INFORMATION_SCHEMA.COLUMNS` filtrando `DATA_TYPE IN ('varchar','nvarchar','char','nchar','text','ntext')` para obtener el mapa completo de columnas candidatas. Las columnas de contraseñas, tokens y hashes se excluyen en esta fase por nombre y por tipo.

```
Resultado: tabla | esquema | columna | tipo | longitud | permite_null
```

---

### Fase 2 — Detección de registros afectados

Para cada columna del inventario se ejecuta una consulta de conteo buscando los patrones corruptos conocidos:

| Patrón corrupto | Carácter correcto |
|-----------------|-------------------|
| `Ã¡`            | `á`               |
| `Ã©`            | `é`               |
| `Ã­`            | `í`               |
| `Ã³`            | `ó`               |
| `Ãº`            | `ú`               |
| `Ã±`            | `ñ`               |
| `Ã`             | `Á`               |
| `Ã‰`            | `É`               |
| `Ã"`            | `Ó`               |
| `Ãš`            | `Ú`               |
| `Ã'`            | `Ñ`               |
| `â€™`           | `'`               |
| `â€œ`           | `"`               |
| `â€`            | `"`               |
| `Â`             | *(espacio / vacío)* |

La fase genera un reporte de **filas afectadas por tabla y columna** sin modificar ningún dato. Esto permite validar el alcance real antes de ejecutar cualquier actualización.

---

### Fase 3 — Corrección controlada por lotes

Se aplica `UPDATE` únicamente a las filas donde se detectó corrupción en la fase anterior. Cada columna recibe un `REPLACE` encadenado aplicando todo el mapa de caracteres en una sola sentencia.

Para tablas con alto volumen se usa un ciclo `WHILE EXISTS` para procesar en lotes de 5 000 filas y evitar bloqueos prolongados.

```sql
-- Ejemplo de patrón de corrección
UPDATE [Tabla]
SET [Columna] = REPLACE(REPLACE(REPLACE([Columna],
    'Ã¡','á'),
    'Ã©','é'),
    'Ã³','ó')
    -- ... resto del mapa
WHERE [Columna] LIKE '%Ã%'
   OR [Columna] LIKE '%â€%'
   OR [Columna] LIKE '%Â%';
```

---

### Fase 4 — Bitácora final

Al completar la corrección en cada columna se inserta un registro en `#BitacoraCorreccion` con:

- Nombre de tabla y columna
- Filas contadas con error (antes)
- Filas actualizadas (después)
- Timestamp de ejecución

El reporte final hace un `SELECT` de la bitácora ordenado por filas corregidas descendente, permitiendo una revisión rápida del impacto total.

---

## Rabbit Holes

Estos son los puntos donde el trabajo puede desbordarse si no se les pone límite explícito:

1. **Columnas sensibles:** Columnas como `PasswordHash`, `Token`, `RefreshToken`, `CodigoRecuperacion` deben excluirse por nombre en la Fase 1. Modificar esos campos rompería la autenticación de todos los usuarios. El script debe tener una lista de exclusión explícita, no confiar en el tipo de dato.

2. **Tablas históricas y de auditoría:** Corregir registros de auditoría (`AuditoriaAcceso`, `HistorialEventos`) altera la fidelidad del histórico. Hay que decidir de forma explícita si se incluyen o se dejan fuera. Por defecto, quedan excluidas en v1.

3. **Collation incompatible por columna:** Si existen columnas con `COLLATE` distinto al de la base de datos, el `REPLACE` puede comportarse de forma silenciosa o lanzar un error de conversión. El inventario de la Fase 1 debe incluir el collation de cada columna y advertir sobre las que difieran.

4. **Volumen alto en tablas transaccionales:** Un `UPDATE` masivo sin lotes en tablas con cientos de miles de filas puede bloquear la base de datos durante minutos. El script debe detectar tablas con más de 10 000 filas afectadas y aplicar automáticamente el modo por lotes.

5. **Reintrodución del problema:** Si el proceso de carga que originó la corrupción sigue activo (importaciones CSV, integraciones externas), la corrección se revertirá parcialmente. Este pitch no cubre ese proceso — es un pitch separado.

---

## No-Gos

Lo siguiente queda **explícitamente fuera** de este pitch:

- **No se cambia el collation** de la base de datos ni de ninguna columna. Es un cambio de esquema mayor con impacto en índices, migraciones y aplicación. Requiere su propio ciclo.
- **No se modifica el código fuente** de la aplicación MVC. Esta corrección es exclusivamente de datos existentes.
- **No se corrigen correos electrónicos** usados como identificadores de acceso (`CorreoAcceso`). Un cambio allí rompería el login de los usuarios afectados.
- **No se incluyen columnas binarias** (`varbinary`, `image`) ni archivos adjuntos almacenados en la base de datos.
- **No se crea ninguna interfaz de usuario** para gestionar esta corrección. El mecanismo es un script SQL ejecutado por un DBA o desarrollador con respaldo previo.
- **No se corrige el proceso de carga** que originó el problema. Eso es trabajo separado de integración.
- **No se garantiza corrección de datos en tablas históricas** (v1 las excluye deliberadamente para preservar la integridad del historial).

---

## Entregables del ciclo

| # | Entregable | Descripción |
|---|-----------|-------------|
| 1 | Script de inventario | Lista todas las columnas texto con metadatos |
| 2 | Script de detección | Reporte de filas afectadas por tabla/columna |
| 3 | Script de corrección | UPDATE masivo por lotes con mapa de reemplazos |
| 4 | Bitácora de ejecución | Registro de filas corregidas antes/después |
| 5 | Validación en QA | Evidencia de muestra revisada antes de producción |

---

## Checklist antes de ejecutar en producción

- [ ] Backup completo de base de datos confirmado
- [ ] Script ejecutado y validado en ambiente QA
- [ ] Revisión por muestra: al menos 10 registros corregidos confirmados visualmente
- [ ] Confirmar que usuarios con correos afectados no son el caso (columna `CorreoAcceso` excluida)
- [ ] Ventana de mantenimiento acordada con el equipo (baja concurrencia)
- [ ] Rollback disponible: backup listo para restaurar si algo falla
