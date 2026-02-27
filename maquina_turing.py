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
    args = parser.parse_args()

    TM_JSON   = args.tm
    N_VALUES  = list(range(0, args.max_n + 1))
    DEMO_N    = 4
    MAX_STEPS = 2_000_000

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

    fit_s = best_poly(x, y_step, (1, 2, 3))
    fit_t = best_poly(x, y_time, (1, 2, 3))

    section("MODELOS DE REGRESION POLINOMIAL")
    print(f"\n  {bold('Pasos de ejecucion:')}")
    if fit_s:
        info("Grado del polinomio",    fit_s["deg"])
        info("R^2 (bondad de ajuste)", f"{fit_s['r2']:.6f}")
        info("Ecuacion",               clr(fmt_poly(fit_s["coeffs"], "n", "pasos"), C))
        info("Notacion asintotica",    clr(BIG_O.get(fit_s["deg"], f"O(n^{fit_s['deg']})"), G)),

    print(f"\n  {bold('Tiempo de CPU:')}")
    if fit_t:
        info("Grado del polinomio",    fit_t["deg"])
        info("R^2 (bondad de ajuste)", f"{fit_t['r2']:.6f}")
        info("Ecuacion",               clr(fmt_poly(fit_t["coeffs"], "n", "tiempo"), C))
        info("Notacion asintotica",    clr(BIG_O.get(fit_t["deg"], f"O(n^{fit_t['deg']})"), G)),
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
        info("Complejidad pasos",  clr(BIG_O.get(fit_s["deg"], f"O(n^{fit_s['deg']})"), C))
    if fit_t:
        info("Complejidad tiempo", clr(BIG_O.get(fit_t["deg"], f"O(n^{fit_t['deg']})"), C))
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