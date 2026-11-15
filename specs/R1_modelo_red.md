# R1 - Modelo de la red vial
Depende de: Catálogo de lugares

## Objetivo
Construir con OSMnx el grafo dirigido de la red vial del Quindío, con longitud (m) y tiempo de viaje (s) en cada arista, quedarse con su componente fuertemente conexa y asociar cada lugar del catálogo a su nodo más cercano.

## Entradas y salidas
- Entradas: red de OpenStreetMap del Quindío (`data/raw/quindio_original.graphml`) y `data/catalogo/catalogo_lugares.csv`.
- Salidas: `data/processed/componente.graphml` (componente con pesos), `data/processed/asociacion_lugares.csv` (id, nodo, distancia_m, mayor_500m) y `resultados/r1_componente.csv` (tamaño y tiempo en 5 redes).

## Reglas del enunciado que aplican
- Todo en Python con OSMnx.
- Estimar la memoria como matriz y como listas de adyacencia (con supuestos) y elegir una: listas de adyacencia. Con V = 8807 y E = 20153: matriz 591,8 MB (un peso) o 1183,5 MB (dos pesos); listas 0,45 MB.
- Pesos `length` (m) y `travel_time` (s). Solo 1307 de 20153 aristas traen `maxspeed`; el resto se imputa por tipo de vía. El tiempo es una estimación del modelo.
- Componente con `ox.truncate.largest_component(G, strongly=True)`; el resto del proyecto trabaja solo con ella.
- Tiempo de la función en redes de 2, 5, 10 y 20 km alrededor de la plaza de Bolívar (`graph_from_point`) y en el departamento, con V y E de cada una.
- Asociación al nodo más cercano por distancia euclidiana en UTM 18N; reportar los lugares a más de 500 m.

## Comportamiento esperado y casos de prueba
| Entrada | Resultado esperado |
|---|---|
| Red del departamento | V = 8807, E = 20153 antes de filtrar; V = 8791, E = 20132 después |
| Componente obtenida | Fuertemente conexa (todo nodo llega a todo nodo) |
| 40 lugares del catálogo | 40 nodos distintos, todos dentro de la componente |
| Lugar a más de 500 m de su nodo | Marcado `mayor_500m` (6 casos: ATR07, ATR09, ATR12, FIN03, FIN04, FIN07) |
| Tramo con `maxspeed` en OSM | Tiempo = longitud / velocidad indicada |

## Qué se mide y con qué protocolo
- Tiempo de `largest_component` en las 5 redes: 5 repeticiones, mediana, en ms, misma máquina (`resultados/r1_r2_maquina.txt`). Resultados en `resultados/r1_componente.csv`.

## Estado
Hecho
