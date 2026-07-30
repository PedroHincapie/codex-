---
name: desarrollo-frontend-airadar
description: Implementar, corregir y validar interfaces frontend de AI Radar con datos trazables, estados completos y evidencia visual. Usar al crear o modificar páginas, dashboards, componentes, flujos, prototipos funcionales o integraciones UI de AI Radar, y al revisar si una entrega frontend cumple responsive, accesibilidad, ausencia de errores en consola y capturas verificables.
---

# Desarrollo frontend AI Radar

## Objetivo

Entregar interfaces funcionales y verificadas, no solo una composición visual.
Tratar datos, estados, responsive, accesibilidad, consola y capturas como criterios
obligatorios de terminación.

## Flujo obligatorio

1. **Reconocer el proyecto**
   - Leer `AGENTS.md`, documentación funcional y contratos relevantes.
   - Inspeccionar el stack, scripts, rutas, componentes y convenciones existentes.
   - Preservar cambios ajenos y reutilizar el sistema visual disponible.
   - Definir qué páginas, flujos y tamaños de viewport quedan dentro del alcance.

2. **Definir la fuente de datos**
   - Usar una API real cuando exista y esté disponible.
   - Si la API no existe, no está disponible o no debe invocarse, usar fixtures
     declarados explícitamente.
   - Identificar en código y en la entrega si cada fuente es `real` o `fixture`.
   - Basar fixtures de AI Radar en contratos o ejemplos versionados del repositorio.
   - No presentar datos inventados como información real, actual o conectada.
   - No ocultar fallos de red reemplazándolos silenciosamente por datos falsos.
   - Mantener el acceso a datos separado de los componentes de presentación para
     poder sustituir fixtures por la API sin reescribir la interfaz.

3. **Inventariar estados antes de implementar**
   - Cubrir, cuando apliquen: inicial, carga, éxito con datos, vacío, error,
     parcial/degradado, sin resultados de filtro y acción en progreso.
   - Definir la recuperación para estados no exitosos: reintentar, limpiar filtros,
     volver o continuar con datos parciales.
   - Evitar loaders permanentes, áreas en blanco y errores que solo aparezcan en
     consola.

4. **Implementar la experiencia**
   - Mantener jerarquía visual, navegación y acciones coherentes con AI Radar.
   - Usar HTML semántico y componentes nativos antes de recrearlos con `div`.
   - Hacer que el layout se adapte por contenido; no limitarse a reducir la escala.
   - Evitar scroll horizontal no intencional, solapamientos, recortes y objetivos
     táctiles difíciles de accionar.
   - No introducir dependencias nuevas si el stack existente resuelve el problema.

5. **Verificar en runtime**
   - Ejecutar los chequeos estáticos, pruebas y build que ofrezca el proyecto.
   - Abrir la aplicación en un navegador real.
   - Recorrer las rutas y acciones modificadas con datos reales o fixtures
     declarados.
   - Inspeccionar la consola desde una carga limpia y después de cada flujo crítico.
   - Corregir errores, excepciones, recursos fallidos y warnings causados por el
     cambio. No silenciarlos ni filtrarlos para aparentar una consola limpia.

6. **Capturar evidencia**
   - Tomar capturas después de terminar la verificación, nunca como sustituto de
     ella.
   - Incluir como mínimo una vista móvil y una de escritorio por página o flujo
     principal modificado.
   - Capturar también estados relevantes que no queden demostrados por la vista de
     éxito, especialmente vacío y error.
   - Guardar las capturas con nombres que indiquen página, estado y viewport.
   - Revisar cada captura para detectar clipping, desbordes, texto ilegible,
     elementos superpuestos o contenido inesperado.

## Puertas de calidad

No declarar la tarea completa hasta satisfacer todas las puertas aplicables.

### Datos trazables

- La API usada es real y su endpoint o cliente puede identificarse, o el fixture
  está declarado como tal.
- El fixture tiene procedencia: contrato, archivo o escenario de prueba.
- Los tipos y la UI contemplan campos ausentes, valores vacíos y fallos.
- Ningún texto afirma sincronización, tiempo real o actualidad sin evidencia.

### Estados completos

- Carga: comunica progreso sin bloquear indefinidamente.
- Vacío: explica qué ocurre y ofrece una siguiente acción útil.
- Error: muestra un mensaje comprensible y una recuperación cuando sea viable.
- Éxito: representa datos reales o fixtures declarados sin inconsistencias.
- Interacciones: muestran estados disabled, pending, selected, focus y feedback
  según corresponda.

### Responsive

- Verificar al menos un viewport móvil cercano a 390 px y uno de escritorio de
  1280 px o más.
- Añadir un viewport intermedio cuando el layout cambie de estructura o el alcance
  incluya tablet.
- Probar contenido largo, listas vacías y densidad representativa.
- Confirmar navegación, tablas, tarjetas, filtros, modales y gráficos sin pérdida
  de información ni scroll horizontal accidental.

### Accesibilidad

- Recorrer con teclado las acciones principales en orden lógico.
- Mantener foco visible y devolverlo correctamente al cerrar overlays.
- Asociar labels, nombres accesibles, encabezados, landmarks y mensajes de error.
- No depender solo de color, hover o movimiento para comunicar información.
- Proporcionar texto alternativo útil; marcar como decorativo lo que corresponda.
- Comprobar contraste y zoom al 200 % sin pérdida de contenido o funcionalidad.
- Respetar `prefers-reduced-motion` cuando haya animaciones no esenciales.
- Ejecutar el verificador de accesibilidad disponible y corregir violaciones
  atribuibles al cambio.

### Consola limpia

- Cero errores de JavaScript.
- Cero promesas rechazadas o requests fallidos causados por el flujo.
- Cero warnings de framework, hidratación, keys, recursos o accesibilidad
  introducidos por el cambio.
- Si queda ruido previo ajeno al alcance, identificarlo con mensaje, ruta y
  evidencia; no describir la consola como limpia.

### Evidencia visual

- Capturas de móvil y escritorio.
- Capturas de estados no felices relevantes.
- Correspondencia entre captura, commit/estado de archivos y runtime probado.
- Archivos accesibles desde la entrega mediante rutas o enlaces claros.

## Matriz mínima de verificación

Registrar una fila por escenario probado:

| Escenario | Fuente | Viewport | Estado | Teclado/a11y | Consola | Captura |
|---|---|---:|---|---|---|---|
| Ruta o flujo | API/fixture declarado | ancho × alto | éxito/error/vacío | resultado | limpia/hallazgo | ruta |

No marcar una celda como aprobada si solo se inspeccionó el código.

## Regla de salida

Entregar:

- resumen de la experiencia implementada;
- fuente de datos y procedencia de fixtures;
- estados cubiertos;
- comandos de build y pruebas con su resultado;
- viewports y recorridos verificados;
- resultado de accesibilidad y consola;
- enlaces a capturas;
- limitaciones o puertas no satisfechas.

Si no hay navegador, runtime, credenciales, API o forma de generar capturas, avanzar
con todo lo verificable y declarar la puerta exacta como pendiente. No sustituir
evidencia ausente por una afirmación de cumplimiento.
