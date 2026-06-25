---
name: ai-radar-signal-reviewer
description: Review, compare, deduplicate, and improve AI Radar daily signal snapshots. Use when Codex needs to audit existing data/fixtures/daily-radar-*.json files, validate editorial quality, detect duplicate or weak signals, compare signals across dates, or recommend changes to impact, status, evidence, tags, and actions.
---

# AI Radar Signal Reviewer

## Objetivo

Auditar snapshots diarios de AI Radar para mejorar calidad editorial,
consistencia y accionabilidad sin convertir la revision en una nueva busqueda
de noticias.

Usar esta skill sobre archivos existentes en `data/fixtures/` y el contrato en
`docs/contracts/ai-radar-daily.schema.json`.

## Inputs

Aceptar uno o varios de estos inputs:

- Un archivo `data/fixtures/daily-radar-YYYY-MM-DD.json`.
- Varios snapshots diarios para comparar.
- Una lista de senales candidatas ya estructuradas.
- Una solicitud de auditoria editorial, deduplicacion o mejora de scoring.

Si el usuario pide verificar hechos nuevos o actualidad, usar busqueda web
solo para confirmar fuentes puntuales. No reemplazar el trabajo de
`ai-radar-signals`.

## Workflow

1. **Reconocer el estado del repo**
   - Leer el contrato diario si existe.
   - Leer los snapshots indicados o los mas recientes en `data/fixtures/`.
   - No asumir CLI, base de datos, dashboard ni validador si no existen.

2. **Validar estructura**
   - Ejecutar `jq empty` sobre cada JSON revisado.
   - Confirmar que cada senal tenga fuente, evidencia, impacto, accion,
     estado y tags.
   - Revisar fechas ISO y que cada `id` empiece con `radarDate`.

3. **Detectar duplicados**
   - Comparar titulo, fuente, tags, actores, evento principal y accion.
   - Marcar como duplicado fuerte si dos senales describen el mismo evento.
   - Marcar como solapamiento si comparten tema pero tienen consecuencias
     distintas.
   - Preferir conservar la senal con mejor fuente, evidencia mas concreta y
     accion mas clara.

4. **Evaluar evidencia**
   - Considerar fuerte la evidencia con fechas, actores, cifras, decisiones,
     documentos, lanzamientos o cambios observables.
   - Considerar debil la evidencia basada en rumores, lenguaje especulativo,
     marketing, opiniones sin datos o fuentes no consultadas.
   - Recomendar mover a `candidate` cuando la evidencia no sostenga el impacto.

5. **Revisar impacto y estado**
   - `high`: cambia acceso, costos, compliance, seguridad o ventaja competitiva.
   - `medium-high`: afecta arquitectura, proveedor, mercado o roadmap.
   - `medium`: amerita seguimiento o experimento, pero no decision inmediata.
   - `low`: contexto util con poca accion concreta.
   - Usar `actionable` solo cuando la accion sea concreta y ejecutable.

6. **Mejorar accion y tags**
   - Convertir acciones vagas en tareas o criterios de seguimiento.
   - Normalizar tags en minusculas con guiones.
   - Evitar tags redundantes o frases largas.

7. **Reportar o editar**
   - Si el usuario pide cambios, editar el snapshot de forma minima.
   - Si solo pide revision, entregar hallazgos con severidad, archivo y senal.
   - Separar bugs de contrato, problemas editoriales y recomendaciones.

## Criterios De Calidad

- La revision debe proteger el contrato existente.
- No inventar fuentes ni evidencia.
- No borrar senales validas solo porque se parecen por tema.
- No subir impacto sin explicar una consecuencia practica.
- No cambiar `publishedAt` ni `retrievedAt` sin verificar la fuente.

## Validaciones

Ejecutar como minimo:

```bash
jq empty docs/contracts/ai-radar-daily.schema.json
jq empty data/fixtures/daily-radar-YYYY-MM-DD.json
```

Si existe un validador JSON Schema o pruebas del proyecto, usarlo despues de
las validaciones basicas.
