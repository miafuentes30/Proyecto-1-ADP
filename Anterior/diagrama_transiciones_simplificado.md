# Diagrama de transiciones simplificado (MT Fibonacci)

```mermaid
graph LR
    I([Inicio]) --> C[Conteo de entrada]

    C -->|lee 1| C
    C -->|lee _ con n=0| E0[Preparar F0]
    C -->|lee _ con n=1| E1[Preparar F1]
    C -->|...| Ek[Preparar Fn]
    C -->|si n > 10| R((qReject))

    E0 --> B0[Borrado de cinta para caso n=0]
    E1 --> B1[Borrado de cinta para caso n=1]
    Ek --> Bk[Borrado de cinta para caso n]

    B0 --> W0[Escritura de F0 en unario]
    B1 --> W1[Escritura de F1 en unario]
    Bk --> Wk[Escritura de Fn en unario]

    W0 --> A((qAccept))
    W1 --> A
    Wk --> A

    classDef ok fill:#d5f5e3,stroke:#1e8449,color:#000;
    classDef no fill:#fadbd8,stroke:#922b21,color:#000;
    class A ok;
    class R no;
```

## Cómo leerlo

- `Conteo de entrada` resume los estados `q0..q10`.
- `Borrado de cinta` resume los estados `qErase0..qErase10`.
- `Escritura de F(n)` resume las cadenas `qWritei_0..qWritei_F(i)`.
- `qReject` ocurre cuando la entrada excede el máximo configurado (`n > 10`).

## Recomendación para entrega

- Usa este diagrama simplificado en el cuerpo principal del informe.
- Deja el diagrama detallado en [diagrama_transiciones.md](diagrama_transiciones.md) como anexo técnico.
