# Demo rápida: explosión de cinta y tiempo (MT Fibonacci)

## 1) Comando base para la demo

```bash
python maquina_turing.py --tm fib_tm_real.json --max-n 18 --max-steps 50000000
```

- `--max-n`: hasta qué `n` quieres medir.
- `--max-steps`: tope de pasos por corrida (útil para mostrar cuándo “explota”).

## 2) Configuración recomendada en vivo

### Opción segura (rápida)
```bash
python maquina_turing.py --tm fib_tm_real.json --max-n 14 --max-steps 10000000
```

### Opción fuerte (mostrar explosión)
```bash
python maquina_turing.py --tm fib_tm_real.json --max-n 18 --max-steps 50000000
```

## 3) Qué mostrarle al profesor

1. En la tabla de análisis empírico, señalar cómo suben `Pasos` y `Tiempo` al crecer `n`.
2. Mostrar que la salida en cinta también crece como `F(n)` (en unario, `F(n)` símbolos `1`).
3. Si alguna corrida pega `max_steps`, explicar que ese corte evidencia el crecimiento explosivo del costo.
4. Enseñar el gráfico `analisis_tm.png` como evidencia visual.

## 4) Guion de 1 minuto (listo para decir)

"Nuestra MT es de una sola cinta y calcula Fibonacci por recurrencia real en cinta, no por tabla precomputada. El punto clave del proyecto es observar cómo el costo crece al aumentar `n`. Como la salida está en unario, la longitud final ya es `F(n)`, y además la máquina hace muchas pasadas para copiar, limpiar y relabelar bloques. Por eso pasos y tiempo se disparan rápidamente. En la tabla y en la gráfica se ve esa tendencia de crecimiento fuerte; cuando alcanzamos el límite de pasos, eso no es un error conceptual, sino evidencia práctica de la explosión de recursos que queríamos analizar." 

## 5) Frase corta para cerrar

"La máquina funciona correctamente, pero su costo empírico crece de forma muy acelerada por la combinación de salida unaria y operaciones repetitivas de una MT de una cinta."