import csv
import osmnx as ox

with open("resultados/r2_municipios_vecinos.csv", encoding="utf-8", newline="") as f:
    pares = [(r["municipio_a"], r["municipio_b"]) for r in csv.DictReader(f)]
municipios = sorted({m for p in pares for m in p})

gdf = ox.geocode_to_gdf([f"{m}, Quindío, Colombia" for m in municipios])
gdf["municipio"] = municipios
g = gdf.set_index("municipio").to_crs(32618).geometry

filas = []
for a, b in pares:
    hueco = g[a].distance(g[b])                                   # m entre los polígonos
    frontera = g[a].boundary.intersection(g[b].buffer(100)).length / 1000   # km aprox.
    filas.append((frontera, hueco, a, b))

print("Frontera compartida aproximada (km) y distancia entre polígonos (m), de menor a mayor:")
for frontera, hueco, a, b in sorted(filas):
    print(f"  {a} - {b}: {frontera:.1f} km | hueco {hueco:.0f} m")