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
