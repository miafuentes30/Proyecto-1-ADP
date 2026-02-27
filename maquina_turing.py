import json
import sys
import time
from dataclasses import dataclass
from typing import Dict, Tuple, List, Optional

import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

def banner(title, width=70):
    #titulo
    bar = "=" * width
    pad = (width - len(title) - 2) // 2
    extra = width - pad - len(title) - 1
    print(f"\n+{bar}+")
    print(f"|{' ' * pad} {title}{' ' * extra}|")
    print(f"+{bar}+")

def section(title):
    # subtitulo
    dashes = "-" * max(0, 62 - len(title))
    print(f"\n[ {title} {dashes}]")

def endsection():
    print(f"{'-' * 67}")

def info(label, value, indent=2):
    sp = " " * indent
    print(f"{sp}> {label}: {value}")

def row_sep(width=70):
    print("-" * width)
    

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


# FIBONACCI Y UNARIO - Mia
# -----------------------------------------------------------------------

def fib(n):
    """Calcula el n-ésimo número de Fibonacci.
    
    F(0)=0, F(1)=1, F(n)=F(n-1)+F(n-2) para n>=2.
    
    F(i+1) = F(i) + F(i-1) es la relación de recurrencia que define la secuencia de Fibonacci de este caso
    """
    a, b = 0, 1
    for _ in range(n): a, b = b, a + b
    return a

def unary(n):
    """Convierte un # a representacion unaria (n repeticiones de '1')."""
    return "1" * n


# GENERADOR DE JSON - Mia
# ------------------------------------------------------------------------

def generate_fib_tm_json(max_n, out_path="fib_tm.json"):
    """Genera y guarda la especificación JSON para Fibonacci.
    
    Construye una MT que:
    - Lee un # n en representacion unaria (n veces el simbolo '1')
    - Calcula F(n) (el n-ésimo número de Fibonacci)
    - Escribe el resultado en representación unaria
    
    La maquina rechaza automáticamente entradas mayores a max_n.
    """
    states = ["qAccept", "qReject"]
    transitions = {}

    for i in range(max_n + 1):
        states.append(f"q{i}")
        if i < max_n:
            transitions[f"q{i},1"] = [f"q{i+1}", "1", "R"]
        else:
            transitions[f"q{i},1"] = ["qReject", "1", "S"]
        transitions[f"q{i},_"] = [f"qErase{i}", "_", "L"]

    for i in range(max_n + 1):
        states.append(f"qErase{i}")
        transitions[f"qErase{i},1"] = [f"qErase{i}", "_", "L"]
        transitions[f"qErase{i},_"] = [f"qWrite{i}_0", "_", "R"]

    for i in range(max_n + 1):
        Fi = fib(i)
        if Fi == 0:
            states.append(f"qWrite{i}_0")
            transitions[f"qWrite{i}_0,_"] = ["qAccept", "_", "S"]
        else:
            for k in range(Fi + 1):
                states.append(f"qWrite{i}_{k}")
            for k in range(Fi):
                transitions[f"qWrite{i}_{k},_"] = [f"qWrite{i}_{k+1}", "1", "R"]
            transitions[f"qWrite{i}_{Fi},_"] = ["qAccept", "_", "S"]

    tm_data = {
        "name": f"Fibonacci MT",
        "description": (
            f"Maquina de Turing que calcula Fibonacci en unario para n cantidad de numeros "
        ),
        "blank": "_",
        "input_alphabet": ["1"],
        "tape_alphabet": ["1", "_"],
        "start_state": "q0",
        "accept_states": ["qAccept"],
        "reject_states": ["qReject"],
        "states": list(dict.fromkeys(states)),
        "transitions": transitions,
    }
    with open(out_path, "w", encoding="utf-8") as f:
        json.dump(tm_data, f, indent=2, ensure_ascii=False)
    return out_path

# ANALISIS EMPIRICO - Angel
# --------------------------------------------------------------------------

def r2_score(y_true, y_pred):
    """
    Calcula el coeficiente de determinación R² para un ajuste.
    
    Mide que tan bien un modelo se ajusta a los datos observados.
    R²=1 indica ajuste perfecto, R²=0 indica que el modelo no explica la varianza.
    """
    ss_r = float(np.sum((y_true - y_pred) ** 2))
    ss_t = float(np.sum((y_true - np.mean(y_true)) ** 2))
    return 1.0 if ss_t == 0 else 1 - ss_r / ss_t

def best_poly(x, y, degrees=(1, 2, 3)):
    """
    Encuentra el mejor ajuste polinomial entre los grados especificados.
    
    Prueba cada grado polinomial y retorna el que maximiza R².
    Sirve para determinar la complejidad temporal/espacial de un algoritmo.
    """
    best = None
    for deg in degrees:
        if len(x) < deg + 1:
            continue
        c = np.polyfit(x, y, deg)
        yh = np.poly1d(c)(x)
        rv = r2_score(y, yh)
        if best is None or rv > best["r2"]:
            best = {"deg": deg, "coeffs": c, "y_hat": yh, "r2": rv}
    return best


def fmt_poly(coeffs, var="n", name="f"):
    """
    Convierte coeficientes polinomiales a una expresion matematica.

    """
    p = np.poly1d(coeffs)
    terms = []
    for i, a in enumerate(p.coeffs):
        pw = p.order - i
        if abs(a) < 1e-12:
            continue
        a_s = f"{a:.4g}"
        if pw == 0:
            terms.append(a_s)
        elif pw == 1:
            terms.append(f"{a_s}*{var}")
        elif pw == 2:
            terms.append(f"{a_s}*{var}^2")
        else:
            terms.append(f"{a_s}*{var}^{pw}")
    expr = " + ".join(terms).replace("+ -", "- ")
    return f"{name}({var}) = {expr}"

BIG_O = {0: "O(1)", 1: "O(n)", 2: "O(n^2)", 3: "O(n^3)"}


def plot_analysis(x, steps_arr, time_arr, fit_s, fit_t, out="analisis_tm.png"):
    """
    Genera graficas del analisis empirico: pasos vs n y tiempo vs n.
    
    Crecen los pasos de ejecución y el tiempo con respecto al tamaño de la entrada, junto con sus ajustes polinomiales.
    """
    dark   = "#0d1117"
    panel  = "#161b22"
    border = "#30363d"
    txt    = "#e6edf3"
    blue   = "#58a6ff"
    green  = "#3fb950"
    red    = "#f78166"
    grid_c = "#21262d"

    fig, axes = plt.subplots(2, 2, figsize=(13, 9))
    fig.patch.set_facecolor(dark)

    def style(ax, title, xl, yl):
        ax.set_facecolor(panel)
        ax.set_title(title, color=txt, fontsize=11, pad=8)
        ax.set_xlabel(xl, color=txt, fontsize=9)
        ax.set_ylabel(yl, color=txt, fontsize=9)
        ax.tick_params(colors=txt, labelsize=8)
        ax.grid(True, color=grid_c, linewidth=0.5)
        for sp in ax.spines.values():
            sp.set_edgecolor(border)

    x_fine = np.linspace(x.min(), x.max(), 300)

    axes[0, 0].scatter(x, steps_arr, color=blue, s=55, zorder=3,
                       edgecolors=border, linewidths=0.5)
    style(axes[0, 0], "Pasos vs n  (dispersion)", "n  (longitud entrada unaria)", "Pasos")

    axes[0, 1].scatter(x, steps_arr, color=blue, s=55, zorder=3,
                       edgecolors=border, linewidths=0.5, label="datos")
    if fit_s:
        axes[0, 1].plot(x_fine, np.poly1d(fit_s["coeffs"])(x_fine),
                        color=red, lw=2.2,
                        label=f"Polinomio g={fit_s['deg']}  R2={fit_s['r2']:.4f}")
    style(axes[0, 1], "Regresion Pasos vs n", "n", "Pasos")
    axes[0, 1].legend(facecolor=panel, labelcolor=txt, fontsize=8, framealpha=0.7)

    axes[1, 0].scatter(x, time_arr, color=green, s=55, zorder=3,
                       edgecolors=border, linewidths=0.5)
    style(axes[1, 0], "Tiempo vs n  (dispersion)", "n  (longitud entrada unaria)", "Tiempo (s)")

    axes[1, 1].scatter(x, time_arr, color=green, s=55, zorder=3,
                       edgecolors=border, linewidths=0.5, label="datos")
    if fit_t:
        axes[1, 1].plot(x_fine, np.poly1d(fit_t["coeffs"])(x_fine),
                        color=red, lw=2.2,
                        label=f"Polinomio g={fit_t['deg']}  R2={fit_t['r2']:.4f}")
    style(axes[1, 1], "Regresion Tiempo vs n", "n", "Tiempo (s)")
    axes[1, 1].legend(facecolor=panel, labelcolor=txt, fontsize=8, framealpha=0.7)

    fig.suptitle("Analisis Empirico -- MT Fibonacci",
                 color=txt, fontsize=14, fontweight="bold", y=1.02)
    plt.tight_layout()
    plt.savefig(out, dpi=160, bbox_inches="tight", facecolor=dark)
    plt.close()
    return out

if __name__ == "__main__":
    main()