# Hallazgos De Fuentes

AI Radar registra limitaciones de recoleccion y descartes editoriales como un
reporte JSON separado. Estos hallazgos no son señales y no cambian
automaticamente la salud del catalogo.

## Comandos

```bash
python3 scripts/record_source_finding.py fetch-failure \
  --source-name "Ars Technica" \
  --url "https://arstechnica.com/ai/" \
  --retrieved-at 2026-07-30 \
  --group secondary-context \
  --http-status 403

python3 scripts/record_source_finding.py candidate-rejection \
  --source-name "IEEE" \
  --url "https://spectrum.ieee.org/artificial-intelligence" \
  --retrieved-at 2026-07-30 \
  --reason-code missing-verifiable-published-at
```

La salida predeterminada vive en
`data/observability/source-findings-YYYY-MM-DD.json`. Repetir el mismo hallazgo
es idempotente por `id`.

## Politicas

- HTTP 401, 403 y 429 se clasifican como `blocked`; otros fallos HTTP se
  clasifican como `degraded`.
- Una fuente accesible sin contenido reciente verificable usa
  `content_unavailable` y `outcome: no_content`.
- Un fallo aislado usa `sourceHealthAction: record-only` y la recoleccion
  continua con las demas fuentes.
- Solo se prueban alternativas presentes en el catalogo (`configured-only`).
- Un candidato sin fecha verificable se excluye con
  `missing-verifiable-published-at`; no se inventa `publishedAt`.
- URL, fuente, fecha de consulta, razon y decision permanecen trazables.
