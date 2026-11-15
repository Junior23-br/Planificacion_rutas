"""Envolvente convexa por divide y vencerás.

Los puntos son tuplas de enteros (x, y). Con enteros, el producto cruzado es exacto:
en Python no desbordan y con enteros de 64 bits basta para coordenadas UTM en metros.
"""


def cruz(o, a, b):
    """Producto cruzado (a - o) x (b - o). Positivo si o -> a -> b gira a la izquierda."""
    return (a[0] - o[0]) * (b[1] - o[1]) - (a[1] - o[1]) * (b[0] - o[0])


def _cadenas(puntos):
    """Barrido de Andrew sobre puntos ordenados por (x, y) y sin repetidos.
    Devuelve (inferior, superior), ambas de izquierda a derecha. Los puntos que no giran
    estrictamente a la izquierda (alineados incluidos) se descartan."""
    inferior = []
    for p in puntos:
        while len(inferior) >= 2 and cruz(inferior[-2], inferior[-1], p) <= 0:
            inferior.pop()
        inferior.append(p)
    superior = []
    for p in reversed(puntos):
        while len(superior) >= 2 and cruz(superior[-2], superior[-1], p) <= 0:
            superior.pop()
        superior.append(p)
    superior.reverse()
    return inferior, superior


def _mezclar(a, b):
    """Une dos listas ordenadas por (x, y) en una sola, sin repetir los extremos comunes."""
    res = []
    i = j = 0
    while i < len(a) and j < len(b):
        if a[i] == b[j]:
            res.append(a[i])
            i += 1
            j += 1
        elif a[i] < b[j]:
            res.append(a[i])
            i += 1
        else:
            res.append(b[j])
            j += 1
    res.extend(a[i:])
    res.extend(b[j:])
    return res


def _dividir(puntos):
    """Devuelve las cadenas (inferior, superior) de la envolvente de `puntos`.
    Caso base: 3 puntos o menos. Si no, se divide en mitades, se resuelve cada una y se unen
    sus vértices (ya ordenados por x) con un solo barrido. T(n) = 2 T(n/2) + O(n)."""
    if len(puntos) <= 3:
        return _cadenas(puntos)
    m = len(puntos) // 2
    ai, a_s = _dividir(puntos[:m])
    bi, b_s = _dividir(puntos[m:])
    return _cadenas(_mezclar(ai, a_s) + _mezclar(bi, b_s))


def envolvente_convexa(puntos):
    """Vértices de la envolvente en sentido antihorario, empezando por el de menor x
    (y menor y si hay empate). Los repetidos se ignoran y los puntos alineados sobre un
    lado no son vértices. Con un punto o ninguno devuelve esos puntos; si todos están
    alineados devuelve los dos extremos."""
    unicos = sorted(set(map(tuple, puntos)))
    if len(unicos) <= 2:
        return unicos
    inferior, superior = _dividir(unicos)
    return inferior + superior[::-1][1:-1]
