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

También puedes indicar explícitamente el JSON de la MT y el rango del análisis empírico:

```bash
python maquina_turing.py --tm fib_tm_real.json --max-n 10 --max-steps 2000000
```

El programa realizará:
1. Carga de la MT desde el archivo JSON indicado (por defecto `fib_tm_real.json`)
2. Simulación para n=4
3. Análisis empírico con valores de n desde 0 hasta el valor de `--max-n`
	(cada ejecución respeta el límite `--max-steps`)
4. Generación de gráficas 
5. Interfaz para probar valores personalizados

> Nota: `fib_tm.json` se mantiene como versión tabulada/acotada (precomputada). Para una MT que calcula por recurrencia en cinta, usa `fib_tm_real.json`.


## Funcionamiento de la MT

1. **Lectura**: Cuenta n símbolos '1' en la entrada
2. **Borrado**: Limpia la cinta de entrada
3. **Escritura**: Escribe F(n) símbolos '1' como resultado
4. **Aceptación**: Transiciona al estado qAccept

## Documentación para entrega

### MT real (recurrencia en cinta)

- Convenciones: [convenciones_mt_real.md](convenciones_mt_real.md)
- Diagrama simplificado: [diagrama_mt_real_simplificado.md](diagrama_mt_real_simplificado.md)
- Componentes MT: [fib_tm_real.json](fib_tm_real.json)

### Versiones anteriores (conservadas)

- Componentes tabulados: [fib_tm.json](fib_tm.json)
- Diagrama detallado tabulado: [diagrama_transiciones.md](diagrama_transiciones.md)
- Diagrama simplificado tabulado: [diagrama_transiciones_simplificado.md](diagrama_transiciones_simplificado.md)
- Diagrama básico explicativo: [diagrama_fases_basico.md](diagrama_fases_basico.md)

### Verificación de cumplimiento

- Checklist contra instrucciones: [checklist_cumplimiento.md](checklist_cumplimiento.md)