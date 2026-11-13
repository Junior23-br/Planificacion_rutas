import os
import networkx as nx
import osmnx as ox

G = ox.load_graphml("data/processed/quindio_con_pesos.graphml")
C = ox.truncate.largest_component(G, strongly=True)
ox.save_graphml(C, "data/processed/componente.graphml")

# Verificación: recargar lo guardado y comprobarlo
R = ox.load_graphml("data/processed/componente.graphml")
print(f"Antes:   V={G.number_of_nodes()} E={G.number_of_edges()}")
print(f"Guardado: V={R.number_of_nodes()} E={R.number_of_edges()}")
print("Fuertemente conexa:", nx.is_strongly_connected(R))
print("Aristas sin length o travel_time:",
      sum(1 for _, _, d in R.edges(data=True) if "length" not in d or "travel_time" not in d))
print("Tamaño (MB):", round(os.path.getsize("data/processed/componente.graphml") / 1024**2, 1))