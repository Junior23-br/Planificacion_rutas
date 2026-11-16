"""Página de Sustentación (R5): material para defender el proyecto.

Secciones: recorrido por requerimientos, simulaciones paso a paso, comparaciones con gráficas
generadas desde resultados/, decisiones y limitaciones y fuentes.

Regla de esta página: toda cifra sale de un archivo de resultados/ o data/, o se calcula en
el momento. Si falta el archivo, la frase que dependía de él no se muestra.
"""
import math
import random
import time

import streamlit as st

from src.app import datos, estilo, graficas
from src.app import simulaciones as sim
from src.app.estilo import (AZUL, BERMELLON, BORDE_FUERTE, FONDO, FONDO_2, TINTA, TINTA_2, TINTA_3,
                            e, ms, num)

# Dentro de un SVG mostrado como imagen no se cargan fuentes web: se usan las del sistema.
FUENTE = "IBM Plex Sans, Segoe UI, Helvetica, Arial, sans-serif"
FUENTE_MONO = "IBM Plex Mono, Consolas, Courier New, monospace"
from src.app.paginas import bloque_maquina, fmt_tiempo

INF = float("inf")


# =======================================================================================
# Cifras leídas de los archivos (se usan en varias secciones)
# =======================================================================================
def _cifras():
    """Reúne en un diccionario las cifras de resultados/ que se citan en la página.
    Una clave solo existe si su archivo existe."""
    c = {}
    r1 = datos.csv(datos.res("r1_componente.csv"))
    if r1 is not None and (r1["red"] == "Departamento").any():
        dep = r1[r1["red"] == "Departamento"].iloc[0]
        c.update(V=int(dep["V_despues"]), E=int(dep["E_despues"]), V_antes=int(dep["V_antes"]),
                 E_antes=int(dep["E_antes"]), scc_ms=float(dep["mediana_ms"]), redes=len(r1))
        c["mem_matriz"], c["mem_matriz2"], c["mem_listas"] = datos.memoria_estimada(c["V_antes"], c["E_antes"])
    coc = datos.csv(datos.res("r2_cociente.csv"))
    if coc is not None:
        for nombre, valor in zip(coc["estadistico"], coc["valor"]):
            c["coc_" + nombre] = float(valor)
    r2 = datos.csv(datos.res("r2_mediciones.csv"))
    if r2 is not None:
        c.update(pares=len(r2), pares_lineal=int(r2["lineal_mediana_ms"].notna().sum()),
                 cola_max=float(r2["cola_mediana_ms"].max()), lineal_max=float(r2["lineal_mediana_ms"].max()))
    r3 = datos.csv(datos.res("r3_tiempos.csv"))
    if r3 is not None and (r3["conjunto"] == "nodos de la red").any():
        f = r3[r3["conjunto"] == "nodos de la red"].iloc[0]
        c.update(env_n=int(f["n_puntos"]), env_v=int(f["vertices"]), env_ms=float(f["propio_mediana_ms"]),
                 env_scipy=float(f["scipy_mediana_ms"]), env_coc=float(f["cociente_propio_scipy"]),
                 env_coc_min=float(r3["cociente_propio_scipy"].min()),
                 env_coc_max=float(r3["cociente_propio_scipy"].max()))
    ex = datos.csv(datos.res("r4_exactas.csv"))
    if ex is not None:
        ok = ex[ex["estado"] == "completada"]
        hk, fb = ok[ok["metodo"] == "held_karp"], ok[ok["metodo"] == "fuerza_bruta"]
        if len(hk) and len(fb):
            c.update(hk_k=int(hk["k"].max()), hk_ms=float(hk[hk["k"] == hk["k"].max()]["mediana_ms"].iloc[0]),
                     fb_k=int(fb["k"].max()), fb_ms=float(fb[fb["k"] == fb["k"].max()]["mediana_ms"].iloc[0]))
            c["hk_en_fb_k"] = float(hk[hk["k"] == c["fb_k"]]["mediana_ms"].iloc[0]) if (hk["k"] == c["fb_k"]).any() else None
            for k in (8,):
                if (hk["k"] == k).any() and (fb["k"] == k).any():
                    c["hk_8"] = float(hk[hk["k"] == k]["mediana_ms"].iloc[0])
                    c["fb_8"] = float(fb[fb["k"] == k]["mediana_ms"].iloc[0])
        c["fb_incompletas"] = [int(k) for k in ex[(ex["estado"] != "completada") & (ex["metodo"] == "fuerza_bruta")]["k"]]
    cal = datos.csv(datos.res("r4_calidad_resumen.csv"))
    if cal is not None and len(cal):
        c.update(cal_prom_min=float(cal["alejamiento_promedio_pct"].min()),
                 cal_prom_max=float(cal["alejamiento_promedio_pct"].max()),
                 cal_max=float(cal["alejamiento_maximo_pct"].max()),
                 cal_instancias=int(cal["instancias"].sum()),
                 cal_ks=", ".join(str(int(k)) for k in cal["k"]))
    aso = datos.csv(datos.ASOCIACION)
    if aso is not None and "mayor_500m" in aso.columns:
        c["lejos"] = int((aso["mayor_500m"].astype(str) == "True").sum())
        c["lugares"] = len(aso)
    base = datos.catalogo_y_matriz()
    if base:
        _, ids, T = base
        n = len(ids)
        c["matriz_n"] = n
        c["asimetricos"] = sum(1 for i in range(n) for j in range(i + 1, n) if abs(T[i][j] - T[j][i]) > 0.5)
        c["pares_matriz"] = n * (n - 1) // 2
    return c


def _si(c, claves, texto):
    """Devuelve el texto formateado solo si existen todas las cifras que necesita."""
    return texto if all(k in c and c[k] is not None for k in claves.split()) else ""


# =======================================================================================
# 1. Recorrido por requerimientos
# =======================================================================================
# Frase de una línea que queda siempre visible sobre cada requerimiento.
_RESUMEN_R = {
    "R1": "La red vial del Quindío como grafo dirigido, con un tiempo de viaje en cada tramo.",
    "R2": "El camino de menor tiempo entre dos lugares, con Dijkstra y cola de prioridad.",
    "R3": "El menor polígono convexo que contiene la red, por divide y vencerás.",
    "R4": "El mejor orden de visita dentro de una jornada, con Held-Karp y vecino más cercano.",
}


def _bloque_requerimiento(titulo, problema, algoritmo, complejidad, tarjetas):
    """Un requerimiento: el resumen siempre se ve y el detalle se despliega. R2 abre por defecto."""
    clave = titulo[:2]
    st.caption(_RESUMEN_R.get(clave, ""))
    with st.expander(titulo, expanded=(clave == "R2")):
        izq, der = st.columns([3, 2], gap="large")
        with izq:
            estilo.ficha("Problema", problema)
            estilo.ficha("Algoritmo", algoritmo)
            estilo.ficha("Complejidad", complejidad)
        with der:
            if tarjetas:
                estilo.tarjetas(tarjetas)
            else:
                estilo.estado_vacio("Sin resultados todavía",
                                    "Faltan los archivos de resultados/ de este requerimiento.")


def _recorrido(c):
    st.write("Cada requerimiento resuelve un problema distinto y deja un resultado que usa el siguiente: "
             "la red de R1 alimenta los caminos de R2 y la envolvente de R3; la matriz de R2 alimenta el "
             "itinerario de R4.")
    _bloque_requerimiento(
        "R1 · Modelo de la red vial",
        "Convertir el mapa de OpenStreetMap del Quindío en un grafo sobre el que se pueda calcular: "
        "dirigido, con un tiempo de viaje en cada tramo y en el que desde cualquier nodo se llegue a "
        "cualquier otro.",
        "Descarga con OSMnx. Se conserva la mayor componente fuertemente conexa "
        "(<code>ox.truncate.largest_component(G, strongly=True)</code>). Donde OpenStreetMap no trae "
        "velocidad máxima, se imputa por tipo de vía. Cada lugar del catálogo se asocia a su nodo más "
        "cercano, con distancias en UTM 18N.",
        "La red se guarda como <b>listas de adyacencia</b>, memoria O(V + E), en lugar de una matriz, "
        "O(V²). La componente la calcula la librería; el proyecto mide su tiempo en "
        + (f"{c['redes']} redes de tamaño creciente." if "redes" in c else "redes de tamaño creciente."),
        [("Nodos (V)", num(c["V"]), f"se descartaron {num(c['V_antes'] - c['V'])} fuera de la componente", True),
         ("Aristas (E)", num(c["E"]), "tramos dirigidos"),
         ("Memoria estimada", f"{num(c['mem_listas'], 2)} MB", f"como matriz: {num(c['mem_matriz'], 1)} MB"),
         ("Componente", ms(c["scc_ms"]), "mediana, red del departamento")] if "V" in c else [])
    _bloque_requerimiento(
        "R2 · Caminos mínimos",
        "Dado un origen y un destino, hallar el camino de menor tiempo por la red. Además, llenar la "
        "matriz de tiempos entre todos los lugares del catálogo.",
        "<b>Dijkstra</b> en dos versiones propias: con cola de prioridad (<code>heapq</code>, entradas "
        "perezosas) y con búsqueda lineal del mínimo. Las dos se detienen al sacar el destino y "
        "reconstruyen la ruta con los predecesores. La matriz se llena ejecutando la versión con cola "
        "una vez desde cada lugar.",
        "Con cola: <b>O((V + E) log V)</b>. Con búsqueda lineal: <b>O(V²)</b>, porque cada paso recorre "
        "todos los nodos para hallar el mínimo.",
        [("Lineal / cola", f"{num(c['coc_mediana'], 1)} ×", "mediana del cociente de tiempos", True),
         ("Pares medidos", f"{c['pares']} y {c['pares_lineal']}", "con cola y con lineal")]
        + ([("Matriz de tiempos", f"{c['matriz_n']} × {c['matriz_n']}",
             f"{num(c['asimetricos'] / c['pares_matriz'] * 100, 0)} % de los pares difiere entre ida y vuelta")]
           if "matriz_n" in c else [])
        + [("Consulta más lenta con cola", ms(c["cola_max"]), f"con lineal: {ms(c['lineal_max'])}")]
        if "coc_mediana" in c and "pares" in c else [])
    _bloque_requerimiento(
        "R3 · Envolvente convexa",
        "Hallar el menor polígono convexo que contiene todos los nodos de la red, como aproximación de "
        "la extensión que cubre.",
        "<b>Divide y vencerás por mitades</b>: se ordenan los puntos por (x, y), se parte la lista en "
        "dos, se resuelve cada mitad y se unen con un barrido de <b>Andrew</b> (cadena monótona). Las "
        "coordenadas se pasan a metros enteros en UTM 18N para que el producto cruzado sea exacto. El "
        "resultado se verifica contra <code>scipy.spatial.ConvexHull</code>.",
        "T(n) = 2·T(n/2) + O(n), que da <b>O(n log n)</b> por el teorema maestro; la ordenación inicial "
        "también es O(n log n). Memoria <b>O(n)</b>.",
        [("Vértices", str(c["env_v"]), f"de {num(c['env_n'])} nodos", True),
         ("Versión propia", ms(c["env_ms"]), "mediana, nodos de la red"),
         ("SciPy (Qhull, en C)", ms(c["env_scipy"]), "mediana, nodos de la red"),
         ("Propia / SciPy", f"{num(c['env_coc'], 1)} ×", "mismos vértices en todas las pruebas")]
        if "env_v" in c else [])
    _bloque_requerimiento(
        "R4 · Ruta óptima e itinerario de un día",
        "Salir de un lugar, visitar k lugares y regresar en el menor tiempo total: el problema del "
        "viajante con tiempos asimétricos. Para el itinerario, además, las visitas deben caber en una "
        "jornada de 11 horas con 6 a 8 atractivos.",
        "<b>Held-Karp</b> (programación dinámica sobre subconjuntos) da el óptimo. Se compara con la "
        "<b>fuerza bruta</b> (todas las permutaciones) y con la heurística del <b>vecino más cercano</b>. "
        "Si el día no cabe, se quitan atractivos con un criterio del grupo.",
        "Fuerza bruta: <b>O(k!)</b> órdenes. Held-Karp: tiempo <b>O(k² · 2^k)</b> y memoria "
        "<b>O(k · 2^k)</b>. Vecino más cercano: <b>O(k²)</b>, sin garantía de óptimo.",
        [("Held-Karp", ms(c["hk_ms"]), f"mediana con k = {c['hk_k']}", True),
         ("Fuerza bruta", ms(c["fb_ms"]), f"con k = {c['fb_k']}"
          + (f"; k = {c['fb_incompletas'][0]} no terminó" if c.get("fb_incompletas") else ""))]
        + ([("Heurística, promedio", f"{num(c['cal_prom_min'], 1)} a {num(c['cal_prom_max'], 1)} %",
             "alejamiento del óptimo según k"),
            ("Heurística, peor caso", f"{num(c['cal_max'], 1)} %", f"en {c['cal_instancias']} instancias")]
           if "cal_max" in c else [])
        if "hk_ms" in c else [])


# =======================================================================================
# 2. Simulaciones
# =======================================================================================
def _ir(clave, paso):
    st.session_state[clave] = paso


def _control_pasos(clave, total):
    """Botones para recorrer una traza. Devuelve el índice del paso actual."""
    actual = max(0, min(st.session_state.get(clave, 0), total - 1))
    st.session_state[clave] = actual
    with st.container(horizontal=True):
        st.button("Reiniciar", key=clave + "_ini", on_click=_ir, args=(clave, 0), disabled=actual == 0)
        st.button("Anterior", key=clave + "_ant", on_click=_ir, args=(clave, actual - 1), disabled=actual == 0)
        st.button("Siguiente", key=clave + "_sig", on_click=_ir, args=(clave, actual + 1), type="primary",
                  disabled=actual == total - 1)
        st.button("Ir al final", key=clave + "_fin", on_click=_ir, args=(clave, total - 1),
                  disabled=actual == total - 1)
    st.progress((actual + 1) / total, text=f"Paso {actual + 1} de {total}")
    return actual


# Dónde se escribe, respecto del centro de cada nodo del grafo de ejemplo, el tiempo y el rótulo
# de origen o destino: ((dx, dy, alineación) del tiempo, (dx, dy, alineación) del rótulo).
_ROTULOS = [
    ((-34, 6, "end"), (0, -36, "middle")),      # 0
    ((0, -36, "middle"), (34, -14, "start")),   # 1
    ((0, 48, "middle"), (-34, 6, "end")),       # 2
    ((0, 48, "middle"), (0, -36, "middle")),    # 3
    ((0, 48, "middle"), (0, -36, "middle")),    # 4
    ((34, 6, "start"), (0, 48, "middle")),      # 5
]


def _svg_grafo(adj, pos, paso, origen, destino):
    """Dibuja el grafo de ejemplo con el estado de un paso de Dijkstra."""
    ancho, alto, radio = 700, 350, 26
    n = len(adj)
    relajadas = {(paso["u"], r["v"]): r for r in paso["relajaciones"]}
    arbol = {(paso["pred"][v], v) for v in range(n) if paso["pred"][v] != -1}
    partes = [f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {ancho} {alto}" width="{ancho}" height="{alto}">']
    for u, vecinos in enumerate(adj):
        for v, w in vecinos:
            color, grosor, trazo = BORDE_FUERTE, 1.5, ""
            if (u, v) in arbol:
                color, grosor = TINTA, 2.5
            if (u, v) in relajadas:
                mejora = relajadas[(u, v)]["mejora"]
                color, grosor = (AZUL, 4) if mejora else (BERMELLON, 3)
                trazo = "" if mejora else ' stroke-dasharray="7 5"'
            (x1, y1), (x2, y2) = pos[u], pos[v]
            largo = math.hypot(x2 - x1, y2 - y1)
            ux, uy = (x2 - x1) / largo, (y2 - y1) / largo
            ax, ay = x1 + ux * radio, y1 + uy * radio                    # sale del borde del nodo u
            bx, by = x2 - ux * (radio + 9), y2 - uy * (radio + 9)        # llega antes de la punta
            px, py = x2 - ux * radio, y2 - uy * radio                    # punta de la flecha
            partes.append(f'<line x1="{ax:.1f}" y1="{ay:.1f}" x2="{bx:.1f}" y2="{by:.1f}" stroke="{color}" '
                          f'stroke-width="{grosor}"{trazo}/>')
            partes.append(f'<polygon points="{px:.1f},{py:.1f} {bx - uy * 5:.1f},{by + ux * 5:.1f} '
                          f'{bx + uy * 5:.1f},{by - ux * 5:.1f}" fill="{color}"/>')
            mx, my = (x1 + x2) / 2, (y1 + y2) / 2
            partes.append(f'<rect x="{mx - 13:.1f}" y="{my - 12:.1f}" width="26" height="24" fill="{FONDO}"/>'
                          f'<text x="{mx:.1f}" y="{my + 6:.1f}" text-anchor="middle" font-family="{FUENTE_MONO}" '
                          f'font-size="16" fill="{color if (u, v) in relajadas else TINTA_2}">{w:g}</text>')
    for i, (x, y) in enumerate(pos):
        es_actual = paso["u"] == i and paso["tipo"] in ("sacar", "destino")
        if es_actual:
            relleno, borde, grosor, texto = TINTA, TINTA, 2, FONDO
        elif paso["hecho"][i]:
            relleno, borde, grosor, texto = AZUL, AZUL, 2, FONDO
        elif paso["dist"][i] != INF:
            relleno, borde, grosor, texto = FONDO, AZUL, 3.5, TINTA
        else:
            relleno, borde, grosor, texto = FONDO, BORDE_FUERTE, 1.5, TINTA_2
        partes.append(f'<circle cx="{x}" cy="{y}" r="{radio}" fill="{relleno}" stroke="{borde}" stroke-width="{grosor}"/>'
                      f'<text x="{x}" y="{y + 7}" text-anchor="middle" font-family="{FUENTE}" font-size="20" '
                      f'font-weight="600" fill="{texto}">{i}</text>')
        # El tiempo y el rótulo van en el lado del nodo donde no pasa ninguna arista
        (tx, ty, ancla), (rx, ry, ancla_r) = _ROTULOS[i]
        partes.append(f'<text x="{x + tx}" y="{y + ty}" text-anchor="{ancla}" font-family="{FUENTE_MONO}" '
                      f'font-size="16" fill="{TINTA}">t = {sim._n(paso["dist"][i])}</text>')
        rotulo = "origen" if i == origen else ("destino" if i == destino else "")
        if rotulo:
            partes.append(f'<text x="{x + rx}" y="{y + ry}" text-anchor="{ancla_r}" font-family="{FUENTE}" '
                          f'font-size="13" font-weight="600" letter-spacing="1" fill="{TINTA_2}">'
                          f'{rotulo.upper()}</text>')
    partes.append("</svg>")
    return "".join(partes)


def _sim_dijkstra(c):
    st.write("Grafo de 6 nodos resuelto a mano en la especificación de R2 (el mismo de las pruebas "
             "unitarias). Avance paso a paso y observe cómo cambian los tiempos y la cola.")
    c1, c2, c3 = st.columns(3)
    version = c1.selectbox("Versión", ["Cola de prioridad", "Búsqueda lineal"], key="sd_version")
    origen = c2.selectbox("Origen", range(6), key="sd_origen", format_func=lambda i: f"Nodo {i}")
    destino = c3.selectbox("Destino", [None] + list(range(6)), key="sd_destino",
                           format_func=lambda i: "Ninguno (recorrer todo)" if i is None else f"Nodo {i}")
    con_cola = version.startswith("Cola")
    traza = (sim.traza_dijkstra_cola if con_cola else sim.traza_dijkstra_lineal)(sim.GRAFO_EJEMPLO, origen, destino)
    i = _control_pasos(f"sd_{con_cola}_{origen}_{destino}", len(traza))
    paso = traza[i]
    st.info(paso["texto"])

    izq, der = st.columns([3, 2], gap="large")
    with izq:
        estilo.svg(_svg_grafo(sim.GRAFO_EJEMPLO, sim.POS_GRAFO, paso, origen, destino),
                   "Grafo de ejemplo con el estado del paso actual: " + paso["texto"])
        estilo.leyenda([(TINTA, "Nodo que sale en este paso"), (AZUL, "Tiempo definitivo"),
                        (FONDO, "Pendiente"), (AZUL, "Arista que mejora un tiempo (línea gruesa)"),
                        (BERMELLON, "Arista revisada que no mejora (línea punteada)")])
    with der:
        filas, nuevas = [], set()
        mejoradas = {r["v"] for r in paso["relajaciones"] if r["mejora"]}
        for v in range(6):
            estado = "definitivo" if paso["hecho"][v] else ("pendiente" if paso["dist"][v] != INF else "sin alcanzar")
            filas.append([str(v), sim._n(paso["dist"][v]), "—" if paso["pred"][v] == -1 else str(paso["pred"][v]), estado])
            if v in mejoradas:
                nuevas |= {(v, 1), (v, 2)}
        estilo.tabla_html(["Nodo", "Tiempo", "Llegó desde", "Estado"], filas, numericas={1, 2},
                          fila_actual=paso["u"] if paso["tipo"] in ("sacar", "destino") else None, nuevas=nuevas)
        if con_cola:
            cola = ", ".join(f"({sim._n(d)}, {v})" for d, v in paso["cola"]) or "vacía"
            estilo.ficha("Cola de prioridad · (tiempo, nodo)", f'<span class="rp-mono">{e(cola)}</span>')
        for r in paso["relajaciones"]:
            signo = "mejora" if r["mejora"] else "no mejora"
            st.caption(f"Arista {paso['u']} → {r['v']}: {sim._n(r['nuevo'] - r['w'])} + {sim._n(r['w'])} = "
                       f"{sim._n(r['nuevo'])}, frente a {sim._n(r['antes'])}: {signo}.")
    ultimo = traza[-1]
    estilo.tarjetas([
        ("Nodos explorados", f"{paso['explorados']} de {ultimo['explorados']}", "hasta este paso"),
        ("Inserciones y extracciones de la cola" if con_cola else "Posiciones revisadas buscando el mínimo",
         str(paso["comparaciones"]), f"al terminar: {ultimo['comparaciones']}"),
    ])
    st.caption("Cambie de versión con el mismo origen y destino: las dos exploran los mismos nodos y dan los "
               "mismos tiempos. Lo que cambia es el trabajo para elegir el siguiente nodo: la lineal revisa "
               "los 6 nodos en cada paso."
               + (f" En la red real son {num(c['V'])} nodos por paso, y esa es la diferencia que se ve en "
                  "las mediciones." if "V" in c else ""))


def _svg_envolvente(unicos, paso):
    """Dibuja los puntos y el estado de un paso del divide y vencerás."""
    ancho, alto, margen = 640, 400, 26

    def sx(x):
        return margen + x / 100 * (ancho - 2 * margen)

    def sy(y):
        return alto - margen - y / 100 * (alto - 2 * margen)

    def figura(puntos, atributos):
        if len(puntos) >= 3:
            return f'<polygon points="{" ".join(f"{sx(x):.1f},{sy(y):.1f}" for x, y in puntos)}" {atributos}/>'
        if len(puntos) == 2:
            (x1, y1), (x2, y2) = puntos
            return f'<line x1="{sx(x1):.1f}" y1="{sy(y1):.1f}" x2="{sx(x2):.1f}" y2="{sy(y2):.1f}" {atributos}/>'
        return ""

    lo, hi = paso["lo"], paso["hi"]
    partes = [f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {ancho} {alto}" width="{ancho}" height="{alto}">',
              f'<rect x="0.5" y="0.5" width="{ancho - 1}" height="{alto - 1}" fill="{FONDO}" stroke="{BORDE_FUERTE}" stroke-width="1"/>']
    # Franja del subproblema activo
    x_izq, x_der = sx(unicos[lo][0]) - 9, sx(unicos[hi - 1][0]) + 9
    partes.append(f'<rect x="{x_izq:.1f}" y="1" width="{x_der - x_izq:.1f}" height="{alto - 2}" fill="{FONDO_2}"/>')
    if "medio" in paso:
        xm = (sx(unicos[paso["medio"] - 1][0]) + sx(unicos[paso["medio"]][0])) / 2
        partes.append(f'<line x1="{xm:.1f}" y1="1" x2="{xm:.1f}" y2="{alto - 1}" stroke="{TINTA_3}" '
                      'stroke-width="1.5" stroke-dasharray="6 5"/>')
    for mitad in (paso["izq"], paso["der"]):
        partes.append(figura(mitad, f'fill="none" stroke="{TINTA_2}" stroke-width="1.5" stroke-dasharray="5 4"'))
    partes.append(figura(paso["casco"], f'fill="{AZUL}" fill-opacity="0.08" stroke="{AZUL}" stroke-width="2.5"'))
    en_casco = set(paso["casco"])
    en_mitades = set(paso["izq"]) | set(paso["der"])
    for n, (x, y) in enumerate(unicos):
        activo = lo <= n < hi
        if (x, y) in en_casco:
            partes.append(f'<circle cx="{sx(x):.1f}" cy="{sy(y):.1f}" r="5.5" fill="{AZUL}"/>')
        elif (x, y) in en_mitades:
            partes.append(f'<circle cx="{sx(x):.1f}" cy="{sy(y):.1f}" r="5" fill="{FONDO}" stroke="{BERMELLON}" stroke-width="2.5"/>')
        elif activo:
            partes.append(f'<circle cx="{sx(x):.1f}" cy="{sy(y):.1f}" r="4" fill="{TINTA}"/>')
        else:
            partes.append(f'<circle cx="{sx(x):.1f}" cy="{sy(y):.1f}" r="3.5" fill="{BORDE_FUERTE}"/>')
    partes.append("</svg>")
    return "".join(partes)


def _sim_envolvente():
    st.write("Puntos al azar dentro de un cuadrado. La simulación usa las mismas funciones que el "
             "proyecto y muestra cada división, cada caso base y cada unión.")
    c1, c2 = st.columns(2)
    n = c1.slider("Número de puntos", 6, 28, 14, key="se_n")
    semilla = c2.number_input("Semilla", 1, 9999, 2026, key="se_semilla",
                              help="Con la misma semilla salen siempre los mismos puntos.")
    unicos, traza = sim.traza_envolvente(sim.puntos_al_azar(n, int(semilla)))
    i = _control_pasos(f"se_{n}_{semilla}", len(traza))
    paso = traza[i]
    st.info(paso["texto"])
    izq, der = st.columns([3, 2], gap="large")
    with izq:
        estilo.svg(_svg_envolvente(unicos, paso), "Puntos y envolvente del paso actual: " + paso["texto"])
        estilo.leyenda([(FONDO_2, "Puntos del subproblema actual (franja)"), (AZUL, "Envolvente de este paso"),
                        (BERMELLON, "Vértice de una mitad descartado al unir (borde)"),
                        (BORDE_FUERTE, "Puntos fuera del subproblema")])
    with der:
        nombres = {"dividir": "Dividir", "base": "Caso base", "unir": "Unir"}
        estilo.tarjetas([
            ("Operación", nombres[paso["tipo"]], f"nivel de recursión {paso['nivel']}", True),
            ("Puntos del subproblema", str(paso["hi"] - paso["lo"]), f"posiciones {paso['lo'] + 1} a {paso['hi']} de {len(unicos)}"),
        ])
        if paso["tipo"] == "unir":
            estilo.tarjetas([
                ("Vértices candidatos", str(paso["candidatos"]), f"{len(paso['izq'])} de la izquierda y {len(paso['der'])} de la derecha"),
                ("Vértices que quedan", str(len(paso["casco"])), f"se descartan {paso['candidatos'] - len(paso['casco'])}"),
            ])
        conteo = {t: sum(1 for p in traza if p["tipo"] == t) for t in nombres}
        st.caption(f"En total: {conteo['dividir']} divisiones, {conteo['base']} casos base y {conteo['unir']} "
                   f"uniones. La envolvente final tiene {len(traza[-1]['casco'])} vértices.")
    st.caption("Al unir no se revisan todos los puntos del subproblema: solo los vértices de las dos "
               "envolventes ya resueltas. Por eso cada unión cuesta O(h) y el total es O(n log n).")


def _casos_tsp():
    """Devuelve (T, inicio, lugares, etiqueta, formato, unidad) según la fuente elegida."""
    fuente = st.radio("Datos", ["Caso de la especificación (4 lugares)", "Lugares del catálogo"],
                      horizontal=True, key="st_fuente")
    base = datos.catalogo_y_matriz()
    if fuente.startswith("Caso") or not base:
        if not fuente.startswith("Caso"):
            st.caption("No se encontró la matriz de tiempos; se usa el caso de la especificación.")
        return (sim.MATRIZ_EJEMPLO, 0, [1, 2, 3], lambda i: f"Lugar {i}", lambda x: "—" if x == INF else f"{x:g}",
                "unidades de tiempo")
    cat, ids, T = base
    nombre = {r["id"]: r["nombre"] for r in cat}
    atr = [i for i in ids if i.startswith("ATR")]
    c1, c2 = st.columns([1, 2])
    partidas = [i for i in ids if not i.startswith("ATR")]      # la partida no puede ser un lugar a visitar
    inicio = c1.selectbox("Partida", partidas, index=partidas.index("CAB01") if "CAB01" in partidas else 0,
                          format_func=lambda i: f"{nombre[i]} ({i})", key="st_inicio")
    elegidos = c2.multiselect("Lugares a visitar (de 3 a 5)", atr, default=atr[:4],
                              format_func=lambda i: f"{nombre[i]} ({i})", key="st_lugares", max_selections=5)
    if len(elegidos) < 3:
        st.warning("Elija al menos 3 lugares para ver la simulación.")
        return None
    pos = {i: n for n, i in enumerate(ids)}
    return (T, pos[inicio], [pos[a] for a in elegidos], lambda i: ids[i],
            lambda x: "—" if x == INF else num(x / 60, 1), "minutos")


def _ruta_texto(ruta, etiqueta):
    return " → ".join(etiqueta(i) for i in ruta)


def _sim_vecino(T, inicio, lugares, etiqueta, fmt, unidad, clave):
    traza = sim.traza_vecino(T, inicio, lugares)
    i = _control_pasos("sv_" + clave, len(traza))
    paso = traza[i]
    if paso["tipo"] == "elegir":
        st.info(f"Desde {etiqueta(paso['actual'])} se compara el tiempo a cada lugar pendiente y se elige el "
                f"menor: {etiqueta(paso['elegido'])} ({fmt(paso['costo'])}).")
    else:
        st.info(f"No quedan lugares pendientes: se regresa a la partida desde {etiqueta(paso['actual'])} "
                f"({fmt(paso['costo'])}).")
    nodos = [inicio] + list(lugares)
    visitados = set(paso["ruta"][:-1]) if paso["tipo"] == "elegir" else set(paso["ruta"])
    filas, nuevas, tenues = [], set(), set()
    for f, a in enumerate(nodos):
        filas.append([etiqueta(a)] + [fmt(T[a][b]) if a != b else "·" for b in nodos])
        for col, b in enumerate(nodos):
            if a == paso["actual"] and b == paso["elegido"]:
                nuevas.add((f, col + 1))
            elif a == paso["actual"] and (b in visitados or a == b) and b != paso["elegido"]:
                tenues.add((f, col + 1))
    estilo.tabla_html(["Desde \\ hacia"] + [etiqueta(b) for b in nodos], filas,
                      numericas=set(range(1, len(nodos) + 1)), fila_actual=nodos.index(paso["actual"]),
                      nuevas=nuevas, tenues=tenues)
    st.caption(f"Matriz de tiempos en {unidad}. La fila resaltada es el lugar actual; la celda subrayada, la "
               "decisión de este paso; en gris, los lugares ya visitados.")
    estilo.tarjetas([
        ("Recorrido hasta ahora", _ruta_texto(paso["ruta"], etiqueta), "", True),
        ("Tiempo acumulado", fmt(paso["acumulado"]), unidad),
    ])
    return traza[-1]["acumulado"]


def _sim_held_karp(T, inicio, lugares, etiqueta, fmt, unidad, clave):
    k = len(lugares)
    traza = sim.traza_held_karp(T, inicio, lugares)
    i = _control_pasos("sh_" + clave, len(traza))
    paso = traza[i]

    def conjunto(mascara):
        return "{" + ", ".join(etiqueta(lugares[j]) for j in range(k) if (mascara >> j) & 1) + "}"

    if paso["tipo"] == "base":
        st.info("Caso base: ir directo de la partida a cada lugar. Son los subconjuntos de un solo lugar.")
    elif paso["tipo"] == "extender":
        st.info(f"Se extiende el subconjunto {conjunto(paso['mascara'])}: desde cada último lugar posible se "
                "prueba ir a cada lugar que todavía falta, y se guarda el costo si mejora el que había.")
    elif paso["tipo"] == "cierre":
        st.info("Cierre: con todos los lugares visitados, se suma el regreso a la partida desde cada último "
                "lugar posible y se toma el menor total.")
    else:
        st.info("Reconstrucción: se retrocede por la tabla de predecesores para obtener el orden de visita.")

    mascaras = sim.subconjuntos_ordenados(k)
    filas, nuevas = [], set()
    for f, m in enumerate(mascaras):
        filas.append([conjunto(m)] + [fmt(paso["C"][m][j]) for j in range(k)])
        for j in range(k):
            if (m, j) in paso["nuevos"]:
                nuevas.add((f, j + 1))
    izq, der = st.columns([3, 2], gap="large")
    with izq:
        estilo.tabla_html(["Visitados \\ termina en"] + [etiqueta(lugares[j]) for j in range(k)], filas,
                          numericas=set(range(1, k + 1)),
                          fila_actual=mascaras.index(paso["mascara"]) if paso["mascara"] else None, nuevas=nuevas)
        st.caption(f"Tabla C en {unidad}: cada fila es un conjunto de lugares ya visitados y cada columna, el "
                   f"lugar donde se termina ({2 ** k - 1} filas por {k} columnas). «—» es un estado imposible "
                   "o todavía sin calcular. Las celdas subrayadas cambiaron en este paso.")
    with der:
        if paso["tipo"] == "extender":
            estilo.tabla_html(
                ["De", "A", "C + salto", "Costo", "¿Mejora?"],
                [[etiqueta(lugares[t["j"]]), etiqueta(lugares[t["n"]]), f"{fmt(t['base'])} + {fmt(t['salto'])}",
                  fmt(t["costo"]), "sí" if t["mejora"] else f"no ({fmt(t['antes'])})"] for t in paso["transiciones"]],
                numericas={2, 3})
        elif paso["tipo"] == "cierre":
            estilo.tabla_html(
                ["Último lugar", "C + regreso", "Total"],
                [[etiqueta(lugares[t["j"]]), f"{fmt(t['base'])} + {fmt(t['regreso'])}", fmt(t["total"])]
                 for t in paso["cierres"]],
                numericas={1, 2}, fila_actual=paso["mejor_j"])
        elif paso["tipo"] == "reconstruir":
            estilo.tarjetas([("Recorrido óptimo", _ruta_texto(paso["ruta"], etiqueta), "", True),
                             ("Tiempo total", fmt(paso["total"]), unidad)])
        llenas = sum(1 for fila in paso["C"] for x in fila if x != INF)
        estilo.tarjetas([("Estados calculados", f"{llenas} de {k * 2 ** (k - 1)}", "celdas posibles: k · 2^(k−1)"),
                         ("Órdenes que probaría la fuerza bruta", num(math.factorial(k)), f"k! con k = {k}")])
    return traza[-1]["total"]


def _sim_tsp():
    st.write("El mismo problema resuelto de dos formas: la heurística decide mirando solo el siguiente "
             "paso; Held-Karp guarda el mejor resultado de cada subconjunto y con eso garantiza el óptimo.")
    caso = _casos_tsp()
    if caso is None:
        return
    T, inicio, lugares, etiqueta, fmt, unidad = caso
    clave = f"{inicio}_{'_'.join(map(str, lugares))}"
    metodo = st.radio("Algoritmo", ["Vecino más cercano", "Held-Karp"], horizontal=True, key="st_metodo")
    if metodo.startswith("Vecino"):
        _sim_vecino(T, inicio, lugares, etiqueta, fmt, unidad, clave)
    else:
        _sim_held_karp(T, inicio, lugares, etiqueta, fmt, unidad, clave)
    total_vm = sim.traza_vecino(T, inicio, lugares)[-1]
    total_hk = sim.traza_held_karp(T, inicio, lugares)[-1]
    dif = total_vm["acumulado"] - total_hk["total"]
    st.subheader("Resultado final de cada algoritmo en este caso")
    estilo.tarjetas([
        ("Held-Karp (óptimo)", fmt(total_hk["total"]), _ruta_texto(total_hk["ruta"], etiqueta), True),
        ("Vecino más cercano", fmt(total_vm["acumulado"]), _ruta_texto(total_vm["ruta"], etiqueta)),
        ("Diferencia", "ninguna" if dif == 0 else f"+ {fmt(dif)}",
         "la heurística encontró el óptimo" if dif == 0 else f"{num(dif / total_hk['total'] * 100, 1)} % sobre el óptimo"),
    ])


def _simulaciones(c):
    st.caption("Úsela para mostrar cómo avanza cada algoritmo paso a paso. Elija uno y avance con Siguiente.")
    cual = st.radio("Algoritmo a simular",
                    ["Dijkstra (R2)", "Envolvente convexa (R3)", "Vecino más cercano y Held-Karp (R4)"],
                    horizontal=True, key="sim_cual")
    if cual.startswith("Dijkstra"):
        _sim_dijkstra(c)
    elif cual.startswith("Envolvente"):
        _sim_envolvente()
    else:
        _sim_tsp()


# =======================================================================================
# 3. Comparaciones
# =======================================================================================
def _medir_memoria_hk():
    """Pico de memoria de Held-Karp con tracemalloc, igual que src/ruta_optima/memoria_hk.py."""
    import tracemalloc
    from src.ruta_optima.medicion import SEMILLA
    from src.ruta_optima.tsp import held_karp

    _, ids, T = datos.catalogo_y_matriz()
    inicio = ids.index("CAB01")
    otros = [i for i in range(len(ids)) if i != inicio]
    random.Random(SEMILLA).shuffle(otros)
    filas = []
    for k in (8, 10, 12):
        tracemalloc.start()
        held_karp(T, inicio, otros[:k])
        _, pico = tracemalloc.get_traced_memory()
        tracemalloc.stop()
        filas.append((k, pico / 1024 / 1024))
    return filas


def _comparaciones(c):
    st.write("Las gráficas se generan aquí desde los CSV de `resultados/`. Debajo de cada una están la "
             "máquina y las condiciones en que se midió. Pase el cursor sobre un punto para ver su valor.")

    # Cifras clave: salen de los mismos CSV que las gráficas; si falta alguno, esa tarjeta no se muestra.
    clave = []
    if "hk_k" in c and "hk_ms" in c:
        clave.append(("Held-Karp, k más grande medido", f"k = {c['hk_k']}", f"mediana de {ms(c['hk_ms'])}"))
    if "env_coc" in c:
        clave.append(("Envolvente propia frente a SciPy", f"{num(c['env_coc'], 1)} ×",
                      "veces el tiempo de SciPy, con los nodos de la red"))
    if "cal_max" in c:
        clave.append(("Peor caso de la heurística", f"{num(c['cal_max'], 2)} %",
                      "más tarda que el óptimo de Held-Karp"))
    if clave:
        estilo.tarjetas(clave)

    # --- R2
    st.subheader("Dijkstra: cola de prioridad frente a búsqueda lineal")
    r2 = datos.csv(datos.res("r2_mediciones.csv"))
    if r2 is None:
        estilo.falta_archivo(datos.res("r2_mediciones.csv"))
    else:
        estilo.grafica(graficas.r2_tiempos(r2), 340)
        estilo.ficha("Qué mirar",
                     "Las dos versiones exploran los mismos nodos; lo que cambia es cuánto cuesta elegir el "
                     "siguiente. El eje vertical es logarítmico: cada división multiplica el tiempo por 10."
                     + _si(c, "coc_mediana coc_minimo coc_maximo",
                           f" El cociente lineal / cola tiene mediana <b>{num(c.get('coc_mediana', 0), 1)}</b>, "
                           f"mínimo {num(c.get('coc_minimo', 0), 1)} y máximo {num(c.get('coc_maximo', 0), 1)}."))
        with st.expander("Cociente lineal / cola en cada par medido con las dos versiones"):
            estilo.grafica(graficas.r2_cociente(r2), 300)
    bloque_maquina("r1_r2_maquina.txt")

    # --- R3
    st.subheader("Envolvente convexa: versión propia frente a SciPy")
    r3 = datos.csv(datos.res("r3_tiempos.csv"))
    if r3 is None:
        estilo.falta_archivo(datos.res("r3_tiempos.csv"), datos.COMANDOS["r3_tiempos.csv"])
    else:
        estilo.grafica(graficas.r3_tiempos(r3), 340)
        estilo.ficha("Qué mirar",
                     "Con los dos ejes logarítmicos, la versión propia crece de forma casi recta, como se "
                     "espera de O(n log n). SciPy es más rápido en todos los tamaños porque Qhull está "
                     "escrito en C y la versión propia en Python"
                     + _si(c, "env_coc_min env_coc_max",
                           f": entre <b>{num(c.get('env_coc_min', 0), 1)}</b> y "
                           f"<b>{num(c.get('env_coc_max', 0), 1)}</b> veces según el conjunto")
                     + ". Las dos dan los mismos vértices en todas las pruebas.")
    bloque_maquina("r3_maquina.txt")

    # --- R4
    st.subheader("Ruta óptima: fuerza bruta frente a Held-Karp")
    ex = datos.csv(datos.res("r4_exactas.csv"))
    if ex is None:
        estilo.falta_archivo(datos.res("r4_exactas.csv"), datos.COMANDOS["r4_exactas.csv"])
    else:
        estilo.grafica(graficas.r4_exactas(ex), 340)
        estilo.ficha("Qué mirar",
                     "Los dos métodos dan el mismo tiempo óptimo, pero la fuerza bruta crece como k! y "
                     "Held-Karp como k² · 2^k."
                     + _si(c, "fb_k fb_ms hk_en_fb_k",
                           f" Con k = {c.get('fb_k')}, la fuerza bruta tardó <b>{ms(c.get('fb_ms', 0))}</b> y "
                           f"Held-Karp <b>{ms(c.get('hk_en_fb_k') or 0)}</b>.")
                     + (f" Con k = {c['fb_incompletas'][0]} la fuerza bruta no terminó dentro del límite de "
                        "5 minutos y no aparece en la gráfica." if c.get("fb_incompletas") else ""))
    st.subheader("Held-Karp frente a la heurística del vecino más cercano")
    det = datos.csv(datos.res("r4_calidad_detalle.csv"))
    resumen = datos.csv(datos.res("r4_calidad_resumen.csv"))
    if det is None or resumen is None:
        estilo.falta_archivo(datos.res("r4_calidad_resumen.csv"), datos.COMANDOS["r4_calidad_resumen.csv"])
    else:
        estilo.grafica(graficas.r4_calidad(det, resumen), 300)
        estilo.ficha("Qué mirar",
                     "Cada cuadrado es una instancia y la raya es el promedio de su k. El alejamiento es "
                     "cuánto más tarda el recorrido de la heurística respecto del óptimo de Held-Karp."
                     + _si(c, "cal_prom_min cal_prom_max cal_max",
                           f" El promedio va de {num(c.get('cal_prom_min', 0), 2)} % a "
                           f"{num(c.get('cal_prom_max', 0), 2)} % según k, y el peor caso es "
                           f"<b>{num(c.get('cal_max', 0), 2)} %</b>.")
                     + " Con tan pocas instancias por k, el promedio no tiene por qué crecer de forma regular.")
    bloque_maquina("r4_maquina.txt")

    with st.expander("Medir ahora la memoria de la tabla de Held-Karp"):
        st.write("Repite `python -m src.ruta_optima.memoria_hk` en este equipo: pico de memoria con "
                 "`tracemalloc` para k = 8, 10 y 12, con los mismos lugares del experimento de tiempos.")
        if datos.catalogo_y_matriz() is None:
            estilo.falta_archivo(datos.MATRIZ, para_que="ejecutar Held-Karp")
        else:
            if st.button("Medir memoria", key="medir_hk"):
                with st.spinner("Midiendo..."):
                    st.session_state["mem_hk"] = _medir_memoria_hk()
            if st.session_state.get("mem_hk"):
                estilo.tarjetas([(f"k = {k}", f"{num(mb, 2)} MB", f"{num(k * 2 ** k)} celdas por tabla (k · 2^k)")
                                 for k, mb in st.session_state["mem_hk"]])
                st.caption("Medición en vivo, una sola ejecución en este equipo. Held-Karp usa dos tablas "
                           "de ese tamaño: costos y predecesores.")

    # --- R1
    st.subheader("Red vial: tiempo de la componente fuertemente conexa")
    r1 = datos.csv(datos.res("r1_componente.csv"))
    if r1 is None:
        estilo.falta_archivo(datos.res("r1_componente.csv"))
    else:
        estilo.grafica(graficas.r1_componente(r1), 300)
        estilo.ficha("Qué mirar", "El tiempo crece con el tamaño de la red. Las redes son círculos de radio "
                                  "creciente alrededor de la plaza de Bolívar de Armenia, más el departamento completo.")

    # Aviso sobre máquinas distintas
    procesadores = {}
    for archivo in ("r1_r2_maquina.txt", "r3_maquina.txt", "r4_maquina.txt"):
        pares = dict(datos.maquina(archivo) or [])
        if "Procesador" in pares:
            procesadores[archivo] = pares["Procesador"]
    if len(set(procesadores.values())) > 1:
        st.warning("Los experimentos no se midieron todos en el mismo equipo: "
                   + "; ".join(f"{a}: {p}" for a, p in procesadores.items())
                   + ". Cada comparación de esta página es válida porque sus dos métodos se midieron en la "
                     "misma máquina, pero no se deben comparar tiempos de un requerimiento con los de otro.")


# =======================================================================================
# 4. Decisiones y limitaciones
# =======================================================================================
def _desplegable(titulo, texto_html):
    """Un punto de decisión o límite: solo el título a la vista, el texto se abre con un clic."""
    with st.expander(titulo):
        st.html(f'<div class="rp-ficha"><p class="tx">{texto_html}</p></div>')


def _decisiones(c):
    st.caption("Cada punto se despliega con un clic: qué se decidió o qué límite tiene el trabajo, y por qué.")
    izq, der = st.columns(2, gap="large")
    with izq:
        st.subheader("Decisiones de diseño")
        _desplegable("Listas de adyacencia, no matriz",
                     "La red es dispersa: cada intersección conecta con muy pocas otras."
                     + _si(c, "mem_matriz mem_listas",
                           f" Con los supuestos de <code>src/red/memoria.py</code>, la matriz ocuparía "
                           f"{num(c.get('mem_matriz', 0), 1)} MB y las listas {num(c.get('mem_listas', 0), 2)} MB."))
        _desplegable("Solo la componente fuertemente conexa",
                     "Así siempre existe camino entre dos lugares y la matriz de tiempos no tiene celdas vacías."
                     + _si(c, "V V_antes", f" Se descartan {num(c.get('V_antes', 0) - c.get('V', 0))} nodos de "
                                           f"{num(c.get('V_antes', 0))}."))
        _desplegable("Cola con entradas perezosas",
                     "<code>heapq</code> no permite disminuir una clave. En vez de implementar esa operación, se "
                     "inserta una entrada nueva y la vieja se descarta al salir. El código queda corto y la "
                     "cota sigue siendo O((V + E) log V).")
        _desplegable("Aristas paralelas y bucles",
                     "Entre dos nodos con varios tramos se conserva el de menor tiempo; los bucles se "
                     "descartan porque nunca mejoran un camino.")
        _desplegable("Coordenadas enteras en UTM 18N",
                     "La envolvente decide cada giro con un producto cruzado. Con metros enteros el "
                     "resultado es exacto y los enteros de Python no desbordan.")
        _desplegable("Divide y vencerás para la envolvente",
                     "Su peor caso es O(n log n) sin importar cómo estén repartidos los puntos; Quickhull "
                     "puede degradarse a O(n²) y los nodos de una red vial están muy agrupados.")
        _desplegable("Comparar la heurística sobre los mismos atractivos",
                     "La heurística ordena los atractivos que dejó Held-Karp tras aplicar la jornada. Así la "
                     "diferencia entre los dos totales es solo de recorrido y no de qué se visitó.")
        _desplegable("Criterio para quitar atractivos",
                     "Si alguna salida hace que el día quepa, se quita el atractivo que deja el total más "
                     "cerca de las 11 h sin pasarse; si ninguna, el que más reduce el total. Busca conservar "
                     "la mayor cantidad de atractivos.")
        _desplegable("Librerías solo donde no está el algoritmo",
                     "OSMnx descarga y prepara la red; NetworkX y SciPy solo verifican; Streamlit y Folium "
                     "son la interfaz. Dijkstra, la envolvente, Held-Karp, la fuerza bruta y la heurística "
                     "son implementaciones propias.")
    with der:
        st.subheader("Limitaciones")
        _desplegable("Los tiempos son una estimación",
                     "Salen de la longitud de cada tramo y una velocidad por tipo de vía cuando OpenStreetMap "
                     "no la trae. No hay tráfico, semáforos ni estado de la vía.")
        _desplegable("De nodo a nodo, no de puerta a puerta",
                     "Cada lugar se representa por su nodo más cercano de la red."
                     + _si(c, "lejos lugares", f" {c.get('lejos')} de los {c.get('lugares')} lugares quedan a más "
                                               "de 500 m de su nodo; ese tramo no está en el tiempo."))
        _desplegable("Held-Karp no escala",
                     "La tabla crece como k · 2^k: cada lugar adicional duplica la memoria y más que duplica "
                     "el tiempo."
                     + _si(c, "hk_k hk_ms", f" Se midió hasta k = {c.get('hk_k')} ({ms(c.get('hk_ms', 0))}); para "
                                            "decenas de lugares haría falta otra técnica."))
        _desplegable("La heurística no garantiza nada",
                     "El vecino más cercano puede quedar lejos del óptimo."
                     + _si(c, "cal_max cal_instancias", f" En las {c.get('cal_instancias')} instancias medidas, el "
                                                        f"peor caso fue {num(c.get('cal_max', 0), 2)} %."))
        _desplegable("Python puro",
                     "Las implementaciones propias priorizan la claridad."
                     + _si(c, "env_coc", f" En la envolvente, SciPy (en C) fue {num(c.get('env_coc', 0), 1)} veces "
                                         "más rápido con los nodos de la red."))
        _desplegable("Alcance de las mediciones",
                     _si(c, "pares pares_lineal", f"La búsqueda lineal se midió en {c.get('pares_lineal')} de los "
                                                  f"{c.get('pares')} pares, los cercanos. ")
                     + (f"La fuerza bruta con k = {c['fb_incompletas'][0]} no terminó en 5 minutos. "
                        if c.get("fb_incompletas") else "")
                     + "No todos los requerimientos se midieron en el mismo equipo (ver Comparaciones).")
        _desplegable("La jornada es un modelo simple",
                     "Se suman traslados y visitas contra 11 horas. No se modelan horarios de apertura, "
                     "comidas ni descansos.")
        _desplegable("El mapa necesita internet",
                     "El fondo del mapa se descarga de un servidor de teselas. Sin conexión, los cálculos "
                     "funcionan pero el fondo queda en blanco.")


# =======================================================================================
# 5. Fuentes
# =======================================================================================
def _fuentes():
    st.caption("Antes de copiar una referencia al documento técnico, confirme el formato de cita que pide el curso.")
    st.subheader("Algoritmos")
    st.markdown(
        "- Dijkstra, E. W. (1959). A note on two problems in connexion with graphs. *Numerische Mathematik*, 1, 269–271.\n"
        "- Held, M. y Karp, R. M. (1962). A dynamic programming approach to sequencing problems. "
        "*Journal of the Society for Industrial and Applied Mathematics*, 10(1), 196–210.\n"
        "- Bellman, R. (1962). Dynamic programming treatment of the travelling salesman problem. "
        "*Journal of the ACM*, 9(1), 61–63.\n"
        "- Rosenkrantz, D. J., Stearns, R. E. y Lewis, P. M. (1977). An analysis of several heuristics for the "
        "traveling salesman problem. *SIAM Journal on Computing*, 6(3), 563–581.\n"
        "- Preparata, F. P. y Hong, S. J. (1977). Convex hulls of finite sets of points in two and three "
        "dimensions. *Communications of the ACM*, 20(2), 87–93.\n"
        "- Andrew, A. M. (1979). Another efficient algorithm for convex hulls in two dimensions. "
        "*Information Processing Letters*, 9(5), 216–219.\n"
        "- Barber, C. B., Dobkin, D. P. y Huhdanpaa, H. (1996). The Quickhull algorithm for convex hulls. "
        "*ACM Transactions on Mathematical Software*, 22(4), 469–483.\n"
        "- Cormen, T. H., Leiserson, C. E., Rivest, R. L. y Stein, C. *Introduction to Algorithms*. MIT Press. "
        "(Teorema maestro, Dijkstra y montículos binarios.)")
    st.subheader("Datos y herramientas")
    st.markdown(
        "- OpenStreetMap y sus colaboradores. Datos de la red vial, bajo licencia ODbL. "
        "[openstreetmap.org/copyright](https://www.openstreetmap.org/copyright)\n"
        "- Boeing, G. (2017). OSMnx: New methods for acquiring, constructing, analyzing, and visualizing "
        "complex street networks. *Computers, Environment and Urban Systems*, 65, 126–139. "
        "[osmnx.readthedocs.io](https://osmnx.readthedocs.io)\n"
        "- SciPy: `scipy.spatial.ConvexHull`, que se apoya en la librería Qhull. "
        "[docs.scipy.org](https://docs.scipy.org/doc/scipy/reference/generated/scipy.spatial.ConvexHull.html) · "
        "[qhull.org](http://www.qhull.org)\n"
        "- Python: módulo `heapq`. [docs.python.org](https://docs.python.org/3/library/heapq.html)\n"
        "- Streamlit, Folium y streamlit-folium para la interfaz; Altair para las gráficas; "
        "fondo del mapa: teselas estándar de OpenStreetMap.\n"
        "- Catálogo de lugares: la fuente de cada lugar está en la columna `fuente` de "
        "`data/catalogo/catalogo_lugares.csv`.")
    st.subheader("Diseño de la aplicación")
    st.markdown(
        "- IBM. Carbon Design System: tipografía y escala tipográfica. "
        "[carbondesignsystem.com](https://carbondesignsystem.com/elements/typography/overview/)\n"
        "- Okabe, M. e Ito, K. (2008). Color Universal Design: how to make figures and presentations that are "
        "friendly to colorblind people. [jfly.uni-koeln.de/color](https://jfly.uni-koeln.de/color/)\n"
        "- Wong, B. (2011). Points of view: Color blindness. *Nature Methods*, 8, 441.\n"
        "- W3C. Web Content Accessibility Guidelines (WCAG) 2.1, criterios 1.4.3 y 1.4.11. "
        "[w3.org/TR/WCAG21](https://www.w3.org/TR/WCAG21/)\n"
        "- Nielsen, J. (1994). 10 Usability Heuristics for User Interface Design. "
        "[nngroup.com](https://www.nngroup.com/articles/ten-usability-heuristics/)\n"
        "- La justificación completa está en `docs/guia_visual.md`.")
    st.subheader("Documentos del proyecto")
    st.markdown(
        "- Especificaciones de cada requerimiento: carpeta `specs/` (R1 a R5).\n"
        "- Mediciones, gráficas y descripción de las máquinas: carpeta `resultados/`.\n"
        "- Instrucciones de instalación y ejecución: `README.md`.")


# =======================================================================================
# Página
# =======================================================================================
def pagina():
    estilo.encabezado(
        "Sustentación",
        "Material para defender el proyecto: qué problema resuelve cada requerimiento, cómo funcionan "
        "los algoritmos paso a paso, qué dicen las mediciones y qué decisiones se tomaron.",
        "Defensa del proyecto")
    c = _cifras()
    secciones = st.tabs(["Recorrido R1–R4", "Simulaciones", "Comparaciones", "Decisiones y límites",
                         "Fuentes"])
    with secciones[0]:
        _recorrido(c)
    with secciones[1]:
        _simulaciones(c)
    with secciones[2]:
        _comparaciones(c)
    with secciones[3]:
        _decisiones(c)
    with secciones[4]:
        _fuentes()
