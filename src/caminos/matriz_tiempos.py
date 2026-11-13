import csv
import random
import time
import networkx as nx
import osmnx as ox
from grafo import cargar_grafo, cargar_lugares
from dijkstra import dijkstra_cola

RUTA = "data/processed/matriz_tiempos.csv"

ids, indice, adj, info = cargar_grafo()
lugares = cargar_lugares(indice)
n = len(lugares)
cods = [l["id"] for l in lugares]          # orden del catálogo

# Una corrida completa (sin destino) desde cada lugar, con la versión de cola de prioridad
t0 = time.perf_counter()
M = []
for l in lugares:
    dist, _, _ = dijkstra_cola(adj, l["idx"])
    M.append([dist[m["idx"]] for m in lugares])
print(f"Matriz {n}x{n} calculada en {time.perf_counter() - t0:.1f} s (medición informal)")

with open(RUTA, "w", encoding="utf-8", newline="") as f:
    w = csv.writer(f)
    w.writerow(["id"] + cods)
    for cod, fila in zip(cods, M):
        w.writerow([cod] + [f"{x:.3f}" for x in fila])

# ---- Verificación sobre el archivo guardado (lo que leerá Jefferson) ----
with open(RUTA, encoding="utf-8", newline="") as f:
    filas = list(csv.reader(f))
assert len(filas) == n + 1 and filas[0][1:] == cods
assert [r[0] for r in filas[1:]] == cods
A = [[float(x) for x in r[1:]] for r in filas[1:]]
assert all(len(r) == n for r in A)
assert all(A[i][i] == 0.0 for i in range(n))
assert all(0 < A[i][j] < 1e9 for i in range(n) for j in range(n) if i != j)
print("1. Formato 40x40, ids en orden del catálogo, diagonal 0, sin vacíos ni infinitos: OK")

asim = sum(1 for i in range(n) for j in range(i + 1, n) if abs(A[i][j] - A[j][i]) > 0.001)
print(f"2. Pares i<j con tiempo de ida distinto al de vuelta: {asim} de {n * (n - 1) // 2}")

viol = sum(1 for i in range(n) for j in range(n) for k in range(n)
           if A[i][k] > A[i][j] + A[j][k] + 0.01)
print("3. Violaciones de la desigualdad triangular:", viol)

G = ox.load_graphml("data/processed/componente.graphml")
random.seed(42)
for _ in range(8):
    i, j = random.sample(range(n), 2)
    esperado = nx.dijkstra_path_length(G, ids[lugares[i]["idx"]], ids[lugares[j]["idx"]],
                                       weight="travel_time")
    assert abs(A[i][j] - esperado) < 0.01, (cods[i], cods[j], A[i][j], esperado)
print("4. 8 celdas al azar iguales a NetworkX: OK")

fuera = [A[i][j] / 60 for i in range(n) for j in range(n) if i != j]
print(f"Tiempos entre lugares: mínimo {min(fuera):.1f} min | máximo {max(fuera):.1f} min")