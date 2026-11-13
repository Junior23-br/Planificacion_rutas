"""R4. Calidad de la heurística del vecino más cercano frente al óptimo de Held-Karp.

Para k = 5, 8, 10 y 12, con 5 instancias por cada k, calcula
    alejamiento (%) = (tiempo heurística - tiempo óptimo) / tiempo óptimo * 100
y reporta el promedio y el máximo por k. Partida en el lugar 0; los k lugares se eligen al azar
con semilla fija entre los demás lugares de la matriz.

Uso (desde la raíz del proyecto):
    python -m src.ruta_optima.calidad --matriz data/processed/matriz_tiempos.csv      (datos reales)
    python -m src.ruta_optima.calidad                                                 (matriz aleatoria de prueba)
Con la matriz real, la partida es CAB01 (Armenia) y los k lugares se eligen al azar entre los
otros 39 del catálogo, con una semilla distinta y fija por instancia.
"""
import argparse
import csv
import os
import random

from src.ruta_optima.datos import leer_matriz
from src.ruta_optima.medicion import generar_matriz, SEMILLA
from src.ruta_optima.tsp import held_karp, vecino_mas_cercano

VALORES_K = (5, 8, 10, 12)
INSTANCIAS = 5
N_LUGARES = 13   # lugar 0 (partida) + 12 candidatos


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--salida", default="resultados")
    ap.add_argument("--matriz", default="", help="CSV con la matriz real de R2; vacío = matrices aleatorias de prueba")
    ap.add_argument("--inicio", default="CAB01", help="id del lugar de partida (con matriz real)")
    args = ap.parse_args()
    os.makedirs(args.salida, exist_ok=True)

    if args.matriz:
        ids, T_real = leer_matriz(args.matriz)
        inicio = ids.index(args.inicio)
        candidatos = [i for i in range(len(ids)) if i != inicio]

    detalle, resumen = [], []
    for k in VALORES_K:
        gaps = []
        for inst in range(1, INSTANCIAS + 1):
            semilla = SEMILLA + 1000 * k + inst          # semilla distinta y reproducible por instancia
            if args.matriz:
                T = T_real
                lugares = sorted(random.Random(semilla).sample(candidatos, k))
            else:
                T, inicio = generar_matriz(N_LUGARES, semilla), 0
                lugares = sorted(random.Random(semilla).sample(range(1, N_LUGARES), k))
            optimo, _ = held_karp(T, inicio, lugares)
            heuristica, _ = vecino_mas_cercano(T, inicio, lugares)
            gap = (heuristica - optimo) / optimo * 100
            gaps.append(gap)
            detalle.append([k, inst, semilla, optimo, heuristica, f"{gap:.2f}"])
            print(f"k={k} inst={inst}: óptimo {optimo}, heurística {heuristica}, alejamiento {gap:.2f} %")
        resumen.append([k, INSTANCIAS, f"{sum(gaps) / len(gaps):.2f}", f"{max(gaps):.2f}"])
        print(f"  -> k={k}: promedio {resumen[-1][2]} %, máximo {resumen[-1][3]} %")

    with open(os.path.join(args.salida, "r4_calidad_detalle.csv"), "w", newline="", encoding="utf-8") as f:
        w = csv.writer(f)
        w.writerow(["k", "instancia", "semilla", "tiempo_optimo_s", "tiempo_heuristica_s", "alejamiento_pct"])
        w.writerows(detalle)
    with open(os.path.join(args.salida, "r4_calidad_resumen.csv"), "w", newline="", encoding="utf-8") as f:
        w = csv.writer(f)
        w.writerow(["k", "instancias", "alejamiento_promedio_pct", "alejamiento_maximo_pct"])
        w.writerows(resumen)
    print("Guardado en", args.salida)


if __name__ == "__main__":
    main()