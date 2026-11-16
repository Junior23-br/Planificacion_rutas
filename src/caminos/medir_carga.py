# Mide cuánto tarda cargar_grafo(): 5 repeticiones, mediana. Correr desde la raíz del repo:
#   python src/caminos/medir_carga.py
import gc
import statistics
import time
from grafo import cargar_grafo

cargar_grafo()            # calentamiento: no se cuenta
gc.disable()
tiempos = []
for _ in range(5):
    t0 = time.perf_counter()
    cargar_grafo()
    tiempos.append((time.perf_counter() - t0) * 1000)
gc.enable()
print("repeticiones (ms):", [round(t, 1) for t in tiempos])
print(f"mediana: {statistics.median(tiempos):.1f} ms")