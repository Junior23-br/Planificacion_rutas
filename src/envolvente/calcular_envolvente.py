import csv

import numpy as np
import osmnx as ox
from pyproj import Transformer
from scipy.spatial import ConvexHull

from src.envolvente.envolvente import envolvente_convexa

RUTA_GRAFO = "data/processed/componente.graphml"
A_UTM = Transformer.from_crs("EPSG:4326", "EPSG:32618", always_xy=True)
A_LONLAT = Transformer.from_crs("EPSG:32618", "EPSG:4326", always_xy=True)


def puntos_de_la_red(ruta=RUTA_GRAFO):
    """Nodos de la componente en UTM 18N (metros), redondeados al entero y sin repetidos."""
    G = ox.load_graphml(ruta)
    lons = [d["x"] for _, d in G.nodes(data=True)]
    lats = [d["y"] for _, d in G.nodes(data=True)]
    xs, ys = A_UTM.transform(lons, lats)
    return sorted({(int(round(x)), int(round(y))) for x, y in zip(xs, ys)})


if __name__ == "__main__":
    puntos = puntos_de_la_red()
    vertices = envolvente_convexa(puntos)

    # Verificación contra SciPy: deben dar los mismos vértices
    h = ConvexHull(np.array(puntos, dtype=float))
    esperado = {puntos[i] for i in h.vertices}
    assert set(vertices) == esperado, "la envolvente propia no coincide con SciPy"

    print(f"Puntos distintos: {len(puntos)} | vértices de la envolvente: {len(vertices)}")
    print("Coincide con scipy.spatial.ConvexHull: OK")

    with open("resultados/r3_envolvente.csv", "w", encoding="utf-8", newline="") as f:
        w = csv.writer(f)
        w.writerow(["x", "y", "lon", "lat"])
        for x, y in vertices:
            lon, lat = A_LONLAT.transform(x, y)
            w.writerow([x, y, round(lon, 6), round(lat, 6)])
    print("Guardado: resultados/r3_envolvente.csv")
