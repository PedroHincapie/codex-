# Modelo Operativo de AI Radar

Este documento explica que hacemos en AI Radar, como lo hacemos y donde viven
las capacidades del proyecto. La regla central es simple: el modelo decide
cuando actuar, pero las tareas repetibles, deterministicas y validables se
convierten en herramientas Python.

## Objetivo

AI Radar convierte noticias, papers, repositorios, herramientas y lanzamientos
de IA en senales accionables para builders. Una senal debe responder:

- que paso,
- que fuente lo sostiene,
- que evidencia concreta existe,
- por que importa,
- que accion sugiere,
- en que estado editorial queda.

## Mapa Del Sistema

```mermaid
flowchart LR
  User[Usuario] --> Agent[Agente Codex]
  Agent --> Manager[ai-radar-source-manager]
  Manager --> Notion[Notion: AI Radar Sources]
  Manager --> Cache[config/sources.json]
  Cache --> Signals[ai-radar-signals]
  Signals --> Skills[Skills AI Radar]
  Skills --> Tools[Scripts Python]
  Tools --> Store[src/radar_store.py]
  Store --> Daily[data/signals/daily/*.json]
  Store --> Reviews[data/reviews/rankings/*.json]
  Store --> Sources[data/sources/candidates/*.json]
  Store --> Persistence[src/persistence.py]
  Persistence --> Supabase[(Supabase Postgres)]
  Daily --> Contract[docs/contracts/ai-radar-daily.schema.json]
  Tools --> Report[Salida JSON o TSV]
  Agent --> Response[Respuesta al usuario]
  Report --> Agent
```

El agente no debe leer y razonar sobre todos los JSON si existe una herramienta
local que puede calcular el resultado. Las skills llaman scripts Python
directamente para consultar, validar o auditar datos.

## Flujo Local-First

Toda solicitud consultable por fecha, tag, fuente, estado, impacto o texto debe
empezar en la base local.

```mermaid
flowchart TD
  A[Solicitud del usuario] --> B[Sincronizar catalogo de fuentes]
  B --> C[Consultar datos locales con scripts/airadar.py]
  C --> D{Hay suficientes senales?}
  D -- Si --> E[Responder desde snapshot local]
  D -- No --> F[Buscar fuentes externas]
  F --> G[Curar senales contra contrato]
  G --> H[Persistir snapshot diario]
  H --> I[Validar y auditar]
  I --> J[Responder desde estado persistido]
```

La sincronizacion consulta Notion antes de la primera recoleccion editorial del
dia. Si Notion no responde, conserva la ultima cache valida y reporta
`fallback-cache`; si tampoco existe cache, reporta `fallback-no-cache`.

Comando base:

```bash
python3 scripts/airadar.py list --date YYYY-MM-DD --limit N --format json
```

## Ciclo De Curacion

```mermaid
sequenceDiagram
  participant U as Usuario
  participant A as Agente
  participant S as Skill ai-radar-signals
  participant T as scripts/airadar.py
  participant F as data/signals/daily
  participant W as Web/Fuentes externas

  U->>A: Lista senales de una fecha
  A->>S: Aplicar flujo AI Radar
  S->>T: list --date YYYY-MM-DD
  T->>F: Leer snapshots locales
  F-->>T: Senales existentes
  T-->>S: Resultado JSON
  alt Hay suficientes senales
    S-->>A: Usar datos locales
    A-->>U: Respuesta trazable al snapshot
  else Faltan senales
    S->>W: Buscar/verificar fuentes
    S->>F: Crear o actualizar snapshot
    S->>T: validate y audit
    T-->>S: Resultado verificable
    S-->>A: Responder desde snapshot persistido
    A-->>U: Respuesta con archivo y validaciones
  end
```

## Administracion De Fuentes

Notion `AI Radar Sources` es la fuente maestra. La skill
`ai-radar-source-manager` valida el catalogo y genera `config/sources.json`,
que `ai-radar-signals` consume en modo de solo lectura.

```mermaid
flowchart LR
  N[Notion: AI Radar Sources] --> M[Source Manager]
  M --> V{Catalogo valido?}
  V -- Si --> C[Cache v2 / TTL 24 h]
  V -- No --> F[Conservar ultima cache valida]
  C --> O[Fuentes oficiales]
  C --> R[Repositorios tecnicos]
  C --> U[Comunidades]
  C --> S[Medios secundarios]
  O --> Q[Curacion y deduplicacion]
  R --> Q
  U --> Q
  S --> Q
```

Cadencia recomendada:

| Operacion | Frecuencia | Resultado |
|---|---|---|
| Sincronizacion | Diaria o cache mayor a 24 horas | Catalogo fresco o fallback explicito |
| Salud | Semanal | Disponibilidad, fallos y contenido reciente |
| Descubrimiento | Mensual | Nuevas fuentes candidatas normalizadas |
| Revision editorial | Trimestral | Cobertura, ruido, duplicados y decisiones humanas |

Altas, desactivaciones y cambios de URL o categoria requieren aprobacion
humana. Las metricas de salud comprobadas pueden actualizarse
automaticamente.

## Cuando Convertir Una Tarea En Tool

Una tarea se convierte en herramienta cuando cumple tres condiciones:

- `repetible`: aparece mas de una vez en el flujo de trabajo.
- `deterministica`: la misma entrada produce la misma salida.
- `validable`: podemos probar o verificar el resultado.

```mermaid
flowchart TD
  A[Tarea recurrente] --> B{Es repetible?}
  B -- No --> C[Resolver con razonamiento del modelo]
  B -- Si --> D{Es deterministica?}
  D -- No --> C
  D -- Si --> E{Es validable?}
  E -- No --> C
  E -- Si --> F[Crear tool Python]
  F --> G[Agregar pruebas unittest]
  G --> H[Documentar comando para skills]
```

Ejemplos que ya son tool:

- listar senales por fecha,
- resumir conteos,
- mostrar una senal por `id`,
- validar snapshots,
- auditar duplicados, evidencia vacia, estados y fuentes.

## Capacidades Actuales

| Capacidad | Comando | Uso |
|---|---|---|
| Listar senales | `python3 scripts/airadar.py list --date YYYY-MM-DD` | Consultar datos locales antes de buscar fuera. |
| Resumir radar | `python3 scripts/airadar.py summary --from YYYY-MM-DD` | Obtener conteos por fecha, impacto, estado, fuente y tags. |
| Mostrar senal | `python3 scripts/airadar.py show SIGNAL_ID` | Revisar una senal completa o campos puntuales. |
| Ranking | `python3 scripts/airadar.py ranking --date YYYY-MM-DD` | Consultar ranking editorial si existe fixture. |
| Validacion | `python3 scripts/airadar.py validate --date YYYY-MM-DD` | Revisar estructura minima del snapshot. |
| Auditoria | `python3 scripts/airadar.py audit --date YYYY-MM-DD` | Detectar duplicados, evidencia vacia, estados y fuentes. |
| Catalogo de fuentes | `python3 skills/ai-radar-source-manager/scripts/validate_sources_cache.py config/sources.json` | Validar TTL, propiedades, URLs, orden y grupos. |
| Preparar persistencia | `python3 scripts/airadar.py persistence` | Validar relaciones y contar registros antes de cargar. |
| Cargar Supabase | `python3 scripts/load_supabase.py --apply` | Ejecutar upserts idempotentes usando una clave secreta de servidor. |

## Flujo De Auditoria

```mermaid
flowchart LR
  A[audit --date YYYY-MM-DD] --> B[Cargar senales]
  B --> C[Contar estados]
  B --> D[Detectar evidencia vacia]
  B --> E[Detectar duplicados por id, URL y titulo]
  B --> F[Listar fuentes principales]
  C --> G[Reporte JSON]
  D --> G
  E --> G
  F --> G
```

La auditoria reduce tokens porque evita que el modelo lea snapshots completos
para tareas mecanicas. El modelo solo interpreta el reporte y decide el
siguiente paso editorial.

## Estructura Operativa

```mermaid
flowchart TD
  A[docs/] --> A1[Contratos y modelo operativo]
  B[data/signals/daily/] --> B1[Snapshots diarios]
  C[data/reviews/rankings/] --> C1[Rankings y auditorias]
  G[data/sources/candidates/] --> G1[Fuentes candidatas]
  J[config/sources.json] --> J1[Cache operativa del catalogo Notion]
  D[src/] --> D1[Logica reusable Python]
  E[scripts/] --> E1[Tools llamadas por skills]
  H[skills/] --> H1[Instrucciones especializadas]
  I[tests/] --> I1[Pruebas unittest]
```

## Reglas De Trabajo

- Consultar local antes de buscar en internet.
- Informar que se reviso el estado local y justificar la busqueda externa antes
  de iniciarla.
- Persistir informacion nueva antes de usarla como respuesta del radar.
- Usar scripts Python directamente desde skills.
- Convertir tareas mecanicas en tools.
- Probar tools con `unittest`.
- Validar JSON con `jq` cuando se editen datos locales o contratos.
- No guardar articulos completos, secretos ni salidas generadas no revisadas.
- Mantener las migraciones Supabase en Git y aplicar el mismo esquema en todos
  los entornos.
- No exponer `SUPABASE_SECRET_KEY` ni `SUPABASE_SERVICE_ROLE_KEY` al navegador.
- Habilitar RLS en todas las tablas `public` y combinar politicas con grants
  explicitos.

## Persistencia Relacional

```mermaid
erDiagram
  RADAR_SNAPSHOTS ||--o{ SIGNALS : contains
  RANKINGS ||--o{ RANKING_ENTRIES : contains
  SIGNALS ||--o{ RANKING_ENTRIES : scores
  SOURCE_CANDIDATE_BATCHES ||--o{ SOURCE_CANDIDATES : contains
```

Los JSON versionados siguen siendo la evidencia editorial auditable. La base
Supabase es una proyeccion relacional idempotente para consultas del dashboard
y futuras APIs. `radar_snapshots`, `signals`, `rankings` y `ranking_entries`
son de lectura publica; `source_candidate_batches` y `source_candidates`
permanecen internos.

## Sincronizacion De Las Skills Activas

Las versiones canonicas de `ai-radar-signals` y
`ai-radar-source-manager` viven en el repositorio. Cuando cambien,
sincronizarlas con las copias activas de Codex y reiniciar la aplicacion para
que una sesion nueva cargue las instrucciones actualizadas:

```bash
diff -u ~/.codex/skills/ai-radar-signals/SKILL.md \
  skills/ai-radar-signals/SKILL.md
cp skills/ai-radar-signals/SKILL.md \
  ~/.codex/skills/ai-radar-signals/SKILL.md
cp -R skills/ai-radar-source-manager \
  ~/.codex/skills/ai-radar-source-manager
```

Despues de copiar, volver a ejecutar `diff`. Una salida vacia confirma que la
skill instalada coincide con la fuente canonica.

## Camino De Evolucion

```mermaid
flowchart LR
  A[Fixtures locales] --> B[Tools Python]
  B --> C[Contratos mas ricos]
  C --> D[Deduplicacion y ranking automatizados]
  D --> E[Dashboard]
  E --> F[APIs y base de datos]
```

El proyecto debe crecer por capas. Primero se estabiliza el contrato local y
las tools; despues se conectan fuentes externas, UI, APIs o base de datos.
