import csv
import itertools
import osmnx as ox

# Los 12 municipios, tal como aparecen en el catálogo
with open("data/catalogo/catalogo_lugares.csv", encoding="utf-8", newline="") as f:
    municipios = sorted({r["municipio"] for r in csv.DictReader(f)})
print(len(municipios), "municipios:", municipios)

# Polígonos administrativos desde OpenStreetMap (Nominatim)
gdf = ox.geocode_to_gdf([f"{m}, Quindío, Colombia" for m in municipios])
gdf["municipio"] = municipios
gdf = gdf.set_index("municipio").to_crs(32618)      # metros (UTM 18N)

print("\nÁrea de cada polígono (km²), para comprobar que son los correctos:")
print((gdf.area / 1e6).round(1).to_string())

# Vecinos = polígonos que se tocan (con 50 m de tolerancia a cada lado por huecos en la frontera)
geom = gdf.geometry.buffer(50)
vecinos = [(a, b) for a, b in itertools.combinations(municipios, 2)
           if geom[a].intersects(geom[b])]

print("\nVecinos de cada municipio:")
for m in municipios:
    ve = sorted({b if a == m else a for a, b in vecinos if m in (a, b)})
    print(f"  {m}: {', '.join(ve)}")

with open("resultados/r2_municipios_vecinos.csv", "w", encoding="utf-8", newline="") as f:
    w = csv.writer(f)
    w.writerow(["municipio_a", "municipio_b"])
    w.writerows(vecinos)
print(f"\n{len(vecinos)} pares de municipios vecinos guardados.")