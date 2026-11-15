import csv

import matplotlib.pyplot as plt

with open("resultados/r3_tiempos.csv", encoding="utf-8", newline="") as f:
    filas = list(csv.DictReader(f))

# Tabla (Markdown) generada desde el CSV
lineas = ["| Conjunto | Puntos | Vértices | Tu versión (ms) | SciPy (ms) | Cociente |",
          "|---|---|---|---|---|---|"]
for r in filas:
    lineas.append(f"| {r['conjunto']} | {r['n_puntos']} | {r['vertices']} | "
                  f"{float(r['propio_mediana_ms']):.3f} | {float(r['scipy_mediana_ms']):.3f} | "
                  f"{float(r['cociente_propio_scipy']):.1f} |")
with open("resultados/r3_tabla.md", "w", encoding="utf-8") as f:
    f.write("\n".join(lineas) + "\n")
print("\n".join(lineas))

# Gráfica: tiempo frente a número de puntos (solo los conjuntos al azar), escala log-log
azar = [r for r in filas if r["conjunto"].startswith("azar")]
n = [int(r["n_puntos"]) for r in azar]
fig, ax = plt.subplots(figsize=(7, 4.5))
ax.plot(n, [float(r["propio_mediana_ms"]) for r in azar], "o-", label="Divide y vencerás (propio)")
ax.plot(n, [float(r["scipy_mediana_ms"]) for r in azar], "s-", label="scipy.spatial.ConvexHull")
ax.set_xscale("log")
ax.set_yscale("log")
ax.set_xlabel("Número de puntos (escala log)")
ax.set_ylabel("Tiempo, mediana de 5 repeticiones (ms, escala log)")
ax.set_title("Envolvente convexa: tiempo frente a número de puntos")
ax.grid(True, which="both", alpha=0.3)
ax.legend()
fig.tight_layout()
fig.savefig("resultados/r3_grafica.png", dpi=200)
print("Guardadas: resultados/r3_tabla.md y resultados/r3_grafica.png")
