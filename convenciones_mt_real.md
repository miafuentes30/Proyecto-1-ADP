# Convenciones de la MT real (Fibonacci en unario)

Este documento corresponde a la máquina definida en [fib_tm_real.json](fib_tm_real.json).

## 1) Convención de entrada

- Un entero no negativo `n` se representa como una cadena unaria con `n` símbolos `1`.
- Ejemplos:
  - `n=0` -> cadena vacía `""`
  - `n=1` -> `"1"`
  - `n=4` -> `"1111"`

## 2) Convención de salida

- La máquina acepta en `qAccept`.
- Al aceptar, la cinta queda con `F(n)` símbolos `1` contiguos (sin marcadores auxiliares).
- Ejemplos:
  - entrada `""` -> salida `""` (`F(0)=0`)
  - entrada `"1"` -> salida `"1"` (`F(1)=1`)
  - entrada `"1111"` -> salida `"111"` (`F(4)=3`)

## 3) Símbolos de trabajo en cinta

Alfabeto de cinta usado por la MT real:
- `1`: marca de unidad en unario
- `_`: blanco
- `|`, `#`: separadores de zonas de trabajo
- `n`, `x`: contador restante y contador consumido
- `a`, `A`: bloque de trabajo para valor anterior de Fibonacci
- `b`, `B`: bloque de trabajo para valor actual de Fibonacci
- `c`: bloque temporal para suma

## 4) Interpretación de cálculo

La máquina implementa recurrencia iterativa en cinta:
- Mantiene dos valores consecutivos de Fibonacci en zonas de trabajo.
- Consume una unidad del contador por iteración.
- Construye la suma en zona temporal y luego actualiza bloques.
- Repite hasta consumir el contador y finalmente limpia marcadores.

No usa tabla precomputada de resultados por `n`.

## 5) Alcance práctico del proyecto

- La definición de [fib_tm_real.json](fib_tm_real.json) fue validada para `n=0..10`.
- El simulador puede ejecutarse con:

```bash
python maquina_turing.py --tm fib_tm_real.json --max-n 10
```
