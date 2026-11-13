import random
import networkx as nx
import osmnx as ox
from grafo import cargar_grafo, cargar_lugares
from dijkstra import dijkstra_cola, ruta_minima

# 1. Caso pequeño resuelto a mano
adj_p = [
    [(1, 4.0), (2, 1.0)],   # 0
    [(3, 1.0)],             # 1
    [(1, 2.0), (3, 5.0)],   # 2
    [(4, 3.0)],             # 3
    [],                     # 4
    [(0, 1.0)],             # 5 (a él no llega nadie)
]
dist, pred, _ = dijkstra_cola(adj_p, 0)
assert dist[:5] == [0.0, 3.0, 1.0, 4.0, 7.0], dist
assert dist[5] == float("inf")
t, ruta, _ = ruta_minima(adj_p, 0, 4)
assert t == 7.0 and ruta == [0, 2, 1, 3, 4], (t, ruta)
t, ruta, _ = ruta_minima(adj_p, 0, 5)
assert t == float("inf") and ruta == []
print("1. Caso pequeño a mano: OK")

ids, indice, adj, info = cargar_grafo()
G = ox.load_graphml("data/processed/componente.graphml")
lugares = cargar_lugares(indice)
random.seed(42)

# 2. Contra NetworkX: todas las distancias desde 3 orígenes
origenes = [lugares[0]["idx"]] + random.sample(range(len(ids)), 2)
for o in origenes:
    dist, _, _ = dijkstra_cola(adj, o)
    esperado = nx.single_source_dijkstra_path_length(G, ids[o], weight="travel_time")
    peor = max(abs(dist[indice[n]] - t) for n, t in esperado.items())
    assert len(esperado) == len(ids) and peor < 1e-6, (len(esperado), peor)
print("2. Contra NetworkX (todas las distancias desde 3 orígenes): OK")

# 3. Pares aleatorios: tiempo y ruta
peso = [dict(a) for a in adj]
for _ in range(30):
    o, d = random.sample(range(len(ids)), 2)
    t, ruta, expl = ruta_minima(adj, o, d)
    esperado = nx.dijkstra_path_length(G, ids[o], ids[d], weight="travel_time")
    assert abs(t - esperado) < 1e-6
    assert ruta[0] == o and ruta[-1] == d
    assert abs(sum(peso[a][b] for a, b in zip(ruta, ruta[1:])) - t) < 1e-6
    assert expl <= len(ids)
print("3. 30 pares aleatorios (tiempo y ruta): OK")

# 4. Ejemplos para comprobar a ojo
por_id = {l["id"]: l["idx"] for l in lugares}
for a, b in (("CAB01", "CAB03"), ("CAB01", "CAB12"), ("CAB07", "CAB06")):
    t, ruta, expl = ruta_minima(adj, por_id[a], por_id[b])
    print(f"   {a} -> {b}: {t / 60:.1f} min, {len(ruta)} nodos en la ruta, {expl} nodos explorados")