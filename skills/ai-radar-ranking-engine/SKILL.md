---
name: ai-radar-ranking-engine
description: Define, apply, and refine AI Radar scoring and ranking rules for signals, candidates, fixtures, and future domain modules. Use when Codex needs to score AI news by novelty, evidence, impact, reliability, actionability, risk, deduplication strength, or produce deterministic ranking guidance for tests and product logic.
---

# AI Radar Ranking Engine

## Objetivo

Convertir senales de IA en un ranking defendible para builders. El ranking debe
explicar por que una senal sube o baja y debe ser lo bastante estable para
convertirse despues en codigo y pruebas.

## Inputs

Aceptar:

- Senales en `data/signals/daily/daily-radar-*.json`.
- Candidatos normalizados por `ai-radar-source-normalizer`.
- Reglas de producto o criterios editoriales nuevos.
- Solicitudes de scoring, desempate, priorizacion o comparacion.

## Dimensiones De Scoring

Usar escala 0-5 para cada dimension cuando el usuario pida puntuacion:

- `novelty`: que tan nuevo o diferencial es el evento.
- `evidence`: fuerza de la evidencia disponible.
- `impact`: efecto practico para builders, producto, arquitectura o compliance.
- `reliability`: calidad de la fuente y claridad del hecho.
- `actionability`: claridad de la accion recomendada.
- `strategicFit`: alineacion con AI Radar y el foco en IA aplicable.
- `risk`: riesgo regulatorio, tecnico, reputacional o de dependencia.

Formula inicial sugerida:

```text
score =
  novelty * 0.15 +
  evidence * 0.20 +
  impact * 0.25 +
  reliability * 0.15 +
  actionability * 0.20 +
  strategicFit * 0.05
```

`risk` no suma por defecto; usarlo como bandera para priorizar revision humana
o compliance.

## Workflow

1. **Leer contexto**
   - Revisar contrato y snapshots relevantes.
   - No asumir que existe modulo de ranking en `src/` si no esta presente.

2. **Normalizar entradas**
   - Asegurar que cada item tenga fuente, fecha, evidencia, impacto, accion,
     estado y tags.
   - Separar candidatos incompletos de senales listas para ranking.

3. **Puntuar**
   - Asignar 0-5 por dimension con una razon corta.
   - Penalizar duplicados, evidencia debil y acciones vagas.
   - No premiar marketing sin cambio observable.

4. **Resolver empates**
   - Priorizar fuente primaria o evidencia mas fuerte.
   - Priorizar senales con accion clara.
   - Priorizar impacto sobre novedad cuando el evento afecte acceso, costos,
     seguridad o compliance.
   - Mantener orden estable por `id` si todo lo demas empata.

5. **Recomendar cambios**
   - Sugerir ajustes a `impact.level`, `status`, `tags` o `action` cuando el
     scoring contradiga el snapshot.
   - Si el usuario pide implementacion, crear o actualizar codigo y pruebas
     siguiendo el stack real del repo.

## Interpretacion De Puntajes

- `4.0-5.0`: senal prioritaria para el radar.
- `3.0-3.9`: senal util, requiere seguimiento o accion acotada.
- `2.0-2.9`: conservar solo si aporta contexto o diversidad.
- `<2.0`: candidata a descartar, archivar o fusionar.

## Reglas

- Explicar todo puntaje que cambie decisiones.
- No mezclar riesgo con impacto; una senal puede ser riesgosa y aun asi poco
  accionable.
- No crear pesos nuevos sin decir por que.
- Mantener reglas deterministas si se van a convertir en pruebas.
- Guardar scoring en `data/reviews/rankings/` solo si el contrato lo permite o si se crea un
  contrato nuevo de forma explicita.

## Validaciones

- Revisar que la lista resultante sea ordenable de forma estable.
- Confirmar que las razones no dependan de datos no verificados.
- Si se edita JSON, ejecutar `jq empty`.
- Si se implementa codigo, agregar pruebas con `unittest`.
