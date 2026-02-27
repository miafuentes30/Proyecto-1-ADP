# Checklist de cumplimiento vs Instrucciones

Referencia: [Instrucciones.md](Instrucciones.md).

## Entregables

1. **Descripción de convenciones elegidas**
   - Cumplido con MT real en [convenciones_mt_real.md](convenciones_mt_real.md).
   - También se mantiene la documentación previa para la versión anterior.

2. **Diagrama de la MT de Fibonacci**
   - Diagrama de la MT real en [diagrama_mt_real_simplificado.md](diagrama_mt_real_simplificado.md).
   - Diagramas previos conservados: [diagrama_transiciones.md](diagrama_transiciones.md), [diagrama_transiciones_simplificado.md](diagrama_transiciones_simplificado.md), [diagrama_fases_basico.md](diagrama_fases_basico.md).

3. **Archivo con componentes de la MT del punto 2**
   - MT real: [fib_tm_real.json](fib_tm_real.json).
   - MT previa/tabulada (conservada): [fib_tm.json](fib_tm.json).

4. **Programa en Python**
   - 4a) Carga componentes por archivo JSON: [maquina_turing.py](maquina_turing.py) con `--tm`.
   - 4b) Permite ingreso de entrada: modo interactivo en [maquina_turing.py](maquina_turing.py).
   - 4c) Muestra configuraciones (estado/cabezal/cinta): `run_tm(..., verbose=True)` en [maquina_turing.py](maquina_turing.py).

5. **Análisis empírico**
   - 5a) Lista de entradas/resultados en consola.
   - 5b) Diagrama de dispersión generado en [analisis_tm.png](analisis_tm.png).
   - 5c) Regresión polinomial reportada por el programa.

## Recomendación para exposición

- Indicar explícitamente que la entrega principal usa la MT real de [fib_tm_real.json](fib_tm_real.json).
- Aclarar que la versión tabulada se mantiene solo como historial de desarrollo.
