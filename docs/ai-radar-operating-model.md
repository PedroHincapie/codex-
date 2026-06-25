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
  Agent --> Skills[Skills AI Radar]
  Skills --> Tools[Scripts Python]
  Tools --> Store[src/radar_store.py]
  Store --> Fixtures[data/fixtures/*.json]
  Fixtures --> Contract[docs/contracts/ai-radar-daily.schema.json]
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
  A[Solicitud del usuario] --> B[Normalizar fecha y filtros]
  B --> C[Consultar fixtures con scripts/airadar.py]
  C --> D{Hay suficientes senales?}
  D -- Si --> E[Responder desde snapshot local]
  D -- No --> F[Buscar fuentes externas]
  F --> G[Curar senales contra contrato]
  G --> H[Persistir snapshot diario]
  H --> I[Validar y auditar]
  I --> J[Responder desde estado persistido]
```

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
  participant F as data/fixtures
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
| Listar senales | `python3 scripts/airadar.py list --date YYYY-MM-DD` | Consultar fixtures antes de buscar fuera. |
| Resumir radar | `python3 scripts/airadar.py summary --from YYYY-MM-DD` | Obtener conteos por fecha, impacto, estado, fuente y tags. |
| Mostrar senal | `python3 scripts/airadar.py show SIGNAL_ID` | Revisar una senal completa o campos puntuales. |
| Ranking | `python3 scripts/airadar.py ranking --date YYYY-MM-DD` | Consultar ranking editorial si existe fixture. |
| Validacion | `python3 scripts/airadar.py validate --date YYYY-MM-DD` | Revisar estructura minima del snapshot. |
| Auditoria | `python3 scripts/airadar.py audit --date YYYY-MM-DD` | Detectar duplicados, evidencia vacia, estados y fuentes. |

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
  B[data/fixtures/] --> B1[Snapshots diarios]
  B --> B2[Rankings y candidatos]
  C[src/] --> C1[Logica reusable Python]
  D[scripts/] --> D1[Tools llamadas por skills]
  E[skills/] --> E1[Instrucciones especializadas]
  F[tests/] --> F1[Pruebas unittest]
```

## Reglas De Trabajo

- Consultar local antes de buscar en internet.
- Persistir informacion nueva antes de usarla como respuesta del radar.
- Usar scripts Python directamente desde skills.
- Convertir tareas mecanicas en tools.
- Probar tools con `unittest`.
- Validar JSON con `jq` cuando se editen fixtures o contratos.
- No guardar articulos completos, secretos ni salidas generadas no revisadas.

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
