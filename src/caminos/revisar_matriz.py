# Lee la matriz guardada y muestra pares concretos. Correr desde la raíz del repo:
#   python src/caminos/revisar_matriz.py
import csv

with open("data/processed/matriz_tiempos.csv", encoding="utf-8", newline="") as f:
    filas = list(csv.reader(f))
ids = filas[0][1:]
A = [[float(x) for x in r[1:]] for r in filas[1:]]
n = len(ids)

nombres = {}
with open("data/catalogo/catalogo_lugares.csv", encoding="utf-8", newline="") as f:
    for r in csv.DictReader(f):
        k = list(r.keys())
        nombres[r[k[0]]] = r[k[1]]

def mostrar(a, b):
    i, j = ids.index(a), ids.index(b)
    print(f"{a} {nombres[a]} -> {b} {nombres[b]}: {A[i][j]/60:.1f} min | vuelta: {A[j][i]/60:.1f} min")

print("== Calarcá (CAB03) y Pijao (CAB10) ==")
mostrar("CAB03", "CAB10")

pares = sorted(((A[i][j], ids[i], ids[j]) for i in range(n) for j in range(n) if i != j))
print("\n== 3 pares más cortos ==")
for s, a, b in pares[:3]:
    mostrar(a, b)
print("\n== 3 pares más largos ==")
for s, a, b in pares[-3:]:
    mostrar(a, b)

asim = sorted(((abs(A[i][j] - A[j][i]), ids[i], ids[j]) for i in range(n) for j in range(i + 1, n)))
print("\n== Mayor diferencia ida/vuelta ==")
d, a, b = asim[-1]
mostrar(a, b)
print(f"Diferencia: {d/60:.1f} min")