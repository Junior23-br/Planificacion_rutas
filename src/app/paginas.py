"""Páginas de la aplicación demostrativa (R5): Inicio, Ruta, Envolvente, Itinerario y Resultados.

La página de Sustentación está en src/app/sustentacion.py. El aspecto (colores, tarjetas,
panel "Cómo se calculó", mapas) está en src/app/estilo.py y la lectura de archivos en
src/app/datos.py. Aquí solo se decide qué se muestra y en qué orden.
"""
import glob
import os
import time

import pandas as pd
import streamlit as st

from src.app import datos, estilo, graficas
from src.app.estilo import ms, num

RESULTADOS = datos.RESULTADOS
ENLACES = {}          # nombre -> st.Page; lo llena app.py para los enlaces de la página de inicio


def registrar_enlaces(paginas):
    ENLACES.clear()
    ENLACES.update(paginas)


def fmt_tiempo(seg):
    """Segundos a texto legible: '1 h 05 min' o '12 min 30 s'.
    Desde una hora se redondea al minuto, igual que la salida por consola de
    src/ruta_optima/itinerario.py, para que la aplicación y la consola digan lo mismo."""
    seg = int(round(seg))
    if seg >= 3600:
        h, m = divmod(int(round(seg / 60)), 60)
        return f"{h} h {m:02d} min"
    m, s = divmod(seg, 60)
    return f"{m} min {s:02d} s"


def datos_red():
    """Grafo, lugares y coordenadas (en caché). Se conserva el nombre por compatibilidad."""
    return datos.red()


def datos_itinerario():
    """(catálogo, ids, T) en caché. Se conserva el nombre por compatibilidad."""
    return datos.catalogo_y_matriz()


def etiqueta_lugar(lugar):
    """Texto de un lugar en los selectores: el nombre primero, que es lo que la gente reconoce."""
    if lugar["nombre"] == lugar["municipio"]:
        return f'{lugar["nombre"]} · cabecera municipal ({lugar["id"]})'
    return f'{lugar["nombre"]} · {lugar["municipio"]} ({lugar["id"]})'


def _red_o_aviso():
    """Devuelve la red cargada, o None después de explicar qué falta."""
    faltan = datos.faltantes_red()
    if faltan:
        estilo.falta_archivo(", ".join(faltan), para_que="cargar la red vial y ubicar los lugares")
        st.caption("Estos archivos vienen en el repositorio. Si los borró, recupérelos con "
                   "`git checkout -- data/`.")
        return None
    try:
        return datos.red()
    except Exception as error:                      # archivo dañado, librería faltante...
        st.error(f"No se pudo cargar la red vial: {error}")
        st.caption("Compruebe la instalación con `python -m pip install -r requirements.txt` "
                   "y que `data/processed/componente.graphml` no esté dañado.")
        return None


def bloque_maquina(nombre):
    """Máquina y condiciones de una medición, leídas de resultados/<nombre>."""
    pares = datos.maquina(nombre)
    if not pares:
        estilo.estado_vacio("Falta la descripción de la máquina",
                            f"No se encontró resultados/{nombre}; sin ese archivo no se puede "
                            "decir en qué equipo se midió.")
        return
    cuerpo = "<br>".join(f"<b>{estilo.e(k)}:</b> {estilo.e(v)}" for k, v in pares)
    estilo.ficha(f"Máquina y condiciones de medición · resultados/{nombre}", cuerpo)


# =======================================================================================
# Inicio
# =======================================================================================
def inicio():
    estilo.encabezado(
        "Rutas del Paisaje Cultural Cafetero",
        "Planificación de rutas turísticas sobre la red vial del Quindío. Cada página usa un "
        "algoritmo implementado por el equipo y explica, al final, cómo llegó al resultado.",
        "Proyecto final · Análisis de Algoritmos")

    # Cifras del proyecto, leídas de los archivos (nada escrito a mano)
    items = []
    base = datos.catalogo_y_matriz()
    if base:
        cat, ids, _ = base
        cab = sum(1 for r in cat if r["id"].startswith("CAB"))
        atr = sum(1 for r in cat if r["id"].startswith("ATR"))
        items.append(("Lugares del catálogo", str(len(cat)),
                      f"{cab} cabeceras, {atr} atractivos y {len(cat) - cab - atr} fincas y centros de acopio"))
        items.append(("Matriz de tiempos", f"{len(ids)} × {len(ids)}", "tiempo de viaje entre cada par de lugares"))
    r1 = datos.csv(datos.res("r1_componente.csv"))
    if r1 is not None and (r1["red"] == "Departamento").any():
        dep = r1[r1["red"] == "Departamento"].iloc[0]
        items.insert(0, ("Nodos de la red", num(dep["V_despues"]), "intersecciones de la componente fuertemente conexa"))
        items.insert(1, ("Tramos de vía", num(dep["E_despues"]), "aristas dirigidas con tiempo de viaje"))
    if items:
        estilo.tarjetas(items)

    st.header("Qué puede hacer aquí")
    opciones = [
        ("Ruta", "Ruta más rápida (R2)", "R2 · Dijkstra con cola de prioridad",
         "Elija dos lugares y vea en el mapa el camino de menor tiempo, calculado en el momento."),
        ("Envolvente", "Envolvente convexa (R3)", "R3 · Divide y vencerás",
         "El menor polígono convexo que contiene toda la red vial del departamento."),
        ("Itinerario", "Itinerario de un día (R4)", "R4 · Held-Karp y vecino más cercano",
         "Ordene de 6 a 8 atractivos dentro de una jornada de 11 horas y compare el óptimo con la heurística."),
        ("Resultados", "Resultados de los experimentos", "R1 a R4 · Mediciones",
         "Tablas y gráficas de las mediciones, con la máquina y las condiciones en que se tomaron."),
        ("Sustentación", "Sustentación", "Defensa del proyecto",
         "Recorrido por los requerimientos, simulaciones paso a paso, comparaciones y decisiones de diseño."),
    ]
    for fila in range(0, len(opciones), 2):          # de a dos por fila; en pantallas angostas se apilan en orden
        columnas = st.columns(2, gap="large")
        for columna, (clave, titulo, ceja, texto) in zip(columnas, opciones[fila:fila + 2]):
            with columna:
                estilo.ficha(ceja, f"<b>{estilo.e(titulo)}.</b> {estilo.e(texto)}")
                if clave in ENLACES:
                    st.page_link(ENLACES[clave], label=f"Abrir {titulo.lower()} →")

    st.header("Antes de empezar")
    st.markdown(
        "- Los tiempos son una **estimación del modelo**, de nodo a nodo de la red: no incluyen "
        "tráfico, semáforos ni el tramo a pie hasta el lugar.\n"
        "- El fondo del mapa necesita conexión a internet; los cálculos no.\n"
        "- La primera consulta de ruta tarda unos segundos porque carga el grafo; después queda en memoria.")
    equipo = datos.integrantes()
    if equipo:
        st.caption(f"Integrantes: {equipo}. Universidad del Quindío.")


# =======================================================================================
# Ruta (R2)
# =======================================================================================
def _intercambiar():
    st.session_state["ruta_o"], st.session_state["ruta_d"] = (
        st.session_state["ruta_d"], st.session_state["ruta_o"])


def _panel_ruta(red, r):
    """Panel "Cómo se calculó" de la página Ruta, con los datos de la consulta r."""
    info = red["info"]
    V = info["V"]
    porcentaje = r["explorados"] / V * 100
    coc = datos.csv(datos.res("r2_cociente.csv"))
    frase_cociente = ""
    if coc is not None and (coc["estadistico"] == "mediana").any():
        mediana = float(coc[coc["estadistico"] == "mediana"]["valor"].iloc[0])
        frase_cociente = (f" En las mediciones del proyecto la versión con cola fue {num(mediana, 1)} "
                          "veces más rápida (mediana de los pares medidos con ambas).")
    r1 = datos.csv(datos.res("r1_componente.csv"))
    frase_memoria = ""
    if r1 is not None and (r1["red"] == "Departamento").any():
        dep = r1[r1["red"] == "Departamento"].iloc[0]
        m1, _, listas = datos.memoria_estimada(int(dep["V_antes"]), int(dep["E_antes"]))
        frase_memoria = (f" Con los supuestos de src/red/memoria.py, una matriz con un peso por celda "
                         f"ocuparía {num(m1, 1)} MB y las listas {num(listas, 2)} MB.")
    estilo.como_se_calculo(
        "La aplicación buscó, entre todas las formas de ir del origen al destino por la red, "
        "la que suma menos tiempo de viaje. No usa ninguna librería para el algoritmo.",
        [
            dict(paso="Camino de menor tiempo", nombre="Dijkstra con cola de prioridad",
                 complejidad="O((V + E) log V)",
                 que_hace="Parte del origen y va fijando, uno por uno, el nodo pendiente con menor tiempo "
                          "acumulado. Al fijarlo revisa sus tramos de salida y, si por ahí se llega antes a "
                          "un vecino, actualiza su tiempo. Se detiene en cuanto sale el destino, sin "
                          "recorrer el resto de la red.",
                 por_que="La otra versión implementada busca el mínimo recorriendo todos los nodos en cada "
                         "paso, O(V²). Con la cola, hallar el mínimo cuesta O(log V)." + frase_cociente),
            dict(paso="Elegir el siguiente nodo", nombre="Montículo binario (heapq) con entradas perezosas",
                 complejidad="O(log V) por operación",
                 que_hace="La cola guarda pares (tiempo, nodo). Cuando un nodo mejora no se busca su entrada "
                          "anterior: se inserta una nueva y la vieja se descarta cuando sale.",
                 por_que="heapq no permite disminuir una clave. Las entradas perezosas evitan esa operación "
                         "y mantienen el código corto; a cambio, la cola puede tener hasta una entrada por arista."),
            dict(paso="Armar el recorrido", nombre="Reconstrucción por predecesores",
                 complejidad="O(nodos de la ruta)",
                 que_hace="Cada nodo recuerda desde cuál se llegó a él con el menor tiempo. Al terminar se "
                          "retrocede desde el destino hasta el origen y se invierte la lista.",
                 por_que="Guardar un predecesor por nodo cuesta O(V) de memoria; guardar la ruta completa de "
                         "cada nodo costaría mucho más y no aporta nada."),
            dict(paso="Representación de la red", nombre="Listas de adyacencia",
                 complejidad="Memoria O(V + E)",
                 que_hace="Cada nodo guarda solo sus vecinos de salida y el tiempo de cada tramo. Entre "
                          "tramos paralelos se conserva el de menor tiempo y los bucles se descartan.",
                 por_que="La red es muy dispersa: cada intersección conecta con pocas otras, así que una "
                         "matriz estaría casi vacía." + frase_memoria),
        ],
        [
            ("Nodos explorados", f"{num(r['explorados'])} de {num(V)} ({num(porcentaje, 1)} %)"),
            ("Tiempo de cálculo", ms(r["ms"])),
            ("Nodos en la ruta", num(len(r["camino"]))),
            ("Tramos en el grafo (E)", num(info["E_final"])),
            ("Tiempo estimado", f"{num(r['tiempo_s'], 3)} s"),
        ],
        "Un nodo cuenta como explorado la primera vez que sale de la cola. El tiempo de cálculo es de una "
        "sola ejecución en este equipo y no incluye la carga del grafo ni el dibujo del mapa. La cota "
        "O((V + E) log V) se deduce del código de src/caminos/dijkstra.py: cada arista inserta como máximo "
        "una entrada en la cola.")


def _comparacion_lineal(red, r, lugares):
    """Opcional: repite la misma consulta con la búsqueda lineal para ver la diferencia en vivo."""
    from src.caminos.dijkstra import dijkstra_cola, dijkstra_lineal

    with st.expander("Comparar con la búsqueda lineal en esta misma consulta"):
        st.write("Ejecuta las dos versiones de Dijkstra sobre el mismo par y muestra cuánto tarda cada "
                 "una. La versión lineal puede tardar varios segundos.")
        if st.button("Ejecutar las dos versiones", key="ruta_comparar"):
            o, d = lugares[r["o"]]["idx"], lugares[r["d"]]["idx"]
            with st.spinner("Ejecutando Dijkstra con cola y con búsqueda lineal..."):
                t0 = time.perf_counter()
                dist_c, _, exp_c = dijkstra_cola(red["adj"], o, d)
                ms_c = (time.perf_counter() - t0) * 1000
                t0 = time.perf_counter()
                dist_l, _, exp_l = dijkstra_lineal(red["adj"], o, d)
                ms_l = (time.perf_counter() - t0) * 1000
            st.session_state["ruta_lineal"] = dict(par=(r["o"], r["d"]), ms_c=ms_c, ms_l=ms_l, exp_c=exp_c,
                                                   exp_l=exp_l, igual=abs(dist_c[d] - dist_l[d]) < 1e-9)
        c = st.session_state.get("ruta_lineal")
        if c and c["par"] == (r["o"], r["d"]):
            estilo.tarjetas([
                ("Con cola de prioridad", ms(c["ms_c"]), f"{num(c['exp_c'])} nodos explorados"),
                ("Con búsqueda lineal", ms(c["ms_l"]), f"{num(c['exp_l'])} nodos explorados"),
                ("Lineal / cola", f"{num(c['ms_l'] / c['ms_c'], 0)} ×", "veces más lenta la lineal"),
                ("Mismo tiempo de viaje", "Sí" if c["igual"] else "No", "las dos versiones deben coincidir"),
            ])
            st.caption("Una sola ejecución de cada versión en este equipo: sirve para ver el orden de "
                       "magnitud, no reemplaza las mediciones con protocolo de la página Resultados.")


def ruta():
    from src.caminos.dijkstra import ruta_minima
    import folium

    estilo.encabezado(
        "Ruta más rápida entre dos lugares (R2)",
        "Elija un origen y un destino del catálogo. El camino de menor tiempo se calcula en el momento "
        "sobre la red vial del Quindío.",
        "R2 · Caminos mínimos")
    red = _red_o_aviso()
    if red is None:
        return
    lugares = red["lugares"]
    indices = range(len(lugares))
    st.session_state.setdefault("ruta_o", 0)
    st.session_state.setdefault("ruta_d", 1)

    c1, c2, c3 = st.columns([5, 5, 2], vertical_alignment="bottom")
    o = c1.selectbox("Origen", indices, format_func=lambda i: etiqueta_lugar(lugares[i]), key="ruta_o",
                     help="Escriba parte del nombre para buscar.")
    d = c2.selectbox("Destino", indices, format_func=lambda i: etiqueta_lugar(lugares[i]), key="ruta_d",
                     help="Escriba parte del nombre para buscar.")
    c3.button("Intercambiar", on_click=_intercambiar, width="stretch",
              help="Pone el destino como origen y el origen como destino.")

    iguales = o == d
    if st.button("Calcular ruta", type="primary", disabled=iguales):
        with st.spinner("Calculando la ruta..."):
            t0 = time.perf_counter()
            tiempo_s, camino, explorados = ruta_minima(red["adj"], lugares[o]["idx"], lugares[d]["idx"])
            milis = (time.perf_counter() - t0) * 1000
        st.session_state["ruta"] = dict(o=o, d=d, tiempo_s=tiempo_s, camino=camino,
                                        explorados=explorados, ms=milis)
    if iguales:
        st.caption("El origen y el destino son el mismo lugar. Elija un destino distinto para calcular.")

    r = st.session_state.get("ruta")
    if not r:
        estilo.estado_vacio("Todavía no hay una ruta calculada",
                            "Elija origen y destino y pulse «Calcular ruta». Aquí aparecerán el tiempo "
                            "estimado, el mapa y la explicación del cálculo.")
        return
    nombre_o, nombre_d = lugares[r["o"]]["nombre"], lugares[r["d"]]["nombre"]
    if r["tiempo_s"] is None or r["tiempo_s"] == float("inf") or not r["camino"]:
        st.error(f"No hay ruta de {nombre_o} a {nombre_d}. No debería ocurrir en una red fuertemente "
                 "conexa: revise que data/processed/ no haya cambiado.")
        return

    st.header(f"{nombre_o} → {nombre_d}")
    if (r["o"], r["d"]) != (o, d):
        st.caption("La selección de arriba cambió. Este resultado es de la consulta anterior; pulse "
                   "«Calcular ruta» para actualizarlo.")

    # Comprobación contra la matriz de tiempos de R2 (mismo par, calculado por otro camino)
    nota_tiempo = "estimación del modelo, de nodo a nodo"
    base = datos.catalogo_y_matriz()
    if base:
        _, ids, T = base
        pos = {i: n for n, i in enumerate(ids)}
        id_o, id_d = lugares[r["o"]]["id"], lugares[r["d"]]["id"]
        if id_o in pos and id_d in pos and abs(T[pos[id_o]][pos[id_d]] - r["tiempo_s"]) < 0.001:
            nota_tiempo = "coincide con la matriz de tiempos de R2"
    estilo.tarjetas([
        ("Tiempo estimado de viaje", fmt_tiempo(r["tiempo_s"]), nota_tiempo, True),
        ("Nodos en la ruta", num(len(r["camino"])), "intersecciones recorridas"),
        ("Nodos explorados", num(r["explorados"]), f"de {num(red['info']['V'])} que tiene la red"),
        ("Tiempo de cálculo", ms(r["ms"]), "solo el algoritmo, en este equipo"),
    ])

    puntos = [red["coord"][i] for i in r["camino"]]
    mapa = estilo.mapa_base(puntos[0], 11)
    folium.PolyLine(puntos, weight=5, color=estilo.AZUL, opacity=0.95,
                    tooltip=f"{nombre_o} → {nombre_d}: {fmt_tiempo(r['tiempo_s'])}").add_to(mapa)
    estilo.marcador(mapa, puntos[0], "Origen: " + nombre_o, "A")
    estilo.marcador(mapa, puntos[-1], "Destino: " + nombre_d, "B")
    mapa.fit_bounds(puntos, padding=(30, 30))
    estilo.mostrar_mapa(mapa, 500, clave="mapa_ruta")
    estilo.leyenda([(estilo.AZUL, "Camino de menor tiempo"), (estilo.FONDO, "A: origen · B: destino")])

    _panel_ruta(red, r)
    _comparacion_lineal(red, r, lugares)


# =======================================================================================
# Envolvente (R3)
# =======================================================================================
def _area_km2(xs, ys):
    """Área del polígono por la fórmula del cordón (coordenadas en metros)."""
    n = len(xs)
    doble = sum(xs[i] * ys[(i + 1) % n] - xs[(i + 1) % n] * ys[i] for i in range(n))
    return abs(doble) / 2 / 1e6


def _recalcular_envolvente(v):
    """Calcula la envolvente en vivo con el algoritmo propio y la compara con el archivo y con SciPy."""
    from pyproj import Transformer
    from src.envolvente.envolvente import envolvente_convexa

    coords = datos.coordenadas_nodos()
    a_utm = Transformer.from_crs("EPSG:4326", "EPSG:32618", always_xy=True)
    xs, ys = a_utm.transform([c[1] for c in coords.values()], [c[0] for c in coords.values()])
    puntos = sorted({(int(round(x)), int(round(y))) for x, y in zip(xs, ys)})
    t0 = time.perf_counter()
    vertices = envolvente_convexa(puntos)
    milis = (time.perf_counter() - t0) * 1000
    resultado = dict(n=len(puntos), vertices=len(vertices), ms=milis,
                     igual_csv=vertices == list(zip(v["x"].astype(int), v["y"].astype(int))),
                     igual_scipy=None, ms_scipy=None)
    try:
        import numpy as np
        from scipy.spatial import ConvexHull
        arreglo = np.array(puntos, dtype=float)
        t0 = time.perf_counter()
        casco = ConvexHull(arreglo)
        resultado["ms_scipy"] = (time.perf_counter() - t0) * 1000
        resultado["igual_scipy"] = {puntos[i] for i in casco.vertices} == set(vertices)
    except ImportError:
        pass
    return resultado


def envolvente():
    import folium

    estilo.encabezado(
        "Envolvente convexa de la red vial (R3)",
        "El menor polígono convexo que contiene todos los nodos de la red: una aproximación de la "
        "extensión que cubre la red vial del departamento.",
        "R3 · Envolvente convexa")
    ruta_csv = datos.res("r3_envolvente.csv")
    v = datos.csv(ruta_csv)
    if v is None or not {"x", "y", "lon", "lat"} <= set(v.columns) or len(v) < 3:
        estilo.falta_archivo(ruta_csv, datos.COMANDOS["r3_envolvente.csv"], "dibujar la envolvente")
        return
    puntos = list(zip(v["lat"], v["lon"]))
    tiempos = datos.csv(datos.res("r3_tiempos.csv"))
    fila_red = None
    if tiempos is not None and (tiempos["conjunto"] == "nodos de la red").any():
        fila_red = tiempos[tiempos["conjunto"] == "nodos de la red"].iloc[0]

    items = [("Vértices de la envolvente", str(len(v)), "en sentido antihorario", True),
             ("Área del polígono", f"{num(_area_km2(list(v['x']), list(v['y'])), 0)} km²",
              "calculada aquí con la fórmula del cordón")]
    if fila_red is not None:
        items.insert(1, ("Puntos de entrada", num(fila_red["n_puntos"]), "nodos de la red, sin repetidos"))
        items.append(("Tiempo de cálculo", ms(fila_red["propio_mediana_ms"]), "mediana medida en el experimento"))
    estilo.tarjetas(items)

    ver_lugares = st.toggle("Mostrar los lugares del catálogo", value=True,
                            help="Dibuja los lugares del catálogo para ver que todos quedan dentro del polígono.")
    mapa = estilo.mapa_base([v["lat"].mean(), v["lon"].mean()], 9)
    folium.Polygon(puntos, color=estilo.AZUL, weight=3, fill=True, fill_color=estilo.AZUL,
                   fill_opacity=0.08, tooltip="Envolvente convexa").add_to(mapa)
    for n, (lat, lon) in enumerate(puntos):
        folium.CircleMarker((lat, lon), radius=5, color=estilo.TINTA, weight=2, fill=True,
                            fill_color=estilo.FONDO, fill_opacity=1,
                            tooltip=f"Vértice {n + 1}: x = {int(v['x'][n])} m, y = {int(v['y'][n])} m").add_to(mapa)
    base = datos.catalogo_y_matriz()
    if ver_lugares and base:
        for r in base[0]:
            try:
                folium.CircleMarker((float(r["latitud"]), float(r["longitud"])), radius=3,
                                    color=estilo.BERMELLON, weight=1, fill=True,
                                    fill_color=estilo.BERMELLON, fill_opacity=0.9,
                                    tooltip=f'{r["id"]} · {r["nombre"]}').add_to(mapa)
            except (KeyError, ValueError):
                continue
    mapa.fit_bounds(puntos, padding=(20, 20))
    estilo.mostrar_mapa(mapa, 540, clave="mapa_envolvente")
    leyenda = [(estilo.AZUL, "Envolvente convexa"), (estilo.FONDO, "Vértice")]
    if ver_lugares and base:
        leyenda.append((estilo.BERMELLON, "Lugar del catálogo"))
    estilo.leyenda(leyenda)

    with st.expander("Coordenadas de los vértices"):
        tabla = v.rename(columns={"x": "x (m, UTM 18N)", "y": "y (m, UTM 18N)", "lon": "Longitud", "lat": "Latitud"})
        tabla.insert(0, "Vértice", range(1, len(tabla) + 1))
        st.dataframe(tabla, hide_index=True, width="stretch")

    # Verificación en vivo
    st.header("Verificar el resultado ahora")
    st.write("El mapa usa el resultado guardado en `resultados/r3_envolvente.csv`. Puede volver a calcular "
             "la envolvente en este equipo, con el algoritmo propio, y compararla con el archivo y con SciPy.")
    if st.button("Recalcular y verificar"):
        if not os.path.exists(datos.GRAFO):
            estilo.falta_archivo(datos.GRAFO, para_que="leer los nodos de la red")
        else:
            try:
                with st.spinner("Proyectando los nodos y calculando la envolvente..."):
                    st.session_state["env_vivo"] = _recalcular_envolvente(v)
            except ImportError as error:
                st.error(f"Falta una librería para recalcular ({error.name}). Instálela con "
                         "`python -m pip install -r requirements.txt`.")
    vivo = st.session_state.get("env_vivo")
    if vivo:
        if vivo["igual_csv"] and vivo["igual_scipy"] is not False:
            st.success("La envolvente recalculada tiene exactamente los mismos vértices que el archivo"
                       + (" y que SciPy." if vivo["igual_scipy"] else "."))
        else:
            st.error("La envolvente recalculada no coincide. Vuelva a generar el archivo con "
                     f"`{datos.COMANDOS['r3_envolvente.csv']}`.")

    cociente = (f" En el experimento, con los nodos de la red, SciPy tardó {ms(fila_red['scipy_mediana_ms'])} "
                f"y la versión propia {ms(fila_red['propio_mediana_ms'])}: SciPy está escrito en C y la "
                "versión propia en Python.") if fila_red is not None else ""
    if vivo:
        cifras = [("Puntos distintos", num(vivo["n"])), ("Vértices", str(vivo["vertices"])),
                  ("Tiempo, versión propia", ms(vivo["ms"])),
                  ("Tiempo, SciPy", ms(vivo["ms_scipy"]) if vivo["ms_scipy"] is not None else "no disponible"),
                  ("Coincide con el archivo", "Sí" if vivo["igual_csv"] else "No"),
                  ("Coincide con SciPy", {True: "Sí", False: "No", None: "no disponible"}[vivo["igual_scipy"]])]
        titulo, nota = "Datos de esta ejecución", (
            "Una sola ejecución en este equipo; solo se cronometra el cálculo de la envolvente, no la "
            "lectura del archivo ni la proyección. Las mediciones con protocolo están en la página Resultados.")
    else:
        cifras = [("Vértices", str(len(v)))]
        if fila_red is not None:
            cifras = [("Puntos distintos", num(fila_red["n_puntos"])), ("Vértices", str(int(fila_red["vertices"]))),
                      ("Tiempo, versión propia", ms(fila_red["propio_mediana_ms"])),
                      ("Tiempo, SciPy", ms(fila_red["scipy_mediana_ms"])),
                      ("Repeticiones", str(int(fila_red["propio_repeticiones"])))]
        titulo, nota = "Datos del resultado guardado", (
            "Cifras leídas de resultados/r3_tiempos.csv (mediana del experimento). Pulse «Recalcular y "
            "verificar» para obtener los datos de una ejecución en este equipo.")
    estilo.como_se_calculo(
        "Se toman todos los nodos de la red y se busca el polígono convexo más pequeño que los contiene, "
        "como si se rodearan con una banda elástica.",
        [
            dict(paso="Preparar los puntos", nombre="Proyección a UTM 18N, redondeo y orden por (x, y)",
                 complejidad="O(n log n)",
                 que_hace="Las coordenadas pasan de grados a metros (EPSG:32618), se redondean al metro, se "
                          "quitan los repetidos con un conjunto y se ordenan de izquierda a derecha.",
                 por_que="Con enteros en metros, el producto cruzado que decide cada giro es exacto: no hay "
                         "errores de redondeo que metan o saquen un vértice por equivocación."),
            dict(paso="Calcular la envolvente", nombre="Divide y vencerás por mitades",
                 complejidad="O(n log n) · memoria O(n)",
                 que_hace="La lista ordenada se parte en dos mitades, se calcula la envolvente de cada una "
                          "por separado y luego se unen. Con 3 puntos o menos se resuelve directamente.",
                 por_que="Los nodos de una red vial se amontonan en corredores y centros urbanos. Este "
                         "algoritmo no depende de cómo estén repartidos: su peor caso sigue siendo "
                         "O(n log n), mientras que Quickhull puede degradarse a O(n²)."),
            dict(paso="Unir dos mitades", nombre="Barrido de Andrew (cadena monótona)",
                 complejidad="O(h), h = vértices de las dos mitades",
                 que_hace="Los vértices de las dos envolventes ya están ordenados por x: se mezclan y se "
                          "recorren una vez, descartando todo punto que no gire estrictamente a la izquierda.",
                 por_que="Al estar todo ordenado, la unión no necesita buscar tangentes: basta un barrido. "
                         "Los puntos alineados sobre un lado se descartan, así que no cuentan como vértices."),
            dict(paso="Comprobar", nombre="scipy.spatial.ConvexHull (Qhull)",
                 complejidad="Librería en C, solo verifica",
                 que_hace="Se calcula la misma envolvente con SciPy y se exige que los vértices sean "
                          "exactamente los mismos.",
                 por_que="SciPy no hace el cálculo del proyecto: sirve de referencia independiente y de "
                         "punto de comparación en el experimento de tiempos." + cociente),
        ],
        cifras, nota, titulo)


def pendiente(nombre):
    """Página de relleno para secciones que todavía no existen."""
    estilo.encabezado(nombre)
    estilo.estado_vacio("Esta página todavía no está construida")


# =======================================================================================
# Itinerario (R4)
# =======================================================================================
def _tabla_plan(res, ids, nombre, dur, T):
    """Orden de visita de un plan, con el traslado hasta cada parada."""
    filas = []
    for n, i in enumerate(res["ruta"]):
        ultimo = n == len(res["ruta"]) - 1
        filas.append({
            "Parada": "Partida" if n == 0 else ("Regreso" if ultimo else str(n)),
            "Lugar": f"{nombre[ids[i]]} ({ids[i]})",
            "Traslado hasta aquí": "—" if n == 0 else fmt_tiempo(T[res["ruta"][n - 1]][i]),
            "Visita": fmt_tiempo(dur[ids[i]]) if ids[i] in dur and 0 < n and not ultimo else "—",
        })
    st.dataframe(pd.DataFrame(filas), hide_index=True, width="stretch")


def _mostrar_plan(titulo, res, ids, nombre, dur, T):
    """Resumen de un plan: totales, si cabe en la jornada y el orden de visita."""
    from src.ruta_optima.itinerario import JORNADA_S
    st.subheader(titulo)
    holgura = JORNADA_S - res["total_s"]
    estilo.tarjetas([
        ("Total del día", fmt_tiempo(res["total_s"]),
         f"cabe en la jornada, sobran {fmt_tiempo(holgura)}" if res["cabe"]
         else f"no cabe: se pasa por {fmt_tiempo(-holgura)}", True),
        ("Desplazamientos", fmt_tiempo(res["viaje_s"]), "suma de los traslados"),
        ("Visitas", fmt_tiempo(res["visitas_s"]), f"{len(res['atractivos'])} atractivos"),
    ])
    _tabla_plan(res, ids, nombre, dur, T)
    for idx, antes, despues in res["quitados"]:
        st.warning(f"Se quitó {nombre[ids[idx]]} ({ids[idx]}): el total pasó de "
                   f"{fmt_tiempo(antes)} a {fmt_tiempo(despues)}.")


def _mapa_itinerario(res, ids, nombre):
    """Dibuja el recorrido: cada tramo entre lugares sigue la ruta real por carretera (Dijkstra)."""
    import folium

    red = _red_o_aviso()
    if red is None:
        return
    idx_red = {l["id"]: l["idx"] for l in red["lugares"]}       # id del catálogo -> nodo del grafo
    paradas = [ids[i] for i in res["ruta"]]                      # empieza y termina en la partida
    todos = []
    mapa = estilo.mapa_base(red["coord"][idx_red[paradas[0]]], 10)
    for n in range(len(paradas) - 1):
        tiempo_s, puntos, _ = datos.tramo(idx_red[paradas[n]], idx_red[paradas[n + 1]])
        todos += puntos
        folium.PolyLine(puntos, weight=5, color=estilo.TRAMOS[n % len(estilo.TRAMOS)], opacity=0.9,
                        tooltip=f"Tramo {n + 1}: {nombre[paradas[n]]} → {nombre[paradas[n + 1]]} "
                                f"({fmt_tiempo(tiempo_s)})").add_to(mapa)
    for n, p in enumerate(paradas[:-1]):                         # la última parada repite la partida
        estilo.marcador(mapa, red["coord"][idx_red[p]],
                        ("Partida y regreso: " if n == 0 else f"Parada {n}: ") + nombre[p],
                        "P" if n == 0 else str(n))
    mapa.fit_bounds(todos, padding=(30, 30))
    estilo.mostrar_mapa(mapa, 540, clave="mapa_itinerario")
    st.caption("P es la partida y el regreso; los números son el orden de visita. Cada tramo cambia de "
               "color y sigue la ruta real por carretera. Pase el cursor sobre un tramo para ver su tiempo.")


def _panel_itinerario(r):
    """Panel "Cómo se calculó" de la página Itinerario."""
    k_ini, k_fin = len(r["elegidos"]), len(r["hk"]["atractivos"])
    frase_fb = ""
    exactas = datos.csv(datos.res("r4_exactas.csv"))
    if exactas is not None:
        ok = exactas[exactas["estado"] == "completada"]
        comunes = sorted(set(ok[ok["metodo"] == "fuerza_bruta"]["k"]) & set(ok[ok["metodo"] == "held_karp"]["k"]))
        if comunes:
            k = comunes[-1]
            fb = float(ok[(ok["metodo"] == "fuerza_bruta") & (ok["k"] == k)]["mediana_ms"].iloc[0])
            hk = float(ok[(ok["metodo"] == "held_karp") & (ok["k"] == k)]["mediana_ms"].iloc[0])
            frase_fb = (f" En las mediciones del proyecto, con k = {k}, la fuerza bruta tardó {ms(fb)} "
                        f"y Held-Karp {ms(hk)}.")
    frase_cal = ""
    calidad = datos.csv(datos.res("r4_calidad_resumen.csv"))
    if calidad is not None and (calidad["k"] == 8).any():
        f8 = calidad[calidad["k"] == 8].iloc[0]
        frase_cal = (f" En las pruebas del proyecto con k = 8 se alejó del óptimo {num(f8['alejamiento_promedio_pct'], 2)} % "
                     f"en promedio y {num(f8['alejamiento_maximo_pct'], 2)} % en el peor caso.")
    dif = r["vm"]["total_s"] - r["hk"]["total_s"]
    estilo.como_se_calculo(
        "Se buscó el orden de visita que menos tiempo gasta en carretera, se sumaron las visitas y se "
        "comprobó que todo quepa en una jornada de 11 horas. El mismo problema se resolvió de dos formas "
        "para comparar.",
        [
            dict(paso="Ordenar las visitas (óptimo)", nombre="Held-Karp, programación dinámica sobre subconjuntos",
                 complejidad="Tiempo O(k² · 2^k) · memoria O(k · 2^k)",
                 que_hace="Para cada grupo de atractivos y cada posible último lugar, guarda el menor tiempo "
                          "para visitarlos todos terminando ahí. Los grupos grandes se arman con los "
                          "pequeños ya resueltos, así ningún cálculo se repite. Al final se suma el regreso.",
                 por_que="Garantiza el recorrido óptimo. La fuerza bruta también, pero prueba los k! órdenes "
                         "posibles." + frase_fb),
            dict(paso="Ordenar las visitas (rápido)", nombre="Heurística del vecino más cercano",
                 complejidad="O(k²)",
                 que_hace="Desde donde está, va siempre al atractivo pendiente más cercano en tiempo; al "
                          "terminar, regresa a la partida.",
                 por_que="Es inmediata y fácil de explicar, pero no garantiza el óptimo: una decisión buena "
                         "ahora puede obligar a un traslado largo después. Se incluye para medir cuánto "
                         "se pierde." + frase_cal),
            dict(paso="Ajustar a la jornada", nombre="Criterio de exclusión del grupo",
                 complejidad="k + 1 recorridos por atractivo quitado",
                 que_hace="Si el total pasa de 11 h, se prueba quitar cada atractivo y se recalcula el "
                          "recorrido. Si alguna salida hace que quepa, se quita el que deja el total más "
                          "cerca de la jornada sin pasarse; si ninguna, el que más reduce el total, y se repite.",
                 por_que="Busca conservar la mayor cantidad posible de atractivos y desperdiciar el menor "
                         "tiempo de la jornada. Es una decisión del grupo, documentada en "
                         "src/ruta_optima/itinerario.py."),
            dict(paso="Tiempo entre dos lugares", nombre="Matriz de tiempos 40 × 40 (R2)",
                 complejidad="Consulta O(1)",
                 que_hace="Los tiempos entre lugares ya están calculados: Dijkstra con cola se ejecutó una "
                          "vez desde cada lugar del catálogo. La matriz no es simétrica: ir no siempre "
                          "tarda lo mismo que volver.",
                 por_que="Held-Karp consulta miles de veces el tiempo entre pares; calcular cada uno sobre "
                         "la red en el momento sería muchísimo más lento."),
            dict(paso="Trazo en el mapa", nombre="Dijkstra con cola de prioridad, tramo por tramo",
                 complejidad="O((V + E) log V) por tramo",
                 que_hace="La matriz solo guarda tiempos, no caminos. Para dibujar, cada tramo del recorrido "
                          "se vuelve a calcular sobre la red y se guarda en caché.",
                 por_que="Así el mapa muestra la carretera real y no una línea recta entre lugares."),
        ],
        [
            ("Atractivos elegidos → visitados", f"{k_ini} → {k_fin}"),
            ("Celdas de la tabla (k · 2^k)", num(k_fin * 2 ** k_fin)),
            ("Recorridos resueltos con Held-Karp", num(r["llamadas_hk"])),
            ("Tiempo de cálculo, Held-Karp", ms(r["ms_hk"])),
            ("Tiempo de cálculo, heurística", ms(r["ms_vm"])),
            ("Heurística − óptimo", f"{num(dif, 0)} s ({num(dif / r['hk']['total_s'] * 100, 2)} %)"),
        ],
        "El tiempo de Held-Karp incluye todos los recorridos que hubo que resolver para decidir qué "
        "atractivos quitar; el de la heurística es un solo recorrido sobre los atractivos finales. "
        "La tabla tiene 2^k filas (subconjuntos) y k columnas (último lugar), como en src/ruta_optima/tsp.py. "
        "Una sola ejecución en este equipo.")


def itinerario():
    import random
    from src.ruta_optima.itinerario import armar_itinerario, JORNADA_S
    from src.ruta_optima.medicion import SEMILLA
    from src.ruta_optima.tsp import held_karp, vecino_mas_cercano

    estilo.encabezado(
        "Itinerario de un día (R4)",
        "Elija un punto de partida y de 6 a 8 atractivos. La aplicación busca el mejor orden de visita "
        "y comprueba que todo quepa en una jornada de 11 horas.",
        "R4 · Ruta óptima de recorrido")
    base = datos.catalogo_y_matriz()
    if base is None:
        falta = datos.CATALOGO if not os.path.exists(datos.CATALOGO) else datos.MATRIZ
        estilo.falta_archivo(falta, para_que="armar el itinerario")
        if falta == datos.MATRIZ:
            st.caption("La matriz de tiempos la genera `src/caminos/matriz_tiempos.py` (R2).")
        return
    cat, ids, T = base
    nombre = {r["id"]: r["nombre"] for r in cat}
    dur = {r["id"]: int(float(r["duracion_visita_min"])) * 60 for r in cat if r["id"].startswith("ATR")}
    pos = {i: n for n, i in enumerate(ids)}
    atr = sorted(dur)

    inicio_id = st.selectbox("Punto de partida y de regreso", ids,
                             index=ids.index("CAB01") if "CAB01" in ids else 0,
                             format_func=lambda i: f"{nombre[i]} ({i})", key="itin_inicio")
    por_defecto = sorted(random.Random(SEMILLA).sample(atr, min(7, len(atr))))
    elegidos = st.multiselect("Atractivos a visitar (de 6 a 8)", atr, default=por_defecto,
                              format_func=lambda i: f"{nombre[i]} · {dur[i] // 60} min ({i})",
                              key="itin_atractivos",
                              help="Entre paréntesis, la duración de la visita según el catálogo.")
    repetido = inicio_id in elegidos                 # la partida no puede ser también una visita
    valido = 6 <= len(elegidos) <= 8 and not repetido
    visitas_elegidas = sum(dur[a] for a in elegidos)
    st.caption(f"{len(elegidos)} atractivos elegidos · {fmt_tiempo(visitas_elegidas)} solo en visitas, "
               f"de una jornada de {fmt_tiempo(JORNADA_S)}.")
    if repetido:
        st.warning(f"{nombre[inicio_id]} es el punto de partida y también está entre los atractivos. "
                   "Quítelo de la lista o cambie la partida.")
    elif not valido:
        st.warning(f"Hay {len(elegidos)} atractivos elegidos y el enunciado pide entre 6 y 8. "
                   + ("Agregue más para poder calcular." if len(elegidos) < 6 else "Quite algunos para poder calcular."))

    if st.button("Calcular itinerario", type="primary", disabled=not valido):
        dur_idx = {pos[a]: dur[a] for a in elegidos}
        idx_elegidos = [pos[a] for a in elegidos]
        llamadas = [0]

        def held_karp_contado(matriz, partida, lugares):
            """El mismo held_karp, contando cuántos recorridos se resuelven (para el panel final)."""
            llamadas[0] += 1
            return held_karp(matriz, partida, lugares)

        with st.spinner("Calculando el itinerario..."):
            t0 = time.perf_counter()
            hk = armar_itinerario(T, pos[inicio_id], idx_elegidos, dur_idx, JORNADA_S, held_karp_contado)
            ms_hk = (time.perf_counter() - t0) * 1000

            # La heurística ordena los MISMOS atractivos que dejó Held-Karp
            t0 = time.perf_counter()
            viaje_vm, ruta_vm = vecino_mas_cercano(T, pos[inicio_id], hk["atractivos"])
            ms_vm = (time.perf_counter() - t0) * 1000
            total_vm = viaje_vm + hk["visitas_s"]
            vm = {"ruta": ruta_vm, "viaje_s": viaje_vm, "visitas_s": hk["visitas_s"],
                  "total_s": total_vm, "quitados": [], "cabe": total_vm <= JORNADA_S,
                  "atractivos": hk["atractivos"]}

            # Aparte: si la heurística también decidiera qué atractivos quitar
            vm_solo = armar_itinerario(T, pos[inicio_id], idx_elegidos, dur_idx, JORNADA_S, vecino_mas_cercano)
        st.session_state["itin"] = dict(hk=hk, vm=vm, vm_solo=vm_solo, ms_hk=ms_hk, ms_vm=ms_vm,
                                        llamadas_hk=llamadas[0], inicio=inicio_id, elegidos=list(elegidos))

    r = st.session_state.get("itin")
    if not r or "elegidos" not in r:
        estilo.estado_vacio("Todavía no hay un itinerario calculado",
                            "Revise la partida y los atractivos y pulse «Calcular itinerario». Aquí "
                            "aparecerán el recorrido, los totales, el mapa y la explicación del cálculo.")
        return
    if (r["inicio"], sorted(r["elegidos"])) != (inicio_id, sorted(elegidos)):
        st.caption("La selección de arriba cambió. Este resultado es del cálculo anterior; pulse "
                   "«Calcular itinerario» para actualizarlo.")

    hk, vm = r["hk"], r["vm"]
    dif = vm["total_s"] - hk["total_s"]
    st.header(f"Itinerario desde {nombre[r['inicio']]}")
    estilo.tarjetas([
        ("Held-Karp (óptimo)", fmt_tiempo(hk["total_s"]),
         "cabe en la jornada de 11 h" if hk["cabe"] else "no cabe en la jornada de 11 h", True),
        ("Vecino más cercano", fmt_tiempo(vm["total_s"]),
         "cabe en la jornada de 11 h" if vm["cabe"] else "no cabe en la jornada de 11 h"),
        ("Diferencia", "+ " + fmt_tiempo(dif), f"{num(dif / hk['total_s'] * 100, 2)} % más con la heurística"),
        ("Atractivos visitados", f"{len(hk['atractivos'])} de {len(r['elegidos'])}",
         "se quitaron algunos para caber" if hk["quitados"] else "no hubo que quitar ninguno"),
    ])
    st.caption("Las visitas son las mismas en los dos planes, así que la diferencia es solo de "
               "desplazamientos. Held-Karp es óptimo: la heurística nunca puede dar menos.")
    for idx, antes, despues in hk["quitados"]:
        st.warning(f"Para caber en la jornada se quitó {nombre[ids[idx]]} ({ids[idx]}): el total pasó de "
                   f"{fmt_tiempo(antes)} a {fmt_tiempo(despues)}.")
    if not hk["cabe"]:
        st.error("Ni quitando atractivos se logra un plan dentro de la jornada desde este punto de partida.")

    st.header("Recorrido")
    cual = st.radio("Plan a mostrar", ["Held-Karp (óptimo)", "Vecino más cercano"], horizontal=True,
                    key="itin_plan")
    plan = hk if cual.startswith("Held") else vm
    estilo.tarjetas([
        ("Total del día", fmt_tiempo(plan["total_s"]),
         f"sobran {fmt_tiempo(JORNADA_S - plan['total_s'])} de la jornada" if plan["cabe"]
         else f"se pasa por {fmt_tiempo(plan['total_s'] - JORNADA_S)}", True),
        ("Desplazamientos", fmt_tiempo(plan["viaje_s"]), "suma de los traslados"),
        ("Visitas", fmt_tiempo(plan["visitas_s"]), f"{len(plan['atractivos'])} atractivos"),
    ])
    _tabla_plan(plan, ids, nombre, dur, T)
    _mapa_itinerario(plan, ids, nombre)

    with st.expander("Si la heurística decidiera sola qué atractivos quitar"):
        _mostrar_plan("Vecino más cercano con su propia exclusión", r["vm_solo"], ids, nombre, dur, T)
        st.caption("Este plan no se compara con Held-Karp: al quitar atractivos distintos, los totales "
                   "no son comparables.")

    _panel_itinerario(r)


# =======================================================================================
# Resultados R1-R4
# =======================================================================================
NOMBRES_COLUMNAS = {
    "red": "Red", "V_antes": "V antes", "E_antes": "E antes", "V_despues": "V después",
    "E_despues": "E después", "repeticiones": "Repeticiones", "mediana_ms": "Mediana (ms)",
    "fuertemente_conexa": "Fuertemente conexa", "origen": "Origen", "destino": "Destino",
    "municipio_origen": "Municipio origen", "municipio_destino": "Municipio destino", "tipo": "Tipo de par",
    "tiempo_viaje_s": "Viaje (s)", "nodos_ruta": "Nodos en la ruta", "explorados_cola": "Explorados (cola)",
    "cola_mediana_ms": "Cola, mediana (ms)", "explorados_lineal": "Explorados (lineal)",
    "lineal_mediana_ms": "Lineal, mediana (ms)", "cociente_lineal_cola": "Lineal / cola",
    "conjunto": "Conjunto", "n_puntos": "Puntos", "vertices": "Vértices",
    "propio_mediana_ms": "Propia, mediana (ms)", "scipy_mediana_ms": "SciPy, mediana (ms)",
    "cociente_propio_scipy": "Propia / SciPy", "metodo": "Método", "k": "k",
    "tiempo_optimo_s": "Tiempo óptimo (s)", "estado": "Estado", "semilla": "Semilla",
    "instancia": "Instancia", "tiempo_heuristica_s": "Heurística (s)", "alejamiento_pct": "Alejamiento (%)",
    "instancias": "Instancias", "alejamiento_promedio_pct": "Alejamiento promedio (%)",
    "alejamiento_maximo_pct": "Alejamiento máximo (%)", "estadistico": "Estadístico", "valor": "Valor",
    "municipio_a": "Municipio", "municipio_b": "Municipio vecino",
}


def tabla(df, columnas=None):
    """Muestra un DataFrame con nombres de columna legibles."""
    if columnas:
        df = df[[c for c in columnas if c in df.columns]]
    st.dataframe(df.rename(columns=NOMBRES_COLUMNAS), hide_index=True, width="stretch")


def _falta_resultado(nombre):
    estilo.falta_archivo(datos.res(nombre), datos.COMANDOS.get(nombre, ""))


def mostrar_archivos(prefijo, omitir=()):
    """Muestra lo que haya en resultados/ con el prefijo (r1_, r2_...) y no esté ya en la página."""
    archivos = [a for a in sorted(glob.glob(os.path.join(RESULTADOS, prefijo + "_*")))
                if os.path.basename(a) not in omitir]
    for ruta_archivo in archivos:
        nombre = os.path.basename(ruta_archivo)
        with st.expander(f"Archivo original: resultados/{nombre}"):
            if nombre.endswith(".csv"):
                df = datos.csv(ruta_archivo)
                if df is None:
                    st.error("No se pudo leer el archivo.")
                else:
                    tabla(df)
            elif nombre.endswith(".png"):
                st.image(ruta_archivo, caption="Gráfica generada por el script del experimento.")
            elif nombre.endswith((".txt", ".md")):
                st.text(datos.texto(ruta_archivo) or "")


def _resultados_r1():
    df = datos.csv(datos.res("r1_componente.csv"))
    if df is None:
        _falta_resultado("r1_componente.csv")
    else:
        if (df["red"] == "Departamento").any():
            dep = df[df["red"] == "Departamento"].iloc[0]
            m1, m2, listas = datos.memoria_estimada(int(dep["V_antes"]), int(dep["E_antes"]))
            estilo.tarjetas([
                ("Nodos (V)", num(dep["V_despues"]), f"de {num(dep['V_antes'])} antes de filtrar", True),
                ("Aristas (E)", num(dep["E_despues"]), f"de {num(dep['E_antes'])} antes de filtrar"),
                ("Componente fuertemente conexa", ms(dep["mediana_ms"]), "mediana, red del departamento"),
                ("Memoria como listas", f"{num(listas, 2)} MB", f"como matriz de un peso: {num(m1, 1)} MB"),
            ])
            st.caption("La memoria es una estimación con los supuestos de `src/red/memoria.py` (8 bytes por "
                       "peso; cada entrada de lista guarda destino, distancia y tiempo), calculada con V y E "
                       f"antes de filtrar. Con dos pesos, la matriz ocuparía {num(m2, 1)} MB.")
        st.subheader("Tiempo de la componente fuertemente conexa según el tamaño de la red")
        estilo.grafica(graficas.r1_componente(df), 300)
        tabla(df)
    aso = datos.csv(datos.ASOCIACION)
    if aso is not None and "mayor_500m" in aso.columns:
        lejos = aso[aso["mayor_500m"].astype(str) == "True"]
        st.subheader("Asociación de los lugares a la red")
        st.write(f"Cada uno de los {len(aso)} lugares del catálogo se asocia a su nodo más cercano. "
                 f"{len(lejos)} quedan a más de 500 m de su nodo: " + ", ".join(lejos["id"]) + ".")
    bloque_maquina("r1_r2_maquina.txt")
    mostrar_archivos("r1", omitir=("r1_componente.csv", "r1_r2_maquina.txt"))


def _resultados_r2():
    df = datos.csv(datos.res("r2_mediciones.csv"))
    coc = datos.csv(datos.res("r2_cociente.csv"))
    if coc is not None:
        valores = dict(zip(coc["estadistico"], coc["valor"]))
        estilo.tarjetas([
            ("Lineal / cola, mediana", f"{num(valores.get('mediana', 0), 1)} ×", "veces más lenta la búsqueda lineal", True),
            ("Mínimo", f"{num(valores.get('minimo', 0), 1)} ×", "par con menor diferencia"),
            ("Máximo", f"{num(valores.get('maximo', 0), 1)} ×", "par con mayor diferencia"),
        ])
    if df is None:
        _falta_resultado("r2_mediciones.csv")
    else:
        n_lineal = int(df["lineal_mediana_ms"].notna().sum())
        st.subheader("Tiempo por consulta frente a nodos explorados")
        estilo.grafica(graficas.r2_tiempos(df), 340)
        st.caption(f"{len(df)} pares medidos con cola de prioridad y {n_lineal} de ellos (los cercanos) "
                   "también con búsqueda lineal. El eje vertical es logarítmico: cada división multiplica por 10.")
        tabla(df, ["origen", "destino", "tipo", "tiempo_viaje_s", "nodos_ruta", "explorados_cola",
                   "cola_mediana_ms", "lineal_mediana_ms", "cociente_lineal_cola"])
    bloque_maquina("r1_r2_maquina.txt")
    mostrar_archivos("r2", omitir=("r2_cociente.csv",))


def _resultados_r3():
    df = datos.csv(datos.res("r3_tiempos.csv"))
    if df is None:
        _falta_resultado("r3_tiempos.csv")
    else:
        if (df["conjunto"] == "nodos de la red").any():
            f = df[df["conjunto"] == "nodos de la red"].iloc[0]
            estilo.tarjetas([
                ("Vértices de la envolvente", str(int(f["vertices"])), f"de {num(f['n_puntos'])} nodos de la red", True),
                ("Versión propia", ms(f["propio_mediana_ms"]), "mediana, nodos de la red"),
                ("SciPy (Qhull)", ms(f["scipy_mediana_ms"]), "mediana, nodos de la red"),
                ("Propia / SciPy", f"{num(f['cociente_propio_scipy'], 1)} ×", "Python frente a C"),
            ])
        st.subheader("Tiempo según el número de puntos")
        estilo.grafica(graficas.r3_tiempos(df), 340)
        st.caption("Las líneas unen los conjuntos al azar (1.000, 10.000 y 50.000 puntos); el punto suelto "
                   "son los nodos de la red. Los dos ejes son logarítmicos.")
        tabla(df, ["conjunto", "n_puntos", "vertices", "propio_mediana_ms", "scipy_mediana_ms",
                   "cociente_propio_scipy"])
    bloque_maquina("r3_maquina.txt")
    mostrar_archivos("r3", omitir=("r3_maquina.txt",))


def _resultados_r4():
    ex = datos.csv(datos.res("r4_exactas.csv"))
    if ex is None:
        _falta_resultado("r4_exactas.csv")
    else:
        ok = ex[ex["estado"] == "completada"]
        hk, fb = ok[ok["metodo"] == "held_karp"], ok[ok["metodo"] == "fuerza_bruta"]
        items = []
        if len(hk):
            f = hk[hk["k"] == hk["k"].max()].iloc[0]
            items.append(("Held-Karp", ms(f["mediana_ms"]), f"mediana con k = {int(f['k'])}", True))
        if len(fb):
            f = fb[fb["k"] == fb["k"].max()].iloc[0]
            items.append(("Fuerza bruta", ms(f["mediana_ms"]), f"con k = {int(f['k'])}, el mayor que terminó"))
        calidad = datos.csv(datos.res("r4_calidad_resumen.csv"))
        if calidad is not None and len(calidad):
            items.append(("Heurística, peor caso", f"{num(calidad['alejamiento_maximo_pct'].max(), 2)} %",
                          f"alejamiento del óptimo en {int(calidad['instancias'].sum())} instancias"))
        if items:
            estilo.tarjetas(items)
        st.subheader("Fuerza bruta frente a Held-Karp")
        estilo.grafica(graficas.r4_exactas(ex), 340)
        incompletas = ex[ex["estado"] != "completada"]
        if len(incompletas):
            st.caption("No completadas dentro del límite de 5 minutos: "
                       + ", ".join(f"{m.replace('_', ' ')} con k = {k}"
                                   for m, k in zip(incompletas["metodo"], incompletas["k"]))
                       + ". No aparecen en la gráfica. El eje vertical es logarítmico.")
        tabla(ex.assign(metodo=ex["metodo"].str.replace("_", " ").str.capitalize()))
    det = datos.csv(datos.res("r4_calidad_detalle.csv"))
    resumen = datos.csv(datos.res("r4_calidad_resumen.csv"))
    if det is None or resumen is None:
        _falta_resultado("r4_calidad_resumen.csv")
    else:
        st.subheader("Calidad de la heurística del vecino más cercano")
        estilo.grafica(graficas.r4_calidad(det, resumen), 300)
        st.caption("Cada cuadrado es una instancia; la raya horizontal es el promedio de ese k. "
                   "0 % significa que la heurística encontró el óptimo.")
        tabla(resumen)
    bloque_maquina("r4_maquina.txt")
    mostrar_archivos("r4", omitir=("r4_maquina.txt", "r4_calidad_resumen.csv"))


def resultados():
    estilo.encabezado(
        "Resultados de los experimentos",
        "Mediciones de cada requerimiento, leídas de la carpeta resultados/. Las gráficas se generan "
        "aquí desde los CSV; los tiempos están en milisegundos salvo que se indique otra unidad.",
        "R1 a R4 · Mediciones")
    if not os.path.isdir(RESULTADOS):
        estilo.estado_vacio("No existe la carpeta resultados/",
                            "Los experimentos guardan allí sus tablas y gráficas. Ejecute los comandos "
                            "del README para generarlos.")
        return
    t1, t2, t3, t4 = st.tabs(["R1 · Red vial", "R2 · Caminos mínimos", "R3 · Envolvente", "R4 · Ruta óptima"])
    with t1:
        _resultados_r1()
    with t2:
        _resultados_r2()
    with t3:
        _resultados_r3()
    with t4:
        _resultados_r4()
