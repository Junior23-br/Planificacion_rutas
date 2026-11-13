import csv, os, platform, statistics, sys, time
import networkx as nx
import osmnx as ox

# Opcional: usar otro servidor Overpass si overpass-api.de sigue saturado
# ox.settings.overpass_url = "https://overpass.kumi.systems/api"

# Centro de los radios: CAB01 (Armenia, Plaza de Bolívar) del catálogo
with open("data/catalogo/catalogo_lugares.csv", encoding="utf-8", newline="") as f:
    fila = next(r for r in csv.DictReader(f) if r["id"] == "CAB01")
centro = (float(fila["latitud"]), float(fila["longitud"]))   # (lat, lon)


def descargar(km, intentos=5):
    espera = 30
    for i in range(intentos):
        try:
            return ox.graph_from_point(centro, dist=km * 1000, network_type="drive")
        except Exception as e:
            print(f"[{km} km] intento {i + 1} falló: {str(e)[:90]}")
            if i == intentos - 1:
                raise
            time.sleep(espera)
            espera *= 2


def obtener(km):
    ruta = f"data/raw/red_{km}km.graphml"
    if os.path.exists(ruta):
        return ox.load_graphml(ruta)
    G = descargar(km)
    ox.save_graphml(G, ruta)
    return G


# La descarga NO se mide; solo se mide largest_component
redes = {f"{km} km": obtener(km) for km in (2, 5, 10, 20)}
redes["Departamento"] = ox.load_graphml("data/raw/quindio_original.graphml")


def medir(R):
    tiempos_ms = []
    for _ in range(5):
        t0 = time.perf_counter()
        C = ox.truncate.largest_component(R, strongly=True)
        tiempos_ms.append((time.perf_counter() - t0) * 1000)
        if tiempos_ms[-1] > 60_000:      # más de 1 minuto: una sola medición
            break
    return C, tiempos_ms


print("Python", sys.version.split()[0], "| OSMnx", ox.__version__,
      "|", platform.platform(), "|", platform.processor())

filas = []
for nombre, R in redes.items():
    C, ts = medir(R)
    f = dict(red=nombre,
             V_antes=R.number_of_nodes(), E_antes=R.number_of_edges(),
             V_despues=C.number_of_nodes(), E_despues=C.number_of_edges(),
             repeticiones=len(ts), mediana_ms=round(statistics.median(ts), 3),
             fuertemente_conexa=nx.is_strongly_connected(C))
    filas.append(f)
    print(f)

with open("resultados/r1_componente.csv", "w", encoding="utf-8", newline="") as f:
    w = csv.DictWriter(f, fieldnames=filas[0].keys())
    w.writeheader()
    w.writerows(filas)