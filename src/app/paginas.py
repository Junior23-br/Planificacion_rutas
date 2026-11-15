"""Páginas de la aplicación demostrativa (R5)."""
import glob
import os
import time

import pandas as pd
import streamlit as st

RESULTADOS = "resultados"


def fmt_tiempo(seg):
    """Segundos a texto legible: '1 h 05 min' o '12 min 30 s'."""
    seg = int(round(seg))
    h, resto = divmod(seg, 3600)
    m, s = divmod(resto, 60)
    return f"{h} h {m:02d} min" if h else f"{m} min {s:02d} s"



def _leer_coordenadas(ruta_graphml):
    """Lee latitud y longitud de cada nodo del GraphML sin usar osmnx."""
    import xml.etree.ElementTree as ET
    ns = "{http://graphml.graphdrawing.org/xmlns}"
    clave = {}                                   # 'x' / 'y' -> id de la clave en el archivo
    coords = {}
    for _, el in ET.iterparse(ruta_graphml, events=("end",)):
        if el.tag == ns + "key" and el.get("for") == "node" and el.get("attr.name") in ("x", "y"):
            clave[el.get("attr.name")] = el.get("id")
        elif el.tag == ns + "node":
            datos = {d.get("key"): d.text for d in el.findall(ns + "data")}
            coords[el.get("id")] = (float(datos[clave["y"]]), float(datos[clave["x"]]))
            el.clear()
    return coords


@st.cache_resource(show_spinner="Cargando la red vial (la primera vez tarda un poco)...")
def datos_red():
    """Carga una sola vez el grafo, los lugares y las coordenadas de cada nodo."""
    from src.caminos.grafo import cargar_grafo, cargar_lugares

    ids, indice, adj, info = cargar_grafo()
    lugares = cargar_lugares(indice)
    por_id = _leer_coordenadas("data/processed/componente.graphml")
    coord = [por_id[str(n)] for n in ids]        # (latitud, longitud) por índice
    return dict(adj=adj, lugares=lugares, coord=coord, info=info)


def inicio():
    st.title("Rutas del Paisaje Cultural Cafetero")
    st.write("Aplicación demostrativa del proyecto final de Análisis de Algoritmos "
             "(Universidad del Quindío). Muestra los resultados de los cinco requerimientos "
             "sobre la red vial del Quindío.")
    st.markdown(
        "- **Ruta (R2):** camino de menor tiempo entre dos lugares del catálogo, con Dijkstra y cola de prioridad.\n"
        "- **Envolvente (R3):** envolvente convexa de la red.\n"
        "- **Itinerario (R4):** recorrido de un día con Held-Karp y con la heurística del vecino más cercano.\n"
        "- **Resultados R1–R4:** tablas y gráficas guardadas en `resultados/`.")
    st.caption("Los tiempos son una estimación del modelo, de nodo a nodo, no el tiempo real de viaje.")


def ruta():
    from src.caminos.dijkstra import ruta_minima
    import folium
    from streamlit_folium import st_folium

    st.header("Ruta entre dos lugares (R2)")
    st.write("Se calcula en el momento con Dijkstra y cola de prioridad. "
             "El tiempo es una estimación del modelo, de nodo a nodo.")
    red = datos_red()
    lugares = red["lugares"]
    nombres = [f'{l["id"]} · {l["nombre"]} ({l["municipio"]})' for l in lugares]
    c1, c2 = st.columns(2)
    o = c1.selectbox("Origen", range(len(lugares)), format_func=lambda i: nombres[i], index=0)
    d = c2.selectbox("Destino", range(len(lugares)), format_func=lambda i: nombres[i], index=1)

    if st.button("Calcular ruta"):
        if o == d:
            st.warning("El origen y el destino son el mismo lugar.")
        else:
            t0 = time.perf_counter()
            tiempo_s, camino, explorados = ruta_minima(red["adj"], lugares[o]["idx"], lugares[d]["idx"])
            ms = (time.perf_counter() - t0) * 1000
            st.session_state["ruta"] = dict(o=o, d=d, tiempo_s=tiempo_s, camino=camino,
                                            explorados=explorados, ms=ms)

    r = st.session_state.get("ruta")
    if not r:
        return
    if r["tiempo_s"] is None or r["tiempo_s"] == float("inf") or not r["camino"]:
        st.error("No hay ruta entre esos dos lugares.")
        return
    st.success(f'{nombres[r["o"]]}  →  {nombres[r["d"]]}: **{fmt_tiempo(r["tiempo_s"])}**')
    n_expl = len(r["explorados"]) if hasattr(r["explorados"], "__len__") else r["explorados"]
    st.caption(f'Nodos explorados: {n_expl:,} · tiempo de cálculo: {r["ms"]:.1f} ms · '
               f'nodos en la ruta: {len(r["camino"])}')

    puntos = [red["coord"][i] for i in r["camino"]]
    mapa = folium.Map(location=puntos[0], zoom_start=11)
    folium.PolyLine(puntos, weight=5, color="#c0392b").add_to(mapa)
    folium.Marker(puntos[0], tooltip="Origen: " + lugares[r["o"]]["nombre"],
                  icon=folium.Icon(color="green")).add_to(mapa)
    folium.Marker(puntos[-1], tooltip="Destino: " + lugares[r["d"]]["nombre"],
                  icon=folium.Icon(color="red")).add_to(mapa)
    mapa.fit_bounds(puntos)
    st_folium(mapa, height=500, width=1100, returned_objects=[])


def mostrar_archivos(prefijo):
    """Muestra todo lo que haya en resultados/ que empiece por el prefijo (r1_, r2_...)."""
    archivos = sorted(glob.glob(os.path.join(RESULTADOS, prefijo + "_*")))
    if not archivos:
        st.info(f"Todavía no hay archivos {prefijo}_* en resultados/.")
        return
    for ruta in archivos:
        nombre = os.path.basename(ruta)
        if nombre.endswith(".csv"):
            st.subheader(nombre)
            st.dataframe(pd.read_csv(ruta))
        elif nombre.endswith(".png"):
            st.subheader(nombre)
            st.image(ruta)
        elif nombre.endswith(".txt"):
            st.subheader(nombre)
            with open(ruta, encoding="utf-8") as f:
                st.text(f.read())


def resultados():
    st.header("Resultados de R1 a R4")
    st.caption("Tablas y gráficas generadas por los experimentos; los tiempos están en milisegundos "
               "salvo que se indique otra unidad.")
    t1, t2, t3, t4 = st.tabs(["R1 Red", "R2 Caminos", "R3 Envolvente", "R4 Ruta óptima"])
    with t1:
        mostrar_archivos("r1")
    with t2:
        mostrar_archivos("r2")
    with t3:
        mostrar_archivos("r3")
    with t4:
        mostrar_archivos("r4")


def pendiente(nombre):
    st.header(nombre)
    st.info("Esta página todavía no está construida.")


@st.cache_data
def datos_itinerario():
    from src.ruta_optima.itinerario import leer_catalogo, leer_matriz
    cat = leer_catalogo("data/catalogo/catalogo_lugares.csv")
    ids, T = leer_matriz("data/processed/matriz_tiempos.csv")
    return cat, ids, T


def _mostrar_plan(titulo, res, ids, nombre, dur):
    st.subheader(titulo)
    st.metric("Total del día", fmt_tiempo(res["total_s"]))
    st.write(f'Desplazamientos: **{fmt_tiempo(res["viaje_s"])}** · '
             f'Visitas: **{fmt_tiempo(res["visitas_s"])}**')
    if res["cabe"]:
        st.success("Cabe en la jornada de 11 h.")
    else:
        st.error("No cabe en la jornada de 11 h.")
    filas = [{"Orden": n, "Id": ids[i], "Lugar": nombre[ids[i]],
              "Visita": fmt_tiempo(dur[ids[i]]) if ids[i] in dur else "-"}
             for n, i in enumerate(res["ruta"])]
    st.dataframe(pd.DataFrame(filas), hide_index=True)
    for idx, antes, despues in res["quitados"]:
        st.warning(f'Se quitó {ids[idx]} ({nombre[ids[idx]]}): el total pasó de '
                   f'{fmt_tiempo(antes)} a {fmt_tiempo(despues)}.')


def itinerario():
    import random
    from src.ruta_optima.itinerario import armar_itinerario, JORNADA_S
    from src.ruta_optima.medicion import SEMILLA
    from src.ruta_optima.tsp import held_karp, vecino_mas_cercano

    st.header("Itinerario de un día (R4)")
    st.write("Se ordenan de 6 a 8 atractivos desde un punto de partida y se comprueba la jornada "
             "de 11 h. Se resuelve con **Held-Karp** (óptimo) y con la **heurística del vecino más "
             "cercano**, y se comparan los totales. Si no cabe, se quitan atractivos con el criterio "
             "del grupo hasta que quepa.")
    cat, ids, T = datos_itinerario()
    nombre = {r["id"]: r["nombre"] for r in cat}
    dur = {r["id"]: int(float(r["duracion_visita_min"])) * 60 for r in cat if r["id"].startswith("ATR")}
    pos = {i: n for n, i in enumerate(ids)}
    atr = sorted(dur)

    inicio = st.selectbox("Punto de partida", ids, index=ids.index("CAB01"),
                          format_func=lambda i: f"{i} · {nombre[i]}")
    por_defecto = sorted(random.Random(SEMILLA).sample(atr, 7))
    elegidos = st.multiselect("Atractivos (de 6 a 8)", atr, default=por_defecto,
                              format_func=lambda i: f"{i} · {nombre[i]} ({dur[i] // 60} min)")
    if not 6 <= len(elegidos) <= 8:
        st.warning(f"Hay {len(elegidos)} atractivos elegidos; el enunciado pide entre 6 y 8.")
        return

    if st.button("Calcular itinerario"):
        dur_idx = {pos[a]: dur[a] for a in elegidos}
        idx_elegidos = [pos[a] for a in elegidos]
        t0 = time.perf_counter()
        hk = armar_itinerario(T, pos[inicio], idx_elegidos, dur_idx, JORNADA_S, held_karp)
        ms_hk = (time.perf_counter() - t0) * 1000

        # La heurística ordena los MISMOS atractivos que dejó Held-Karp
        t0 = time.perf_counter()
        viaje_vm, ruta_vm = vecino_mas_cercano(T, pos[inicio], hk["atractivos"])
        ms_vm = (time.perf_counter() - t0) * 1000
        total_vm = viaje_vm + hk["visitas_s"]
        vm = {"ruta": ruta_vm, "viaje_s": viaje_vm, "visitas_s": hk["visitas_s"],
              "total_s": total_vm, "quitados": [], "cabe": total_vm <= JORNADA_S,
              "atractivos": hk["atractivos"]}

        # Aparte: si la heurística también decidiera qué atractivos quitar
        vm_solo = armar_itinerario(T, pos[inicio], idx_elegidos, dur_idx, JORNADA_S, vecino_mas_cercano)
        st.session_state["itin"] = dict(hk=hk, vm=vm, vm_solo=vm_solo, ms_hk=ms_hk, ms_vm=ms_vm)

    r = st.session_state.get("itin")
    if not r:
        return
    c1, c2 = st.columns(2)
    with c1:
        _mostrar_plan("Held-Karp (óptimo)", r["hk"], ids, nombre, dur)
        st.caption(f'Tiempo de cálculo (incluye la exclusión de atractivos): {r["ms_hk"]:.1f} ms')
    with c2:
        _mostrar_plan("Vecino más cercano (heurística)", r["vm"], ids, nombre, dur)
        st.caption(f'Mismos atractivos que Held-Karp. Tiempo de cálculo: {r["ms_vm"]:.2f} ms')

    dif = r["vm"]["total_s"] - r["hk"]["total_s"]
    st.subheader("Diferencia entre los dos totales")
    st.metric("Heurística − Held-Karp", fmt_tiempo(dif),
              delta=f"{dif / r['hk']['total_s'] * 100:+.2f} % sobre el total del día",
              delta_color="inverse")
    st.caption("Las visitas son las mismas en ambos, así que la diferencia es solo de desplazamientos. "
               "Held-Karp es óptimo: la heurística nunca puede dar menos.")

    with st.expander("Si la heurística decidiera sola qué atractivos quitar"):
        _mostrar_plan("Vecino más cercano con su propia exclusión", r["vm_solo"], ids, nombre, dur)
        st.caption("Aquí no se compara con Held-Karp: al quitar atractivos distintos, los totales "
                   "no son comparables.")