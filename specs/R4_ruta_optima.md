# R4. Ruta óptima de recorrido

Depende de: R2 (matriz de tiempos)

## Objetivo
Salir de un lugar de partida, visitar k lugares y regresar al mínimo tiempo total según la matriz de tiempos de R2. Problema del viajante asimétrico.

## Entradas y salidas
- Entrada: matriz T de tiempos (T[i][j] puede ser distinto de T[j][i]), índice del lugar de partida y lista de k lugares a visitar.
- Salida: el recorrido (orden de visita, empezando y terminando en la partida) y su tiempo total.

## Reglas del enunciado que aplican
- Fuerza bruta (todas las permutaciones) y Held-Karp, ambas con implementación propia. Held-Karp devuelve el recorrido, no solo el tiempo.
- Heurística voraz propia, saliendo de la partida y regresando a ella.
- k desde 5 hasta 12, o hasta el límite de 5 minutos (se reporta "no completada").
- Calidad de la heurística: k = 5, 8, 10 y 12, mínimo 5 instancias por k, en porcentaje (promedio y máximo).
- Itinerario de un día: 6 a 8 atractivos, jornada de 11 h.
- Experimentos con partida en Armenia y k lugares al azar con semilla fija.

## Comportamiento esperado y casos de prueba
Caso 1 (hecho a mano). 4 lugares, partida 0, matriz T:

| desde \ hacia | 0 | 1 | 2 | 3 |
|---|---|---|---|---|
| 0 | 0 | 10 | 15 | 20 |
| 1 | 5 | 0 | 9 | 10 |
| 2 | 6 | 13 | 0 | 12 |
| 3 | 8 | 8 | 9 | 0 |

| Entrada | Resultado esperado |
|---|---|
| Fuerza bruta, partida 0, visitar {1,2,3} | Recorrido 0→1→3→2→0, tiempo 35 |
| Held-Karp, mismo caso | Recorrido 0→1→3→2→0, tiempo 35 |
| Heurística del vecino más cercano, mismo caso | Recorrido 0→1→2→3→0, tiempo 39 (no es óptimo) |
| Fuerza bruta y Held-Karp en instancias aleatorias con k ≤ 8 | Mismo tiempo total en ambos |

## Qué se mide y con qué protocolo
Tiempo de fuerza bruta y de Held-Karp en función de k, memoria estimada de la tabla de Held-Karp, y alejamiento de la heurística respecto del óptimo. 5 repeticiones y mediana; semilla fija documentada.

## Estado
En curso: algoritmos y scripts listos; faltan mediciones con la matriz real de R2