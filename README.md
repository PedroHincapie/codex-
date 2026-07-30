# AI Radar

AI Radar es el proyecto del curso avanzado de Codex.

El objetivo del producto es organizar noticias, herramientas, papers, repos y lanzamientos de IA para convertirlos en senales accionables para builders: que paso, por que importa, que tan confiable es y que vale la pena probar.

Estado actual: nucleo local operativo para administrar fuentes, normalizar
candidatos, curar senales, auditarlas y producir rankings deterministas. Notion
funciona como fuente maestra del catalogo editorial y el repositorio conserva
contratos, cache operativa, snapshots y evidencia de validacion. La persistencia
Supabase ya cuenta con esquema versionado, RLS, carga idempotente y validacion
local; la creacion del proyecto remoto permanece como paso controlado.

## Problema

El ritmo de la inteligencia artificial genera demasiado ruido:

- lanzamientos repetidos en varias fuentes,
- repos que parecen importantes pero no tienen adopcion,
- demos sin documentacion suficiente,
- papers sin ejemplo practico,
- herramientas con impacto real mezcladas con marketing.

AI Radar debe ayudar a separar ruido de senales utiles.

## Producto Objetivo

Al final del curso, AI Radar debe poder:

- recopilar novedades de IA desde fuentes seleccionadas,
- normalizar noticias, repos, papers y productos,
- detectar duplicados y noticias parecidas,
- agrupar senales por tema,
- rankear por novedad, impacto, evidencia y accionabilidad,
- generar guias practicas para decidir que probar,
- exponer resultados en un dashboard,
- guardar trazas de decisiones y validaciones,
- desplegarse con infraestructura controlada.

## Estado Actual

Al 29 de julio de 2026, el proyecto cuenta con:

- 15 fuentes activas y saludables administradas en Notion;
- una cache local v2 con TTL de 24 horas y fallback explicito;
- cuatro grupos de fuentes para recoleccion paralela;
- siete skills canonicas para fuentes, normalizacion, senales, revision,
  ranking, fixtures y desarrollo frontend;
- snapshots diarios, candidatos normalizados y rankings editoriales;
- CLI local para consulta, validacion, auditoria, cobertura y ranking;
- persistencia Supabase local con esquema versionado, RLS y carga idempotente;
- 29 pruebas `unittest` para el dominio, el CLI, el catalogo, la persistencia y
  la sincronizacion de skills.

El corte verificable, las decisiones tomadas y las piezas pendientes se
documentan en
[docs/ai-radar-current-state.md](docs/ai-radar-current-state.md).

## Stack Objetivo

El stack debe mantenerse simple para que el foco del curso sea Codex, no el framework.

- Frontend: HTML, CSS y JavaScript.
- Dominio y scripts internos: Python con libreria estandar.
- CLI interno: `scripts/airadar.py` para comandos del proyecto y skills.
- Automatizacion local: scripts Python llamados directamente por skills.
- Proyecto agent-friendly: Dekk cuando existan comandos que deban usar humanos y agentes.
- API: Vercel Functions cuando hagan falta endpoints.
- Datos locales: snapshots, rankings y candidatos antes de conectar servicios externos.
- Base de datos: Supabase cuando el contrato local ya funcione.
- QA: `unittest` para dominio y Playwright cuando exista interfaz visual.
- Demo final: video programatico con la evidencia del proyecto.

## Reglas Iniciales Para Codex

Antes de implementar, Codex debe distinguir:

- vision del producto,
- estado actual del repositorio,
- decisiones tecnicas tomadas,
- decisiones pendientes,
- limites de seguridad.

Codex no debe inventar archivos, comandos, servicios ni integraciones como si ya existieran.

## Documentacion Operativa

El modelo operativo completo, con diagramas de flujo, arquitectura, criterios
para crear tools y capacidades actuales, esta en:

- [docs/ai-radar-operating-model.md](docs/ai-radar-operating-model.md)
- [docs/ai-radar-current-state.md](docs/ai-radar-current-state.md)
- [skills/ai-radar-source-manager/references/source-contract.md](skills/ai-radar-source-manager/references/source-contract.md)

La portada operativa y el administrador visual de fuentes viven en
[AI Radar — Centro de operacion y fuentes](https://app.notion.com/p/3ac17079ee1581bd9a0dda605b898701).

## Skills Del Proyecto

| Skill | Responsabilidad |
|---|---|
| `ai-radar-source-manager` | Sincronizar Notion, validar salud, generar cache y gobernar cambios. |
| `ai-radar-source-normalizer` | Convertir entradas heterogeneas en candidatos comparables. |
| `ai-radar-signals` | Curar noticias recientes usando el catalogo preparado. |
| `ai-radar-signal-reviewer` | Auditar calidad editorial y deduplicacion. |
| `ai-radar-ranking-engine` | Puntuar y ordenar senales deterministicamente. |
| `ai-radar-test-fixture-builder` | Convertir reglas editoriales en fixtures y pruebas. |
| `desarrollo-frontend-airadar` | Implementar y verificar interfaces con datos trazables, estados completos, accesibilidad y evidencia visual. |

La existencia de la skill frontend define el proceso de entrega, pero no
significa que el dashboard objetivo ya este versionado o desplegado.

## Herramientas Locales

El repositorio incluye scripts Python internos para consultar datos locales sin
cargar todos los JSON en contexto. Las skills deben llamarlos directamente; no
se mantienen ejecutadores de paquete.

```bash
python3 scripts/airadar.py list --tag agents --fields id,title,action
python3 scripts/airadar.py summary --from 2026-06-15
python3 scripts/airadar.py ranking --limit 3
python3 scripts/airadar.py ranking --generate --date 2026-06-25 --limit 3
python3 scripts/airadar.py show 2026-06-18-deepmind-agent-control-roadmap --fields title,action,url
python3 scripts/airadar.py validate --date 2026-06-20
python3 scripts/airadar.py audit --date 2026-06-20
python3 scripts/airadar.py coverage --from 2026-06-13 --to 2026-07-09
python3 scripts/airadar.py persistence
python3 scripts/load_supabase.py
python3 scripts/check_skill_sync.py
python3 skills/ai-radar-source-manager/scripts/validate_sources_cache.py config/sources.json
```

Comandos disponibles:

- `list`: filtra senales diarias por fecha, tag, impacto, estado, fuente o texto.
- `summary`: resume conteos por fecha, impacto, estado, fuente y tags.
- `show`: muestra una senal especifica por `id`.
- `ranking`: genera rankings deterministas acumulados con `--generate --date`
  y consulta rankings editoriales en
  `data/reviews/rankings/signal-review-ranking-YYYY-MM-DD.json`.
- `validate`: valida estructura minima, ids, evidencias y tags de snapshots
  diarios.
- `audit`: detecta duplicados, evidencia vacia, conteos por estado y fuentes
  principales.
- `coverage`: reporta rango observado, dias con snapshot, dias faltantes y
  conteos de cobertura local sin crear snapshots nuevos.
- `persistence`: normaliza y valida los registros que corresponden a las tablas
  Supabase sin modificar ninguna base.
- `scripts/check_skill_sync.py`: compara las siete skills canonicas del
  repositorio con las copias activas de Codex y falla si falta o difiere algun
  archivo.

La carga remota o local requiere una URL y una clave secreta de servidor. El
script hace un dry-run por defecto y solo escribe con `--apply`:

```bash
SUPABASE_URL=https://PROJECT_REF.supabase.co \
SUPABASE_SECRET_KEY=... \
python3 scripts/load_supabase.py --apply
```

La clave secreta no debe guardarse en el repositorio ni exponerse al frontend.

Filtros utiles:

- `--date YYYY-MM-DD`
- `--from YYYY-MM-DD`
- `--to YYYY-MM-DD`
- `--tag agents`
- `--impact high`
- `--status actionable`
- `--source Axios`
- `--q DeepMind`
- `--limit 5`
- `--fields id,title,action,url`
- `--format json`

## Flujo Local-First Para Senales

Cuando una solicitud pida senales por fecha, tag, fuente, impacto, estado o
texto, AI Radar debe consultar primero los datos locales:

```bash
python3 scripts/airadar.py list --date 2026-06-17 --limit 2 --format json
```

Si el resultado contiene suficientes senales, la respuesta debe usar esos datos
persistidos. Si no hay datos suficientes, se buscan fuentes externas, se curan
las senales contra el contrato diario y se guarda o actualiza
`data/signals/daily/daily-radar-YYYY-MM-DD.json` antes de responder.

La regla practica es: local primero, web solo cuando falte informacion, y toda
curacion nueva debe quedar versionada en `data/signals/daily/` salvo que se pida
explicitamente una respuesta exploratoria sin persistencia.

## Estructura De Datos Locales

Los datos versionados separan responsabilidades por directorio:

- `data/signals/daily/`: snapshots diarios curados por `source.publishedAt`.
- `data/reviews/rankings/`: rankings y auditorias editoriales sobre senales.
- `data/sources/candidates/`: candidatos normalizados antes de curacion final.

## Persistencia Supabase

La definicion reproducible vive en `supabase/`:

- `supabase/config.toml`: entorno de desarrollo local.
- `supabase/migrations/`: esquema, indices, grants y politicas RLS versionados.
- `src/persistence.py`: mapeo determinista desde los JSON a registros
  relacionales.
- `scripts/load_supabase.py`: upserts por lotes, protegidos por `--apply`.

El esquema separa datos publicados de datos editoriales internos. Los roles
`anon` y `authenticated` solo tienen `SELECT` sobre snapshots, senales,
rankings y entradas de ranking. Los lotes de candidatos y sus registros solo
son accesibles mediante un backend con clave secreta.

## Criterio Para Crear Tools

Una tarea debe convertirse en herramienta cuando sea repetible, deterministica
y validable. En AI Radar, las skills deben usar `scripts/airadar.py` para
operaciones que siguen siempre la misma logica:

```bash
python3 scripts/airadar.py audit --date 2026-06-20
```

La auditoria local cubre cuatro capacidades que no requieren razonamiento del
modelo:

- detectar senales duplicadas por `id`, URL o titulo normalizado,
- contar senales por estado,
- detectar evidencia vacia,
- listar fuentes principales y su frecuencia.
