"""R4. Gráfica de tiempo frente a k para fuerza bruta y Held-Karp (misma figura).

Lee resultados/r4_exactas.csv (lo genera medicion.py) y guarda resultados/r4_tiempos.png.
Eje vertical en escala logarítmica, porque los dos métodos difieren en órdenes de magnitud.
Las ejecuciones "no completada" no tienen tiempo: se marcan con una línea vertical punteada en su k.

Uso (desde la raíz del proyecto):
    python -m src.ruta_optima.graficas
    python -m src.ruta_optima.graficas --entrada resultados/r4_exactas.csv --salida resultados/r4_tiempos.png
"""
import argparse
import csv

import matplotlib

matplotlib.use("Agg")   # guarda a archivo, sin abrir ventana
import matplotlib.pyplot as plt

NOMBRES = {"fuerza_bruta": "Fuerza bruta", "held_karp": "Held-Karp"}
ESTILO = {"fuerza_bruta": ("tab:red", "o"), "held_karp": ("tab:blue", "s")}


def leer(ruta):
    """Devuelve {metodo: {"k": [...], "ms": [...], "no_completada": [k, ...]}}."""
    datos = {}
    with open(ruta, encoding="utf-8", newline="") as f:
        for fila in csv.DictReader(f):
            d = datos.setdefault(fila["metodo"], {"k": [], "ms": [], "no_completada": []})
            if fila["estado"] == "completada":
                d["k"].append(int(fila["k"]))
                d["ms"].append(float(fila["mediana_ms"]))
            else:
                d["no_completada"].append(int(fila["k"]))
    return datos


def graficar(datos, salida):
    fig, ax = plt.subplots(figsize=(7, 4.5), dpi=150)
    for metodo, d in datos.items():
        color, marcador = ESTILO.get(metodo, (None, "o"))
        ax.plot(d["k"], d["ms"], marker=marcador, color=color, label=NOMBRES.get(metodo, metodo))
        for k in d["no_completada"]:
            ax.axvline(k, color=color, linestyle=":", alpha=0.7,
                       label=f"{NOMBRES.get(metodo, metodo)}: no completada (k = {k})")
    ax.set_yscale("log")
    ax.set_xlabel("k (número de lugares a visitar)")
    ax.set_ylabel("Tiempo de ejecución, mediana (ms, escala logarítmica)")
    ax.set_title("R4. Tiempo frente a k: fuerza bruta y Held-Karp")
    todos_k = sorted({k for d in datos.values() for k in d["k"] + d["no_completada"]})
    ax.set_xticks(todos_k)
    ax.grid(True, which="both", alpha=0.3)
    ax.legend()
    fig.tight_layout()
    fig.savefig(salida)
    print("Guardado en", salida)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--entrada", default="resultados/r4_exactas.csv")
    ap.add_argument("--salida", default="resultados/r4_tiempos.png")
    args = ap.parse_args()
    graficar(leer(args.entrada), args.salida)


if __name__ == "__main__":
    main()

