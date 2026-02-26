from dataclasses import dataclass
from typing import Dict, Tuple, List, Optional

import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

# DEFINICION DE LA MAQUINA DE TURING  - Mia 
# ----------------------------------------------------------------------
@dataclass
class TMDefinition:
    """
    Definicion completa de una maquina de Turing, 
    Representa todos los componentes matemáticos necesarios para una MT:
    estados, simbolos del alfabeto, transiciones y estados aceptores/rechazadores.
    """
    name: str
    description: str
    blank: str
    start_state: str
    accept_states: set
    reject_states: set
    tape_alphabet: set
    input_alphabet: set
    transitions: dict


def load_tm_from_json(path):
    """
    Carga la config de la maquina de Turing desde un archivo JSON.
    
    El JSON tiene: estados, alfabetos, transiciones y estados aceptores.
    Las transiciones se representan como (estado, símbolo) -> (nuevo_estado, escritura, movimiento).
    """
    with open(path, "r", encoding="utf-8") as f:
        data = json.load(f)
    transitions = {}
    for k, v in data.get("transitions", {}).items():
        if "," not in k or not isinstance(v, list) or len(v) != 3:
            raise ValueError(f"Transicion invalida: {k} -> {v}")
        state, sym = k.split(",", 1)
        transitions[(state.strip(), sym.strip())] = (v[0], v[1], v[2])
    return TMDefinition(
        name          = data.get("name", "MT"),
        description   = data.get("description", ""),
        blank         = data["blank"],
        start_state   = data["start_state"],
        accept_states = set(data.get("accept_states", [])),
        reject_states = set(data.get("reject_states", [])),
        tape_alphabet = set(data.get("tape_alphabet", [])),
        input_alphabet= set(data.get("input_alphabet", [])),
        transitions   = transitions,
    )

# CINTA - Mia 
# ----------------------------------------------------------------------
class Tape:
    """Simulación de la cinta infinita de una mt
    
    Permite lectura, escritura y navegación en una cinta infinita.
    Utiliza un diccionario disperso para optimizar memoria (solo almacena celdas no-blanco).
    """
    def __init__(self, blank):
        self.blank = blank
        self.cells = {}

    def load(self, s):
        self.cells = {i: ch for i, ch in enumerate(s)}

    def read(self, pos):
        return self.cells.get(pos, self.blank)

    def write(self, pos, sym):
        if sym == self.blank:
            self.cells.pop(pos, None)
        else:
            self.cells[pos] = sym

    def snapshot(self, head, window=20):
        # Retorna una vista de la cinta alrededor de la posición actual del cabezal
        lo, hi = head - window, head + window
        parts = []
        for i in range(lo, hi + 1):
            s = self.read(i)
            if i == head:
                parts.append(f"[{s}]")
            else:
                parts.append(f" {s} ")
        return "".join(parts)

    def trimmed(self):
        if not self.cells:
            return ""
        lo, hi = min(self.cells), max(self.cells)
        return "".join(self.read(i) for i in range(lo, hi + 1))
    
# EJECUCION - Mia
# ----------------------------------------------------------------------
@dataclass
class TMResult:
    """Resultado de la ejecucion MT
    
    Contiene información sobre el reultado final (aceptada/rechazada),
    el número de pasos, tiempo de ejecución y contenido final de la cinta.
    """
    accepted:    bool
    rejected:    bool
    halted:      bool
    final_state: str
    steps:       int
    time_sec:    float
    output_tape: str
    reason:      str


def run_tm(tm, input_str, max_steps=2_000_000, verbose=False, window=18):
    """
    Simula paso a paso el funcionamiento de la mt, siguiendo sus transiciones
    hasta llegar a un estado aceptor, rechazador o alcanzar el límite de pasos.
    
    Retorna un TMResult con información completa sobre la ejecucion.
    """
    tape = Tape(tm.blank)
    tape.load(input_str)
    state, head, steps = tm.start_state, 0, 0
    t0 = time.perf_counter()
    header_shown = False

    while steps < max_steps:
        if state in tm.accept_states:
            return TMResult(True, False, True, state, steps,
                            time.perf_counter() - t0, tape.trimmed(), "accept")
        if state in tm.reject_states:
            return TMResult(False, True, True, state, steps,
                            time.perf_counter() - t0, tape.trimmed(), "reject")

        read_sym = tape.read(head)
        key = (state, read_sym)

        if key not in tm.transitions:
            return TMResult(False, True, True, state, steps,
                            time.perf_counter() - t0, tape.trimmed(),
                            f"sin_transicion({state},{read_sym})")

        new_state, write_sym, move = tm.transitions[key]

        if verbose:
            show = steps < 20 or steps % 1000 == 0
            if show:
                if not header_shown:
                    section("LISTADO DE CONFIGURACIONES")
                    print(
                        f"  {'Paso':>6}  {'Estado actual':<22}  {'Cab':>4}  "
                        f"{'Lee':>5}  {'Escribe':>8}  {'Mueve':>6}  {'Siguiente estado'}"
                    )
                    row_sep()
                    header_shown = True

                print(
                    f"  {str(steps).rjust(6)}  "
                    f"{state:<22}  "
                    f"{str(head).rjust(4)}  "
                    f"{repr(read_sym).rjust(5)}  "
                    f"{repr(write_sym).rjust(8)}  "
                    f"{move.rjust(6)}  "
                    f"{new_state}"
                )
                if steps < 8 or steps % 5000 == 0:
                    print(f"         Cinta: {tape.snapshot(head, window)}")

        tape.write(head, write_sym)
        head += {"L": -1, "R": 1}.get(move, 0)
        state = new_state
        steps += 1

    return TMResult(False, False, False, state, steps,
                    time.perf_counter() - t0, tape.trimmed(), "max_pasos_alcanzado")

