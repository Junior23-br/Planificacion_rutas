"""R4. Viajante asimétrico: fuerza bruta, Held-Karp y heurística del vecino más cercano.

Convenciones:
- T es la matriz de tiempos: T[a][b] = tiempo de ir de a a b (no necesariamente igual a T[b][a]).
- inicio es el índice del lugar de partida y de regreso.
- lugares es la lista de índices de los k lugares a visitar (sin incluir el inicio).
- Todas las funciones devuelven (tiempo_total, ruta), con la ruta empezando y terminando en inicio.
"""

INF = float("inf")


def tiempo_de_ruta(T, ruta):
    """Suma los saltos de una ruta dada como lista de índices."""
    return sum(T[ruta[i]][ruta[i + 1]] for i in range(len(ruta) - 1))


def _permutaciones(elementos):
    """Genera todas las permutaciones de una lista (implementación propia, recursiva)."""
    if len(elementos) <= 1:
        yield list(elementos)
        return
    for i in range(len(elementos)):
        resto = elementos[:i] + elementos[i + 1:]
        for p in _permutaciones(resto):
            yield [elementos[i]] + p


def fuerza_bruta(T, inicio, lugares):
    """Prueba todos los órdenes posibles (k! órdenes) y devuelve el de menor tiempo."""
    if not lugares:
        return 0, [inicio, inicio]
    mejor_tiempo, mejor_ruta = INF, None
    for orden in _permutaciones(list(lugares)):
        ruta = [inicio] + orden + [inicio]
        t = tiempo_de_ruta(T, ruta)
        if t < mejor_tiempo:
            mejor_tiempo, mejor_ruta = t, ruta
    return mejor_tiempo, mejor_ruta


def held_karp(T, inicio, lugares):
    """Programación dinámica sobre subconjuntos. Devuelve (tiempo, ruta).

    C[mascara][j] = menor tiempo para salir de inicio, visitar exactamente los lugares
    de la máscara y terminar en el lugar número j (posición dentro de 'lugares').
    padre[mascara][j] = lugar anterior (posición) que dio ese mínimo.
    """
    k = len(lugares)
    if k == 0:
        return 0, [inicio, inicio]

    C = [[INF] * k for _ in range(1 << k)]
    padre = [[-1] * k for _ in range(1 << k)]

    for j in range(k):                                  # caso base: ir directo de inicio a j
        C[1 << j][j] = T[inicio][lugares[j]]

    for mascara in range(1, 1 << k):                    # orden creciente: subconjuntos pequeños primero
        for j in range(k):
            if not (mascara >> j) & 1 or C[mascara][j] == INF:
                continue
            for n in range(k):                          # siguiente lugar a visitar
                if (mascara >> n) & 1:
                    continue
                nueva = mascara | (1 << n)
                costo = C[mascara][j] + T[lugares[j]][lugares[n]]
                if costo < C[nueva][n]:
                    C[nueva][n] = costo
                    padre[nueva][n] = j

    completa = (1 << k) - 1
    mejor_tiempo, mejor_j = INF, -1
    for j in range(k):                                  # cierre: sumar el regreso al inicio
        total = C[completa][j] + T[lugares[j]][inicio]
        if total < mejor_tiempo:
            mejor_tiempo, mejor_j = total, j

    orden = []                                          # reconstrucción hacia atrás con 'padre'
    mascara, j = completa, mejor_j
    while j != -1:
        orden.append(lugares[j])
        anterior = padre[mascara][j]
        mascara ^= (1 << j)
        j = anterior
    orden.reverse()
    return mejor_tiempo, [inicio] + orden + [inicio]


def vecino_mas_cercano(T, inicio, lugares):
    """Heurística voraz: desde el lugar actual, ir al lugar no visitado más barato."""
    pendientes = list(lugares)
    ruta = [inicio]
    actual = inicio
    while pendientes:
        siguiente = min(pendientes, key=lambda x: T[actual][x])
        pendientes.remove(siguiente)
        ruta.append(siguiente)
        actual = siguiente
    ruta.append(inicio)
    return tiempo_de_ruta(T, ruta), ruta