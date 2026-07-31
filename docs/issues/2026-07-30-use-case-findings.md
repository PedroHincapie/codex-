# Issues Del Caso De Uso 2026-07-30

Los hallazgos fueron publicados el 31 de julio de 2026 en GitHub:

- [#1 Navegacion lateral](https://github.com/PedroHincapie/codex-/issues/1)
- [#2 Notificaciones](https://github.com/PedroHincapie/codex-/issues/2)
- [#3 Sincronizacion documental](https://github.com/PedroHincapie/codex-/issues/3)
- [#4 Bloqueos HTTP 403](https://github.com/PedroHincapie/codex-/issues/4)
- [#5 Fecha no verificable](https://github.com/PedroHincapie/codex-/issues/5)

## Frontend: hacer operativas las secciones del menu lateral

### Contexto

Hallazgo observado durante la revision end-to-end del 30 de julio de 2026 en
`http://127.0.0.1:8000/frontend/`.

### Evidencia

El menu presenta Radar, Rankings, Fuentes, Evidencia y Revisiones como
`button.nav-item`. `frontend/app.js` no contiene listeners ni un contrato de
navegacion para esos controles. Solo Radar tiene `is-active` y
`aria-current="page"`.

### Pasos para reproducir

1. Ejecutar `python3 -m http.server 8000` desde la raiz.
2. Abrir `http://127.0.0.1:8000/frontend/`.
3. Pulsar Rankings, Fuentes, Evidencia y Revisiones.
4. Observar contenido, URL, foco y estado activo.

### Resultado esperado

Cada boton abre una vista definida, actualiza el estado activo y comunica el
cambio de forma accesible. Un destino no disponible no aparenta ser operativo.

### Resultado actual

Los botones no producen un cambio visible ni actualizan navegacion, contenido
o estado accesible.

### Archivo probable

- `frontend/index.html`
- `frontend/app.js`
- `frontend/styles.css`

### Criterios de aceptacion

- [ ] Cada seccion tiene un destino o comportamiento definido.
- [ ] El control activo actualiza `is-active` y `aria-current`.
- [ ] Contenido y foco se actualizan de forma accesible.
- [ ] La navegacion funciona en escritorio y movil.
- [ ] Hay pruebas o evidencia visual de todas las secciones.
- [ ] La consola no presenta errores al navegar.

## Frontend: definir el proposito del boton de notificaciones

### Contexto

Hallazgo observado en el navegador interno el 30 de julio de 2026.

### Evidencia

La cabecera expone un boton con `aria-label="Notificaciones"` y un
`.notification-dot`. `frontend/app.js` no registra ninguna accion para el
control y la interfaz no explica que evento origina el indicador.

### Pasos para reproducir

1. Levantar el frontend.
2. Abrir `http://127.0.0.1:8000/frontend/`.
3. Pulsar Notificaciones.
4. Observar si aparece un panel, historial o cambio de estado.

### Resultado esperado

El boton abre una experiencia con proposito explicito, o se elimina/deshabilita
hasta que exista. El indicador representa un estado verificable y accesible.

### Resultado actual

El boton no ejecuta ninguna accion y el indicador carece de significado
observable.

### Archivo probable

- `frontend/index.html`
- `frontend/app.js`
- `frontend/styles.css`

### Criterios de aceptacion

- [ ] Se definen los eventos que generan notificaciones.
- [ ] El boton abre una vista verificable.
- [ ] El indicador representa cantidad o estado real.
- [ ] Abrir, cerrar y recorrer funciona con teclado.
- [ ] Existe un estado vacio.
- [ ] Hay evidencia visual y la consola queda sin errores.

## Documentacion: sincronizar conteos despues de una ingestion

### Contexto

Hallazgo detectado al agregar el snapshot y ranking del 30 de julio de 2026.

### Evidencia

`python3 -m unittest` ejecuto 36 pruebas: 35 aprobaron y fallo
`DocumentationSyncTest.test_canonical_documentation_matches_verifiable_project_facts`.
Faltaron los marcadores `24 snapshots`, `115 senales`, `449 filas` y sus
equivalentes en `docs/supabase-cloud.md`.

### Pasos para reproducir

1. Agregar un snapshot valido y generar su ranking.
2. Ejecutar `python3 scripts/check_documentation_sync.py`.
3. Ejecutar `python3 -m unittest`.
4. Revisar los marcadores faltantes.

### Resultado esperado

La documentacion canonica permanece sincronizada o el flujo exige su
actualizacion antes de entregar.

### Resultado actual

El snapshot y ranking son validos, pero la suite falla por conteos anteriores.

### Archivo probable

- `scripts/check_documentation_sync.py`
- `README.md`
- `docs/ai-radar-current-state.md`
- `docs/supabase-cloud.md`
- `docs/ai-radar-operating-model.md`

### Criterios de aceptacion

- [x] El flujo define cuando actualizar conteos.
- [x] Los documentos reflejan los datos versionados.
- [x] El validador documental termina con codigo 0.
- [x] La suite completa aprueba.
- [x] Se recuerda verificar Notion.
- [x] Los conteos no dependen de una edicion manual silenciosa.

### Resolucion

Completado el 31 de julio de 2026 con 24 snapshots, 115 senales, 4 rankings,
282 entradas, 449 filas, 8 skills sincronizadas y 36 pruebas aprobadas. El
issue [#3](https://github.com/PedroHincapie/codex-/issues/3) quedo cerrado.

## Fuentes: registrar bloqueos HTTP 403

### Contexto

Hallazgo de cobertura durante la recoleccion paralela del 30 de julio de 2026.

### Evidencia

Ars Technica respondio HTTP 403. La recoleccion continuo, pero el fallo quedo
solamente en el reporte conversacional.

### Pasos para reproducir

1. Sincronizar el catalogo.
2. Ejecutar una recoleccion que incluya Ars Technica.
3. Recuperar contenido reciente desde su URL activa.
4. Revisar si queda una incidencia estructurada.

### Resultado esperado

El flujo registra fuente, URL, fecha, codigo y estrategia, continua con otras
fuentes y no desactiva automaticamente la fuente.

### Resultado actual

El 403 solo queda documentado manualmente.

### Archivo probable

- `skills/ai-radar-source-manager/SKILL.md`
- `skills/ai-radar-signals/SKILL.md`
- `skills/ai-radar-source-manager/scripts/validate_sources_cache.py`

### Criterios de aceptacion

- [ ] El 403 genera un hallazgo estructurado.
- [ ] Un fallo aislado no desactiva la fuente.
- [ ] Solo se intentan alternativas configuradas y permitidas.
- [ ] Los demas grupos continuan.
- [ ] El reporte diferencia bloqueo, degradacion y falta de contenido.
- [ ] Existe un fixture determinista para 403.

## Fuentes: registrar el rechazo por fecha no verificable

### Contexto

Hallazgo editorial durante la recoleccion paralela del 30 de julio de 2026.

### Evidencia

IEEE no entrego metadatos de fecha suficientes para elevar un candidato. La
exclusion correcta quedo solamente en el reporte conversacional.

### Pasos para reproducir

1. Sincronizar el catalogo.
2. Consultar contenido reciente de IEEE.
3. Normalizar los metadatos disponibles.
4. Intentar determinar `publishedAt`.
5. Revisar como queda registrado el descarte.

### Resultado esperado

El normalizador obtiene una fecha verificable o rechaza el candidato con una
razon estructurada y conserva trazabilidad.

### Resultado actual

El candidato no se eleva, pero el motivo solo aparece en el reporte manual.

### Archivo probable

- `skills/ai-radar-source-normalizer/SKILL.md`
- `skills/ai-radar-signals/SKILL.md`
- `docs/contracts/ai-radar-daily.schema.json`
- `data/sources/candidates/`

### Criterios de aceptacion

- [ ] La fecha solo se acepta desde evidencia verificable.
- [ ] El descarte usa una razon estructurada.
- [ ] Se conservan URL, fuente y `retrievedAt`.
- [ ] Una señal no usa fechas inferidas sin evidencia.
- [ ] El reporte contabiliza descartes por metadatos insuficientes.
- [ ] Existe un fixture para ausencia de `publishedAt`.
