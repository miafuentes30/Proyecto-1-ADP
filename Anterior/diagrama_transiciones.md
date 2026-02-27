# Diagrama de transiciones (MT Fibonacci)

```mermaid
graph LR
    INICIO([Inicio]) --> q0

  subgraph Conteo_entrada[Conteo de entrada q0 a q10]
      q0((q0)) -->|1/1,R| q1((q1))
      q1 -->|1/1,R| q2((q2))
      q2 -->|1/1,R| q3((q3))
      q3 -->|1/1,R| q4((q4))
      q4 -->|1/1,R| q5((q5))
      q5 -->|1/1,R| q6((q6))
      q6 -->|1/1,R| q7((q7))
      q7 -->|1/1,R| q8((q8))
      q8 -->|1/1,R| q9((q9))
      q9 -->|1/1,R| q10((q10))
      q10 -->|1/1,S| qReject((qReject))
    end

    q0 -->|_/_,L| qErase0((qErase0))
    q1 -->|_/_,L| qErase1((qErase1))
    q2 -->|_/_,L| qErase2((qErase2))
    q3 -->|_/_,L| qErase3((qErase3))
    q4 -->|_/_,L| qErase4((qErase4))
    q5 -->|_/_,L| qErase5((qErase5))
    q6 -->|_/_,L| qErase6((qErase6))
    q7 -->|_/_,L| qErase7((qErase7))
    q8 -->|_/_,L| qErase8((qErase8))
    q9 -->|_/_,L| qErase9((qErase9))
    q10 -->|_/_,L| qErase10((qErase10))

    subgraph Borrado[Patron de borrado para cada i]
      E1((qErasei)) -->|1/_,L| E1
      E1 -->|_/_,R| W0((qWritei_0))
    end

    subgraph Escritura[Patron de escritura para cada i]
      W0 -->|_/1,R| W1((qWritei_1))
      W1 -->|...| Wk((qWritei_k))
      Wk -->|_/1,R| WF((qWritei_Fi))
      WF -->|_/_,S| qAccept((qAccept))
    end

    qErase0 -. entra a .-> WN0
    qErase1 -. entra a .-> WN1
    qErase2 -. entra a .-> WN2
    qErase3 -. entra a .-> WN3
    qErase4 -. entra a .-> WN4
    qErase5 -. entra a .-> WN5
    qErase6 -. entra a .-> WN6
    qErase7 -. entra a .-> WN7
    qErase8 -. entra a .-> WN8
    qErase9 -. entra a .-> WN9
    qErase10 -. entra a .-> WN10

    WN0([qWrite0_0]) -->|_/_,S| qAccept

    WN1([qWrite1_0]) -->|_/1,R| WN1b([qWrite1_1])
    WN1b -->|_/_,S| qAccept

    WN4([qWrite4_0]) -->|_/1,R| WN4_1([qWrite4_1])
    WN4_1 -->|_/1,R| WN4_2([qWrite4_2])
    WN4_2 -->|_/1,R| WN4_3([qWrite4_3])
    WN4_3 -->|_/_,S| qAccept

    WN10([qWrite10_0 ... qWrite10_55]) -->|escribe 55 unos| qAccept

    classDef final fill:#d5f5e3,stroke:#1e8449,color:#000;
    classDef reject fill:#fadbd8,stroke:#922b21,color:#000;
    class qAccept final;
    class qReject reject;
```

## Convención de etiquetas

Cada etiqueta tiene formato: `lee/escribe,movimiento`.

- `1/1,R`: lee `1`, escribe `1`, mueve a la derecha.
- `1/_,L`: lee `1`, escribe blanco `_`, mueve a la izquierda.
- `_/_,S`: lee blanco, escribe blanco, no se mueve.
