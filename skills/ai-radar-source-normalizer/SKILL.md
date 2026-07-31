---
name: ai-radar-source-normalizer
description: Normalize AI Radar source candidates from URLs, articles, papers, repositories, product announcements, and raw notes into comparable records. Use when Codex needs to extract canonical source fields, classify source type, remove tracking noise, preserve provenance, prepare candidates before signal curation, or design parsing and normalization fixtures for AI Radar.
---

# AI Radar Source Normalizer

## Objetivo

Convertir entradas heterogeneas de IA en registros comparables antes de crear
senales. La salida debe preservar provenance, separar hechos de inferencias y
evitar perder datos necesarios para deduplicacion y ranking.

## Inputs

Aceptar:

- URLs de noticias, blogs, papers, repositorios o lanzamientos.
- Titulares, notas manuales o listas copiadas.
- Snapshots diarios que necesiten normalizar fuentes.
- Fixtures de entrada para futuras pruebas de parsing.

Cuando el usuario pida actualidad, verificar fuentes en internet. Cuando el
input ya viene del repo, no asumir datos ausentes.

## Registro Normalizado Recomendado

Usar esta forma cuando no exista un contrato mas especifico:

```json
{
  "sourceId": "source-slug",
  "canonicalUrl": "https://example.com/item",
  "sourceName": "Example",
  "sourceType": "news",
  "title": "Titulo original o normalizado",
  "publishedAt": "YYYY-MM-DD",
  "retrievedAt": "YYYY-MM-DD",
  "actors": ["openai"],
  "topics": ["agents"],
  "rawInput": "entrada original breve",
  "facts": ["hecho verificable"],
  "inferences": ["inferencia marcada como tal"],
  "confidence": "medium"
}
```

## Workflow

1. **Reconocer contratos existentes**
   - Revisar `docs/contracts/`, `data/signals/daily/` y
     `data/sources/candidates/`.
   - No crear un contrato nuevo si el usuario solo pidio una normalizacion
     conversacional.

2. **Limpiar URL**
   - Conservar dominio, path y parametros necesarios para identificar el item.
   - Remover parametros de tracking como `utm_*`, `fbclid`, `gclid` y
     similares cuando no afecten el recurso.
   - Mantener DOI, arXiv id, release tag, commit o slug de articulo.

3. **Clasificar fuente**
   - `news`: medio periodistico.
   - `official`: anuncio de empresa, gobierno o laboratorio.
   - `paper`: arXiv, revista o preprint.
   - `repo`: GitHub, GitLab u otro repositorio.
   - `product`: pagina de producto, changelog o release.
   - `social`: post usado solo como pista, no como evidencia fuerte.

4. **Extraer campos**
   - Capturar `sourceName`, `title`, `publishedAt`, `retrievedAt` y
     `canonicalUrl`.
   - Extraer actores principales y temas sin sobre-etiquetar.
   - Separar `facts` de `inferences`.

5. **Asignar confianza**
   - `high`: fuente primaria o medio confiable con detalles verificables.
   - `medium`: fuente secundaria creible o paper aun no revisado.
   - `low`: rumor, social, marketing ambiguo o informacion incompleta.

6. **Preparar salida**
   - Si el destino es una senal diaria, adaptar los campos al contrato
     `ai-radar-daily`.
   - Si el destino son candidatos versionados, mantener entradas pequenas y estables.
   - No guardar articulos completos ni citas extensas.

## Reglas

- No inventar fechas de publicacion.
- Si falta una fecha verificable, excluir el candidato y registrar
  `missing-verifiable-published-at` mediante
  `scripts/record_source_finding.py candidate-rejection`. Conservar fuente,
  URL, `retrievedAt` y `rawInput`; nunca agregar un `publishedAt` inferido.
- No tratar una inferencia como hecho.
- Preferir slugs estables en `kebab-case`.
- Mantener tags y topics en minusculas con guiones.
- Registrar la fecha de consulta con fecha absoluta.

## Validaciones

- Revisar que cada URL canonica sea trazable al input original.
- Confirmar que cada fuente tenga tipo y nombre.
- Confirmar que cada hecho pueda apuntar a una fuente.
- Confirmar que los descartes por metadatos insuficientes queden en
  `data/observability/source-findings-YYYY-MM-DD.json`.
- Ejecutar `jq empty` si se genera JSON.
