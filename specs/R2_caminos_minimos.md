# R2 - Caminos mínimos
Depende de: R1

## Objetivo
Implementar Dijkstra con búsqueda lineal del mínimo y con cola de prioridad, compararlos con mediciones y calcular la matriz de tiempos entre los lugares del catálogo.

## Entradas y salidas
- Entradas: listas de adyacencia de la componente (`cargar_grafo`), índice de origen e índice de destino (el destino es opcional).
- Salidas: `dijkstra_cola` y `dijkstra_lineal` devuelven `(dist, pred, explorados)`; `ruta_minima(adj, origen, destino)` devuelve `(tiempo_s, ruta, explorados)`, con ruta vacía y tiempo infinito si no hay camino.
- Matriz: `data/processed/matriz_tiempos.csv`, 40×40, segundos, ids en la primera fila y columna, diagonal 0.

## Reglas del enunciado que aplican
- Implementación propia; NetworkX solo para verificar.
- Ambas versiones se detienen al sacar el destino y reconstruyen la ruta con el predecesor.
- Un nodo se cuenta como explorado la primera vez que sale de la cola.
- Aristas paralelas: se conserva la de menor tiempo; los bucles se descartan.
- Medir la cola con 20 pares del catálogo y la lineal con 10 de ellos, cercanos (mismo municipio o municipios vecinos).
- Matriz con la versión de cola, ejecutada una vez desde cada lugar sin detenerse.

## Comportamiento esperado y casos de prueba
| Entrada | Resultado esperado |
|---|---|
| Grafo de 6 nodos resuelto a mano, origen 0 | Distancias 0, 3, 1, 4, 7 e infinito al nodo 5; ruta 0→2→1→3→4 |
| Destino inalcanzable | Tiempo infinito y ruta vacía |
| Grafos aleatorios pequeños | Cola y lineal dan las mismas distancias que Bellman-Ford propio |
| Pares del catálogo | Mismo tiempo que NetworkX y mismo número de nodos explorados en ambas versiones |
| Matriz de tiempos | Diagonal 0, sin celdas vacías, sin violaciones de la desigualdad triangular |

## Qué se mide y con qué protocolo
- Tiempo y nodos explorados por consulta; 5 repeticiones, mediana, en ms, misma máquina (`resultados/r1_r2_maquina.txt`), semilla 2026.
- Resultados en `resultados/r2_mediciones.csv` y `resultados/r2_cociente.csv`; gráfica en `resultados/r2_grafica.png`, generada desde el CSV.
- Cociente lineal / cola: mediana 439,5.

## Estado
Hecho
