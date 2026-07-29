---
name: ai-radar-source-manager
description: Manage the AI Radar source registry in Notion, synchronize and validate config/sources.json, monitor source health, group active sources for subagents, discover candidate sources, and govern additions or deactivations. Use when Codex needs a fresh source catalog before news collection, must recover from Notion failures, audit broken or stale sources, or perform weekly, monthly, or quarterly source maintenance.
---

# AI Radar Source Manager

## Objetivo

Mantener un catalogo de fuentes confiable, disponible y gobernado para AI
Radar. Usar Notion `AI Radar Sources` como fuente maestra y
`config/sources.json` como cache operativa.

No buscar ni curar noticias. Entregar un catalogo valido para que
`ai-radar-signals` distribuya la recoleccion entre subagents.

## Modos

- `sync`: sincronizar Notion con la cache. Ejecutar antes de la primera
  busqueda editorial del dia o cuando la cache supere 24 horas.
- `health`: comprobar disponibilidad, redirecciones y contenido reciente.
  Ejecutar semanalmente.
- `discover`: buscar y normalizar fuentes nuevas. Ejecutar mensualmente con
  `ai-radar-source-normalizer`.
- `review`: evaluar cobertura, ruido, duplicados y fuentes degradadas. Ejecutar
  trimestralmente.

Una skill no programa ejecuciones por si sola. Aplicar estas cadencias cuando
la invoque una automatizacion, tarea recurrente o flujo editorial.

## Flujo De Sincronizacion

1. Buscar en Notion la base exacta `AI Radar Sources` y obtener su data source.
2. Consultar todas las filas activas y los campos definidos en
   [references/source-contract.md](references/source-contract.md).
3. Normalizar nombres, URLs, selects, fechas, checkboxes y multiselects.
4. Rechazar el lote si esta vacio, contiene URLs invalidas, tipos desconocidos
   o duplicados.
5. Ordenar fuentes por `type` y `name`, sin distinguir mayusculas.
6. Generar `config/sources.json` con TTL de 24 horas y grupos deterministas:
   - `official-verification`: `fuente_oficial`.
   - `technical-repos`: `repo_tecnico`.
   - `community-discovery`: `comunidad`.
   - `secondary-context`: `medio_secundario`.
7. Ejecutar:
   `python3 skills/ai-radar-source-manager/scripts/validate_sources_cache.py config/sources.json`.
8. Reemplazar la cache solo despues de validar el catalogo completo.

Si Notion no responde, conservar la ultima cache valida sin modificarla.
Reportar `fallback-cache` si la cache existe o `fallback-no-cache` si tampoco
esta disponible. Incluir siempre el motivo del fallback.

## Control De Salud

1. Revisar cada fuente segun `Frecuencia`.
2. Preferir RSS o API verificados; usar la URL canonica cuando no existan.
3. Registrar exito solo si la fuente responde y permite identificar contenido.
4. Actualizar `Ultimo exito`, `Ultimo contenido detectado` y
   `Fallos consecutivos` con evidencia de la comprobacion.
5. Mantener `saludable` con cero fallos, usar `degradada` para fallos
   transitorios y `en_revision` despues de tres fallos consecutivos.
6. No desactivar, borrar ni reemplazar una fuente automaticamente.

Un codigo HTTP aislado, bloqueo por robots, necesidad de JavaScript o limite
temporal no demuestra que una fuente haya dejado de existir. Registrar la
limitacion antes de cambiar su salud.

## Descubrimiento Y Revision

- Consultar primero el catalogo para evitar duplicados.
- Buscar fuentes que cubran vacios de actores, regiones, investigacion,
  infraestructura, seguridad o regulacion.
- Normalizar candidatos con `ai-radar-source-normalizer`.
- Proponer nombre, URL, tipo, prioridad, uso, frecuencia, confianza y razon.
- Requerir aprobacion humana antes de crear o desactivar registros.
- En la revision trimestral, comparar volumen util, duplicados, fallos y
  aportes exclusivos. No premiar frecuencia si la fuente agrega ruido.

## Politica De Mutacion

- Permitir actualizaciones automaticas de metricas de salud comprobadas.
- Exigir aprobacion para altas, desactivaciones y cambios de URL o categoria.
- No sobrescribir una cache valida con un resultado parcial.
- No almacenar secretos, cookies ni credenciales en Notion o la cache.
- Mantener Notion como fuente maestra; nunca reconstruirlo desde la cache.

## Reporte

Informar:

- modo ejecutado;
- `sourceCatalogStatus`: `fresh`, `fallback-cache` o `fallback-no-cache`;
- `cacheGeneratedAt` y `cacheExpiresAt`;
- cantidad total y por tipo;
- fuentes degradadas o en revision;
- cambios realizados y decisiones pendientes de aprobacion.

## Recursos

- Leer [references/source-contract.md](references/source-contract.md) antes de
  cambiar el esquema de Notion o el formato de cache.
- Usar
  [scripts/validate_sources_cache.py](scripts/validate_sources_cache.py) para
  validar sintaxis, campos, duplicados, orden y agrupacion.
