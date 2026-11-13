import random
import time
from grafo import cargar_grafo, cargar_lugares
from dijkstra import dijkstra_cola, dijkstra_lineal, reconstruir_ruta

# 1. Caso pequeño resuelto a mano (el mismo de la versión con cola)
adj_p = [
    [(1, 4.0), (2, 1.0)],   # 0
    [(3, 1.0)],             # 1
    [(1, 2.0), (3, 5.0)],   # 2
    [(4, 3.0)],             # 3
    [],                     # 4
    [(0, 1.0)],             # 5 (a él no llega nadie)
]
dist, pred, _ = dijkstra_lineal(adj_p, 0)
assert dist[:5] == [0.0, 3.0, 1.0, 4.0, 7.0], dist
assert dist[5] == float("inf")
assert reconstruir_ruta(pred, 0, 4) == [0, 2, 1, 3, 4]
print("1. Caso pequeño a mano: OK")

ids, indice, adj, info = cargar_grafo()
lugares = cargar_lugares(indice)
por_id = {l["id"]: l["idx"] for l in lugares}
random.seed(7)

# 2. Sin destino: las distancias a todos los nodos coinciden con la versión con cola
o = por_id["CAB01"]
t0 = time.perf_counter()
d_lin, _, _ = dijkstra_lineal(adj, o)
seg = time.perf_counter() - t0
d_col, _, _ = dijkstra_cola(adj, o)
assert max(abs(a - b) for a, b in zip(d_lin, d_col)) < 1e-9
print(f"2. Todas las distancias desde CAB01 iguales en las dos versiones: OK "
      f"(lineal completa tardó {seg:.1f} s, medición informal)")

# 3. 10 pares de lugares: mismo tiempo en las dos versiones
pares = [("CAB01", "CAB03"), ("CAB01", "CAB12"), ("CAB07", "CAB06")]
ids_l = [l["id"] for l in lugares]
while len(pares) < 10:
    a, b = random.sample(ids_l, 2)
    if (a, b) not in pares:
        pares.append((a, b))

print("3. 10 pares de lugares:")
for a, b in pares:
    o, d = por_id[a], por_id[b]
    t0 = time.perf_counter()
    dl, pl, el = dijkstra_lineal(adj, o, d)
    seg = time.perf_counter() - t0
    dc, pc, ec = dijkstra_cola(adj, o, d)
    assert abs(dl[d] - dc[d]) < 1e-9, (a, b, dl[d], dc[d])
    ruta = reconstruir_ruta(pl, o, d)
    assert ruta[0] == o and ruta[-1] == d
    print(f"   {a}->{b}: {dl[d] / 60:.1f} min | explorados lineal={el} cola={ec} "
          f"| lineal tardó {seg:.1f} s (informal)")
print("   Todos los pares coinciden: OK")