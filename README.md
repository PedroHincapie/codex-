# AI Radar

AI Radar es el proyecto del curso avanzado de Codex.

El objetivo del producto es organizar noticias, herramientas, papers, repos y lanzamientos de IA para convertirlos en senales accionables para builders: que paso, por que importa, que tan confiable es y que vale la pena probar.

Estado inicial: definicion de producto, stack objetivo y reglas iniciales. La implementacion se construye por capas durante el curso con Codex.

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

## Estado Inicial

El starter contiene:

- `README.md`
- `.gitignore`

La primera clase usa este estado para mostrar como `AGENTS.md` cambia la forma en que Codex entiende un proyecto antes de escribir codigo.

## Stack Objetivo

El stack debe mantenerse simple para que el foco del curso sea Codex, no el framework.

- Frontend: HTML, CSS y JavaScript.
- Dominio y scripts internos: Python con libreria estandar.
- CLI interno: `scripts/airadar.py` para comandos del proyecto y skills.
- Automatizacion local: scripts Python llamados directamente por skills.
- Proyecto agent-friendly: Dekk cuando existan comandos que deban usar humanos y agentes.
- API: Vercel Functions cuando hagan falta endpoints.
- Datos locales: fixtures y snapshots antes de conectar servicios externos.
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

## Herramientas Locales

El repositorio incluye scripts Python internos para consultar fixtures sin
cargar todos los JSON en contexto. Las skills deben llamarlos directamente; no
se mantienen ejecutadores de paquete.

```bash
python3 scripts/airadar.py list --tag agents --fields id,title,action
python3 scripts/airadar.py summary --from 2026-06-15
python3 scripts/airadar.py ranking --limit 3
python3 scripts/airadar.py show 2026-06-24-deepmind-agent-control-roadmap --fields title,action,url
python3 scripts/airadar.py validate --date 2026-06-20
python3 scripts/airadar.py audit --date 2026-06-20
```

Comandos disponibles:

- `list`: filtra senales diarias por fecha, tag, impacto, estado, fuente o texto.
- `summary`: resume conteos por fecha, impacto, estado, fuente y tags.
- `show`: muestra una senal especifica por `id`.
- `ranking`: consulta el ranking editorial cuando exista un fixture
  `signal-review-ranking-YYYY-MM-DD.json`.
- `validate`: valida estructura minima, ids, evidencias y tags de snapshots
  diarios.
- `audit`: detecta duplicados, evidencia vacia, conteos por estado y fuentes
  principales.

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
texto, AI Radar debe consultar primero los fixtures locales:

```bash
python3 scripts/airadar.py list --date 2026-06-17 --limit 2 --format json
```

Si el resultado contiene suficientes senales, la respuesta debe usar esos datos
persistidos. Si no hay datos suficientes, se buscan fuentes externas, se curan
las senales contra el contrato diario y se guarda o actualiza
`data/fixtures/daily-radar-YYYY-MM-DD.json` antes de responder.

La regla practica es: local primero, web solo cuando falte informacion, y toda
curacion nueva debe quedar versionada en `data/fixtures/` salvo que se pida
explicitamente una respuesta exploratoria sin persistencia.

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
