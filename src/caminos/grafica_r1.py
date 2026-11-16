import csv
import statistics
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

with open("resultados/r1_componente.csv", encoding="utf-8", newline="") as f:
    filas = list(csv.DictReader(f))

# largest_component trabaja sobre el grafo ANTES de quedarse con la componente: x = V_antes + E_antes
x = [int(r["V_antes"]) + int(r["E_antes"]) for r in filas]
y = [float(r["mediana_ms"]) for r in filas]
nombres = [r["red"] for r in filas]

fig, ax = plt.subplots(figsize=(8, 5))
ax.plot(x, y, marker="o", linestyle="-")
for xi, yi, nom in zip(x, y, nombres):
    ax.annotate(nom, (xi, yi), textcoords="offset points", xytext=(6, -12))
ax.set_xlabel("Tamaño de la red (V + E, antes de filtrar)")
ax.set_ylabel("Tiempo de largest_component, mediana de 5 repeticiones (ms)")
ax.set_title("R1: tiempo de la componente fuertemente conexa frente a V + E")
ax.grid(True, alpha=0.3)
fig.tight_layout()
fig.savefig("resultados/r1_grafica.png", dpi=200)

por_mil = [t / (xi / 1000) for xi, t in zip(x, y)]
print("ms por cada 1000 (V+E):", [round(p, 2) for p in por_mil])
print(f"mínimo {min(por_mil):.2f} | mediana {statistics.median(por_mil):.2f} | máximo {max(por_mil):.2f}")
print("Gráfica guardada en resultados/r1_grafica.png")