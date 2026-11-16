"""Trazas paso a paso para las simulaciones de la página de Sustentación.

Este módulo no usa Streamlit: solo produce listas de pasos (diccionarios) que la página dibuja.
Cada traza repite, instrucción por instrucción, el algoritmo del proyecto y va guardando
una foto del estado. Las pruebas de tests/test_simulaciones.py comprueban que el resultado
final de cada traza es idéntico al de la función original (src/caminos/dijkstra.py,
src/envolvente/envolvente.py y src/ruta_optima/tsp.py).
"""
import heapq
import random

from src.envolvente.envolvente import _cadenas, _mezclar

INF = float("inf")

# ---------------------------------------------------------------------------------------
# Datos de ejemplo
# ---------------------------------------------------------------------------------------
# Grafo de 6 nodos resuelto a mano en specs/R2_caminos_minimos.md (el mismo de tests/test_dijkstra.py).
GRAFO_EJEMPLO = [
    [(1, 4.0), (2, 1.0)],   # 0
    [(3, 1.0)],             # 1
    [(1, 2.0), (3, 5.0)],   # 2
    [(4, 3.0)],             # 3
    [],                     # 4
    [(0, 1.0)],             # 5 (a él no llega nadie)
]
# Posición de cada nodo en el dibujo (x, y), en un lienzo de 700 x 340.
POS_GRAFO = [(90, 150), (270, 60), (270, 250), (450, 150), (620, 150), (90, 290)]

# Matriz del caso hecho a mano en specs/R4_ruta_optima.md (4 lugares, partida 0).
MATRIZ_EJEMPLO = [
    [0, 10, 15, 20],
    [5, 0, 9, 10],
    [6, 13, 0, 12],
    [8, 8, 9, 0],
]


def puntos_al_azar(n, semilla):
    """n puntos enteros distintos en un cuadrado de 100 x 100, con semilla fija."""
    rng = random.Random(semilla)
    puntos = set()
    while len(puntos) < n:
        puntos.add((rng.randint(4, 96), rng.randint(4, 96)))
    return sorted(puntos)


# ---------------------------------------------------------------------------------------
# R2. Dijkstra
# ---------------------------------------------------------------------------------------
def _foto(tipo, texto, dist, pred, hecho, explorados, **extra):
    paso = dict(tipo=tipo, texto=texto, dist=list(dist), pred=list(pred), hecho=list(hecho),
                explorados=explorados, u=None, relajaciones=[], cola=None, comparaciones=0)
    paso.update(extra)
    return paso


def traza_dijkstra_cola(adj, origen, destino=None):
    """Mismos pasos que dijkstra_cola. Un paso por cada extracción de la cola."""
    n = len(adj)
    dist = [INF] * n
    pred = [-1] * n
    hecho = [False] * n
    dist[origen] = 0.0
    cola = [(0.0, origen)]
    explorados = 0
    operaciones = 1                       # inserciones y extracciones de la cola
    pasos = [_foto("inicio", f"Se pone el origen ({origen}) en la cola con tiempo 0. "
                             "Los demás nodos empiezan con tiempo infinito.",
                   dist, pred, hecho, explorados, cola=sorted(cola), comparaciones=operaciones)]
    while cola:
        d, u = heapq.heappop(cola)
        operaciones += 1
        if hecho[u]:
            pasos.append(_foto("descartar", f"Sale ({_n(d)}, nodo {u}), pero el nodo {u} ya había "
                                            "salido antes con un tiempo menor: es una entrada vieja "
                                            "y se descarta.",
                               dist, pred, hecho, explorados, u=u, cola=sorted(cola),
                               comparaciones=operaciones))
            continue
        hecho[u] = True
        explorados += 1
        if u == destino:
            pasos.append(_foto("destino", f"Sale el nodo {u} con tiempo {_n(d)}. Es el destino: "
                                          "su tiempo ya es definitivo y la búsqueda se detiene.",
                               dist, pred, hecho, explorados, u=u, cola=sorted(cola),
                               comparaciones=operaciones))
            break
        relajaciones = []
        for v, w in adj[u]:
            nd = d + w
            mejora = nd < dist[v]
            relajaciones.append(dict(v=v, w=w, nuevo=nd, antes=dist[v], mejora=mejora))
            if mejora:
                dist[v] = nd
                pred[v] = u
                heapq.heappush(cola, (nd, v))
                operaciones += 1
        pasos.append(_foto("sacar", f"Sale el nodo {u} con tiempo {_n(d)}, el menor de la cola. "
                                    "Su tiempo queda definitivo y se revisan sus aristas de salida.",
                           dist, pred, hecho, explorados, u=u, relajaciones=relajaciones,
                           cola=sorted(cola), comparaciones=operaciones))
    else:
        pasos.append(_foto("fin", "La cola quedó vacía: ya no hay más nodos alcanzables.",
                           dist, pred, hecho, explorados, cola=[], comparaciones=operaciones))
    return pasos


def traza_dijkstra_lineal(adj, origen, destino=None):
    """Mismos pasos que dijkstra_lineal. Un paso por cada búsqueda lineal del mínimo."""
    n = len(adj)
    dist = [INF] * n
    pred = [-1] * n
    hecho = [False] * n
    dist[origen] = 0.0
    explorados = 0
    revisados = 0                         # posiciones de la lista revisadas buscando el mínimo
    pasos = [_foto("inicio", f"El origen ({origen}) empieza con tiempo 0 y los demás con infinito. "
                             "No hay cola: el mínimo se busca recorriendo toda la lista.",
                   dist, pred, hecho, explorados)]
    while True:
        u = -1
        mejor = INF
        for i in range(n):
            if not hecho[i] and dist[i] < mejor:
                mejor = dist[i]
                u = i
        revisados += n
        if u == -1:
            pasos.append(_foto("fin", f"Se recorren los {n} nodos y ninguno pendiente es alcanzable: "
                                      "la búsqueda termina.",
                               dist, pred, hecho, explorados, comparaciones=revisados))
            break
        hecho[u] = True
        explorados += 1
        if u == destino:
            pasos.append(_foto("destino", f"Se recorren los {n} nodos y el menor pendiente es el {u} "
                                          f"(tiempo {_n(mejor)}). Es el destino: la búsqueda se detiene.",
                               dist, pred, hecho, explorados, u=u, comparaciones=revisados))
            break
        relajaciones = []
        for v, w in adj[u]:
            nd = mejor + w
            mejora = nd < dist[v]
            relajaciones.append(dict(v=v, w=w, nuevo=nd, antes=dist[v], mejora=mejora))
            if mejora:
                dist[v] = nd
                pred[v] = u
        pasos.append(_foto("sacar", f"Se recorren los {n} nodos para hallar el menor pendiente: "
                                    f"el {u} (tiempo {_n(mejor)}). Queda definitivo y se revisan sus aristas.",
                           dist, pred, hecho, explorados, u=u, relajaciones=relajaciones,
                           comparaciones=revisados))
    return pasos


def _n(x):
    """Número corto para los textos: 3.0 -> '3', inf -> '∞'."""
    if x == INF:
        return "∞"
    return f"{x:g}"


# ---------------------------------------------------------------------------------------
# R3. Envolvente convexa por divide y vencerás
# ---------------------------------------------------------------------------------------
def _poligono(inferior, superior):
    """Une las dos cadenas en un polígono antihorario (igual que envolvente_convexa)."""
    return inferior + superior[::-1][1:-1]


def traza_envolvente(puntos):
    """Mismos pasos que _dividir, usando las funciones reales _cadenas y _mezclar.
    Devuelve (unicos, pasos). Cada paso trabaja sobre unicos[lo:hi]."""
    unicos = sorted(set(map(tuple, puntos)))
    pasos = []

    def dividir(lo, hi, nivel):
        sub = unicos[lo:hi]
        if len(sub) <= 3:
            inferior, superior = _cadenas(sub)
            pasos.append(dict(tipo="base", lo=lo, hi=hi, nivel=nivel,
                              casco=_poligono(inferior, superior), izq=[], der=[],
                              texto=f"Caso base: {len(sub)} punto(s). Se resuelve directamente "
                                    "con el producto cruzado."))
            return inferior, superior
        m = len(sub) // 2
        pasos.append(dict(tipo="dividir", lo=lo, hi=hi, medio=lo + m, nivel=nivel, casco=[],
                          izq=[], der=[],
                          texto=f"Dividir: {len(sub)} puntos ordenados por x se parten en una mitad "
                                f"izquierda de {m} y una derecha de {len(sub) - m}."))
        ai, a_s = dividir(lo, lo + m, nivel + 1)
        bi, b_s = dividir(lo + m, hi, nivel + 1)
        candidatos = _mezclar(ai, a_s) + _mezclar(bi, b_s)
        inferior, superior = _cadenas(candidatos)
        casco = _poligono(inferior, superior)
        pasos.append(dict(tipo="unir", lo=lo, hi=hi, medio=lo + m, nivel=nivel, casco=casco,
                          izq=_poligono(ai, a_s), der=_poligono(bi, b_s),
                          candidatos=len(candidatos),
                          texto=f"Unir: los {len(candidatos)} vértices de las dos mitades se barren "
                                f"una vez (cadena monótona). Quedan {len(casco)} y se descartan "
                                f"{len(candidatos) - len(casco)} que no giran a la izquierda."))
        return inferior, superior

    if len(unicos) >= 1:
        dividir(0, len(unicos), 0)
    return unicos, pasos


# ---------------------------------------------------------------------------------------
# R4. Vecino más cercano y Held-Karp
# ---------------------------------------------------------------------------------------
def traza_vecino(T, inicio, lugares):
    """Mismos pasos que vecino_mas_cercano. Un paso por cada decisión."""
    pendientes = list(lugares)
    ruta = [inicio]
    actual = inicio
    acumulado = 0
    pasos = []
    while pendientes:
        opciones = [(x, T[actual][x]) for x in pendientes]
        siguiente = min(pendientes, key=lambda x: T[actual][x])
        acumulado += T[actual][siguiente]
        pendientes.remove(siguiente)
        ruta.append(siguiente)
        pasos.append(dict(tipo="elegir", actual=actual, opciones=opciones, elegido=siguiente,
                          costo=T[actual][siguiente], acumulado=acumulado, ruta=list(ruta)))
        actual = siguiente
    acumulado += T[actual][inicio]
    ruta.append(inicio)
    pasos.append(dict(tipo="regreso", actual=actual, opciones=[(inicio, T[actual][inicio])],
                      elegido=inicio, costo=T[actual][inicio], acumulado=acumulado, ruta=list(ruta)))
    return pasos


def traza_held_karp(T, inicio, lugares):
    """Mismos pasos que held_karp. Un paso por el caso base, uno por cada subconjunto que
    se extiende, uno por el cierre y uno por la reconstrucción.
    C[mascara][j] y padre[mascara][j] significan lo mismo que en src/ruta_optima/tsp.py."""
    k = len(lugares)
    C = [[INF] * k for _ in range(1 << k)]
    padre = [[-1] * k for _ in range(1 << k)]
    pasos = []

    def foto(tipo, **extra):
        paso = dict(tipo=tipo, C=[fila[:] for fila in C], mascara=None, transiciones=[],
                    nuevos=set())
        paso.update(extra)
        pasos.append(paso)

    for j in range(k):
        C[1 << j][j] = T[inicio][lugares[j]]
    foto("base", nuevos={(1 << j, j) for j in range(k)})

    for mascara in range(1, 1 << k):
        transiciones = []
        nuevos = set()
        for j in range(k):
            if not (mascara >> j) & 1 or C[mascara][j] == INF:
                continue
            for n in range(k):
                if (mascara >> n) & 1:
                    continue
                nueva = mascara | (1 << n)
                costo = C[mascara][j] + T[lugares[j]][lugares[n]]
                mejora = costo < C[nueva][n]
                transiciones.append(dict(j=j, n=n, nueva=nueva, base=C[mascara][j],
                                         salto=T[lugares[j]][lugares[n]], costo=costo,
                                         antes=C[nueva][n], mejora=mejora))
                if mejora:
                    C[nueva][n] = costo
                    padre[nueva][n] = j
                    nuevos.add((nueva, n))
        if transiciones:
            foto("extender", mascara=mascara, transiciones=transiciones, nuevos=nuevos)

    completa = (1 << k) - 1
    mejor_tiempo, mejor_j = INF, -1
    cierres = []
    for j in range(k):
        total = C[completa][j] + T[lugares[j]][inicio]
        cierres.append(dict(j=j, base=C[completa][j], regreso=T[lugares[j]][inicio], total=total))
        if total < mejor_tiempo:
            mejor_tiempo, mejor_j = total, j
    foto("cierre", mascara=completa, cierres=cierres, mejor_j=mejor_j, total=mejor_tiempo)

    orden = []
    mascara, j = completa, mejor_j
    while j != -1:
        orden.append(lugares[j])
        anterior = padre[mascara][j]
        mascara ^= (1 << j)
        j = anterior
    orden.reverse()
    foto("reconstruir", mascara=completa, total=mejor_tiempo, ruta=[inicio] + orden + [inicio])
    return pasos


def subconjuntos_ordenados(k):
    """Máscaras de 1 a 2^k - 1, primero las de menos lugares (para mostrar la tabla)."""
    return sorted(range(1, 1 << k), key=lambda m: (bin(m).count("1"), m))
