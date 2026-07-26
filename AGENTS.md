# Repository Guidelines

## Estructura del proyecto

AI Radar convierte novedades de IA en señales curadas y rankings locales. Distingue la visión en `README.md` de las capacidades implementadas.

- `src/`: lógica de dominio; `radar_store.py` carga, filtra, valida y audita señales, y `ranking_engine.py` crea rankings deterministas.
- `scripts/airadar.py`: CLI local del proyecto.
- `tests/`: pruebas `unittest` para el dominio y el CLI.
- `data/signals/daily/`: snapshots curados `daily-radar-YYYY-MM-DD.json`.
- `data/reviews/rankings/`: rankings editoriales `signal-review-ranking-YYYY-MM-DD.json`.
- `data/sources/candidates/`: fuentes normalizadas antes de la curación final.
- `docs/contracts/`: contrato y esquema JSON de señales diarias; `docs/ai-radar-operating-model.md` explica el flujo operativo.
- `skills/`: instrucciones de capacidades de AI Radar.

## Desarrollo y comandos

El proyecto usa solo Python y biblioteca estándar; no hay build ni gestor de dependencias. Ejecuta desde la raíz:

```bash
python3 -m unittest
python3 scripts/airadar.py list --tag agents --fields id,title,action
python3 scripts/airadar.py validate --date 2026-06-20
python3 scripts/airadar.py audit --date 2026-06-20
python3 scripts/airadar.py coverage --from 2026-06-13 --to 2026-07-09
python3 scripts/airadar.py ranking --generate --date 2026-06-25 --limit 3
```

`list`, `summary` y `show` consultan señales; `validate` verifica contratos; `audit` detecta duplicados y evidencia vacía; `coverage` informa días faltantes. Usa `--format json` para resultados procesables.

## Estilo y datos

Escribe Python y JSON con indentación de 2 espacios, funciones y variables en `snake_case`, y constantes reales en `UPPER_SNAKE_CASE`. Nombra módulos como `radar_store.py` y pruebas como `test_radar_store.py`. Respeta el esquema de `docs/contracts/ai-radar-daily.schema.json`; no modifiques snapshots o rankings sin validar fechas, IDs, URLs, evidencia y tags.

## Pruebas

Añade pruebas `unittest` para cambios de parsing, filtrado, validación, auditoría, cobertura o ranking. Mantén fixtures deterministas y cubre casos vacíos, errores y límites. Ejecuta `python3 -m unittest` antes de entregar cambios.

## Commits y pull requests

Usa Conventional Commits, por ejemplo: `feat: agregar filtro por source type`, `test: cubrir cobertura de snapshots` o `docs: actualizar contrato diario`. El PR debe explicar qué cambió y por qué, incluir evidencia de pruebas y enlazar la tarea o issue. Incluye capturas únicamente cuando exista una interfaz visual.

## Seguridad y consulta local primero

No subas secretos, `.env`, claves, certificados ni bases de datos. Para preguntas sobre señales, fechas, tags, fuentes, impacto o estado, consulta primero el CLI y los archivos locales. Recurre a la web solo si los datos son insuficientes o requieren verificación actual; antes, indica qué se revisó localmente. Toda curación persistente debe respetar el contrato y quedar versionada en `data/signals/daily/`.
