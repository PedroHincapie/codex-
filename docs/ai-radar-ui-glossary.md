# Glosario de interfaz de AI Radar

Este glosario mantiene una terminología única en español para la interfaz. Los
nombres internos de contratos, estados y campos pueden conservarse en inglés;
la capa visible debe usar los términos aprobados aquí.

## Contextos de trabajo

| Término visible | Significado |
|---|---|
| Explorar | Consultar señales publicadas, priorización y fuentes citadas. |
| Revisar | Operar la cola editorial, comprobar evidencia y preparar un borrador local. |
| Lectura de inteligencia | Contexto de consumo para entender qué importa y qué acción se recomienda. |
| Operación editorial | Contexto de revisión humana antes de publicar o persistir cambios. |

## Términos aprobados

| Usar | No usar en la interfaz | Definición |
|---|---|---|
| Ranking de señales | Signal ranking | Orden editorial determinista de las señales cargadas. |
| Puntaje | Impacto, cuando representa el total ponderado | Resultado ponderado mostrado en una escala de 0 a 100. |
| Confianza editorial | Confidence | Banda derivada de la confiabilidad de la fuente; no es una probabilidad estadística. |
| Etiquetas | Tags | Descriptores temáticos normalizados de una señal. |
| Detalle de señal | Dossier | Panel con evidencia, procedencia, justificación y acción recomendada. |
| Puntuación editorial | Scoring | Edición de dimensiones que alimentan el puntaje ponderado. |
| Puntaje total ponderado | Weighted impact score | Suma de las dimensiones según los pesos versionados. |
| Control de calidad de la evidencia | Evidence quality checklist | Verificaciones previas a la decisión editorial. |
| Borrador local | Snapshot local | Propuesta exportable que no modifica Supabase ni los cortes versionados. |
| Corte editorial | Snapshot | Conjunto versionado de señales para una fecha determinada. |
| Respaldo local | Fallback local | Datos versionados usados cuando la fuente principal no está disponible. |
| Fuentes citadas | Fuentes, cuando el conteo proviene de señales | Fuentes observadas en los cortes cargados, distintas del catálogo gobernado en Notion. |

## Regla de redacción

- Priorizar acciones y resultados sobre términos de implementación.
- Mantener nombres propios de productos, como Supabase Cloud, sin traducir.
- Explicar siglas técnicas la primera vez que sean relevantes.
- No presentar confianza editorial como una probabilidad medida.
- Diferenciar siempre el catálogo de fuentes de Notion de las fuentes citadas en señales.
