import csv, random
from collections import Counter
import networkx as nx
import osmnx as ox

G = ox.load_graphml("data/processed/componente.graphml")
V, E = G.number_of_nodes(), G.number_of_edges()

# 1. Conteos y estructura
print("V =", V, "| E =", E)
print("Suma de grados de salida == E:", sum(d for _, d in G.out_degree()) == E)
print("Suma de grados de entrada == E:", sum(d for _, d in G.in_degree()) == E)
print("Fuertemente conexa:", nx.is_strongly_connected(G))
print("Autolazos:", nx.number_of_selfloops(G))
pares = Counter((u, v) for u, v, _ in G.edges(keys=True))
print("Pares (u,v) con aristas paralelas:", sum(1 for c in pares.values() if c > 1))

# 2. Pesos válidos (Dijkstra exige pesos no negativos)
L = [d["length"] for _, _, d in G.edges(data=True)]
T = [d["travel_time"] for _, _, d in G.edges(data=True)]
print(f"length min={min(L):.2f} m | travel_time min={min(T):.3f} s | ninguno <= 0:",
      min(L) > 0 and min(T) > 0)

# 3. Un tramo para medir a mano (semilla fija = 42)
random.seed(42)
cand = [(u, v, d) for u, v, d in G.edges(data=True) if 100 <= d["length"] <= 300]
u, v, d = random.choice(cand)
y1, x1, y2, x2 = G.nodes[u]["y"], G.nodes[u]["x"], G.nodes[v]["y"], G.nodes[v]["x"]
recta = ox.distance.great_circle(y1, x1, y2, x2)
esperado = d["length"] / (d["speed_kph"] * 1000 / 3600)
print(f"\nTramo {u} -> {v}")
print(f"  length (modelo): {d['length']:.1f} m | distancia en línea recta: {recta:.1f} m")
print(f"  speed_kph: {d['speed_kph']:.1f} | travel_time guardado: {d['travel_time']:.2f} s | "
      f"a mano: {esperado:.2f} s")
print(f"  Mapa: https://www.google.com/maps/dir/{y1},{x1}/{y2},{x2}")

# 4. Asociaciones: distancia UTM del CSV frente a distancia de gran círculo
with open("data/catalogo/catalogo_lugares.csv", encoding="utf-8", newline="") as f:
    cat = {r["id"]: r for r in csv.DictReader(f)}
dif = []
with open("data/processed/asociacion_lugares.csv", encoding="utf-8", newline="") as f:
    for r in csv.DictReader(f):
        lug, n = cat[r["id"]], G.nodes[int(r["nodo"])]
        dh = ox.distance.great_circle(float(lug["latitud"]), float(lug["longitud"]), n["y"], n["x"])
        dif.append(abs(dh - float(r["distancia_m"])))
print(f"\nAsociaciones: {len(dif)} lugares | diferencia máxima UTM vs gran círculo = {max(dif):.2f} m")