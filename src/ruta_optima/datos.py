"""Lectura de la matriz de tiempos de R2 (data/processed/matriz_tiempos.csv)."""
import csv


def leer_matriz(ruta):
    """CSV cuadrado: primera fila y primera columna con ids, tiempos en segundos.
    Devuelve (ids, T) con T[i][j] = tiempo de ir de ids[i] a ids[j]."""
    with open(ruta, encoding="utf-8", newline="") as f:
        filas = list(csv.reader(f))
    ids = filas[0][1:]
    T = [[float(x) for x in fila[1:]] for fila in filas[1:]]
    assert [fila[0] for fila in filas[1:]] == ids, "los ids de filas y columnas son distintos"
    assert all(len(fila) == len(ids) for fila in T), "la matriz no es cuadrada"
    assert all(T[i][i] == 0 for i in range(len(ids))), "la diagonal debe valer 0"
    return ids, T