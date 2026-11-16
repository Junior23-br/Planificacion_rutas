"""Aplicación demostrativa del proyecto (R5).

Se ejecuta desde la raíz del repositorio con:
    python -m streamlit run src/app/app.py

Este archivo solo arma el menú. Las páginas están en paginas.py y sustentacion.py, el aspecto
en estilo.py (y .streamlit/config.toml) y la lectura de archivos en datos.py.
"""
import os
import sys

RAIZ = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
if RAIZ not in sys.path:
    sys.path.insert(0, RAIZ)
os.chdir(RAIZ)   # las rutas a data/ y resultados/ son relativas a la raíz del proyecto

import streamlit as st

from src.app import estilo, paginas, sustentacion

st.set_page_config(page_title="Rutas del Paisaje Cultural Cafetero", layout="wide",
                   initial_sidebar_state="expanded")
estilo.aplicar()

PAGINAS = {
    "Inicio": st.Page(paginas.inicio, title="Inicio", url_path="inicio", default=True),
    "Ruta": st.Page(paginas.ruta, title="Ruta más rápida (R2)", url_path="ruta"),
    "Envolvente": st.Page(paginas.envolvente, title="Envolvente convexa (R3)", url_path="envolvente"),
    "Itinerario": st.Page(paginas.itinerario, title="Itinerario de un día (R4)", url_path="itinerario"),
    "Resultados": st.Page(paginas.resultados, title="Resultados", url_path="resultados"),
    "Sustentación": st.Page(sustentacion.pagina, title="Sustentación", url_path="sustentacion"),
}
paginas.registrar_enlaces(PAGINAS)

# Menú en dos grupos (ley de Hick: pocas opciones y agrupadas por propósito)
navegacion = st.navigation({
    "Aplicación": [PAGINAS["Inicio"], PAGINAS["Ruta"], PAGINAS["Envolvente"], PAGINAS["Itinerario"]],
    "Evidencia": [PAGINAS["Resultados"], PAGINAS["Sustentación"]],
})
estilo.marca_lateral()
estilo.pie_lateral("Los tiempos son estimaciones del modelo, de nodo a nodo; no son tiempos reales de viaje.")
navegacion.run()
