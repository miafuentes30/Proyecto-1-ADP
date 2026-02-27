# Máquina de Turing - Calculadora de Fibonacci

## Descripción

Este proyecto implementa una Máquina de Turing determinista de una cinta que calcula Fibonacci en representación unaria.

El programa incluye:
- simulación completa de la MT,
- ejecución demostrativa con trazado de configuraciones,
- análisis empírico de pasos y tiempo de CPU,
- selección automática de modelos de regresión,
- generación de gráficas del ajuste.

## Características

- **Simulación de MT**: cinta infinita, estados, transiciones y alfabetos definidos desde JSON.
- **Cálculo de Fibonacci**: entrada unaria (n símbolos `1`) y salida unaria de `F(n)`.
- **Análisis empírico**: evaluación de crecimiento en pasos y tiempo para un rango de `n`.
- **Modelado de regresión**: comparación de modelos polinomial, exponencial e híbridos.
- **Visualización**: gráficas de dispersión y curvas de regresión en `analisis_tm.png`.
- **Interfaz de usuario**: modo interactivo para probar valores de `n`.

## Requisitos

- Python 3.8+
- NumPy
- Matplotlib

Instalación rápida:

```bash
pip install numpy matplotlib
```

## Ejecución

Ejecución básica:

```bash
python maquina_turing.py
```

Con parámetros:

```bash
python maquina_turing.py --tm fib_tm_real.json --max-n 18 --max-steps 50000000
```

El programa realiza:
1. Carga de la MT desde `fib_tm_real.json` (o la ruta indicada).
2. Simulación demostrativa para `n=4`.
3. Análisis empírico para `n=0..max-n`.
4. Ajuste y selección del modelo de regresión.
5. Generación de la gráfica `analisis_tm.png`.
6. Modo interactivo para consultas manuales.

## Funcionamiento general de la MT

La MT real implementa la recurrencia de Fibonacci en cinta:

1. Convierte y marca la entrada unaria en la zona de trabajo.
2. Inicializa los acumuladores de la recurrencia.
3. Itera consumiendo marcas y actualizando acumuladores.
4. Limpia símbolos auxiliares.
5. Deja en cinta la salida unaria de `F(n)` y acepta.

## Archivos principales

- Script principal: [maquina_turing.py](maquina_turing.py)
- Definición de la MT real: [fib_tm_real.json](fib_tm_real.json)
- Convenciones de la MT: [convenciones_mt_real.md](convenciones_mt_real.md)
- Diagrama simplificado: [diagrama_mt_real_simplificado.md](diagrama_mt_real_simplificado.md)
- Diagrama completo: [diagrama_mt_real_completo.md](diagrama_mt_real_completo.md)
- Diagrama completo agrupado: [diagrama_mt_real_completo_agrupado.md](diagrama_mt_real_completo_agrupado.md)
- Gráfica de análisis empírico: [analisis_tm.png](analisis_tm.png)
- Informe: [Informe.pdf](Informe.pdf)