import csv
import statistics
import matplotlib.pyplot as plt

with open("resultados/r2_mediciones.csv", encoding="utf-8", newline="") as f:
    filas = list(csv.DictReader(f))

cola = [(int(r["explorados_cola"]), float(r["cola_mediana_ms"]), r["tipo"]) for r in filas]
lineal = [(int(r["explorados_lineal"]), float(r["lineal_mediana_ms"])) for r in filas if r["lineal_mediana_ms"]]

fig, ax = plt.subplots(figsize=(8, 5))
ax.scatter([c[0] for c in cola if c[2] == "cercano"], [c[1] for c in cola if c[2] == "cercano"],
           marker="o", label="Con cola de prioridad (pares cercanos)")
ax.scatter([c[0] for c in cola if c[2] == "otro"], [c[1] for c in cola if c[2] == "otro"],
           marker="^", label="Con cola de prioridad (otros pares)")
ax.scatter([l[0] for l in lineal], [l[1] for l in lineal],
           marker="s", label="Búsqueda lineal (pares cercanos)")
ax.set_yscale("log")
ax.set_xlabel("Nodos explorados")
ax.set_ylabel("Tiempo de ejecución, mediana de 5 repeticiones (ms, escala log)")
ax.set_title("Dijkstra: tiempo frente a nodos explorados")
ax.grid(True, which="both", alpha=0.3)
ax.legend()
fig.tight_layout()
fig.savefig("resultados/r2_grafica.png", dpi=200)

# Tiempo por nodo explorado (apoya la discusión teórica)
pn_cola = [t / n for n, t, _ in cola]
pn_lin = [t / n for n, t in lineal]
print(f"ms por nodo explorado, cola:   mediana {statistics.median(pn_cola):.5f}")
print(f"ms por nodo explorado, lineal: mediana {statistics.median(pn_lin):.5f}")
print("Guardada: resultados/r2_grafica.png")