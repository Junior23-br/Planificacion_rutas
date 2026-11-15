# R3 - Envolvente convexa
Depende de: R1 (nodos de la red)

## Objetivo
Calcular la envolvente convexa de los nodos de la componente fuertemente conexa, como aproximación de la extensión de la red vial, con un algoritmo propio de divide y vencerás, y compararlo con `scipy.spatial.ConvexHull`.

## Entradas y salidas
- Entrada: nodos de `data/processed/componente.graphml` (8 791), con su longitud y latitud.
- Salida: lista de vértices de la envolvente en sentido antihorario, empezando por el punto de menor x (y de menor y si hay empate). Se guarda en `resultados/r3_envolvente.csv` con columnas x, y (metros, UTM 18N) y lon, lat (para dibujarla en la aplicación).
- Tiempos del experimento en `resultados/r3_tiempos.csv`.

## Reglas del enunciado que aplican
- Convertir las coordenadas a metros en UTM zona 18N (EPSG:32618), redondear cada una al entero más cercano y eliminar los puntos que queden repetidos.
- Los giros y alineaciones se calculan con coordenadas enteras. Con enteros de tamaño fijo se usan enteros de 64 bits para evitar desbordamientos; en Python los enteros no desbordan.
- Los puntos alineados sobre un lado del polígono no cuentan como vértices.
- Implementación propia de un algoritmo de divide y vencerás, justificando la elección según la distribución de los puntos de la red.
- Calcular también la envolvente con `scipy.spatial.ConvexHull` y verificar que ambas den los mismos vértices en todas las pruebas. SciPy solo se usa para comprobar y para el experimento.
- Fuente de la complejidad en tiempo y en memoria (citar autor y título o enlace).

## Algoritmos que se usan
| Para qué | Algoritmo | Propio o librería |
|---|---|---|
| Calcular la envolvente | Divide y vencerás por mitades, con unión por barrido de Andrew (cadena monótona) | Propio |
| Decidir si tres puntos giran a la izquierda | Producto cruzado con enteros | Propio |
| Ordenar los puntos por (x, y) | Ordenamiento de Python (Timsort), O(n log n); se cita en el análisis | Librería permitida |
| Quitar repetidos tras redondear | Conjunto (`set`), O(n) esperado | Estructura de Python |
| Pasar de longitud y latitud a UTM 18N | Proyección con `pyproj` (EPSG:32618) | Librería permitida |
| Verificar y comparar | `scipy.spatial.ConvexHull` (Qhull, Quickhull en C) | Librería, solo para comprobar |

## Algoritmo elegido y justificación
Divide y vencerás por mitades. Se ordenan los puntos distintos por (x, y). Si quedan 3 puntos o menos, se resuelve directamente. Si no, se parte la lista en dos mitades, se calcula la envolvente de cada una de forma recursiva y se unen: como todos los puntos de la mitad izquierda quedan antes que los de la derecha en el orden, basta recorrer los vértices de las dos envolventes con el barrido de Andrew (cadena monótona, con producto cruzado entero), que descarta los puntos que no giran estrictamente a la izquierda. La unión cuesta O(h), con h el número de vértices de las dos mitades, y h ≤ n.
La elección se justifica por la distribución de los nodos: en una red vial están agrupados en corredores y centros urbanos, con una distribución muy irregular. Este algoritmo no depende de esa distribución, porque su peor caso sigue siendo O(n log n), mientras que Quickhull puede degradarse a O(n²).
Complejidad: T(n) = 2T(n/2) + O(n), que da O(n log n) (teorema maestro, Cormen et al., Introduction to Algorithms), más la ordenación inicial, también O(n log n). Memoria O(n). Referencias para el divide y vencerás de envolventes: Preparata y Hong (1977) y Andrew (1979) para el barrido; confirmar las citas antes de ponerlas en el documento.

## Comportamiento esperado y casos de prueba
| Entrada | Resultado esperado |
|---|---|
| (0,0), (4,0), (4,4), (0,4), (2,2) | [(0,0), (4,0), (4,4), (0,4)]; el punto interior no es vértice |
| El cuadrado anterior más (2,0) sobre un lado | El mismo resultado; (2,0) está alineado sobre un lado y no cuenta |
| (0,0), (6,0), (0,6), (3,3), (1,1) | [(0,0), (6,0), (0,6)]; (3,3) está sobre la hipotenusa y (1,1) adentro |
| Puntos repetidos: (0,0), (0,0), (4,0), (4,4), (0,4) | [(0,0), (4,0), (4,4), (0,4)] |
| Coordenadas reales (0.4, 0.4), (0.1, 0.2), (4.2, 0.3), (3.9, 4.4), (0.3, 3.8) | Tras redondear y quitar repetidos: [(0,0), (4,0), (4,4), (0,4)] |
| (0,0), (1,1), (2,2), todos alineados | [(0,0), (2,2)]; solo los dos extremos |
| Un solo punto, o ninguno | Ese punto, o lista vacía |
| Coordenadas del orden de 10⁹ | Resultado correcto, sin desbordamiento |
| 1 000 puntos al azar con semilla 2026 | Mismos vértices que `scipy.spatial.ConvexHull` |
| Nodos de la componente | Mismos vértices que SciPy; vértices guardados en el CSV |

## Qué se mide y con qué protocolo
- Mi versión y SciPy con los nodos de la red y con 1 000, 10 000 y 50 000 puntos al azar dentro de un cuadrado, con semilla fija (2026).
- Misma máquina, solo se mide el cálculo de la envolvente (no la conversión ni la lectura de archivos), 5 repeticiones y mediana, en milisegundos; una sola repetición si pasa de un minuto; límite de 5 minutos.
- Tabla de tiempos generada desde `resultados/r3_tiempos.csv`, con un párrafo que diga si coincide con lo esperado.
- Investigar y citar qué algoritmo y qué lenguaje usa SciPy por dentro: ConvexHull se apoya en la librería Qhull, que está en C y usa Quickhull (Barber, Dobkin y Huhdanpaa, "The Quickhull algorithm for convex hulls", ACM Transactions on Mathematical Software, 1996). Confirma la cita en la documentación de SciPy y de Qhull antes de ponerla en el documento.

## Estado
Pendiente
