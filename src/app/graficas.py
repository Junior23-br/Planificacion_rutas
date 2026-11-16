"""Gráficas de los experimentos, generadas desde los CSV de resultados/ (Altair).

Cada función recibe el DataFrame ya leído y devuelve una gráfica sin tema; el tema lo pone
estilo.grafica(). Convención de color en toda la aplicación: azul = método principal del
proyecto, bermellón = la alternativa con la que se compara. La forma del punto repite la
misma información para no depender solo del color.
"""
import math

import altair as alt
import pandas as pd

from src.app.estilo import AZUL, BERMELLON, TINTA, TINTA_2, num

# Vega escribe los números en inglés (1,000.5). Estas expresiones los pasan a español en los ejes;
# en las descripciones emergentes se usan columnas de texto ya formateadas con estilo.num().
MILES = "replace(format(datum.value, ','), /,/g, '.')"
LOG = "replace(replace(replace(format(datum.value, ',~f'), /,/g, '#'), '.', ','), /#/g, '.')"


def _eje(titulo, expresion=MILES, **extra):
    return alt.Axis(title=titulo, labelExpr=expresion, **extra)


def _decadas(valores):
    """Potencias de 10 que cubren los valores: marcas limpias para un eje logarítmico."""
    bajo, alto = math.floor(math.log10(min(valores))), math.ceil(math.log10(max(valores)))
    return [10.0 ** exp for exp in range(bajo, alto + 1)]


def _serie_125(valores):
    """Marcas 1, 2, 5, 10, 20, 50... dentro del rango de los valores."""
    marcas = [m * d for d in _decadas(valores) for m in (1, 2, 5)]
    return [m for m in marcas if min(valores) * 0.99 <= m <= max(valores) * 1.01]


def _txt(df, columna, decimales=0):
    """Agrega la columna '<columna>_txt' con el número formateado en español."""
    df[columna + "_txt"] = [("" if pd.isna(v) else num(v, decimales)) for v in df[columna]]
    return df


def _escala(principal, alternativa):
    return (alt.Scale(domain=[principal, alternativa], range=[AZUL, BERMELLON]),
            alt.Scale(domain=[principal, alternativa], range=["circle", "square"]))


def r1_componente(df):
    """Tiempo de la componente fuertemente conexa según el tamaño de la red."""
    df = _txt(_txt(_txt(df.copy(), "V_antes"), "E_antes"), "mediana_ms", 1)
    base = alt.Chart(df).encode(
        x=alt.X("V_antes:Q", axis=_eje("Nodos de la red (V)")),
        y=alt.Y("mediana_ms:Q", axis=_eje("Tiempo, mediana (ms)")),
        tooltip=[alt.Tooltip("red:N", title="Red"), alt.Tooltip("V_antes_txt:N", title="V"),
                 alt.Tooltip("E_antes_txt:N", title="E"),
                 alt.Tooltip("mediana_ms_txt:N", title="Mediana (ms)")])
    return (base.mark_line(color=AZUL, strokeWidth=2) + base.mark_point(color=AZUL, size=90, filled=True)
            + base.mark_text(dy=-14, color=TINTA_2, fontSize=12).encode(text="red:N"))


def r2_tiempos(df):
    """Tiempo por consulta frente a nodos explorados, cola y lineal (eje vertical logarítmico)."""
    cola = df[["origen", "destino", "explorados_cola", "cola_mediana_ms"]].copy()
    cola.columns = ["origen", "destino", "explorados", "ms"]
    cola["metodo"] = "Cola de prioridad"
    lineal = df.dropna(subset=["lineal_mediana_ms"])[
        ["origen", "destino", "explorados_lineal", "lineal_mediana_ms"]].copy()
    lineal.columns = ["origen", "destino", "explorados", "ms"]
    lineal["metodo"] = "Búsqueda lineal"
    datos = pd.concat([cola, lineal], ignore_index=True)
    datos["par"] = datos["origen"] + " → " + datos["destino"]
    datos = _txt(_txt(datos, "explorados"), "ms", 3)
    color, forma = _escala("Cola de prioridad", "Búsqueda lineal")
    return alt.Chart(datos).mark_point(size=80, filled=True, opacity=0.9).encode(
        x=alt.X("explorados:Q", axis=_eje("Nodos explorados en la consulta")),
        y=alt.Y("ms:Q", scale=alt.Scale(type="log"),
                axis=_eje("Tiempo, mediana (ms) · escala logarítmica", LOG, values=_decadas(datos["ms"]))),
        color=alt.Color("metodo:N", title="Versión de Dijkstra", scale=color),
        shape=alt.Shape("metodo:N", title="Versión de Dijkstra", scale=forma),
        tooltip=[alt.Tooltip("par:N", title="Par"), alt.Tooltip("metodo:N", title="Versión"),
                 alt.Tooltip("explorados_txt:N", title="Explorados"),
                 alt.Tooltip("ms_txt:N", title="Mediana (ms)")])


def r2_cociente(df):
    """Cuántas veces más lenta fue la búsqueda lineal en cada par medido con ambas."""
    datos = df.dropna(subset=["cociente_lineal_cola"]).copy()
    datos["par"] = datos["origen"] + " → " + datos["destino"]
    datos = _txt(_txt(datos, "cociente_lineal_cola", 1), "explorados_cola")
    return alt.Chart(datos).mark_bar(color=AZUL).encode(
        y=alt.Y("par:N", title=None, sort="-x"),
        x=alt.X("cociente_lineal_cola:Q", axis=_eje("Tiempo lineal / tiempo con cola")),
        tooltip=[alt.Tooltip("par:N", title="Par"),
                 alt.Tooltip("cociente_lineal_cola_txt:N", title="Cociente"),
                 alt.Tooltip("explorados_cola_txt:N", title="Explorados")])


def r3_tiempos(df):
    """Envolvente propia frente a SciPy según el número de puntos (ambos ejes logarítmicos)."""
    azar = df[df["conjunto"].str.startswith("azar")]
    filas = []
    for _, f in df.iterrows():
        filas.append(dict(conjunto=f["conjunto"], n=f["n_puntos"], ms=f["propio_mediana_ms"],
                          metodo="Divide y vencerás (propia)", vertices=f["vertices"]))
        filas.append(dict(conjunto=f["conjunto"], n=f["n_puntos"], ms=f["scipy_mediana_ms"],
                          metodo="SciPy (Qhull)", vertices=f["vertices"]))
    datos = _txt(_txt(pd.DataFrame(filas), "n"), "ms", 3)
    color, forma = _escala("Divide y vencerás (propia)", "SciPy (Qhull)")
    cod = dict(
        x=alt.X("n:Q", scale=alt.Scale(type="log"),
                axis=_eje("Número de puntos · escala logarítmica", LOG, values=_serie_125(datos["n"]))),
        y=alt.Y("ms:Q", scale=alt.Scale(type="log"),
                axis=_eje("Tiempo, mediana (ms) · escala logarítmica", LOG, values=_decadas(datos["ms"]))),
        color=alt.Color("metodo:N", title="Implementación", scale=color),
        tooltip=[alt.Tooltip("conjunto:N", title="Conjunto"), alt.Tooltip("metodo:N", title="Implementación"),
                 alt.Tooltip("n_txt:N", title="Puntos"),
                 alt.Tooltip("vertices:Q", title="Vértices"),
                 alt.Tooltip("ms_txt:N", title="Mediana (ms)")])
    lineas = alt.Chart(datos[datos["conjunto"].isin(azar["conjunto"])]).mark_line(strokeWidth=2).encode(**cod)
    puntos = alt.Chart(datos).mark_point(size=90, filled=True).encode(
        shape=alt.Shape("metodo:N", title="Implementación", scale=forma), **cod)
    return lineas + puntos


def r4_exactas(df):
    """Fuerza bruta frente a Held-Karp según k (eje vertical logarítmico)."""
    datos = df[df["estado"] == "completada"].copy()
    datos["metodo"] = datos["metodo"].map({"held_karp": "Held-Karp", "fuerza_bruta": "Fuerza bruta"})
    datos = _txt(datos, "mediana_ms", 3)
    color, forma = _escala("Held-Karp", "Fuerza bruta")
    cod = dict(
        x=alt.X("k:O", title="Lugares a visitar (k)", axis=alt.Axis(labelAngle=0)),
        y=alt.Y("mediana_ms:Q", scale=alt.Scale(type="log"),
                axis=_eje("Tiempo, mediana (ms) · escala logarítmica", LOG,
                          values=_decadas(datos["mediana_ms"]))),
        color=alt.Color("metodo:N", title="Método exacto", scale=color),
        tooltip=[alt.Tooltip("metodo:N", title="Método"), alt.Tooltip("k:O", title="k"),
                 alt.Tooltip("mediana_ms_txt:N", title="Mediana (ms)"),
                 alt.Tooltip("repeticiones:Q", title="Repeticiones")])
    return (alt.Chart(datos).mark_line(strokeWidth=2).encode(**cod)
            + alt.Chart(datos).mark_point(size=90, filled=True).encode(
                shape=alt.Shape("metodo:N", title="Método exacto", scale=forma), **cod))


def r4_calidad(detalle, resumen):
    """Alejamiento de la heurística respecto del óptimo: cada instancia y el promedio por k."""
    detalle = _txt(detalle.copy(), "alejamiento_pct", 2)
    resumen = _txt(_txt(resumen.copy(), "alejamiento_promedio_pct", 2), "alejamiento_maximo_pct", 2)
    puntos = alt.Chart(detalle).mark_point(size=70, color=BERMELLON, shape="square", filled=True,
                                           opacity=0.75).encode(
        x=alt.X("k:O", title="Lugares a visitar (k)", axis=alt.Axis(labelAngle=0)),
        y=alt.Y("alejamiento_pct:Q", axis=_eje("Alejamiento del óptimo (%)")),
        tooltip=[alt.Tooltip("k:O", title="k"), alt.Tooltip("instancia:Q", title="Instancia"),
                 alt.Tooltip("semilla:Q", title="Semilla"),
                 alt.Tooltip("alejamiento_pct_txt:N", title="Alejamiento (%)")])
    promedio = alt.Chart(resumen).mark_tick(color=TINTA, thickness=3, size=44).encode(
        x=alt.X("k:O"), y=alt.Y("alejamiento_promedio_pct:Q"),
        tooltip=[alt.Tooltip("k:O", title="k"),
                 alt.Tooltip("alejamiento_promedio_pct_txt:N", title="Promedio (%)"),
                 alt.Tooltip("alejamiento_maximo_pct_txt:N", title="Máximo (%)")])
    return puntos + promedio
