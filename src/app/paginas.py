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