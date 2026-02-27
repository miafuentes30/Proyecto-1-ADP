# Diagrama simplificado de la MT real (por fases)

Este diagrama describe la máquina de [fib_tm_real.json](fib_tm_real.json).

```mermaid
graph LR
    I([Inicio]) --> N[Inicializa contador n en cinta]
    N --> B[Inicializa bloques de trabajo a,b]
    B --> L{Quedan marcas n sin consumir?}

    L -->|Sí| C[Consume una marca n -> x]
    C --> S[Calcula c = a + b]
    S --> U[Actualiza: a <- b y b <- c]
    U --> L

    L -->|No| F[Limpieza final de símbolos auxiliares]
    F --> A((qAccept))
```

## Relación con estados del JSON

- Inicio / preparación: `qStart`, `qInit*`, `qReturnToNStart`.
- Bucle principal: `qLoopSeekN`, `qGoBarForIter`.
- Cálculo de suma y actualización: estados `qCopy*`, `qA_*`, `qB_*`, `qRelabelPass`, `qRestore*`.
- Finalización: `qFinalize*`, `qAccept`.

## Nota

Los diagramas anteriores de `q0..q10`, `qErase*` y `qWrite*` se conservan como versión tabulada previa.
