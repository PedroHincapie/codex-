---
name: ai-radar-signals
description: Convert recent artificial intelligence news, links, article lists, or research/product updates into structured AI Radar daily signals. Use when Codex must curate AI news into evidence-backed signals, create or reuse an AI Radar JSON contract, generate daily JSON snapshots, document signal decisions, or validate future news batches against the AI Radar format.
---

# AI Radar Signals

## Objetivo

Convertir noticias recientes de inteligencia artificial en senales
estructuradas, accionables y versionables para AI Radar.

La salida debe separar noticia, fuente, evidencia, impacto, accion y estado.
No guardar articulos completos ni titulares sin analisis.

AI Radar opera con un flujo local-first: antes de buscar informacion externa,
consultar los snapshots existentes. Si la senal ya existe localmente, responder
desde el fixture. Si no existe y se cura informacion nueva, persistirla en el
snapshot diario antes de entregar el resultado, salvo que el usuario pida
explicitamente una respuesta descartable sin guardar.

## Inputs

Aceptar uno o varios de estos inputs:

- Lista de URLs, titulares, articulos, papers, repositorios o lanzamientos.
- Una busqueda solicitada por el usuario sobre noticias recientes de IA.
- Un archivo JSON diario existente para actualizar o comparar.
- Un contrato existente en `docs/contracts/ai-radar-daily.schema.json`.
- Una fecha de corte. Si no se indica, usar la fecha actual del entorno.

Si el usuario pide noticias recientes, buscar/verificar en internet antes de
producir senales. Comparar fechas de publicacion y evitar noticias antiguas
presentadas como nuevas.

## Workflow

1. **Normalizar la solicitud**
   - Convertir fechas relativas o incompletas a fechas ISO concretas cuando el
     contexto lo permita.
   - Si el ano no es inferible con seguridad, pedir aclaracion antes de buscar.
   - Definir cuantas senales se solicitan y para que fecha editorial.

2. **Consultar la base local primero**
   - Revisar si existen `docs/contracts/ai-radar-daily.schema.json`,
     `docs/contracts/ai-radar-daily.md` y archivos diarios en
     `data/signals/daily/`.
   - Si existe CLI local, usarlo para consultar antes de buscar en internet:
     `python3 scripts/airadar.py list --date YYYY-MM-DD --limit N --format json`.
   - Llamar los scripts Python directamente desde la skill; no depender de
     ejecutadores de paquete.
   - Si hay suficientes senales locales, responder desde esos datos y no
     hacer busqueda externa.
   - No asumir comandos, APIs, dashboard o base de datos si no existen.

3. **Recolectar candidatos solo si falta informacion local**
   - Antes de usar internet, comunicar que se consulto el estado local y la
     razon concreta por la que resulta insuficiente o requiere verificacion.
   - Reunir noticias de IA recientes desde inputs del usuario o busqueda web.
   - Priorizar fuentes primarias u organizaciones periodisticas confiables.
   - Capturar URL, fuente, fecha de publicacion y fecha de consulta.

4. **Seleccionar senales**
   - Elegir noticias con consecuencia practica para builders.
   - Descartar duplicados, rumores debiles, marketing sin evidencia y notas
     repetidas sin novedad.
   - Preferir eventos con actores claros, fechas, decisiones, cifras o cambios
     observables.

5. **Estructurar cada senal**
   - Crear `id` con formato `YYYY-MM-DD-slug`.
   - Escribir `title` como resumen claro de la senal.
   - Completar `source` con `name`, `url`, `publishedAt`, `retrievedAt`.
   - Agregar `evidence` como lista de hechos verificables.
   - Clasificar `impact.level`: `low`, `medium`, `medium-high` o `high`.
   - Escribir `impact.summary` con razon especifica y defendible.
   - Definir `action` como recomendacion concreta.
   - Definir `status`: `candidate`, `debated`, `evolving`, `confirmed`,
     `actionable` o `archived`.
   - Agregar `tags` normalizados en minusculas con guiones.

6. **Crear o reutilizar contrato**
   - Si el schema existe, respetarlo.
   - Si no existe, crear `docs/contracts/ai-radar-daily.schema.json`.
   - Si hace falta explicar el contrato, crear o actualizar
     `docs/contracts/ai-radar-daily.md`.

7. **Guardar snapshot diario**
   - Crear `data/signals/daily/daily-radar-YYYY-MM-DD.json`.
   - Si el archivo ya existe, agregar o actualizar solo las senales necesarias,
     evitando duplicados por `id`, URL o evento equivalente.
   - Incluir `$schema`, `contractVersion`, `radarDate`, `generatedAt`,
     `topic`, `locale` y `signals`.
   - Mantener el archivo pequeno, revisable y apto para pruebas futuras.
   - Persistir el snapshot antes de responder cuando se haya curado informacion
     nueva para el ecosistema AI Radar.

8. **Validar**
   - Validar sintaxis JSON con `jq empty <archivo>`.
   - Validar el schema JSON con `jq empty <schema>`.
   - Si existe el CLI Python, ejecutar
     `python3 scripts/airadar.py validate --date YYYY-MM-DD`.
   - Para controles repetibles de calidad editorial, ejecutar
     `python3 scripts/airadar.py audit --date YYYY-MM-DD`.
   - Si existe un validador de JSON Schema en el repo, usarlo.
   - Revisar que cada senal tenga fuente, evidencia, impacto, accion y estado.

9. **Responder desde el estado persistido**
   - Si las senales venian de datos locales existentes, indicarlo.
   - Si se curaron senales nuevas, responder despues de guardar y validar el
     snapshot diario.
   - Usar el formato de conversacion solicitado por el usuario, pero mantener
     trazabilidad hacia el archivo diario.

10. **Reportar**
   - Resumir archivos creados o modificados.
   - Indicar validaciones ejecutadas.
   - Mencionar cualquier supuesto, fuente no verificada o limitacion.

## Reglas

- Distinguir estado actual del repositorio y vision futura del producto.
- No inventar comandos, integraciones, APIs, bases de datos ni dashboards.
- No guardar secretos, credenciales, `.env`, bases de datos ni certificados.
- No copiar articulos completos ni citas extensas.
- No usar una fuente como evidencia si no fue consultada o provista.
- No presentar una inferencia como hecho; marcarla como inferencia si aplica.
- No buscar en internet sin consultar primero los datos locales cuando la
  solicitud sea por fecha, tag, fuente, estado, impacto o texto consultable.
- No iniciar una busqueda externa sin informar antes que se reviso la base
  local y por que no basta para responder.
- No dejar informacion curada solo en la conversacion cuando falte en la base
  local; guardarla como snapshot diario salvo instruccion explicita en contra.
- Preferir ASCII en archivos nuevos salvo que el repo ya use otro criterio.
- Mantener nombres de archivos en `kebab-case`.
- Usar fechas absolutas en formato ISO cuando haya ambiguedad temporal.
- Si el contrato no representa una necesidad real, evolucionarlo antes de
  forzar datos ambiguos.

## Artefactos Generados

El flujo puede generar o actualizar:

- `docs/contracts/ai-radar-daily.schema.json`: contrato JSON Schema.
- `docs/contracts/ai-radar-daily.md`: explicacion humana del contrato.
- `data/signals/daily/daily-radar-YYYY-MM-DD.json`: snapshot diario de senales.
- Opcionalmente, pruebas futuras bajo `tests/` cuando el repo tenga tooling.

## Validaciones

Validar como minimo:

```bash
jq empty docs/contracts/ai-radar-daily.schema.json
jq empty data/signals/daily/daily-radar-YYYY-MM-DD.json
```

Revisar manualmente:

- `contractVersion` usa version semantica.
- `radarDate`, `generatedAt`, `publishedAt` y `retrievedAt` son coherentes.
- Cada `id` empieza con la fecha del radar y tiene slug estable.
- Cada `evidence` contiene hechos concretos, no opiniones.
- Cada `impact.summary` justifica el nivel elegido.
- Cada `action` puede convertirse en una tarea o criterio de seguimiento.
- Cada `tag` usa minusculas, numeros o guiones.

## Formato De Salida

Cuando el usuario pida solo resultados en conversacion, responder con una
tabla o lista usando estos campos:

- Senal
- Fuente
- Evidencias
- Impacto
- Accion
- Estado

Cuando el usuario pida guardar el resultado, crear un JSON diario con esta
forma:

```json
{
  "$schema": "../../docs/contracts/ai-radar-daily.schema.json",
  "contractVersion": "1.0.0",
  "radarDate": "YYYY-MM-DD",
  "generatedAt": "YYYY-MM-DDTHH:mm:ssZ",
  "topic": "artificial-intelligence",
  "locale": "es",
  "signals": [
    {
      "id": "YYYY-MM-DD-slug",
      "title": "Resumen corto de la senal",
      "source": {
        "name": "Fuente",
        "url": "https://example.com/article",
        "publishedAt": "YYYY-MM-DD",
        "retrievedAt": "YYYY-MM-DD"
      },
      "evidence": [
        "Hecho verificable 1",
        "Hecho verificable 2"
      ],
      "impact": {
        "level": "medium-high",
        "summary": "Por que importa esta senal."
      },
      "action": "Accion concreta sugerida.",
      "status": "actionable",
      "tags": [
        "agents",
        "safety"
      ]
    }
  ]
}
```
