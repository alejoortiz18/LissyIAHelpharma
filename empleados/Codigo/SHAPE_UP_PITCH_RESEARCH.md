# 🎯 Shape Up Research Initiative: Plataforma de Gestión de Recursos Humanos

## 📋 Pitch de Investigación

---

## 1️⃣ PROBLEMA

### Contexto Actual
Las organizaciones actuales carecen de una solución centralizada para gestionar integralmente el ciclo de vida de los empleados. Este fragmentación genera:

- **Pérdida de visibilidad operativa**: Sin forma consistente de rastrear quién está activo, en permiso, incapacidad o vacaciones
- **Procesos manuales y propensos a errores**: Registro desorganizado de eventos laborales, horarios y horas extras
- **Falta de auditoría y transparencia**: Imposibilidad de registrar quién autorizó cada movimiento administrativo
- **Toma de decisiones lenta**: Información dispersa entre sistemas, documentos físicos y correos electrónicos

### Impacto Específico
- Retrasos en la resolución de solicitudes administrativas
- Imposibilidad de garantizar cumplimiento normativo
- Ineficiencia en el cálculo de nómina y compensaciones
- Pérdida de confianza en datos organizacionales

---

## 2️⃣ APETITO (Scope de Investigación)

**Duración recomendada: 2-3 semanas en R&D mode**

Esta es una fase de **INVESTIGACION Y VALIDACION**, no de construcción. El objetivo es:
- Validar la viabilidad técnica y de negocio
- Identificar riesgos y rabbit holes
- Definir claramente el alcance MVP (Mínimo Producto Viable)
- Crear la base para decisiones de inversión

**Entregables esperados:**
1. Documento de requisitos refinado
2. Arquitectura de sistema propuesta (diagrama)
3. Matriz de riesgos y dependencias
4. Estimación preliminar por módulo
5. Recomendación de go/no-go

---

## 3️⃣ SOLUCIÓN

### Visión General
Una plataforma web centralizada que integra **4 módulos funcionales** interdependientes para gestionar el ciclo completo del empleado.

### Módulos Core

#### 🧑‍💼 **Módulo 1: Gestión de Empleados**
**Objetivo:** Single Source of Truth para información del personal

**Funcionalidades clave:**
- Registro de datos personales, de identificación y contacto
- Mapeo organizacional: cargos, tipos de contrato, jefes inmediatos
- Estados de empleado: Activo/Inactivo con registro de motivos y fechas
- Asignación obligatoria a sede y cargo
- Control de permisos: El registro de nuevos empleados únicamente lo puede hacer el jefe dentro de su login, quien podrá ver el formulario y asignar el nuevo empleado al sistema, ingresarlo directamente o asignarlo a un jefe y zona o área de trabajo

**Datos críticos:** Persona → Identificación → Cargo → Sede → Jefe → Contrato

---

#### 📄 **Módulo 2: Control de Eventos Laborales**
**Objetivo:** Gestionar novedades administrativas con auditoría completa

**Funcionalidades clave:**
- Registro de eventos: Vacaciones, Incapacidades, Permisos
- **Regla de negocio crítica:** Un empleado = Un estado activo simultáneamente
- Adjuntos de soporte (documentos compilados)
- Auditoría obligatoria: Quién creó, modificó y autorizó cada evento
- Estados de revisión: Pendiente → Aprobado/Rechazado
- Visualización del histórico de los eventos por usuario


**Relaciones:** Empleado → Evento → Soporte → Autorizador → Estado

---

#### 🕒 **Módulo 3: Administración de Jornadas y Horarios**
**Objetivo:** Definir disponibilidad esperada del equipo

**Funcionalidades clave:**
- Programación de turnos: Entrada/Salida estándar
- Configuración por día festivo y fin de semana
- Responsable de programación (auditoría)
- Asignación por empleado o grupo

**Relaciones:** Sede/Área → Turno → Empleado → Responsable

---

#### ⏱️ **Módulo 4: Gestión de Horas Extras**
**Objetivo:** Registrar y controlar tiempo suplementario

**Funcionalidades clave:**
- Reporte detallado: Fecha, cantidad de horas, justificación
- Flujo de aprobación con estados
- Vinculación con jornada programada
- Historial de cambios y razones

**Relaciones:** Empleado → Solicitud de Extra → Justificación → Autorizador → Estado

---

### Arquitectura Propuesta (Nivel Alto)

```
┌─────────────────────────────────────────┐
│   CAPA DE PRESENTACION                 │
│  ┌──────────┬──────────┬──────┬──────┐ │
│  │Empleados │ Eventos  │Turnos│Extras│ │
│  └──────────┴──────────┴──────┴──────┘ │
└──────────────┬───────────────────────┘
               │
┌──────────────┴───────────────────────┐
│   CAPA DE NEGOCIO / API              │
│  ├─ Employees Service               │
│  ├─ Events Service                  │
│  ├─ Schedules Service               │
│  ├─ Overtime Service                │
│  └─ Audit Service (auditoría global)│
└──────────────┬───────────────────────┘
               │
┌──────────────┴───────────────────────┐
│   CAPA DE DATOS                      │
│  ├─ employees                        │
│  ├─ events                           │
│  ├─ schedules                        │
│  ├─ overtimes                        │
│  ├─ audit_logs                       │
│  └─ attachments                      │
└──────────────────────────────────────┘
```

---

## 4️⃣ RABBIT HOLES 🕳️

*Áreas críticas que requieren investigación detallada para desriesgar el proyecto*

### Rabbit Hole 1: **Integridad de Datos - "Regla de Evento Único"**
**El reto:** Garantizar que un empleado NO pueda tener 2 estados ACTIVOS simultáneamente (ej: de vacaciones Y en incapacidad)

**Por qué es un rabbit hole:**
- Requiere validación en tiempo real contra todo tipo de evento
- Necesita lógica transaccional robusta
- Validación de solapamientos de fechas complejas
- Impacto en nómina y reportes

**Investigación necesaria:**
- ¿Con qué frecuencia ocurren conflictos de eventos?
- ¿Necesitamos prevención en tiempo real o solo detección/reporte?
- ¿Qué pasa si se detecta un conflicto después de autorizar?
- ¿Cómo se revierte/corrige?

---

### Rabbit Hole 2: **Cadena de Autorización y Auditoría**
**El reto:** Registrar QUIÉN autorizó cada acción y en qué contexto

**Por qué es un rabbit hole:**
- Múltiples niveles de aprobación (¿gerente directo? ¿RH? ¿Ambos?)
- Diferentes flujos por tipo de evento (vacaciones ≠ incapacidades)
- Cambios retroactivos y auditoría de cambios
- Cumplimiento normativo variable por jurisdicción

**Investigación necesaria:**
- ¿Cuál es la cadena de autorización para cada evento?
- ¿Pueden autorizadores rechazar? ¿Requieren justificación?
- ¿Qué sucede si un autorizador "desaparece" (se va de la empresa)?
- ¿Se pueden modificar eventos ya autorizados?

---

### Rabbit Hole 3: **Manejo de Adjuntos y Evidencia**
**El reto:** Adjuntar documentos que respalden cada evento

**Por qué es un rabbit hole:**
- Gestión de archivos (almacenamiento, versiones, eliminación)
- Seguridad y privacidad de documentos
- Tipos de archivo aceptados
- Límites de tamaño y cumplimiento

**Investigación necesaria:**
- ¿Dónde se almacenan los adjuntos? (Base de datos / Storage externo)
- ¿Quién puede acceder a los documentos de un empleado?
- ¿Cuál es el ciclo de vida de los adjuntos? (retención, eliminación)
- ¿Necesitamos control de versiones de documentos?

---

### Rabbit Hole 4: **Integración con Sistemas Existentes**
**El reto:** Esta plataforma no opera en el vacío; necesitará conectarse con...

**Por qué es un rabbit hole:**
- Sistemas de nómina (envío de datos)
- Sistemas de seguridad/acceso físico (sincronización de estados)
- Calendarios corporativos (días festivos, eventos)
- Posibles sistemas legados ya en uso

**Investigación necesaria:**
- ¿Qué sistemas existentes debe conectar?
- ¿Existen APIs disponibles o necesitamos integración personalizada?
- ¿Cuál es el modelo de datos en sistemas existentes?
- ¿Qué tan crítico es mantener sincronización en tiempo real?

---

### Rabbit Hole 5: **Reportes y Analítica**
**El reto:** Diferentes stakeholders necesitan diferentes vistas de los datos

**Por qué es un rabbit hole:**
- Reportes de nómina (consolidación de extras, eventos)
- Reportes operativos (disponibilidad de equipo)
- Reportes de cumplimiento (auditoría de autorizaciones)
- Análisis de tendencias (patrones de ausencia, horas extras)

**Investigación necesaria:**
- ¿Cuáles son los top 10 reportes críticos?
- ¿Frecuencia de ejecución? (diaria, semanal, mensual?)
- ¿Quién accede a qué reportes?
- ¿Necesitamos dashboards en tiempo real o reportes programados?

---

### Rabbit Hole 6: **Flexibilidad Organizacional**
**El reto:** La estructura de la organización puede cambiar

**Por qué es un rabbit hole:**
- Empleados cambian de sede, cargo, jefe
- ¿Historial de cambios? ¿Cómo afecta esto a eventos pasados?
- Reorganizaciones masivas
- Cambios de estructura de autorización

**Investigación necesaria:**
- ¿Necesitamos auditoría histórica completa de cambios organizacionales?
- ¿Cómo se resuelven eventos autorizados por gerentes que ya no están?
- ¿Se pueden cambiar automáticamente jefes cuando un empleado se mueve?
- ¿Qué pasa con los horarios cuando un empleado cambia de sede?

---

## 5️⃣ NO-GOs 🚫

*Explícitamente FUERA de alcance para esta iniciativa de investigación*

| Área | Por qué se excluye |
|------|-------------------|
| **Gestión de Nómina** | Sistema complejo que requiere su propia iniciativa. HR platform sólo alimentará datos. |
| **Cumplimiento Legal/Normativo por País** | Fuera de alcance de plataforma base. Se requiere análisis separado por jurisdicción. |
| **Integración SSO/LDAP** | Usar credenciales simples inicialmente. SSO es optimización post-MVP. |
| **Mobile App** | Iniciar con web responsive. App nativa es fase posterior. |
| **Análisis Predictivo/IA** | No incluir ML para patrones de ausencia. Solo reportes descriptivos. |
| **Gestión de Beneficios** | Pensiones, seguros, etc. Son procesos separados. |
| **Reclutamiento** | Out of scope. Enfoque solo en gestión de personal actual. |
| **Training/Capacitación** | No incluida en ciclo de vida para esta fase. |
| **Evaluación de Desempeño** | Distinto proceso. No relacionado con eventos laborales. |

---

## 6️⃣ PREGUNTAS CRÍTICAS A RESOLVER

**Antes de mover a "Betting Table":**

1. ✅ **¿Hay demanda/pain real?** ¿Está el cliente dispuesto a invertir?
2. ✅ **¿Viabilidad técnica?** ¿Los rabbit holes son solucionables en 6 semanas post-investigación?
3. ✅ **¿Equipo disponible?** ¿Tenemos backend, frontend y diseñador simultáneamente?
4. ✅ **¿Dependencias externas?** ¿Se necesita información de sistemas legacy antes de empezar?
5. ✅ **¿Competencia?** ¿Hay soluciones en el mercado? ¿Por qué esta es diferente?

---

## 🎯 RECOMENDACIONES DE INVESTIGACIÓN

**Hitos de la fase R&D:**

### Semana 1: Validación de Requisitos
- [ ] Entrevistas con usuario final (RH, finanzas, operaciones)
- [ ] Mapeo de flujos actuales (cómo se hace ahora?)
- [ ] Identificación de "pain points" más críticos
- [ ] Revisión de cumplimiento legal por jurisdicción

### Semana 2: Arquitectura y Riesgos
- [ ] Propuesta de arquitectura técnica
- [ ] Spike técnico: Validar solución a Rabbit Hole 1 (Regla de Evento Único)
- [ ] Mapeo de integraciones necesarias
- [ ] Estimación refinada por módulo

### Semana 3: Decisión y Plan
- [ ] Documento de decisión go/no-go
- [ ] Roadmap de fases (MVP → V2 → V3)
- [ ] Asignación de equipo
- [ ] Preparación para "Betting Table"

---

## 📊 TAMAÑO DE APUESTA (Si se aprueba investigación)

Basado en análisis inicial:

| Módulo | Tamaño Estimado | Riesgo |
|--------|-----------------|--------|
| Gestión de Empleados | Pequeño (1-2 semanas) | Bajo |
| Control de Eventos | Medio (2-3 semanas) | Medio-Alto |
| Administración de Jornadas | Pequeño (1-2 semanas) | Bajo |
| Gestión de Horas Extras | Pequeño (1-2 semanas) | Bajo |
| Integraciones | Variable | Medio |
| **TOTAL MVP** | **~6 semanas** | **Medio** |

---

## ✅ PRÓXIMOS PASOS

**Para mover a "Betting Table":**

1. ✋ **Detener aquí** y compartir este documento con stakeholders
2. 📞 **Feedback round**: ¿Afirmamos los rabbit holes? ¿Validamos los no-gos?
3. 🔧 **Ejecutar investigación** de 2-3 semanas si hay apoyo
4. 📋 **Refinar estimaciones** basadas en hallazgos reales
5. 🎰 **Presentar apuesta** en Betting Table (decisión go/no-go/reshape)

---

**Documento preparado siguiendo metodología Shape Up de Basecamp®**  
*Referencia: https://basecamp.com/shapeup*
