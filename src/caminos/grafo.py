import csv
import osmnx as ox


def cargar_grafo(ruta="data/processed/componente.graphml"):
    """Devuelve (ids, indice, adj, info).
    ids[i]    -> id de OSM del nodo i
    indice[n] -> posición del nodo con id n
    adj[i]    -> lista de (j, tiempo_s) con los vecinos de salida de i
    """
    G = ox.load_graphml(ruta)
    ids = list(G.nodes())
    indice = {n: i for i, n in enumerate(ids)}

    mejor = [dict() for _ in ids]            # mejor[i][j] = menor tiempo de i a j
    autolazos = 0
    for u, v, d in G.edges(data=True):
        if u == v:
            autolazos += 1                   # un autolazo nunca mejora un camino
            continue
        i, j, t = indice[u], indice[v], d["travel_time"]
        if j not in mejor[i] or t < mejor[i][j]:
            mejor[i][j] = t
    adj = [list(m.items()) for m in mejor]

    E_final = sum(len(a) for a in adj)
    info = dict(V=len(ids), E_original=G.number_of_edges(), autolazos=autolazos,
                paralelas_descartadas=G.number_of_edges() - autolazos - E_final,
                E_final=E_final)
    return ids, indice, adj, info


def cargar_lugares(indice, ruta_cat="data/catalogo/catalogo_lugares.csv",
                   ruta_aso="data/processed/asociacion_lugares.csv"):
    """Lugares en el orden del catálogo: lista de dict(id, nombre, municipio, idx)."""
    with open(ruta_aso, encoding="utf-8", newline="") as f:
        nodo_de = {r["id"]: int(r["nodo"]) for r in csv.DictReader(f)}
    lugares = []
    with open(ruta_cat, encoding="utf-8", newline="") as f:
        for r in csv.DictReader(f):
            lugares.append(dict(id=r["id"], nombre=r["nombre"], municipio=r["municipio"],
                                idx=indice[nodo_de[r["id"]]]))
    return lugares


if __name__ == "__main__":
    ids, indice, adj, info = cargar_grafo()
    print(info)

    G = ox.load_graphml("data/processed/componente.graphml")
    # 1. Mismos vecinos que NetworkX (sin autolazos)
    distintos = 0
    for n in G.nodes():
        esperados = {indice[m] for m in G.successors(n) if m != n}
        if esperados != {j for j, _ in adj[indice[n]]}:
            distintos += 1
    print("Nodos con vecinos distintos a NetworkX:", distintos)

    # 2. Cada tiempo es el mínimo entre las aristas paralelas
    malos = 0
    for n in G.nodes():
        for j, t in adj[indice[n]]:
            m = min(d["travel_time"] for d in G[n][ids[j]].values())
            if abs(m - t) > 1e-9:
                malos += 1
    print("Aristas con tiempo distinto al mínimo paralelo:", malos)
    print("Tiempo mínimo en adj:", min(t for a in adj for _, t in a))

    lugares = cargar_lugares(indice)
    print("Lugares:", len(lugares), "| nodos distintos:", len({l["idx"] for l in lugares}))