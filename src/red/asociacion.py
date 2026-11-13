import csv, math
import osmnx as ox
from pyproj import Transformer

G = ox.load_graphml("data/processed/quindio_con_pesos.graphml")
C = ox.truncate.largest_component(G, strongly=True)
print(f"Antes: V={G.number_of_nodes()} E={G.number_of_edges()} | "
      f"Componente: V={C.number_of_nodes()} E={C.number_of_edges()}")

# lon/lat (EPSG:4326) -> metros UTM 18N (EPSG:32618)
tr = Transformer.from_crs("EPSG:4326", "EPSG:32618", always_xy=True)
nodos = {n: tr.transform(d["x"], d["y"]) for n, d in C.nodes(data=True)}

filas = []
with open("data/catalogo/catalogo_lugares.csv", encoding="utf-8", newline="") as f:
    for r in csv.DictReader(f):
        x, y = tr.transform(float(r["longitud"]), float(r["latitud"]))
        nodo, dist = min(((n, math.hypot(x - nx, y - ny)) for n, (nx, ny) in nodos.items()),
                         key=lambda t: t[1])
        filas.append(dict(id=r["id"], nombre=r["nombre"], categoria=r["categoria"],
                          nodo=nodo, distancia_m=round(dist, 1), mayor_500m=dist > 500))

with open("data/processed/asociacion_lugares.csv", "w", encoding="utf-8", newline="") as f:
    w = csv.DictWriter(f, fieldnames=filas[0].keys())
    w.writeheader()
    w.writerows(filas)

d = [x["distancia_m"] for x in filas]
print(f"Lugares: {len(filas)} | distancia media {sum(d)/len(d):.1f} m | máxima {max(d)} m")
print("Más lejanos:")
for x in sorted(filas, key=lambda x: -x["distancia_m"])[:8]:
    print(f"  {x['id']} {x['nombre']}: {x['distancia_m']} m")
print("Lugares a más de 500 m:", [x["id"] for x in filas if x["mayor_500m"]])