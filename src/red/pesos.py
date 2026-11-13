import osmnx as ox

G = ox.load_graphml("data/raw/quindio_original.graphml")

# Cuántas aristas traen velocidad máxima en OSM (antes de imputar)
con_maxspeed = sum(1 for _, _, d in G.edges(data=True) if "maxspeed" in d)
print(f"Aristas con maxspeed en OSM: {con_maxspeed} de {G.number_of_edges()}")

# Velocidad (km/h) y tiempo de viaje (s) por arista
G = ox.routing.add_edge_speeds(G)
G = ox.routing.add_edge_travel_times(G)

# Resumen de los tres pesos
import statistics as st
L = [d["length"] for _, _, d in G.edges(data=True)]
S = [d["speed_kph"] for _, _, d in G.edges(data=True)]
T = [d["travel_time"] for _, _, d in G.edges(data=True)]
for nombre, v in (("length (m)", L), ("speed_kph", S), ("travel_time (s)", T)):
    print(f"{nombre:16} min={min(v):.2f}  media={st.mean(v):.2f}  max={max(v):.2f}")
print("Aristas con peso <= 0:", sum(1 for x in L + T if x <= 0))

# Comprobación a mano en una arista
u, v, d = next(iter(G.edges(data=True)))
esperado = d["length"] / (d["speed_kph"] * 1000 / 3600)
print("Arista de prueba:", d["length"], "m,", d["speed_kph"], "km/h")
print("travel_time guardado:", d["travel_time"], " calculado a mano:", round(esperado, 2))

ox.save_graphml(G, "data/processed/quindio_con_pesos.graphml")