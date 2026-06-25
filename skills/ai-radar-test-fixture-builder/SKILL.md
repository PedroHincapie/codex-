---
name: ai-radar-test-fixture-builder
description: Create and maintain stable AI Radar fixtures and unittest coverage for parsing, normalization, deduplication, ranking, scoring, and contract validation. Use when Codex needs to add data/fixtures examples, expected outputs, tests under tests/, or minimal domain modules that turn AI Radar editorial rules into executable behavior.
---

# AI Radar Test Fixture Builder

## Objetivo

Crear fixtures pequenos, estables y utiles para probar el dominio de AI Radar.
La prioridad es cubrir parsing, normalizacion, duplicados, ranking y scoring
antes de conectar servicios externos.

## Inputs

Aceptar:

- Reglas editoriales o contratos existentes.
- Snapshots diarios en `data/fixtures/`.
- Ejemplos de URLs, articulos, papers, repos o lanzamientos.
- Solicitudes de pruebas con `unittest`.

## Workflow

1. **Reconocer estado del proyecto**
   - Revisar `README.md`, `AGENTS.md`, `docs/contracts/` y `data/fixtures/`.
   - Usar Python y `unittest` salvo que el repo introduzca otro toolchain.
   - No asumir ejecutadores de paquete; preferir `python3 -m unittest` y
     scripts Python llamados directamente.

2. **Elegir comportamiento a cubrir**
   - Parsing de entradas.
   - Normalizacion de fuentes.
   - Deteccion de duplicados.
   - Ranking y scoring.
   - Validacion de contrato diario.

3. **Disenar fixtures**
   - Mantener archivos pequenos y revisables.
   - Separar input y expected output cuando pruebe transformaciones.
   - Usar nombres `kebab-case`.
   - Usar datos realistas pero no articulos completos.
   - Incluir casos limite: fecha faltante, fuente secundaria, duplicado
     parcial, tags invalidos, accion vaga.

4. **Crear pruebas**
   - Colocar pruebas bajo `tests/` cuando sea necesario.
   - Nombrar pruebas segun la unidad probada, por ejemplo
     `test_source_normalizer.py`.
   - Usar `unittest` de la libreria estandar.
   - Crear modulos en `src/` solo cuando la prueba requiera logica reusable.

5. **Validar**
   - Ejecutar pruebas solo si existen comandos o si se puede invocar Node
     directamente.
   - Validar JSON con `jq empty`.
   - No conectar red, APIs, bases de datos ni dashboards para pruebas de
     dominio local.

## Patrones De Fixture

Entrada cruda:

```json
{
  "rawInput": "https://example.com/news/ai-launch?utm_source=test",
  "retrievedAt": "YYYY-MM-DD"
}
```

Salida esperada:

```json
{
  "canonicalUrl": "https://example.com/news/ai-launch",
  "sourceType": "news",
  "confidence": "medium"
}
```

Prueba base:

```python
import unittest

class SourceNormalizerTest(unittest.TestCase):
  def test_normalizes_tracking_parameters_from_source_urls(self):
    self.assertEqual(True, True)


if __name__ == "__main__":
  unittest.main()
```

## Reglas

- No crear snapshots enormes para probar una regla pequena.
- No usar datos que requieran secretos o credenciales.
- No depender de internet en pruebas unitarias.
- No convertir fixtures diarios editoriales en pruebas fragiles si cambian por
  criterio humano.
- Preferir funciones puras para parsing, deduplicacion y scoring.

## Validaciones

Usar segun aplique:

```bash
jq empty data/fixtures/<file>.json
python3 -m unittest tests/<file>.py
```

No agregar ejecutadores de paquete para pruebas o scripts internos salvo que el
usuario lo pida explicitamente.
