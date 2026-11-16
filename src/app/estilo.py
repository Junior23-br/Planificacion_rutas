"""Sistema visual de la aplicación (R5).

Todo lo que tiene que ver con el aspecto vive aquí: colores, CSS, encabezados, tarjetas,
estados vacíos, el panel "Cómo se calculó", los mapas y el tema de las gráficas.
Las páginas no escriben CSS ni colores sueltos: llaman a estas funciones.

La justificación de la paleta, las tipografías y los principios de diseño está en
docs/guia_visual.md. Los colores base también están en .streamlit/config.toml.
"""
import html

import streamlit as st

# ---------------------------------------------------------------------------------------
# Paleta. Entre paréntesis, el contraste sobre blanco (WCAG 2.1).
# ---------------------------------------------------------------------------------------
TINTA = "#161616"          # texto principal (18,10:1)
TINTA_2 = "#525252"        # texto secundario (7,81:1)
TINTA_3 = "#6F6F6F"        # texto de apoyo y etiquetas (5,02:1)
FONDO = "#FFFFFF"
FONDO_2 = "#F4F4F4"        # superficies
BORDE = "#E0E0E0"          # separadores decorativos
BORDE_FUERTE = "#8D8D8D"   # bordes que sí comunican algo (3,32:1)
ACENTO = "#005D5D"         # acciones y selección (7,71:1)
ACENTO_SUAVE = "#D9FBFB"   # fondo de elementos resaltados

# Colores de datos (Okabe-Ito). El mismo color significa lo mismo en toda la aplicación.
AZUL = "#0072B2"           # el método principal: cola de prioridad, Held-Karp, versión propia
BERMELLON = "#D55E00"      # la alternativa: búsqueda lineal, heurística, SciPy, fuerza bruta
VERDE = "#009E73"
PURPURA = "#CC79A7"
INDIGO = "#332288"         # Paul Tol; solo para tramos del mapa
VINO = "#882255"           # Paul Tol; solo para tramos del mapa
TRAMOS = [AZUL, BERMELLON, VERDE, INDIGO, VINO, TINTA_2]   # todos con 3:1 o más sobre blanco

EXITO = "#198038"
ERROR = "#DA1E28"
AVISO = "#8E6A00"

FUENTE = "'IBM Plex Sans', 'Segoe UI', Helvetica, Arial, sans-serif"
FUENTE_MONO = "'IBM Plex Mono', Consolas, 'Courier New', monospace"

_CSS = f"""
<style>
/* Ancho de lectura y aire alrededor del contenido */
[data-testid="stMainBlockContainer"] {{
    max-width: 1180px;
    padding-top: 3rem;
    padding-bottom: 5rem;
}}

/* Una sola jerarquía tipográfica (escala de Carbon: 32 / 24 / 20 / 16 / 14 / 12) */
[data-testid="stMainBlockContainer"] h1 {{ font-size: 2rem; line-height: 2.5rem; font-weight: 500; letter-spacing: 0; padding: 0 0 .5rem 0; }}
[data-testid="stMainBlockContainer"] h2 {{ font-size: 1.5rem; line-height: 2rem; font-weight: 500; letter-spacing: 0; padding: 2rem 0 .5rem 0; }}
[data-testid="stMainBlockContainer"] h3 {{ font-size: 1.25rem; line-height: 1.75rem; font-weight: 600; letter-spacing: 0; padding: 1.25rem 0 .25rem 0; }}
[data-testid="stMainBlockContainer"] h4 {{ font-size: 1rem; line-height: 1.5rem; font-weight: 600; letter-spacing: 0; padding: .75rem 0 .25rem 0; }}
[data-testid="stCaptionContainer"], [data-testid="stCaptionContainer"] p {{ color: {TINTA_2} !important; opacity: 1 !important; }}

/* Plano: sin sombras en ningún componente */
[data-testid="stMainBlockContainer"] *, [data-testid="stSidebar"] * {{ box-shadow: none !important; }}

/* Foco visible para quien navega con teclado */
button:focus-visible, a:focus-visible, input:focus-visible, [role="tab"]:focus-visible,
[data-baseweb="select"] > div:focus-within {{
    outline: 2px solid {ACENTO} !important;
    outline-offset: 2px;
}}

/* Botones: objetivo de al menos 44 px de alto (ley de Fitts) */
[data-testid="stMainBlockContainer"] .stButton > button {{ min-height: 2.75rem; padding: 0 1.25rem; font-weight: 500; }}

/* Avisos planos: una barra a la izquierda en lugar de un bloque de color saturado */
[data-testid="stAlertContainer"] {{ border-radius: 0; border-left: 3px solid {BORDE_FUERTE}; background: {FONDO_2}; color: {TINTA}; }}
[data-testid="stAlertContentInfo"] {{ color: {TINTA}; }}
[data-testid="stAlertContainer"]:has([data-testid="stAlertContentSuccess"]) {{ border-left-color: {EXITO}; }}
[data-testid="stAlertContainer"]:has([data-testid="stAlertContentWarning"]) {{ border-left-color: {AVISO}; }}
[data-testid="stAlertContainer"]:has([data-testid="stAlertContentError"]) {{ border-left-color: {ERROR}; }}
[data-testid="stAlertContainer"] p {{ color: {TINTA}; }}

/* Pestañas y desplegables */
[data-testid="stTabs"] [role="tab"] {{ padding: .75rem 1rem; }}
[data-testid="stExpander"] details {{ border-radius: 0; border-color: {BORDE}; }}
[data-testid="stExpander"] summary {{ font-weight: 500; }}

/* Enlaces a otras páginas dentro del contenido */
[data-testid="stMainBlockContainer"] [data-testid="stPageLink"] a {{ padding-left: 0; min-height: 2.75rem; }}
[data-testid="stMainBlockContainer"] [data-testid="stPageLink"] a p {{ color: {ACENTO}; font-weight: 500; text-decoration: underline; text-underline-offset: 3px; }}

/* Barra lateral */
[data-testid="stSidebarNav"] a {{ min-height: 2.5rem; }}
.rp-marca {{ font-family: {FUENTE}; padding: 0 0 1rem 0; }}
.rp-marca b {{ display: block; font-size: 1rem; line-height: 1.375rem; font-weight: 600; color: {TINTA}; }}
.rp-marca span {{ display: block; font-size: .75rem; line-height: 1rem; color: {TINTA_2}; margin-top: .25rem; }}
.rp-pie {{ font-size: .75rem; line-height: 1.125rem; color: {TINTA_2}; }}

/* Encabezado de página */
.rp-enc {{ font-family: {FUENTE}; margin: 0 0 1.5rem 0; }}
.rp-ceja {{ font-size: .75rem; line-height: 1rem; letter-spacing: .08em; text-transform: uppercase; font-weight: 600; color: {ACENTO}; margin: 0 0 .5rem 0; }}
.rp-enc h1 {{ margin: 0; }}
.rp-enc p {{ font-size: 1.125rem; line-height: 1.75rem; color: {TINTA_2}; max-width: 46rem; margin: .25rem 0 0 0; }}

/* Tarjetas de métricas */
.rp-tarjetas {{ font-family: {FUENTE}; display: grid; grid-template-columns: repeat(auto-fit, minmax(170px, 1fr)); gap: 1px; background: {BORDE}; border: 1px solid {BORDE}; margin: .5rem 0 1rem 0; }}
.rp-tarjeta {{ background: {FONDO}; padding: 1rem 1rem 1.125rem 1rem; min-width: 0; }}
.rp-tarjeta .et {{ font-size: .75rem; line-height: 1rem; letter-spacing: .02em; color: {TINTA_2}; margin: 0 0 .5rem 0; }}
.rp-tarjeta .va {{ font-family: {FUENTE_MONO}; font-size: 1.5rem; line-height: 2rem; font-weight: 500; color: {TINTA}; margin: 0; overflow-wrap: anywhere; }}
.rp-tarjeta .no {{ font-size: .8125rem; line-height: 1.125rem; color: {TINTA_2}; margin: .375rem 0 0 0; }}
.rp-tarjeta.principal {{ border-top: 3px solid {ACENTO}; padding-top: calc(1rem - 3px); }}

/* Estado vacío */
.rp-vacio {{ font-family: {FUENTE}; border: 1px dashed {BORDE_FUERTE}; padding: 2rem 1.5rem; margin: 1rem 0; text-align: left; }}
.rp-vacio b {{ display: block; font-size: 1rem; font-weight: 600; color: {TINTA}; }}
.rp-vacio span {{ display: block; font-size: .875rem; line-height: 1.375rem; color: {TINTA_2}; margin-top: .25rem; max-width: 40rem; }}
.rp-vacio code {{ font-family: {FUENTE_MONO}; font-size: .8125rem; background: {FONDO_2}; padding: .125rem .375rem; }}

/* Panel "Cómo se calculó" */
.rp-como {{ font-family: {FUENTE}; border: 1px solid {BORDE}; border-top: 3px solid {TINTA}; margin: 2.5rem 0 1rem 0; }}
.rp-como > header {{ padding: 1.25rem 1.5rem .25rem 1.5rem; }}
.rp-como > header b {{ display: block; font-size: 1.25rem; line-height: 1.75rem; font-weight: 600; color: {TINTA}; }}
.rp-como > header span {{ display: block; font-size: .875rem; line-height: 1.375rem; color: {TINTA_2}; margin-top: .25rem; max-width: 48rem; }}
.rp-alg {{ display: grid; grid-template-columns: minmax(180px, 1fr) 3fr; gap: 0 2rem; padding: 1.25rem 1.5rem; border-top: 1px solid {BORDE}; }}
.rp-alg:first-of-type {{ border-top: 0; }}
.rp-alg .paso {{ font-size: .75rem; line-height: 1rem; letter-spacing: .08em; text-transform: uppercase; font-weight: 600; color: {TINTA_2}; margin: .125rem 0 .375rem 0; }}
.rp-alg .nombre {{ font-size: 1rem; line-height: 1.5rem; font-weight: 600; color: {TINTA}; margin: 0; }}
.rp-alg .comp {{ display: inline-block; font-family: {FUENTE_MONO}; font-size: .8125rem; line-height: 1.25rem; color: {TINTA}; background: {FONDO_2}; padding: .125rem .5rem; margin: .5rem 0 0 0; }}
.rp-alg dl {{ margin: 0; }}
.rp-alg dt {{ font-size: .75rem; line-height: 1rem; font-weight: 600; color: {TINTA_2}; margin: 0 0 .125rem 0; }}
.rp-alg dd {{ font-size: .9375rem; line-height: 1.5rem; color: {TINTA}; margin: 0 0 .75rem 0; max-width: 44rem; }}
.rp-alg dd:last-child {{ margin-bottom: 0; }}
.rp-como > footer {{ border-top: 1px solid {BORDE}; padding: 1.25rem 1.5rem 1.5rem 1.5rem; background: {FONDO_2}; }}
.rp-como > footer > b {{ display: block; font-size: .75rem; line-height: 1rem; letter-spacing: .08em; text-transform: uppercase; font-weight: 600; color: {TINTA_2}; margin-bottom: .75rem; }}
.rp-datos {{ display: grid; grid-template-columns: repeat(auto-fit, minmax(150px, 1fr)); gap: 1rem 1.5rem; }}
.rp-datos div span {{ display: block; font-size: .75rem; line-height: 1rem; color: {TINTA_2}; }}
.rp-datos div strong {{ display: block; font-family: {FUENTE_MONO}; font-size: 1.0625rem; line-height: 1.5rem; font-weight: 500; color: {TINTA}; overflow-wrap: anywhere; }}
.rp-como .nota {{ font-size: .8125rem; line-height: 1.25rem; color: {TINTA_2}; margin: 1rem 0 0 0; max-width: 48rem; }}

/* Fichas de texto (recorrido por requerimientos, decisiones) */
.rp-ficha {{ font-family: {FUENTE}; border-top: 1px solid {TINTA}; padding: 1rem 0 .5rem 0; margin: 0 0 1rem 0; }}
.rp-ficha .et {{ font-size: .75rem; line-height: 1rem; letter-spacing: .08em; text-transform: uppercase; font-weight: 600; color: {TINTA_2}; margin: 0 0 .25rem 0; }}
.rp-ficha .tx {{ font-size: .9375rem; line-height: 1.5rem; color: {TINTA}; margin: 0; }}
.rp-ficha .tx code, .rp-mono {{ font-family: {FUENTE_MONO}; font-size: .875em; background: {FONDO_2}; padding: .0625rem .375rem; }}

/* Leyenda con muestra de color (para mapas y simulaciones) */
.rp-leyenda {{ font-family: {FUENTE}; display: flex; flex-wrap: wrap; gap: .375rem 1.25rem; font-size: .8125rem; line-height: 1.25rem; color: {TINTA_2}; margin: .5rem 0 1rem 0; }}
.rp-leyenda i {{ display: inline-block; width: .75rem; height: .75rem; margin-right: .375rem; vertical-align: -1px; border: 1px solid {TINTA}; }}

/* Tablas propias (simulaciones) */
.rp-tabla-caja {{ overflow-x: auto; margin: .5rem 0 1rem 0; }}
.rp-tabla {{ font-family: {FUENTE}; border-collapse: collapse; width: 100%; font-size: .875rem; line-height: 1.25rem; }}
.rp-tabla th {{ text-align: left; font-weight: 600; color: {TINTA_2}; font-size: .75rem; padding: .5rem .75rem; border-bottom: 1px solid {TINTA}; white-space: nowrap; }}
.rp-tabla td {{ padding: .5rem .75rem; border-bottom: 1px solid {BORDE}; color: {TINTA}; white-space: nowrap; }}
.rp-tabla th.num {{ text-align: right; }}
.rp-tabla td.num {{ text-align: right; font-family: {FUENTE_MONO}; }}
.rp-tabla tr.actual td {{ background: {ACENTO_SUAVE}; }}
.rp-tabla td.nuevo {{ font-weight: 600; border-bottom: 2px solid {ACENTO}; }}
.rp-tabla td.tenue {{ color: {TINTA_3}; }}

/* Pantallas angostas */
@media (max-width: 720px) {{
    [data-testid="stMainBlockContainer"] {{ padding-top: 2rem; padding-left: 1rem; padding-right: 1rem; }}
    [data-testid="stMainBlockContainer"] h1 {{ font-size: 1.75rem; line-height: 2.25rem; }}
    .rp-enc p {{ font-size: 1rem; line-height: 1.5rem; }}
    .rp-alg {{ grid-template-columns: 1fr; gap: .75rem 0; }}
    .rp-como > header, .rp-alg, .rp-como > footer {{ padding-left: 1rem; padding-right: 1rem; }}
}}
</style>
"""


def e(texto):
    """Escapa un texto para insertarlo en HTML."""
    return html.escape(str(texto), quote=True)


def aplicar():
    """Inyecta el CSS de la aplicación. Se llama una vez por ejecución, desde app.py."""
    st.html(_CSS)


def marca_lateral():
    """Nombre del proyecto en la parte alta de la barra lateral."""
    st.sidebar.html('<div class="rp-marca"><b>Rutas del Paisaje Cultural Cafetero</b>'
                    '<span>Análisis de Algoritmos · Universidad del Quindío</span></div>')


def pie_lateral(texto):
    st.sidebar.html(f'<p class="rp-pie">{e(texto)}</p>')


def encabezado(titulo, descripcion="", ceja=""):
    """Encabezado común de todas las páginas: ceja (a qué requerimiento pertenece),
    título y una frase que dice para qué sirve la página."""
    partes = ['<div class="rp-enc">']
    if ceja:
        partes.append(f'<p class="rp-ceja">{e(ceja)}</p>')
    partes.append(f'<h1>{e(titulo)}</h1>')
    if descripcion:
        partes.append(f'<p>{e(descripcion)}</p>')
    partes.append('</div>')
    st.html("".join(partes))


def tarjetas(items):
    """Fila de tarjetas de métricas. items: lista de (etiqueta, valor, nota) o
    (etiqueta, valor, nota, True) para resaltar la tarjeta principal."""
    bloques = []
    for item in items:
        etiqueta, valor, nota = item[0], item[1], item[2] if len(item) > 2 else ""
        clase = "rp-tarjeta principal" if len(item) > 3 and item[3] else "rp-tarjeta"
        nota_html = f'<p class="no">{e(nota)}</p>' if nota else ""
        bloques.append(f'<div class="{clase}"><p class="et">{e(etiqueta)}</p>'
                       f'<p class="va">{e(valor)}</p>{nota_html}</div>')
    st.html(f'<div class="rp-tarjetas">{"".join(bloques)}</div>')


def estado_vacio(titulo, texto="", comando=""):
    """Caja para cuando todavía no hay nada que mostrar. Dice qué hacer a continuación."""
    extra = f' <code>{e(comando)}</code>' if comando else ""
    st.html(f'<div class="rp-vacio"><b>{e(titulo)}</b><span>{e(texto)}{extra}</span></div>')


def falta_archivo(ruta, comando="", para_que=""):
    """Mensaje de error útil cuando falta un archivo: cuál es, para qué se usa y cómo generarlo."""
    texto = f"No se encontró {ruta}."
    if para_que:
        texto += f" Se necesita para {para_que}."
    if comando:
        texto += " Se genera desde la raíz del repositorio con:"
    estado_vacio("Falta un archivo", texto, comando)


def ficha(etiqueta, texto_html):
    """Bloque de texto con etiqueta. texto_html admite <code> y <b>; lo escribe la aplicación."""
    st.html(f'<div class="rp-ficha"><p class="et">{e(etiqueta)}</p><p class="tx">{texto_html}</p></div>')


def leyenda(items):
    """items: lista de (color, texto)."""
    st.html('<div class="rp-leyenda">' + "".join(
        f'<span><i style="background:{c}"></i>{e(t)}</span>' for c, t in items) + '</div>')


def svg(codigo, descripcion):
    """Muestra un dibujo SVG generado por la aplicación, a todo el ancho de su columna.
    Se usa st.image porque st.html descarta las etiquetas <svg> al limpiar el HTML."""
    st.image(codigo, width="stretch", alt=descripcion)


def tabla_html(columnas, filas, numericas=(), fila_actual=None, nuevas=(), tenues=()):
    """Tabla propia para las simulaciones, con resaltado.

    columnas     encabezados.
    filas        lista de listas de textos.
    numericas    índices de las columnas alineadas a la derecha y en fuente monoespaciada.
    fila_actual  índice de la fila que se está procesando (fondo resaltado).
    nuevas       conjunto de (fila, columna) que cambiaron en este paso.
    tenues       conjunto de (fila, columna) que ya no participan.
    """
    cab = "".join(f'<th class="{"num" if n in numericas else ""}">{e(c)}</th>' for n, c in enumerate(columnas))
    cuerpo = []
    for i, fila in enumerate(filas):
        celdas = []
        for j, valor in enumerate(fila):
            clases = [c for c, ok in (("num", j in numericas), ("nuevo", (i, j) in nuevas),
                                      ("tenue", (i, j) in tenues)) if ok]
            celdas.append(f'<td class="{" ".join(clases)}">{e(valor)}</td>')
        cuerpo.append(f'<tr class="{"actual" if i == fila_actual else ""}">{"".join(celdas)}</tr>')
    st.html(f'<div class="rp-tabla-caja"><table class="rp-tabla"><thead><tr>{cab}</tr></thead>'
            f'<tbody>{"".join(cuerpo)}</tbody></table></div>')


def como_se_calculo(resumen, algoritmos, datos, nota="", titulo_datos="Datos de esta ejecución"):
    """Panel que cierra cada resultado.

    resumen     una o dos frases en lenguaje llano.
    algoritmos  lista de dict(paso, nombre, complejidad, que_hace, por_que):
                  paso         en qué parte del cálculo se usó
                  nombre       nombre del algoritmo
                  complejidad  texto corto, por ejemplo "O(n log n)"
                  que_hace     explicación para alguien que no es experto
                  por_que      por qué este y no la alternativa
    datos       lista de (etiqueta, valor) con cifras reales de esta ejecución.
    nota        aclaración final (de dónde sale una cifra, qué no incluye un tiempo...).
    titulo_datos  cambia el rótulo cuando las cifras vienen de un archivo y no de un cálculo en vivo.
    """
    filas = []
    for a in algoritmos:
        filas.append(
            '<div class="rp-alg"><div>'
            f'<p class="paso">{e(a["paso"])}</p><p class="nombre">{e(a["nombre"])}</p>'
            f'<span class="comp">{e(a["complejidad"])}</span></div>'
            f'<dl><dt>Qué hace</dt><dd>{e(a["que_hace"])}</dd>'
            f'<dt>Por qué este y no otro</dt><dd>{e(a["por_que"])}</dd></dl></div>')
    celdas = "".join(f'<div><span>{e(k)}</span><strong>{e(v)}</strong></div>' for k, v in datos)
    nota_html = f'<p class="nota">{e(nota)}</p>' if nota else ""
    st.html('<section class="rp-como"><header><b>Cómo se calculó</b>'
            f'<span>{e(resumen)}</span></header>{"".join(filas)}'
            f'<footer><b>{e(titulo_datos)}</b><div class="rp-datos">{celdas}</div>'
            f'{nota_html}</footer></section>')


# ---------------------------------------------------------------------------------------
# Formato de cifras (en español: punto para miles, coma para decimales)
# ---------------------------------------------------------------------------------------
def num(valor, decimales=0):
    """12345.678 -> '12.346' (decimales=0) o '12.345,68' (decimales=2)."""
    texto = f"{valor:,.{decimales}f}"
    return texto.replace(",", " ").replace(".", ",").replace(" ", ".")


def ms(valor):
    """Milisegundos con una precisión razonable según el tamaño."""
    if valor >= 100:
        return f"{num(valor, 0)} ms"
    if valor >= 1:
        return f"{num(valor, 1)} ms"
    return f"{num(valor, 3)} ms"


# ---------------------------------------------------------------------------------------
# Mapas
# ---------------------------------------------------------------------------------------
def mapa_base(centro, zoom=10):
    """Mapa con el fondo de OpenStreetMap atenuado, para que resalten los trazos del tema.
    Se usan las teselas estándar de OpenStreetMap porque no piden clave; la transparencia
    las aclara sin depender de CSS dentro del mapa."""
    import folium
    mapa = folium.Map(location=centro, zoom_start=zoom, tiles=None, control_scale=True)
    folium.TileLayer("OpenStreetMap", opacity=0.55, control=False).add_to(mapa)
    return mapa


def marcador(mapa, punto, texto, etiqueta="", color=TINTA):
    """Marcador circular plano con una letra o número dentro. No depende solo del color."""
    import folium
    estilo = (f"background:{FONDO};border:2px solid {color};color:{color};border-radius:50%;"
              "width:28px;height:28px;line-height:24px;text-align:center;"
              f"font:600 13px/24px {FUENTE};")
    folium.Marker(punto, tooltip=texto,
                  icon=folium.DivIcon(icon_size=(28, 28), icon_anchor=(14, 14),
                                      html=f'<div style="{estilo}">{e(etiqueta)}</div>')).add_to(mapa)


def mostrar_mapa(mapa, alto=520, clave=None):
    """Dibuja el mapa a todo el ancho disponible (se adapta a la pantalla)."""
    from streamlit_folium import st_folium
    st_folium(mapa, height=alto, use_container_width=True, returned_objects=[], key=clave)


# ---------------------------------------------------------------------------------------
# Gráficas (Altair)
# ---------------------------------------------------------------------------------------
# Las gráficas se dibujan en un lienzo: si la fuente web aún no cargó, hace falta una de respaldo.
FUENTE_GRAFICA = "IBM Plex Sans, Segoe UI, Helvetica, Arial, sans-serif"


def grafica(chart, alto=320):
    """Aplica el tema a una gráfica de Altair y la muestra a todo el ancho."""
    chart = (chart.properties(height=alto)
             .configure(font=FUENTE_GRAFICA, background=FONDO)
             .configure_view(stroke=None)
             .configure_axis(labelColor=TINTA_2, titleColor=TINTA_2, labelFontSize=12,
                             titleFontSize=12, titleFontWeight=500, gridColor=BORDE,
                             domainColor=BORDE_FUERTE, tickColor=BORDE_FUERTE, labelFont=FUENTE_GRAFICA,
                             titleFont=FUENTE_GRAFICA, titlePadding=10)
             .configure_legend(labelColor=TINTA, titleColor=TINTA_2, labelFontSize=12,
                               titleFontSize=12, titleFontWeight=500, orient="top",
                               labelFont=FUENTE_GRAFICA, titleFont=FUENTE_GRAFICA, symbolSize=90)
             .configure_text(font=FUENTE_GRAFICA))
    st.altair_chart(chart, width="stretch", theme=None)
