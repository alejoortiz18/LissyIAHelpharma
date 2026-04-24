# Plan de Corrección Masiva de Datos en Base de Datos

## Objetivo

Realizar una validación completa sobre toda la base de datos para identificar y corregir problemas de codificación en campos tipo texto, especialmente caracteres especiales mal almacenados o con errores de interpretación de encoding, por ejemplo:

* `EstÃ¡ndar` → `Estándar`
* `InformaciÃ³n` → `Información`
* `DirecciÃ³n` → `Dirección`
* `FarmacÃ©utico` → `Farmacéutico`
* `NiÃ±o` → `Niño`

El proceso debe recorrer todas las tablas y todas las columnas tipo texto, corregir la información y actualizar los registros afectados.

---

## Alcance

Aplicar validación en todos los objetos de datos activos:

* Tablas principales
  n- Tablas maestras
* Tablas transaccionales
* Tablas históricas
* Tablas de configuración
* Catálogos
* Logs funcionales (si aplica)

Tipos de datos incluidos:

* `varchar`
* `nvarchar`
* `char`
* `nchar`
* `text`
* `ntext` (si existen)

---

## Problema Detectado

Existen registros almacenados con caracteres corruptos por errores de codificación UTF-8 / ANSI / Latin1.

Ejemplos comunes:

| Incorrecto    | Correcto     |
| ------------- | ------------ |
| EstÃ¡ndar     | Estándar     |
| InformaciÃ³n  | Información  |
| FarmacÃ©utico | Farmacéutico |
| AtenciÃ³n     | Atención     |
| GestiÃ³n      | Gestión      |
| AÃ±o          | Año          |
| NiÃ±o         | Niño         |
| CorazÃ³n      | Corazón      |
| MedellÃ­n      | Medellín     |

---

## Estrategia Técnica

## Fase 1 – Inventario de columnas texto

Consultar metadatos del sistema para detectar todas las columnas tipo texto.

Fuentes sugeridas:

* `INFORMATION_SCHEMA.COLUMNS`
* `sys.tables`
* `sys.columns`
* `sys.types`

Resultado esperado:

* Tabla
* Columna
* Tipo dato
* Longitud
* Permite null

---

## Fase 2 – Detección de registros afectados

Buscar patrones sospechosos como:

* `Ã¡`
* `Ã©`
* `Ã­`
* `Ã³`
* `Ãº`
* `Ã±`
* `Â`
* `â€™`
* `â€œ`
* `â€`

Generar reporte con:

* Tabla
* Columna
* Id del registro (si aplica)
* Valor actual
* Valor sugerido corregido

---

## Fase 3 – Corrección controlada

Aplicar actualización únicamente a registros detectados.

Reglas:

* Mantener respaldo previo.
* No modificar registros sanos.
* Ejecutar por lotes si volumen es alto.
* Registrar cantidad de filas actualizadas.

---

## Fase 4 – Validación posterior

Confirmar que no existan más patrones corruptos.

Validar especialmente:

* Nombres de cargos
* Nombres de usuarios
* Direcciones
* Correos descriptivos
* Catálogos maestros
* Ciudades
* Documentos impresos
* Reportes

---

## Requerimiento SQL Esperado

Desarrollar script dinámico que:

1. Recorra todas las tablas.
2. Detecte todas las columnas texto.
3. Busque caracteres dañados.
4. Genere script `UPDATE`.
5. Ejecute actualización.
6. Genere bitácora final.

---

## Recomendación de Respaldo

Antes de ejecutar:

* Backup completo de base de datos.
* Snapshot si aplica.
* Ejecución previa en ambiente QA.
* Validación por muestra.

---

## Entregables Esperados

1. Script de inventario de columnas texto.
2. Script de detección de errores.
3. Script de actualización masiva.
4. Reporte antes/después.
5. Evidencia de registros corregidos.

---

## Resultado Final Esperado

Toda la base de datos debe quedar normalizada a español latino correcto, sin caracteres corruptos ni errores de codificación visibles en formularios, reportes o consultas.

---

## Observación Técnica

Si el problema proviene de collation o importaciones antiguas, evaluar adicionalmente:

* Collation de base de datos.
* Collation por columna.
* Encoding de archivos de carga.
* Integraciones externas.
* Exportaciones Excel/CSV.
