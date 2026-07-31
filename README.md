# AI Radar

AI Radar es el proyecto del curso avanzado de Codex.

El objetivo del producto es organizar noticias, herramientas, papers, repos y lanzamientos de IA para convertirlos en senales accionables para builders: que paso, por que importa, que tan confiable es y que vale la pena probar.

Estado actual: nucleo local operativo para administrar fuentes, normalizar
candidatos, curar senales, auditarlas y producir rankings deterministas. Notion
funciona como fuente maestra del catalogo editorial y el repositorio conserva
contratos, cache operativa, snapshots y evidencia de validacion. La persistencia
Supabase ya cuenta con proyecto Cloud, esquema versionado, RLS, carga
idempotente y validacion local y remota.

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

Al 31 de julio de 2026, el proyecto cuenta con:

- 16 fuentes activas y saludables administradas en Notion;
- una cache local v2 con TTL de 24 horas y fallback explicito;
- cuatro grupos de fuentes para recoleccion paralela;
- 8 skills canonicas para fuentes, normalizacion, senales, revision, ranking,
  fixtures, desarrollo frontend y auditoria de casos de uso;
- 24 snapshots diarios con 115 senales, 2 lotes con 22 candidatos
  normalizados y 4 rankings con 282 entradas;
- CLI local para consulta, validacion, auditoria, cobertura y ranking;
- persistencia Supabase local y Cloud con 4 migraciones versionadas, RLS y 449
  filas;
- dashboard estatico responsive en `frontend/`, conectado primero a Supabase
  Cloud, con cinco secciones operativas, notificaciones verificables, fixtures
  versionados como fallback visible y 12 capturas de
  evidencia;
- 44 pruebas `unittest` para el dominio, el CLI, el catalogo, la persistencia y
  la sincronizacion de skills y documentacion.

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
- [docs/supabase-cloud.md](docs/supabase-cloud.md)
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
| `ai-radar-use-case-auditor` | Ejecutar casos de uso end-to-end, conservar evidencia y convertir hallazgos en issues reproducibles. |

El dashboard ya esta versionado en `frontend/`, consulta Supabase Cloud mediante
la Data API y declara visualmente si opera en Cloud o en fallback local. Su
despliegue sigue pendiente.

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
python3 scripts/load_supabase.py --local --apply
python3 scripts/record_source_finding.py --help
python3 scripts/check_skill_sync.py
python3 scripts/check_documentation_sync.py
python3 skills/ai-radar-source-manager/scripts/validate_sources_cache.py config/sources.json
python3 -m http.server 8000
```

Con el servidor estatico activo, el dashboard se abre en
`http://127.0.0.1:8000/frontend/`. Los estados de demostracion reproducibles
usan `?demo=empty` y `?demo=error`; la evidencia visual revisada vive en
`frontend/evidence/`.

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
- `scripts/check_skill_sync.py`: compara las 8 skills canonicas del
  repositorio con las copias activas de Codex y falla si falta o difiere algun
  archivo.
- `scripts/check_documentation_sync.py`: deriva metricas desde datos, pruebas,
  skills, migraciones y evidencia visual; falla si README o los documentos
  canonicos dejan de reflejarlas.
- `scripts/record_source_finding.py`: registra bloqueos HTTP y descartes por
  metadatos insuficientes en `data/observability/` sin detener los otros grupos
  ni inventar fechas.

La carga remota o local requiere una URL y una clave secreta de servidor. El
script hace un dry-run por defecto y solo escribe con `--apply`:

```bash
SUPABASE_URL=https://PROJECT_REF.supabase.co \
SUPABASE_SECRET_KEY=... \
python3 scripts/load_supabase.py --apply
```

La clave secreta no debe guardarse en el repositorio ni exponerse al frontend.
La configuracion publica del frontend vive en `frontend/supabase-config.js` y
usa exclusivamente una clave `sb_publishable_...`.

Para cargar la instancia local sin copiar ni mostrar sus claves:

```bash
npx --yes supabase@2.110.0 status
python3 scripts/load_supabase.py --local --apply
```

`--local` obtiene las credenciales efimeras mediante Supabase CLI, las mantiene
solo en memoria y reporta exclusivamente los conteos aplicados.

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

El proyecto Cloud, sus conteos, controles de acceso y procedimiento operativo
se documentan en [docs/supabase-cloud.md](docs/supabase-cloud.md).

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

## Sincronizacion Documental

La implementacion es la fuente de las metricas; README, documentos canonicos y
Notion son sus proyecciones explicativas.

| Estado verificable | Reflejo obligatorio |
|---|---|
| Datos y rankings bajo `data/` | README, estado actual y Supabase Cloud |
| Skills bajo `skills/` | README, estado actual, modelo operativo y copias activas |
| Migraciones y proyecto Supabase | README, estado actual, modelo operativo, documento Cloud y Notion |
| Dashboard y `frontend/evidence/` | README, estado actual, modelo operativo y Notion |
| Suite `unittest` | README, estado actual y Notion |

Antes de cerrar un cambio material:

```bash
python3 scripts/check_skill_sync.py
python3 scripts/check_documentation_sync.py
python3 -m unittest
```

El segundo comando valida las proyecciones versionadas. La portada
[AI Radar — Centro de operacion y fuentes](https://app.notion.com/p/3ac17079ee1581bd9a0dda605b898701)
debe compararse mediante el conector de Notion porque no forma parte del
filesystem local.
