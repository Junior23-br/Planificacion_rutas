import csv
import itertools
import platform
import random
import statistics
import sys
import time
import networkx as nx
import osmnx as ox
from grafo import cargar_grafo, cargar_lugares
from dijkstra import dijkstra_cola, dijkstra_lineal, reconstruir_ruta
import gc
import ctypes

REPS = 5

try:  # prioridad alta y un solo núcleo de rendimiento (Windows)
    kernel32 = ctypes.windll.kernel32
    proceso = kernel32.GetCurrentProcess()
    kernel32.SetPriorityClass(proceso, 0x00000080)
    kernel32.SetProcessAffinityMask(proceso, 0x4)   # solo el procesador lógico 2
except Exception:
    pass

SEMILLA = 2026
CAMPOS = ["origen", "destino", "municipio_origen", "municipio_destino", "tipo",
          "tiempo_viaje_s", "nodos_ruta",
          "explorados_cola", "cola_mediana_ms", "cola_repeticiones", "cola_tiempos_ms",
          "explorados_lineal", "lineal_mediana_ms", "lineal_repeticiones", "lineal_tiempos_ms",
          "cociente_lineal_cola"]

ids, indice, adj, info = cargar_grafo()
lugares = cargar_lugares(indice)


def consulta_cola(o, d):
    dist, pred, ex = dijkstra_cola(adj, o, d)
    return dist[d], reconstruir_ruta(pred, o, d), ex


def consulta_lineal(o, d):
    dist, pred, ex = dijkstra_lineal(adj, o, d)
    return dist[d], reconstruir_ruta(pred, o, d), ex


def medir(funcion, *args):
    """5 repeticiones (1 sola si una pasa de 1 minuto). Tiempos en milisegundos."""
    tiempos = []
    gc.collect()
    gc.disable()
    try:
        for _ in range(REPS):
            t0 = time.perf_counter_ns()
            resultado = funcion(*args)
            dt = (time.perf_counter_ns() - t0) / 1e6
            tiempos.append(dt)
            if dt > 60_000:
                break
    finally:
        gc.enable()
    return resultado, tiempos


# ---- 1. Selección de pares (semilla fija) ----
rng = random.Random(SEMILLA)
with open("resultados/r2_municipios_vecinos.csv", encoding="utf-8", newline="") as f:
    vecinos = {frozenset((r["municipio_a"], r["municipio_b"])) for r in csv.DictReader(f)}


def cercano(a, b):
    return a["municipio"] == b["municipio"] or frozenset((a["municipio"], b["municipio"])) in vecinos


todos = list(itertools.combinations(range(len(lugares)), 2))
cerca = [p for p in todos if cercano(lugares[p[0]], lugares[p[1]])]
lejos = [p for p in todos if not cercano(lugares[p[0]], lugares[p[1]])]
print(f"Pares no ordenados: {len(todos)} | cercanos: {len(cerca)} | no cercanos: {len(lejos)}")


def con_sentido(pares):
    return [(i, j) if rng.random() < 0.5 else (j, i) for i, j in pares]


sel_cerca = con_sentido(rng.sample(cerca, 10))
sel_otros = con_sentido(rng.sample(lejos, 10))
pares = [("cercano", i, j) for i, j in sel_cerca] + [("otro", i, j) for i, j in sel_otros]

# ---- 2. Verificación antes de medir ----
G = ox.load_graphml("data/processed/componente.graphml")
for tipo, i, j in pares:
    o, d = lugares[i]["idx"], lugares[j]["idx"]
    t, ruta, _ = consulta_cola(o, d)
    ref = nx.dijkstra_path_length(G, ids[o], ids[d], weight="travel_time")
    assert abs(t - ref) < 1e-6 and ruta[0] == o and ruta[-1] == d
    if tipo == "cercano":
        tl, _, _ = consulta_lineal(o, d)
        assert abs(t - tl) < 1e-9
print("Verificación previa (NetworkX y cola = lineal): OK")

# ---- 3. Mediciones ----
print("Python", sys.version.split()[0], "|", platform.platform(), "|", platform.processor())
filas = []
# Calentamiento (no se mide): evita el efecto de arranque en frío en el primer par
for _ in range(3):
    for tipo, i, j in pares[:3]:
        consulta_cola(lugares[i]["idx"], lugares[j]["idx"])
        consulta_lineal(lugares[i]["idx"], lugares[j]["idx"])
for tipo, i, j in pares:
    a, b = lugares[i], lugares[j]
    o, d = a["idx"], b["idx"]
    fila = dict.fromkeys(CAMPOS, "")
    (t, ruta, ex_c), tc = medir(consulta_cola, o, d)
    fila.update(origen=a["id"], destino=b["id"], municipio_origen=a["municipio"],
                municipio_destino=b["municipio"], tipo=tipo, tiempo_viaje_s=round(t, 3),
                nodos_ruta=len(ruta), explorados_cola=ex_c,
                cola_mediana_ms=round(statistics.median(tc), 3), cola_repeticiones=len(tc),
                cola_tiempos_ms=" ".join(f"{x:.3f}" for x in tc))
    linea = (f"{tipo:8} {a['id']}->{b['id']}: {t / 60:5.1f} min | explorados {ex_c:5d} "
             f"| cola {fila['cola_mediana_ms']:8.3f} ms")
    if tipo == "cercano":
        (_, _, ex_l), tl = medir(consulta_lineal, o, d)
        fila.update(explorados_lineal=ex_l, lineal_mediana_ms=round(statistics.median(tl), 3),
                    lineal_repeticiones=len(tl),
                    lineal_tiempos_ms=" ".join(f"{x:.3f}" for x in tl),
                    cociente_lineal_cola=round(statistics.median(tl) / statistics.median(tc), 2))
        linea += f" | lineal {fila['lineal_mediana_ms']:9.3f} ms | cociente {fila['cociente_lineal_cola']}"
    print(linea)
    filas.append(fila)

with open("resultados/r2_mediciones.csv", "w", encoding="utf-8", newline="") as f:
    w = csv.DictWriter(f, fieldnames=CAMPOS)
    w.writeheader()
    w.writerows(filas)

# ---- 4. Cociente lineal / cola en los 10 pares medidos con ambas ----
q = [fl["cociente_lineal_cola"] for fl in filas if fl["cociente_lineal_cola"] != ""]
est = [("mediana", statistics.median(q)), ("minimo", min(q)), ("maximo", max(q))]
print("Cociente tiempo lineal / tiempo con cola:", {k: round(v, 2) for k, v in est})
with open("resultados/r2_cociente.csv", "w", encoding="utf-8", newline="") as f:
    w = csv.writer(f)
    w.writerow(["estadistico", "valor"])
    w.writerows([(k, round(v, 2)) for k, v in est])