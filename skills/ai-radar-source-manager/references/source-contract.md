# Contrato Del Catalogo De Fuentes

## Notion

Usar la base `AI Radar Sources` con estas propiedades:

| Propiedad | Tipo | Valores |
|---|---|---|
| Fuente | title | Nombre editorial unico |
| Tipo | select | `fuente_oficial`, `repo_tecnico`, `comunidad`, `medio_secundario` |
| URL | url | URL canonica |
| Activa | checkbox | Fuente habilitada |
| Descripcion | rich text | Proposito editorial |
| Ultima revision | date | Revision humana |
| Prioridad | select | `alta`, `media`, `baja` |
| Uso | multi-select | `evidencia`, `descubrimiento`, `contexto` |
| Frecuencia | select | `diaria`, `semanal`, `mensual` |
| Estado salud | select | `saludable`, `degradada`, `en_revision` |
| Ultimo exito | date | Ultima comprobacion correcta |
| Fallos consecutivos | number | Entero mayor o igual que cero |
| Feed URL | url | RSS o API verificados; puede estar vacio |
| Ultimo contenido detectado | date | Puede estar vacio |
| Confianza editorial | select | `alta`, `media`, `baja` |

Los nombres acentuados de Notion son equivalentes a los nombres ASCII de esta
tabla.

## Cache

Guardar `config/sources.json` con `version: 2`:

```json
{
  "version": 2,
  "generatedAt": "YYYY-MM-DDTHH:mm:ssZ",
  "cachePolicy": {
    "ttlHours": 24,
    "expiresAt": "YYYY-MM-DDTHH:mm:ssZ"
  },
  "sourceCatalog": {
    "provider": "notion",
    "databaseName": "AI Radar Sources",
    "databaseUrl": "https://...",
    "dataSourceUrl": "collection://...",
    "status": "fresh"
  },
  "sources": [
    {
      "name": "Example",
      "type": "fuente_oficial",
      "url": "https://example.com/",
      "active": true,
      "description": "Proposito.",
      "lastReviewed": "YYYY-MM-DD",
      "priority": "alta",
      "uses": ["evidencia", "descubrimiento"],
      "frequency": "diaria",
      "health": "saludable",
      "lastSuccess": "YYYY-MM-DD",
      "consecutiveFailures": 0,
      "feedUrl": null,
      "lastContentDetected": null,
      "editorialConfidence": "alta"
    }
  ],
  "subagentGroups": [
    {
      "id": "official-verification",
      "types": ["fuente_oficial"],
      "sourceUrls": ["https://example.com/"]
    }
  ]
}
```

Ordenar `sources` por tipo y nombre usando comparacion sin distincion de
mayusculas. Ordenar URLs dentro de cada grupo con la misma regla.

## Fallback

- `fresh`: Notion entrego y valido el catalogo completo.
- `fallback-cache`: Notion fallo y se uso una cache valida sin reescribirla.
- `fallback-no-cache`: Notion fallo y no existe una cache valida.

El estado de fallback pertenece al reporte de ejecucion. No cambiar una cache
valida de `fresh` a `fallback-cache` solo para registrar un fallo temporal.
