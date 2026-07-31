# Plantilla De Hallazgo

Usar esta estructura para cada issue. Sustituir todos los campos entre
corchetes y eliminar instrucciones internas antes de publicar.

```markdown
## Contexto

[Caso de uso, fecha absoluta, entorno y alcance.]

## Evidencia

[Observacion verificable: salida, conteo, selector, URL, archivo o error.]

## Pasos para reproducir

1. [Precondicion determinista.]
2. [Accion.]
3. [Accion.]
4. [Observacion.]

## Resultado esperado

[Comportamiento observable que deberia ocurrir.]

## Resultado actual

[Comportamiento observado, sin inferir una causa no demostrada.]

## Archivo probable

- `[ruta/inspeccionada]`

## Criterios de aceptación

- [ ] [Resultado binario y verificable.]
- [ ] [Cobertura de error, vacio o limite relevante.]
- [ ] [Prueba automatizada o evidencia visual apropiada.]
- [ ] [Consola, validadores o suite quedan sin regresiones.]
```

## Control De Calidad

- Escribir el titulo como problema o capacidad ausente, no como solucion
  prematura.
- Usar fechas ISO o fechas absolutas.
- Mantener evidencia separada de la interpretacion.
- Incluir solamente pasos que otra persona pueda repetir.
- Dividir issues si los criterios de aceptacion requieren equipos o archivos
  distintos.
- Buscar duplicados antes de publicar.
- Verificar URL y numero del issue despues de crearlo.
