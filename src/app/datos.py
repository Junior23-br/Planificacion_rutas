"""Lectura de datos para la aplicación (R5), con caché y tolerante a archivos faltantes.

Regla: ninguna función de este módulo hace fallar la aplicación si falta un archivo.
Devuelven None y la página decide qué mensaje mostrar (ver estilo.falta_archivo).
Todas las rutas son relativas a la raíz del repositorio (app.py hace os.chdir a la raíz).
"""
import os
import re

import pandas as pd
import streamlit as st

RESULTADOS = "resultados"
GRAFO = "data/processed/componente.graphml"
CATALOGO = "data/catalogo/catalogo_lugares.csv"
ASOCIACION = "data/processed/asociacion_lugares.csv"
MATRIZ = "data/processed/matriz_tiempos.csv"

# Cómo se genera cada archivo (para los mensajes de error). Tomado del README.
COMANDOS = {
    "r3_envolvente.csv": "python -m src.envolvente.calcular_envolvente",
    "r3_tiempos.csv": "python -m src.envolvente.mediciones_r3",
    "r4_exactas.csv": "python -m src.ruta_optima.medicion --matriz data/processed/matriz_tiempos.csv --inicio CAB01",
    "r4_calidad_resumen.csv": "python -m src.ruta_optima.calidad --matriz data/processed/matriz_tiempos.csv --inicio CAB01",
    "r4_calidad_detalle.csv": "python -m src.ruta_optima.calidad --matriz data/processed/matriz_tiempos.csv --inicio CAB01",
}


def res(nombre):
    """Ruta de un archivo dentro de resultados/."""
    return f"{RESULTADOS}/{nombre}"       # con "/" funciona en Windows y se lee igual en los mensajes


def _marca(ruta):
    """Fecha de modificación: forma parte de la clave de caché, así un archivo regenerado
    se vuelve a leer sin reiniciar la aplicación."""
    try:
        return os.path.getmtime(ruta)
    except OSError:
        return None


@st.cache_data(show_spinner=False)
def _csv(ruta, marca):
    return pd.read_csv(ruta)


def csv(ruta):
    """DataFrame del CSV, o None si no existe o no se puede leer."""
    marca = _marca(ruta)
    if marca is None:
        return None
    try:
        return _csv(ruta, marca)
    except Exception:
        return None


@st.cache_data(show_spinner=False)
def _texto(ruta, marca):
    with open(ruta, encoding="utf-8") as f:
        return f.read()


def texto(ruta):
    """Contenido de un archivo de texto, o None si no existe."""
    marca = _marca(ruta)
    if marca is None:
        return None
    try:
        return _texto(ruta, marca)
    except Exception:
        return None


def maquina(nombre):
    """Lee resultados/<nombre> (archivos *_maquina.txt) como lista de (campo, valor)."""
    contenido = texto(res(nombre))
    if not contenido:
        return None
    pares = []
    for linea in contenido.splitlines():
        if ":" in linea:
            campo, valor = linea.split(":", 1)
            pares.append((campo.strip(), valor.strip()))
    return pares


def integrantes():
    """Nombres del equipo tal como están en el README (no se escriben en el código)."""
    contenido = texto("README.md") or ""
    m = re.search(r"^Integrantes:\s*(.+)$", contenido, flags=re.MULTILINE)
    return m.group(1).strip() if m else ""


@st.cache_data(show_spinner=False)
def _catalogo_y_matriz(marca_cat, marca_mat):
    from src.ruta_optima.itinerario import leer_catalogo, leer_matriz
    cat = leer_catalogo(CATALOGO)
    ids, T = leer_matriz(MATRIZ)
    return cat, ids, T


def catalogo_y_matriz():
    """(catálogo, ids, T) o None si falta el catálogo o la matriz de tiempos."""
    marca_cat, marca_mat = _marca(CATALOGO), _marca(MATRIZ)
    if marca_cat is None or marca_mat is None:
        return None
    return _catalogo_y_matriz(marca_cat, marca_mat)


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


@st.cache_resource(show_spinner="Leyendo las coordenadas de la red...")
def coordenadas_nodos():
    """dict id de nodo (texto) -> (latitud, longitud). Es rápido: no carga el grafo."""
    return _leer_coordenadas(GRAFO)


@st.cache_resource(show_spinner="Cargando la red vial (solo la primera vez, tarda unos segundos)...")
def red():
    """Carga una sola vez el grafo, los lugares y las coordenadas de cada nodo."""
    from src.caminos.grafo import cargar_grafo, cargar_lugares

    ids, indice, adj, info = cargar_grafo(GRAFO)
    lugares = cargar_lugares(indice, CATALOGO, ASOCIACION)
    por_id = coordenadas_nodos()
    coord = [por_id[str(n)] for n in ids]        # (latitud, longitud) por índice
    return dict(adj=adj, lugares=lugares, coord=coord, info=info)


def faltantes_red():
    """Archivos que necesita red() y que no están."""
    return [r for r in (GRAFO, CATALOGO, ASOCIACION) if not os.path.exists(r)]


@st.cache_data(show_spinner=False, max_entries=512)
def tramo(origen_idx, destino_idx):
    """Camino de menor tiempo entre dos nodos de la red, listo para dibujar.
    Devuelve (tiempo_s, puntos, explorados). En caché: redibujar un mapa no recalcula."""
    from src.caminos.dijkstra import ruta_minima
    r = red()
    tiempo_s, camino, explorados = ruta_minima(r["adj"], origen_idx, destino_idx)
    return tiempo_s, [r["coord"][i] for i in camino], explorados


def memoria_estimada(V, E):
    """Memoria del grafo como matriz y como listas, con los supuestos de src/red/memoria.py:
    8 bytes por peso; cada entrada de lista guarda destino (4 B) + distancia (8 B) + tiempo (8 B);
    un índice de 8 bytes por nodo. Devuelve MB: (matriz 1 peso, matriz 2 pesos, listas)."""
    MB = 1024 ** 2
    return V * V * 8 / MB, 2 * V * V * 8 / MB, (E * (4 + 8 + 8) + V * 8) / MB
