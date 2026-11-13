import osmnx as ox

G = ox.load_graphml("data/raw/quindio_original.graphml")
V, E = G.number_of_nodes(), G.number_of_edges()
print("V =", V, " E =", E)

MB = 1024 ** 2

# Supuesto: cada peso (distancia en m, tiempo en s) ocupa 8 bytes (float64)
B_PESO = 8
# Supuesto: cada entrada de lista guarda destino (4 B) + distancia (8 B) + tiempo (8 B)
B_ENTRADA = 4 + 8 + 8
# Supuesto: un puntero/índice por nodo para el inicio de su lista
B_NODO = 8

matriz_1_peso = V * V * B_PESO
matriz_2_pesos = 2 * V * V * B_PESO   # una matriz de distancia y otra de tiempo
listas = E * B_ENTRADA + V * B_NODO

print(f"Matriz, 1 peso:   {matriz_1_peso / MB:,.1f} MB")
print(f"Matriz, 2 pesos:  {matriz_2_pesos / MB:,.1f} MB")
print(f"Listas (2 pesos): {listas / MB:,.2f} MB")
print(f"Densidad: {E / (V * V):.5%}  |  grado medio: {E / V:.2f}")
print(f"Razón matriz(2 pesos) / listas: {matriz_2_pesos / listas:,.0f}")