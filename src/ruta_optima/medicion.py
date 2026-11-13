"""R4. Medición de fuerza bruta y Held-Karp según el protocolo del enunciado (sección 6).

Reglas que implementa:
- Solo se mide el algoritmo (el reloj envuelve únicamente la llamada a la función).
- 5 repeticiones y se reporta la mediana; si una ejecución pasa de 1 minuto, se mide una sola vez.
- Límite de 5 minutos por ejecución: si se pasa, se detiene y se reporta "no completada".
- Datos aleatorios con semilla fija.
- Unidad de tiempo: milisegundos. Resultados en CSV.

Uso (desde la raíz del proyecto):
    python -m src.ruta_optima.medicion
Para probar rápido:
    python -m src.ruta_optima.medicion --k-max 8 --limite-s 20
"""
import argparse
import csv
import multiprocessing as mp
import os
import platform
import random
import statistics
import time

from src.ruta_optima.tsp import fuerza_bruta, held_karp

SEMILLA = 2026
REPETICIONES = 5
UMBRAL_UNA_SOLA_VEZ_S = 60.0   # ejecuciones de más de 1 minuto se miden una sola vez
ALGORITMOS = {"fuerza_bruta": fuerza_bruta, "held_karp": held_karp}


def generar_matriz(n, semilla=SEMILLA):
    """Matriz asimétrica aleatoria de tiempos (segundos), con diagonal 0."""
    rng = random.Random(semilla)
    return [[0 if i == j else rng.randint(60, 3600) for j in range(n)] for i in range(n)]


def _ejecutar(nombre, T, inicio, lugares, cola):
    """Se ejecuta en un proceso aparte. Mide solo la llamada al algoritmo."""
    f = ALGORITMOS[nombre]
    t0 = time.perf_counter_ns()
    tiempo, ruta = f(T, inicio, lugares)
    t1 = time.perf_counter_ns()
    cola.put(((t1 - t0) / 1e6, tiempo))   # (ms medidos, tiempo de viaje óptimo)


def medir_una_vez(nombre, T, inicio, lugares, limite_s):
    """Devuelve (ms, optimo) o None si pasó el límite."""
    cola = mp.Queue()
    p = mp.Process(target=_ejecutar, args=(nombre, T, inicio, lugares, cola))
    p.start()
    p.join(limite_s)
    if p.is_alive():
        p.terminate()
        p.join()
        return None
    return cola.get()


def medir(nombre, T, inicio, lugares, limite_s):
    """Aplica el protocolo: hasta 5 repeticiones y mediana; una sola vez si pasa de 1 minuto."""
    tiempos, optimo = [], None
    for _ in range(REPETICIONES):
        r = medir_una_vez(nombre, T, inicio, lugares, limite_s)
        if r is None:
            return None, None, len(tiempos)
        ms, optimo = r
        tiempos.append(ms)
        if ms / 1000.0 > UMBRAL_UNA_SOLA_VEZ_S:
            break
    return statistics.median(tiempos), optimo, len(tiempos)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--k-min", type=int, default=5)
    ap.add_argument("--k-max", type=int, default=12)
    ap.add_argument("--limite-s", type=float, default=300.0)
    ap.add_argument("--salida", default="resultados")
    args = ap.parse_args()

    os.makedirs(args.salida, exist_ok=True)
    with open(os.path.join(args.salida, "r4_maquina.txt"), "w", encoding="utf-8") as f:
        f.write(f"Sistema operativo: {platform.platform()}\n")
        f.write(f"Procesador: {platform.processor()}\n")
        f.write(f"Python: {platform.python_version()}\n")
        f.write("Memoria RAM: [completar a mano]\n")

    T = generar_matriz(args.k_max + 1)   # partida = 0; lugares = 1..k
    filas = []
    for nombre in ALGORITMOS:
        for k in range(args.k_min, args.k_max + 1):
            lugares = list(range(1, k + 1))
            mediana, optimo, n_rep = medir(nombre, T, 0, lugares, args.limite_s)
            if mediana is None:
                print(f"{nombre} k={k}: no completada (más de {args.limite_s:g} s)")
                filas.append([nombre, k, n_rep, "", "", "no completada", SEMILLA])
                break                      # con k mayor tardaría aún más
            print(f"{nombre} k={k}: mediana {mediana:.3f} ms ({n_rep} rep.), óptimo {optimo}")
            filas.append([nombre, k, n_rep, f"{mediana:.3f}", optimo, "completada", SEMILLA])

    ruta = os.path.join(args.salida, "r4_exactas.csv")
    with open(ruta, "w", newline="", encoding="utf-8") as f:
        w = csv.writer(f)
        w.writerow(["metodo", "k", "repeticiones", "mediana_ms", "tiempo_optimo_s", "estado", "semilla"])
        w.writerows(filas)
    print("Guardado en", ruta)


if __name__ == "__main__":
    main()