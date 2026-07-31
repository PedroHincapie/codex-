# Supabase Cloud De AI Radar

Fecha de ultima verificacion: 31 de julio de 2026.

## Proyecto

| Campo | Valor |
|---|---|
| Organizacion | `PedroHincapie` |
| Proyecto | `AI Radar` |
| Project ref | `xredenxxhnzkmfxxnrlg` |
| Region | `us-east-1` |
| API URL | `https://xredenxxhnzkmfxxnrlg.supabase.co` |

El frontend usa una clave `sb_publishable_...`. Esta clave identifica el
proyecto ante la Data API, pero la autorizacion efectiva depende de grants y
RLS. Las claves secretas y `service_role` quedan exclusivamente fuera del
navegador y del repositorio.

## Datos

La proyeccion Cloud conserva el mismo corte validado localmente:

| Tabla | Filas | Acceso publico |
|---|---:|---|
| `radar_snapshots` | 24 | Lectura |
| `signals` | 115 | Lectura |
| `rankings` | 4 | Lectura |
| `ranking_entries` | 282 | Lectura |
| `source_candidate_batches` | 2 | Denegado |
| `source_candidates` | 22 | Denegado |

Total: 449 filas.

Los datos se cargaron desde los JSON versionados del repositorio mediante una
importacion controlada. La extension HTTP temporal se elimino al terminar.

## Frontend

`frontend/data.js` consulta primero Supabase Cloud. Si la Data API no responde,
usa los JSON locales y muestra `Fallback local` junto con un aviso de modo
degradado. El fallback nunca se presenta como una respuesta Cloud.
Cada peticion tiene un maximo de ocho segundos y el arranque cuenta con un
watchdog independiente: una falla de red o de modulos ya no puede dejar la
interfaz mostrando el loader indefinidamente.

Estados reproducibles:

- `?demo=fallback`: fuerza el fallback local;
- `?demo=empty`: muestra el estado vacio;
- `?demo=error`: muestra el error general recuperable.

## Seguridad Y Verificacion

- RLS habilitado en las seis tablas;
- politicas publicas de solo lectura en las cuatro tablas publicadas;
- politicas explicitas `using (false)` en las dos tablas internas;
- Data API: `signals` y `rankings` responden `200` con la clave publicable;
- Data API: `source_candidates` responde `401`;
- asesores de seguridad Supabase sin hallazgos;
- ninguna clave secreta se persiste o se envia al navegador.

La clave publicable puede rotarse en Supabase. Si cambia, actualizar
`frontend/supabase-config.js`, ejecutar la suite y repetir la validacion en
navegador.

## Compatibilidad Con La Data API

Las migraciones conceden `SELECT` de forma explicita solo a las cuatro tablas
publicadas y habilitan RLS en las seis tablas. Este diseño es compatible con el
cambio de Supabase que deja de exponer automaticamente las tablas nuevas:

- [Securing your API](https://supabase.com/docs/guides/api/securing-your-api)
- [Tables not exposed automatically](https://supabase.com/changelog/45329-breaking-change-tables-not-exposed-to-data-and-graphql-api-automatically)
- [Understanding API keys](https://supabase.com/docs/guides/getting-started/api-keys)

La validacion del 31 de julio de 2026 confirmo proyecto saludable, Postgres 17,
449 filas, RLS en las seis tablas y cero hallazgos del asesor de seguridad. El
asesor de rendimiento solo reporto indices aun no utilizados; se conservan
hasta contar con trafico representativo del dashboard.
