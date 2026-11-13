"""R4. Pico de memoria de Held-Karp con la matriz real (tracemalloc).

Mide k = 8, 10 y 12, con los mismos lugares que usa medicion.py (partida CAB01, mezcla con
semilla fija). tracemalloc ralentiza el programa: estas corridas son solo para memoria,
nunca para tiempos.

Uso (desde la raíz del proyecto):
    python -m src.ruta_optima.memoria_hk
"""
import random
import tracemalloc

from src.ruta_optima.datos import leer_matriz
from src.ruta_optima.medicion import SEMILLA
from src.ruta_optima.tsp import held_karp


def main():
    ids, T = leer_matriz("data/processed/matriz_tiempos.csv")
    inicio = ids.index("CAB01")
    otros = [i for i in range(len(ids)) if i != inicio]
    random.Random(SEMILLA).shuffle(otros)

    for k in (8, 10, 12):
        tracemalloc.start()
        held_karp(T, inicio, otros[:k])
        _, pico = tracemalloc.get_traced_memory()
        tracemalloc.stop()
        print(f"k={k}: pico de memoria {pico / 1024 / 1024:.2f} MB")


if __name__ == "__main__":
    main()

