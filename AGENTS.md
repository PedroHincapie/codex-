# Repository Guidelines

## Estructura del Proyecto y Organización de Módulos

AI Radar es un repositorio inicial mínimo. La raíz contiene `README.md` con la visión del producto y decisiones de stack, además de `.gitignore` para archivos generados, datos locales y secretos.

Usa estas ubicaciones cuando el proyecto crezca:

- `src/`: módulos Python reutilizables del dominio.
- `public/` o `app/`: HTML, CSS y JS del navegador.
- `scripts/`: automatización con Python.
- `tests/`: pruebas con `unittest` y specs de Playwright cuando exista UI.
- `data/signals/daily/`: snapshots diarios curados, un archivo por fecha.
- `data/reviews/rankings/`: rankings, auditorias y scoring editorial.
- `data/sources/candidates/`: fuentes candidatas antes de curacion final.

## Comandos de Build, Prueba y Desarrollo

No hay comandos de build, prueba o desarrollo implementados. No dependas de comandos hasta que existan los archivos necesarios.

Los comandos futuros deben ser simples:

- `python3 -m unittest`: ejecuta pruebas de dominio con `unittest`.
- `python3 scripts/airadar.py <command>`: ejecuta flujos internos usados por skills.
- `python3 scripts/airadar.py validate --date YYYY-MM-DD`: valida snapshots diarios.
- `python3 scripts/airadar.py audit --date YYYY-MM-DD`: audita duplicados, evidencia vacia, estados y fuentes.

## Estilo de Código y Convenciones de Nombres

Prefiere Python para dominio, scripts y automatizacion. Usa HTML, CSS y JavaScript planos solo para navegador salvo que el repositorio introduzca un toolchain. Usa indentación de 2 espacios para Python, JSON, CSS y HTML.

Usa nombres descriptivos:

- Archivos Python: `snake_case.py`.
- Archivos web: `kebab-case.js`, `kebab-case.css` o `kebab-case.html`.
- Funciones y variables Python: `snake_case`.
- Constantes: `UPPER_SNAKE_CASE` solo para constantes reales.
- Pruebas: según la unidad probada, como `test_source_normalizer.py`.

## Guías de Pruebas

El framework objetivo para pruebas de dominio es `unittest`. Agrega pruebas para parsing, normalización, duplicados, ranking y scoring antes de conectar servicios externos. Usa fixtures para entradas y salidas esperadas estables.

Usa Playwright solo cuando exista un dashboard visual.

## Guías de Commits y Pull Requests

El historial usa prefijos estilo Conventional Commits, como `docs:` y `chore:`. Mantén ese patrón:

- `docs: actualizar guia de producto`
- `chore: agregar tooling del proyecto`
- `feat: agregar normalizacion de fuentes`
- `test: cubrir reglas de ranking`

Los pull requests deben incluir descripción breve, razón del cambio, evidencia de pruebas y capturas para cambios de UI. Enlaza issues o tareas del curso cuando existan.

## Seguridad y Configuración

Nunca hagas commit de secretos, `.env`, API keys, bases de datos o certificados privados. Mantén fuera de Git salidas generadas como `.airadar/`, reportes, búsquedas, grabaciones y snapshots salvo revisión explícita.

Los agentes deben distinguir el estado actual del repositorio de la visión del producto. No asumas que existen archivos, comandos, APIs, bases de datos o integraciones hasta que estén presentes en el repo.
