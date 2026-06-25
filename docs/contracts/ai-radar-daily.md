# Contrato Diario de AI Radar

Este documento explica en lenguaje humano el contrato definido en
`ai-radar-daily.schema.json`. El objetivo es fijar una base comun para
guardar busquedas diarias como senales accionables, sin mezclar titulares,
opiniones y decisiones tecnicas.

## Proposito

Una busqueda diaria de AI Radar debe convertir noticias recientes de
inteligencia artificial en senales utiles para builders. Cada senal debe
responder:

- que paso,
- de donde viene la informacion,
- que evidencia sostiene la senal,
- por que importa,
- que accion concreta sugiere,
- en que estado queda.

El archivo JSON diario es un snapshot versionado. No intenta ser una base de
datos completa ni una transcripcion de articulos. Su funcion es conservar una
lectura curada del dia con suficiente contexto para revisarla, compararla y
automatizarla despues.

## Flujo Operativo Local-First

AI Radar debe consultar primero sus snapshots locales antes de buscar nuevas
fuentes. Para una solicitud por fecha, tag, fuente, impacto, estado o texto, el
primer paso operativo es usar el store local o el CLI:

```bash
python3 scripts/airadar.py list --date YYYY-MM-DD --limit N --format json
```

Si hay suficientes senales locales, la respuesta debe salir de esos fixtures.
Si no existen o son insuficientes, se pueden buscar fuentes externas, pero la
curacion resultante debe persistirse como `data/fixtures/daily-radar-YYYY-MM-DD.json`
antes de responder. La unica excepcion es una instruccion explicita del usuario
para obtener una respuesta exploratoria o descartable sin guardar.

Este flujo evita perder trabajo editorial, mantiene trazabilidad de fuentes y
permite que busquedas futuras reutilicen la base local en vez de repetir la
misma investigacion.

Las skills deben usar los scripts Python directamente. El proyecto no depende
de ejecutadores de paquete para estas consultas internas.

```bash
python3 scripts/airadar.py validate --date YYYY-MM-DD
python3 scripts/airadar.py audit --date YYYY-MM-DD
```

Usar `audit` cuando la tarea sea repetible, deterministica y validable:
detectar duplicados, contar estados, revisar evidencia vacia y listar fuentes
principales no requiere razonamiento del modelo.

## Estructura Del Archivo Diario

Cada archivo diario debe tener estos campos raiz:

- `$schema`: ruta al contrato JSON Schema usado para validar el archivo.
- `contractVersion`: version semantica del contrato, por ejemplo `1.0.0`.
- `radarDate`: fecha que representa el corte editorial del radar.
- `generatedAt`: fecha y hora en que se genero el snapshot.
- `topic`: tema principal de la busqueda, por ejemplo `artificial-intelligence`.
- `locale`: idioma o contexto de salida, por ejemplo `es`.
- `signals`: lista de senales seleccionadas para ese dia.

## Definicion De Una Senal

Una senal es una noticia, evento, paper, lanzamiento o movimiento de mercado
que puede cambiar decisiones practicas. No todo titular es una senal.

Cada senal debe incluir:

- `id`: identificador estable con fecha y slug. Ejemplo:
  `2026-06-20-deepmind-agent-controls`.
- `title`: resumen corto de la senal en lenguaje claro.
- `source`: fuente principal usada para sostener la senal.
- `evidence`: lista de hechos verificables extraidos o inferidos de la fuente.
- `impact`: nivel y resumen del posible efecto.
- `action`: recomendacion practica para un builder, equipo o producto.
- `status`: estado editorial de la senal.
- `tags`: etiquetas normalizadas para agrupar senales.

## Fuente

`source` describe la referencia principal:

- `name`: medio, organizacion, paper o fuente oficial.
- `url`: enlace directo.
- `publishedAt`: fecha de publicacion de la fuente.
- `retrievedAt`: fecha en que AI Radar consulto la fuente.

Si una senal depende de varias fuentes, el contrato actual guarda solo la
fuente principal. Las fuentes secundarias deben incorporarse como evidencia
solo si son necesarias. Si esto se vuelve frecuente, el contrato debe
evolucionar a `sources`.

## Evidencias

`evidence` debe contener hechos concretos, no opiniones vagas. Una buena
evidencia cumple al menos una de estas condiciones:

- confirma que el evento ocurrio,
- muestra quien esta involucrado,
- aporta fecha, decision, cifra o cambio observable,
- explica una consecuencia directa ya reportada.

Evitar evidencias como "es importante" o "hay mucho interes". Eso pertenece a
`impact`.

## Impacto

`impact.level` clasifica el posible efecto:

- `low`: informacion util pero sin accion inmediata clara.
- `medium`: puede afectar seguimiento, roadmap o investigacion.
- `medium-high`: puede alterar decisiones de proveedor, arquitectura,
  mercado o cumplimiento.
- `high`: puede cambiar acceso, costos, regulacion, seguridad o ventaja
  competitiva de forma relevante.

`impact.summary` explica por que el nivel fue asignado. Debe ser especifico y
defendible.

## Accion

`action` transforma la senal en una recomendacion concreta. Debe poder
convertirse en una tarea, experimento o criterio de seguimiento.

Ejemplos:

- "Preparar fallback multi-provider."
- "Evaluar proveedores soberanos si el producto opera en la Union Europea."
- "Disenar agentes con logs, permisos minimos y kill-switch."

## Estado

`status` indica como debe leerse la senal:

- `candidate`: senal prometedora, pero falta evidencia suficiente.
- `debated`: hay debate publico o incertidumbre material.
- `evolving`: el hecho esta activo y puede cambiar pronto.
- `confirmed`: el hecho principal esta confirmado por la fuente usada.
- `actionable`: ya sugiere una accion tecnica o de producto clara.
- `archived`: se conserva por historial, pero ya no requiere seguimiento.

## Tags

`tags` permite agrupar y rankear senales. Deben escribirse en minusculas,
usando guiones para separar palabras. Ejemplos:

- `agents`
- `frontier-models`
- `national-security`
- `ai-for-science`

No usar tags como frases largas ni duplicar informacion ya presente en el
titulo.

## Reglas Editoriales

- Distinguir noticia, evidencia, impacto y accion.
- No guardar articulos completos ni citas largas.
- No asumir que una vision futura ya esta implementada.
- Consultar snapshots locales antes de buscar informacion externa.
- Persistir informacion nueva curada antes de usarla como respuesta del radar.
- Preferir senales con fecha, fuente y consecuencia clara.
- Mantener el JSON diario pequeno, revisable y versionable.
- Si el contrato no alcanza para representar una necesidad real, evolucionar
  el schema antes de forzar datos ambiguos.

## Relacion Con El Proyecto

Este contrato es la primera base operativa de AI Radar. Permite empezar con
fixtures locales antes de conectar APIs, bases de datos o dashboards. Las
capas futuras del proyecto pueden usar estos archivos para probar parsing,
normalizacion, ranking, deduplicacion y visualizacion.
