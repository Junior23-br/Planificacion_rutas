"""R4. Itinerario de un día: ordenar de 6 a 8 atractivos con Held-Karp y comprobar la jornada de 11 h.

Tiempo total = tiempos de desplazamiento (matriz de R2) + duraciones de las visitas (catálogo).
Si no cabe en la jornada, se quitan atractivos con este criterio DEL GRUPO (se puede cambiar),
pensado para conservar la mayor cantidad posible de atractivos:
    en cada paso se prueba quitar cada atractivo y se recalcula el recorrido con Held-Karp.
    - Si alguna salida hace que quepa, se quita el atractivo que deja el total más cercano a la
      jornada sin pasarse (el que menos tiempo desperdicia).
    - Si ninguna hace que quepa, se quita el que más reduce el total, y se repite.

Uso (desde la raíz del proyecto):
    python -m src.ruta_optima.itinerario --sintetica                 (matriz de ejemplo)
    python -m src.ruta_optima.itinerario                             (matriz real de R2)
    python -m src.ruta_optima.itinerario --atractivos ATR01,ATR03,ATR05,ATR08,ATR09,ATR12
"""
import argparse
import csv
import random

from src.ruta_optima.medicion import generar_matriz, SEMILLA
from src.ruta_optima.tsp import held_karp

JORNADA_S = 11 * 3600


def armar_itinerario(T, inicio, atractivos, duraciones_s, jornada_s=JORNADA_S):
    """T: matriz (índices). duraciones_s: dict índice -> segundos de visita.
    Devuelve dict con ruta, tiempos, atractivos quitados (con su justificación) y si cabe."""
    actuales = list(atractivos)
    quitados = []
    while True:
        viaje, ruta = held_karp(T, inicio, actuales)
        visitas = sum(duraciones_s[a] for a in actuales)
        total = viaje + visitas
        if total <= jornada_s or not actuales:
            break
        opciones = []                                   # (atractivo, total si se quita)
        for a in actuales:
            resto = [x for x in actuales if x != a]
            v, _ = held_karp(T, inicio, resto)
            opciones.append((a, v + sum(duraciones_s[x] for x in resto)))
        caben = [o for o in opciones if o[1] <= jornada_s]
        mejor = max(caben, key=lambda o: o[1]) if caben else min(opciones, key=lambda o: o[1])
        quitados.append((mejor[0], total, mejor[1]))    # (atractivo, total antes, total después)
        actuales.remove(mejor[0])
    return {"ruta": ruta, "viaje_s": viaje, "visitas_s": visitas, "total_s": total,
            "quitados": quitados, "cabe": total <= jornada_s, "atractivos": actuales}


def leer_catalogo(ruta):
    with open(ruta, encoding="utf-8", newline="") as f:
        return list(csv.DictReader(f))


def leer_matriz(ruta):
    """CSV 40x40: primera fila y columna con ids, tiempos en segundos."""
    with open(ruta, encoding="utf-8", newline="") as f:
        filas = list(csv.reader(f))
    ids = filas[0][1:]
    T = [[float(x) for x in fila[1:]] for fila in filas[1:]]
    assert [fila[0] for fila in filas[1:]] == ids, "ids de filas y columnas distintos"
    return ids, T


def fmt(seg):
    h, m = divmod(int(round(seg / 60)), 60)
    return f"{h} h {m:02d} min"


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--catalogo", default="data/catalogo/catalogo_lugares.csv")
    ap.add_argument("--matriz", default="data/processed/matriz_tiempos.csv")
    ap.add_argument("--sintetica", action="store_true", help="usa una matriz aleatoria de ejemplo")
    ap.add_argument("--inicio", default="CAB01", help="id del lugar de partida (por defecto Armenia)")
    ap.add_argument("--atractivos", default="", help="ids separados por coma (6 a 8); vacío = al azar")
    ap.add_argument("--cantidad", type=int, default=7)
    args = ap.parse_args()

    cat = leer_catalogo(args.catalogo)
    nombre = {r["id"]: r["nombre"] for r in cat}
    dur = {r["id"]: int(float(r["duracion_visita_min"])) * 60 for r in cat if r["id"].startswith("ATR")}
    if args.sintetica:
        ids = [r["id"] for r in cat]
        T = generar_matriz(len(ids))
    else:
        ids, T = leer_matriz(args.matriz)
    pos = {i: n for n, i in enumerate(ids)}

    if args.atractivos:
        elegidos = [x.strip() for x in args.atractivos.split(",")]
    else:
        todos = sorted(dur)
        elegidos = sorted(random.Random(SEMILLA).sample(todos, args.cantidad))
    assert 6 <= len(elegidos) <= 8, "el enunciado pide entre 6 y 8 atractivos"

    res = armar_itinerario(T, pos[args.inicio], [pos[a] for a in elegidos],
                           {pos[a]: dur[a] for a in elegidos})
    print(f"Partida: {args.inicio} {nombre[args.inicio]}")
    print("Atractivos elegidos:", ", ".join(f"{a} ({nombre[a]})" for a in elegidos))
    for idx, antes, despues in res["quitados"]:
        print(f"Se quitó {ids[idx]} ({nombre[ids[idx]]}): el total pasó de {fmt(antes)} a {fmt(despues)}")
    print("Recorrido:", " -> ".join(f"{ids[i]}" for i in res["ruta"]))
    print(f"Desplazamientos: {fmt(res['viaje_s'])} | Visitas: {fmt(res['visitas_s'])} | "
          f"Total: {fmt(res['total_s'])} (jornada: {fmt(JORNADA_S)})")
    print("Cabe en la jornada:", "sí" if res["cabe"] else "no")


if __name__ == "__main__":
    main()