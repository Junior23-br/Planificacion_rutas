import heapq


def dijkstra_cola(adj, origen, destino=None):
    """Dijkstra con cola de prioridad (heapq, entradas perezosas).
    Devuelve (dist, pred, explorados):
      dist[v]    menor tiempo (s) de origen a v (inf si no se alcanza)
      pred[v]    predecesor de v en el camino mínimo (-1 si no tiene)
      explorados nodos que salieron de la cola por primera vez (cada uno se cuenta una vez)
    Si destino no es None, se detiene al sacar el destino de la cola.
    """
    n = len(adj)
    INF = float("inf")
    dist = [INF] * n
    pred = [-1] * n
    hecho = [False] * n
    dist[origen] = 0.0
    cola = [(0.0, origen)]
    explorados = 0
    while cola:
        d, u = heapq.heappop(cola)
        if hecho[u]:
            continue                      # entrada vieja: ya salió con menor tiempo
        hecho[u] = True
        explorados += 1
        if u == destino:
            break
        for v, w in adj[u]:
            nd = d + w
            if nd < dist[v]:
                dist[v] = nd
                pred[v] = u
                heapq.heappush(cola, (nd, v))
    return dist, pred, explorados


def dijkstra_lineal(adj, origen, destino=None):
    """Dijkstra con búsqueda lineal del mínimo, O(V^2).
    Devuelve (dist, pred, explorados), con el mismo significado que dijkstra_cola.
    """
    n = len(adj)
    INF = float("inf")
    dist = [INF] * n
    pred = [-1] * n
    hecho = [False] * n
    dist[origen] = 0.0
    explorados = 0
    while True:
        # búsqueda lineal del nodo no terminado con menor distancia: O(V)
        u = -1
        mejor = INF
        for i in range(n):
            if not hecho[i] and dist[i] < mejor:
                mejor = dist[i]
                u = i
        if u == -1:                      # no quedan nodos alcanzables
            break
        hecho[u] = True
        explorados += 1
        if u == destino:
            break
        for v, w in adj[u]:
            nd = mejor + w
            if nd < dist[v]:
                dist[v] = nd
                pred[v] = u
    return dist, pred, explorados

def reconstruir_ruta(pred, origen, destino):
    """Secuencia de nodos origen -> destino, o [] si no hay camino."""
    ruta = []
    v = destino
    while v != -1:
        ruta.append(v)
        if v == origen:
            break
        v = pred[v]
    ruta.reverse()
    return ruta if ruta and ruta[0] == origen else []


def ruta_minima(adj, origen, destino):
    """Interfaz para R5: devuelve (tiempo_s, ruta, explorados)."""
    dist, pred, explorados = dijkstra_cola(adj, origen, destino)
    return dist[destino], reconstruir_ruta(pred, origen, destino), explorados