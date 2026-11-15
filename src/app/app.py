"""Aplicación demostrativa del proyecto (R5).

Se ejecuta desde cualquier carpeta con:
    python -m streamlit run src/app/app.py
"""
import os
import sys

RAIZ = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
if RAIZ not in sys.path:
    sys.path.insert(0, RAIZ)
os.chdir(RAIZ)   # las rutas a data/ y resultados/ son relativas a la raíz del proyecto

import streamlit as st

from src.app import paginas

st.set_page_config(page_title="Rutas del Paisaje Cultural Cafetero", layout="wide")

PAGINAS = {
    "Inicio": paginas.inicio,
    "Ruta (R2)": paginas.ruta,
    "Envolvente (R3)": paginas.envolvente,
    "Itinerario (R4)": paginas.itinerario,
    "Resultados R1-R4": paginas.resultados,
    "Sustentación": lambda: paginas.pendiente("Ayudas para la sustentación"),
}

opcion = st.sidebar.radio("Menú", list(PAGINAS))
PAGINAS[opcion]()