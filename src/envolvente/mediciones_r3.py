import csv
import gc
import platform
import random
import statistics
import sys
import time

import numpy as np
from scipy.spatial import ConvexHull

from src.envolvente.calcular_envolvente import puntos_de_la_red
from src.envolvente.envolvente import envolvente_convexa

SEMILLA = 2026
LADO = 1_000_000          # cuadrado de 1 000 km de lado, coordenadas enteras
TAMANOS = (1_000, 10_000, 50_000)
CAMPOS = ["conjunto", "n_puntos", "vertices",
          "propio_mediana_ms", "propio_repeticiones", "propio_tiempos_ms",
          "scipy_mediana_ms", "scipy_repeticiones", "scipy_tiempos_ms",
          "cociente_propio_scipy"]


def medir(funcion, *args):
    """5 repeticiones (1 sola si una pasa de 1 minuto). Tiempos en milisegundos."""
    tiempos = []
    gc.collect()
    gc.disable()
    try:
        for _ in range(5):
            t0 = time.perf_counter_ns()
            resultado = funcion(*args)
            dt = (time.perf_counter_ns() - t0) / 1e6
            tiempos.append(dt)
            if dt > 60_000:
                break
    finally:
        gc.enable()
    return resultado, tiempos


def al_azar(n, rng):
    return sorted({(rng.randrange(LADO), rng.randrange(LADO)) for _ in range(n)})


def hull_scipy(arreglo):
    return ConvexHull(arreglo)


if __name__ == "__main__":
    rng = random.Random(SEMILLA)
    conjuntos = [("nodos de la red", puntos_de_la_red())]
    conjuntos += [(f"azar {n}", al_azar(n, rng)) for n in TAMANOS]

    print("Python", sys.version.split()[0], "|", platform.platform(), "|", platform.processor())
    filas = []
    for nombre, puntos in conjuntos:
        arreglo = np.array(puntos, dtype=float)       # la conversión queda fuera del tiempo

        # Verificación antes de medir: mismos vértices que SciPy
        propio = envolvente_convexa(puntos)
        esperado = {puntos[i] for i in ConvexHull(arreglo).vertices}
        assert set(propio) == esperado, f"no coincide con SciPy en '{nombre}'"

        _, tp = medir(envolvente_convexa, puntos)
        _, ts = medir(hull_scipy, arreglo)
        mp, ms = statistics.median(tp), statistics.median(ts)
        filas.append({
            "conjunto": nombre, "n_puntos": len(puntos), "vertices": len(propio),
            "propio_mediana_ms": round(mp, 3), "propio_repeticiones": len(tp),
            "propio_tiempos_ms": " ".join(f"{t:.3f}" for t in tp),
            "scipy_mediana_ms": round(ms, 3), "scipy_repeticiones": len(ts),
            "scipy_tiempos_ms": " ".join(f"{t:.3f}" for t in ts),
            "cociente_propio_scipy": round(mp / ms, 1)})
        print(f"{nombre:16} n={len(puntos):6d} vértices={len(propio):3d} | "
              f"propio {mp:9.3f} ms | scipy {ms:8.3f} ms | cociente {mp / ms:6.1f}")

    with open("resultados/r3_tiempos.csv", "w", encoding="utf-8", newline="") as f:
        w = csv.DictWriter(f, fieldnames=CAMPOS)
        w.writeheader()
        w.writerows(filas)
    print("Guardado: resultados/r3_tiempos.csv")
