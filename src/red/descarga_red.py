import time, datetime
import osmnx as ox

print("OSMnx:", ox.__version__)
print("Fecha de descarga:", datetime.date.today())

t0 = time.perf_counter()
G = ox.graph_from_place("Quindío, Colombia", network_type="drive")
t1 = time.perf_counter()

print("V =", G.number_of_nodes(), " E =", G.number_of_edges())
print("Descarga (s):", round(t1 - t0, 1))

ox.save_graphml(G, "data/raw/quindio_original.graphml")