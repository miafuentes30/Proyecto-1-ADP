# Máquina de Turing - Calculadora de Fibonacci

## Descripción

Este proyecto implementa una Máquina de Turing que calcula la secuencia de Fibonacci para números en representación unaria. El programa incluye una simulación completa de la MT, análisis empírico de complejidad temporal y espacial, y visualizaciones del rendimiento.

## Características

- **Simulación de Máquina de Turing**: Implementación completa con cinta infinita, estados, transiciones y alfabetos
- **Cálculo de Fibonacci**: Convierte entrada unaria (n×'1') al n-ésimo número de Fibonacci
- **Análisis Empírico**: Regresión polinomial para determinar complejidad temporal O(n)
- **Visualización**: Gráficas de dispersión y ajuste para pasos de ejecución y tiempo de CPU
- **Iterfaz de usuario**: Interfaz de usuario para probar diferentes valores de n
- **Trazado**: Visualización paso a paso de las configuraciones de la MT

## Requisitos

- Python 3.7+
- NumPy
- Matplotlib

```bash
pip install numpy matplotlib
```

## Ejecución

Ejecuta el programa principal:

```bash
python maquina_turing.py
```

El programa realizará:
1. Generación automática del archivo `fib_tm.json` con la definición de la MT
2. Simulación para n=4
3. Análisis empírico con valores de n desde 0 hasta 10 (por rendimiendo del CPU); se puede modificar la entrada en la línea 437 (MAX_N = 10)
4. Generación de gráficas 
5. Interfaz para probar valores personalizados


## Funcionamiento de la MT

1. **Lectura**: Cuenta n símbolos '1' en la entrada
2. **Borrado**: Limpia la cinta de entrada
3. **Escritura**: Escribe F(n) símbolos '1' como resultado
4. **Aceptación**: Transiciona al estado qAccept