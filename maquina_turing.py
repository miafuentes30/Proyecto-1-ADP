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