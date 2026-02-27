import json
import sys
import time
import argparse
from dataclasses import dataclass
from typing import Dict, Tuple, List, Optional

import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

# Colores ANSI
R    = "\033[91m"
G    = "\033[92m"
Y    = "\033[93m"
B    = "\033[94m"
M    = "\033[95m"
C    = "\033[96m"
W    = "\033[97m"
DIM  = "\033[2m"
BOLD = "\033[1m"
RST  = "\033[0m"

def clr(text, color):  return f"{color}{text}{RST}"
def bold(text):        return f"{BOLD}{text}{RST}"
def dim(text):         return f"{DIM}{text}{RST}"

def banner(title, color=C, width=68):
    line = "─" * width
    print(f"\n{color}{line}{RST}")
    print(f"{color}  {bold(title)}{RST}")
    print(f"{color}{line}{RST}")

def section(title, color=Y):
    print(f"\n{color}  {bold(title)}{RST}")
    print(f"{color}  {'=' * (len(title) + 3)}{RST}")

def endsection(color=Y):
    print(f"{color}  {'─' * 58}{RST}")

def info(label, value, indent=2):
    sp = " " * indent
    print(f"{sp}{clr('>', C)} {clr(label, W)}: {clr(str(value), Y)}")

def row_sep(width=70):
    print(dim("-" * width))
    

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
                parts.append(clr(f"[{s}]", M))
            else:
                parts.append(dim(f" {s} "))
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

                sc = G if steps < 20 else DIM
                print(
                    f"  {clr(str(steps).rjust(6), sc)}  "
                    f"{clr(state, C):<22}  "
                    f"{clr(str(head).rjust(4), Y)}  "
                    f"{clr(repr(read_sym).rjust(5), M)}  "
                    f"{clr(repr(write_sym).rjust(8), M)}  "
                    f"{clr(move.rjust(6), B)}  "
                    f"{clr(new_state, C)}"
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
            best = {"model": "poly", "deg": deg, "coeffs": c, "y_hat": yh, "r2": rv}
    return best


def best_exponential(x, y):
    """
    Ajusta un modelo exponencial y = a * b^n usando transformacion logaritmica.

    Requiere y > 0 para aplicar log(y). Si no hay suficientes puntos validos,
    retorna None.
    """
    mask = y > 0
    if np.sum(mask) < 2:
        return None

    x_pos = x[mask]
    y_pos = y[mask]
    m, c = np.polyfit(x_pos, np.log(y_pos), 1)
    a = float(np.exp(c))
    b = float(np.exp(m))
    y_hat_pos = a * np.power(b, x_pos)
    rv = r2_score(y_pos, y_hat_pos)

    return {
        "model": "exp",
        "a": a,
        "b": b,
        "slope": float(m),
        "intercept_ln": float(c),
        "r2": rv,
    }


PHI = (1 + np.sqrt(5)) / 2


def best_hybrid(x, y, poly_degrees=(0, 1, 2, 3), phi=PHI):
    """
    Ajusta un modelo hibrido con base fija:
        y = phi^n * p(n)

    donde p(n) es polinomio de grado variable. Equivale a ajustar
    p(n) sobre la señal escalada y / phi^n.
    """
    mask = np.isfinite(x) & np.isfinite(y)
    if np.sum(mask) < 2:
        return None

    x_ok = x[mask]
    y_ok = y[mask]
    scaled = y_ok / np.power(phi, x_ok)
    best = None

    for deg in poly_degrees:
        if len(x_ok) < deg + 1:
            continue

        coeffs = np.polyfit(x_ok, scaled, deg)
        p_vals = np.poly1d(coeffs)(x_ok)
        y_hat = np.power(phi, x_ok) * p_vals
        rv = r2_score(y_ok, y_hat)

        candidate = {
            "model": "hybrid_phi",
            "phi": float(phi),
            "poly_deg": int(deg),
            "coeffs": coeffs,
            "r2": rv,
        }
        if best is None or rv > best["r2"]:
            best = candidate

    return best


def best_hybrid_free_base(x, y, poly_degrees=(0, 1, 2, 3), b_min=1.01, b_max=3.5, grid_size=120):
    """
    Ajusta modelo hibrido con base libre:
        y = b^n * p(n)

    Recorre una malla de b y para cada base ajusta p(n) polinomial.
    Retorna el mejor por R².
    """
    mask = np.isfinite(x) & np.isfinite(y)
    if np.sum(mask) < 2:
        return None

    x_ok = x[mask]
    y_ok = y[mask]

    exp_seed = best_exponential(x_ok, np.abs(y_ok) + 1e-12)
    if exp_seed is not None:
        b0 = float(exp_seed["b"])
        b_min_eff = max(1.001, min(b_min, b0 * 0.6))
        b_max_eff = max(b_max, b0 * 1.6)
    else:
        b_min_eff, b_max_eff = b_min, b_max

    b_grid = np.logspace(np.log10(b_min_eff), np.log10(b_max_eff), int(grid_size))

    best = None
    for b in b_grid:
        scaled = y_ok / np.power(b, x_ok)
        for deg in poly_degrees:
            if len(x_ok) < deg + 1:
                continue
            coeffs = np.polyfit(x_ok, scaled, deg)
            p_vals = np.poly1d(coeffs)(x_ok)
            y_hat = np.power(b, x_ok) * p_vals
            rv = r2_score(y_ok, y_hat)

            candidate = {
                "model": "hybrid_free",
                "b": float(b),
                "poly_deg": int(deg),
                "coeffs": coeffs,
                "r2": rv,
            }
            if best is None or rv > best["r2"]:
                best = candidate

    return best


def best_model(
    x,
    y,
    poly_degrees=(1, 2, 3),
    allow_exp=True,
    allow_hybrid_phi=True,
    hybrid_phi_degrees=(0, 1, 2, 3),
    allow_hybrid_free=True,
    hybrid_free_degrees=(0, 1, 2, 3),
):
    """
    Compara modelos candidatos:
    - polinomial
    - exponencial
    - hibrido con base fija phi: phi^n * p(n)
    - hibrido con base libre:   b^n * p(n)

    y retorna el de mayor R².
    """
    candidates = []
    poly_fit = best_poly(x, y, poly_degrees)
    if poly_fit is not None:
        candidates.append(poly_fit)

    if allow_exp:
        exp_fit = best_exponential(x, y)
        if exp_fit is not None:
            candidates.append(exp_fit)

    if allow_hybrid_phi:
        hybrid_phi_fit = best_hybrid(x, y, hybrid_phi_degrees)
        if hybrid_phi_fit is not None:
            candidates.append(hybrid_phi_fit)

    if allow_hybrid_free:
        hybrid_free_fit = best_hybrid_free_base(x, y, hybrid_free_degrees)
        if hybrid_free_fit is not None:
            candidates.append(hybrid_free_fit)

    if not candidates:
        return None
    return max(candidates, key=lambda m: m["r2"])


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


def eval_model(model, x):
    """Evalua un modelo (polinomial o exponencial) sobre x."""
    if model is None:
        return None
    if model["model"] == "poly":
        return np.poly1d(model["coeffs"])(x)
    if model["model"] == "hybrid_phi":
        return np.power(model["phi"], x) * np.poly1d(model["coeffs"])(x)
    if model["model"] == "hybrid_free":
        return np.power(model["b"], x) * np.poly1d(model["coeffs"])(x)
    return model["a"] * np.power(model["b"], x)


def fmt_model(model, var="n", name="f"):
    """Formatea la ecuacion del modelo seleccionado."""
    if model is None:
        return f"{name}({var}) = N/A"
    if model["model"] == "poly":
        return fmt_poly(model["coeffs"], var, name)
    if model["model"] == "hybrid_phi":
        poly_expr = fmt_poly(model["coeffs"], var, "p").split("=", 1)[1].strip()
        return f"{name}({var}) = ({model['phi']:.6f}^{var})*({poly_expr})"
    if model["model"] == "hybrid_free":
        poly_expr = fmt_poly(model["coeffs"], var, "p").split("=", 1)[1].strip()
        return f"{name}({var}) = ({model['b']:.4g}^{var})*({poly_expr})"
    return f"{name}({var}) = {model['a']:.4g}*({model['b']:.4g}^{var})"


def asymptotic_from_model(model, var="n"):
    """Infiere notacion asintotica segun el tipo de modelo ajustado."""
    if model is None:
        return "N/A"
    if model["model"] == "poly":
        deg = model["deg"]
        return BIG_O.get(deg, f"O({var}^{deg})")

    if model["model"] == "hybrid_phi":
        deg = model["poly_deg"]
        if deg == 0:
            return f"O(({model['phi']:.6f})^{var})"
        return f"O({var}^{deg}*({model['phi']:.6f})^{var})"

    if model["model"] == "hybrid_free":
        deg = model["poly_deg"]
        b = model["b"]
        if b <= 1 + 1e-12:
            return BIG_O.get(deg, f"O({var}^{deg})")
        if deg == 0:
            return f"O(({b:.4g})^{var})"
        return f"O({var}^{deg}*({b:.4g})^{var})"

    b = model["b"]
    if b <= 1 + 1e-12:
        return "O(1)"
    return f"O(({b:.4g})^{var})"


def model_label(model):
    """Etiqueta compacta para leyendas de graficas."""
    if model is None:
        return "sin ajuste"
    if model["model"] == "poly":
        return f"Polinomio g={model['deg']}  R2={model['r2']:.4f}"
    if model["model"] == "hybrid_phi":
        return f"Hibrido phi, g={model['poly_deg']}  R2={model['r2']:.4f}"
    if model["model"] == "hybrid_free":
        return f"Hibrido b libre, g={model['poly_deg']}, b={model['b']:.4g}  R2={model['r2']:.4f}"
    return f"Exponencial b={model['b']:.4g}  R2={model['r2']:.4f}"


BIG_O = {0: "O(1)", 1: "O(n)", 2: "O(n^2)", 3: "O(n^3)"}


def plot_analysis(x, steps_arr, time_arr, fit_s, fit_t, out="analisis_tm.png"):
    """
    Genera graficas del analisis empirico: pasos vs n y tiempo vs n.
    
    Crecen los pasos de ejecución y el tiempo con respecto al tamaño de la entrada, junto con sus ajustes.
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

    def short_eq(model, var, name, max_len=72):
        eq = fmt_model(model, var, name)
        if len(eq) <= max_len:
            return eq
        return eq[: max_len - 3] + "..."

    x_fine = np.linspace(x.min(), x.max(), 300)

    # Recalcular en este punto para asegurar que la grafica use
    # siempre el modelo con mejor ajuste disponible.
    fit_s_plot = best_model(
        x, steps_arr,
        (1, 2, 3),
        allow_exp=True,
        allow_hybrid_phi=True,
        hybrid_phi_degrees=(0, 1, 2, 3),
        allow_hybrid_free=True,
        hybrid_free_degrees=(0, 1, 2, 3),
    )
    fit_t_plot = best_model(
        x, time_arr,
        (1, 2, 3),
        allow_exp=True,
        allow_hybrid_phi=True,
        hybrid_phi_degrees=(0, 1, 2, 3),
        allow_hybrid_free=True,
        hybrid_free_degrees=(0, 1, 2, 3),
    )

    axes[0, 0].scatter(x, steps_arr, color=blue, s=55, zorder=3,
                       edgecolors=border, linewidths=0.5)
    if fit_s_plot:
        axes[0, 0].plot(x_fine, eval_model(fit_s_plot, x_fine),
                        color=red, lw=2.0, alpha=0.9, label="regresion")
        axes[0, 0].legend(facecolor=panel, labelcolor=txt, fontsize=8, framealpha=0.7)
    style(axes[0, 0], "Pasos vs n  (datos + regresion)", "n  (longitud entrada unaria)", "Pasos")

    axes[0, 1].scatter(x, steps_arr, color=blue, s=55, zorder=3,
                       edgecolors=border, linewidths=0.5, label="datos")
    if fit_s_plot:
        axes[0, 1].plot(x_fine, eval_model(fit_s_plot, x_fine),
                        color=red, lw=2.2,
                        label=model_label(fit_s_plot))
    tipo_s_plot = {
        "poly": "Polinomial",
        "exp": "Exponencial",
        "hybrid_phi": "Hibrido phi",
        "hybrid_free": "Hibrido b libre",
    }.get(
        fit_s_plot["model"], fit_s_plot["model"]
    ) if fit_s_plot else "Sin ajuste"
    style(axes[0, 1], f"Regresion Pasos vs n ({tipo_s_plot})", "n", "Pasos")
    axes[0, 1].legend(facecolor=panel, labelcolor=txt, fontsize=8, framealpha=0.7)
    if fit_s_plot:
        axes[0, 1].text(
            0.02, 0.97,
            short_eq(fit_s_plot, "n", "pasos"),
            transform=axes[0, 1].transAxes,
            fontsize=7,
            color=txt,
            ha="left",
            va="top",
            bbox=dict(facecolor=panel, edgecolor=border, alpha=0.8, boxstyle="round,pad=0.25"),
        )

    axes[1, 0].scatter(x, time_arr, color=green, s=55, zorder=3,
                       edgecolors=border, linewidths=0.5)
    if fit_t_plot:
        axes[1, 0].plot(x_fine, eval_model(fit_t_plot, x_fine),
                        color=red, lw=2.0, alpha=0.9, label="regresion")
        axes[1, 0].legend(facecolor=panel, labelcolor=txt, fontsize=8, framealpha=0.7)
    style(axes[1, 0], "Tiempo vs n  (datos + regresion)", "n  (longitud entrada unaria)", "Tiempo (s)")

    axes[1, 1].scatter(x, time_arr, color=green, s=55, zorder=3,
                       edgecolors=border, linewidths=0.5, label="datos")
    if fit_t_plot:
        axes[1, 1].plot(x_fine, eval_model(fit_t_plot, x_fine),
                        color=red, lw=2.2,
                        label=model_label(fit_t_plot))
    tipo_t_plot = {
        "poly": "Polinomial",
        "exp": "Exponencial",
        "hybrid_phi": "Hibrido phi",
        "hybrid_free": "Hibrido b libre",
    }.get(
        fit_t_plot["model"], fit_t_plot["model"]
    ) if fit_t_plot else "Sin ajuste"
    style(axes[1, 1], f"Regresion Tiempo vs n ({tipo_t_plot})", "n", "Tiempo (s)")
    axes[1, 1].legend(facecolor=panel, labelcolor=txt, fontsize=8, framealpha=0.7)
    if fit_t_plot:
        axes[1, 1].text(
            0.02, 0.97,
            short_eq(fit_t_plot, "n", "tiempo"),
            transform=axes[1, 1].transAxes,
            fontsize=7,
            color=txt,
            ha="left",
            va="top",
            bbox=dict(facecolor=panel, edgecolor=border, alpha=0.8, boxstyle="round,pad=0.25"),
        )

    fig.suptitle("Analisis Empirico -- MT Fibonacci",
                 color=txt, fontsize=14, fontweight="bold", y=1.02)
    plt.tight_layout()
    plt.savefig(out, dpi=160, bbox_inches="tight", facecolor=dark)
    plt.close()
    return out


# PIPELINE PRINCIPAL - Angel
#--------------------------------------------------------------------------

def main():
    """
    Generación de la MT, simulación demostrativa, analisis empirico
    de complejidad temporal/espacial e input usuario.
    """
    parser = argparse.ArgumentParser(
        description="Simulador de Máquina de Turing determinista de una cinta"
    )
    parser.add_argument(
        "--tm",
        default="fib_tm_real.json",
        help="Ruta al archivo JSON con la definición de la MT",
    )
    parser.add_argument(
        "--max-n",
        type=int,
        default=10,
        help="Máximo n para el análisis empírico (solo para pruebas automáticas)",
    )
    parser.add_argument(
        "--max-steps",
        type=int,
        default=2_000_000,
        help="Límite máximo de pasos por ejecución de la MT",
    )
    args = parser.parse_args()

    TM_JSON   = args.tm
    N_VALUES  = list(range(0, args.max_n + 1))
    DEMO_N    = 4
    MAX_STEPS = args.max_steps

    # Cargar MT desde archivo JSON
    banner("MAQUINA DE TURING", C)
    tm = load_tm_from_json(TM_JSON)

    section("JSON", G)
    info("Estado inicial",    tm.start_state)
    info("Estado aceptor",    ", ".join(sorted(tm.accept_states)))
    info("Estado rechazor",   ", ".join(sorted(tm.reject_states)))
    info("Alfabeto entrada",  "{" + ", ".join(sorted(tm.input_alphabet)) + "}")
    info("Alfabeto cinta",    "{" + ", ".join(sorted(tm.tape_alphabet)) + "}")
    info("Transiciones",      len(tm.transitions))
    info("Archivo de la MT",  TM_JSON)
    endsection(G)

    # Simulacion demostrativa
    banner(f"TABLA DE CONFIGURACIONES  (n = {DEMO_N})", M)
    print(f"  {clr('Convension entrada:', W)}  n={DEMO_N}  ->  cinta = {clr(repr(unary(DEMO_N)), Y)}")
    print(f"  {clr('Resultado esperado:', W)}  F({DEMO_N}) = {clr(fib(DEMO_N), G)}"
          f"  (en unario: {clr(unary(fib(DEMO_N)) or '(vacia)', Y)})\n")

    demo = run_tm(tm, unary(DEMO_N), max_steps=MAX_STEPS, verbose=True)

    endsection(B)
    section("RESULTADOS", G)
    ok = demo.accepted and len(demo.output_tape) == fib(DEMO_N)
    col = G if ok else R
    info("Estado final",       clr(demo.final_state, col))
    info("Estado de acpetación",          clr("ACEPTADA" if demo.accepted else "RECHAZADA", col))
    info("Pasos ejecutados",   demo.steps)
    info("Tiempo de CPU",      f"{demo.time_sec:.6f} s")
    cinta_str = demo.output_tape if demo.output_tape else "(vacia -- F=0)"
    info("Cinta de salida",    clr(cinta_str, Y))
    info("F(n) leido en cinta",
         f"{len(demo.output_tape)}  ->  F({DEMO_N}) = {clr(len(demo.output_tape), G)}")
    endsection(G)

    # Analisis empirico
    banner("ANALISIS EMPIRICO")
    section("ENTRADAS DE PRUEBA Y RESULTADOS")
    print(
        f"  {'n':>4}  {'F(n) esperado':>14}  {'F(n) en cinta':>14}  "
        f"{'Pasos':>7}  {'Tiempo (s)':>11}  Estado de aceptación"
    )
    row_sep()

    rows = []
    for n in N_VALUES:
        res = run_tm(tm, unary(n), max_steps=MAX_STEPS, verbose=False)
        fib_n = fib(n)
        out_n = len(res.output_tape)
        correcto = res.accepted and out_n == fib_n
        icono = clr("OK", G) if correcto else clr("ERROR", R)
        rows.append({
            "n": n, "fib_n": fib_n, "out_len": out_n,
            "steps": res.steps, "time_sec": res.time_sec,
            "accepted": res.accepted, "reason": res.reason,
        })
        print(
            f"  {clr(str(n).rjust(4), W)}  "
            f"{clr(str(fib_n).rjust(14), DIM)}  "
            f"{clr(str(out_n).rjust(14), Y)}  "
            f"{clr(str(res.steps).rjust(7), C)}  "
            f"{clr(f'{res.time_sec:.6f}'.rjust(11), DIM)}  "
            f"{icono}"
        )
    endsection()

    # Regresiones
    acc_rows = [r for r in rows if r["accepted"]]
    x        = np.array([r["n"]        for r in acc_rows], dtype=float)
    y_step   = np.array([r["steps"]    for r in acc_rows], dtype=float)
    y_time   = np.array([r["time_sec"] for r in acc_rows], dtype=float)

    fit_s = best_model(
        x, y_step, (1, 2, 3),
        allow_exp=True,
        allow_hybrid_phi=True,
        hybrid_phi_degrees=(0, 1, 2, 3),
        allow_hybrid_free=True,
        hybrid_free_degrees=(0, 1, 2, 3),
    )
    fit_t = best_model(
        x, y_time, (1, 2, 3),
        allow_exp=True,
        allow_hybrid_phi=True,
        hybrid_phi_degrees=(0, 1, 2, 3),
        allow_hybrid_free=True,
        hybrid_free_degrees=(0, 1, 2, 3),
    )

    section("MODELOS DE REGRESION")
    print(f"\n  {bold('Pasos de ejecucion:')}")
    if fit_s:
        tipo_s = {
            "poly": "Polinomial",
            "exp": "Exponencial",
            "hybrid_phi": "Hibrido phi",
            "hybrid_free": "Hibrido b libre",
        }.get(fit_s["model"], fit_s["model"])
        info("Tipo de modelo",         tipo_s)
        if fit_s["model"] == "poly":
            info("Grado del polinomio", fit_s["deg"])
        elif fit_s["model"] == "hybrid_phi":
            info("Base fija",           f"phi = {fit_s['phi']:.6f}")
            info("Grado de p(n)",       fit_s["poly_deg"])
        elif fit_s["model"] == "hybrid_free":
            info("Base exponencial",    f"b = {fit_s['b']:.6f}")
            info("Grado de p(n)",       fit_s["poly_deg"])
        else:
            info("Base exponencial",    f"b = {fit_s['b']:.6f}")
        info("R^2 (bondad de ajuste)", f"{fit_s['r2']:.6f}")
        info("Ecuacion",               clr(fmt_model(fit_s, "n", "pasos"), C))
        info("Notacion asintotica",    clr(asymptotic_from_model(fit_s, "n"), G))

    print(f"\n  {bold('Tiempo de CPU:')}")
    if fit_t:
        tipo_t = {
            "poly": "Polinomial",
            "exp": "Exponencial",
            "hybrid_phi": "Hibrido phi",
            "hybrid_free": "Hibrido b libre",
        }.get(fit_t["model"], fit_t["model"])
        info("Tipo de modelo",         tipo_t)
        if fit_t["model"] == "poly":
            info("Grado del polinomio", fit_t["deg"])
        elif fit_t["model"] == "hybrid_phi":
            info("Base fija",           f"phi = {fit_t['phi']:.6f}")
            info("Grado de p(n)",       fit_t["poly_deg"])
        elif fit_t["model"] == "hybrid_free":
            info("Base exponencial",    f"b = {fit_t['b']:.6f}")
            info("Grado de p(n)",       fit_t["poly_deg"])
        else:
            info("Base exponencial",    f"b = {fit_t['b']:.6f}")
        info("R^2 (bondad de ajuste)", f"{fit_t['r2']:.6f}")
        info("Ecuacion",               clr(fmt_model(fit_t, "n", "tiempo"), C))
        info("Notacion asintotica",    clr(asymptotic_from_model(fit_t, "n"), G))
    endsection()

    # Graficas
    section("GRAFICAS")
    out_img = plot_analysis(x, y_step, y_time, fit_s, fit_t)
    info("Imagen guardada en", out_img)
    endsection()

    # Resumen
    banner("RESUMEN")
    n_acc = sum(1 for r in rows if r["accepted"])
    n_rej = len(rows) - n_acc
    info("Total pruebas",     len(rows))
    info("Aceptadas",         clr(str(n_acc), G))
    info("Rechazadas",        clr(str(n_rej), R) if n_rej else clr("0", G))
    if fit_s:
        info("Complejidad pasos",  clr(asymptotic_from_model(fit_s, "n"), C))
    if fit_t:
        info("Complejidad tiempo", clr(asymptotic_from_model(fit_t, "n"), C))
    print()

    # Modo interactivo
    banner("INTERFAZ DE USUARIO")
    print("  Ingresa n para calcular F(n) con la MT cargada.")
    print(f"  Escribe {clr('salir', R)} o presiona Ctrl+C para terminar.\n")

    while True:
        try:
            sys.stdout.write(f"  {C}n{RST} = ")
            sys.stdout.flush()
            raw = sys.stdin.readline()
            if raw == "":          # EOF
                break
            raw = raw.strip()
        except KeyboardInterrupt:
            break

        if raw.lower() in ("salir", "exit", "q", "quit"):
            break
        if not raw.isdigit():
            print(clr("  Ingresa un entero no negativo (0, 1, 2, ...).\n", R))
            continue

        n_in = int(raw)
        sys.stdout.write(f"\n  Ejecutando MT:  n={clr(n_in, Y)}  "
                         f"entrada unaria={clr(repr(unary(n_in)), DIM)}\n")
        sys.stdout.flush()
        res = run_tm(tm, unary(n_in), max_steps=MAX_STEPS, verbose=False)

        col = G if res.accepted else R
        print(f"  {clr('Estado final:', W)}  {clr(res.final_state, col)}")
        print(f"  {clr('Estado de aceptación:', W)}    {clr('ACEPTADA' if res.accepted else 'RECHAZADA', col)}")
        print(f"  {clr('Pasos:', W)}        {res.steps}")
        print(f"  {clr('Tiempo:', W)}       {res.time_sec:.6f} s")
        if res.accepted:
            fn = len(res.output_tape)
            cinta = res.output_tape if res.output_tape else "(vacia -- F=0)"
            print(f"  {clr('F(n):', W)}         {clr(fn, G)}")
            print(f"  {clr('Cinta salida:', W)}  {clr(cinta, Y)}\n")
        else:
            print(clr(f"  Entrada no aceptada por la MT cargada. Razón: {res.reason}\n", R))

    print(f"\n  {clr('bye bye!', G)}\n")


if __name__ == "__main__":
    main()