# Rutas del Paisaje Cultural Cafetero

Proyecto final de Análisis de Algoritmos, 2026-2, Universidad del Quindío.
Planificación de rutas turísticas sobre la red vial del Quindío: construcción de la red (R1),
caminos de menor tiempo con Dijkstra (R2), envolvente convexa (R3), itinerario de un día con
Held-Karp y heurística del vecino más cercano (R4) y aplicación demostrativa (R5).

Integrantes: Meller Batero, Jefferson Rodríguez y Cesar Tulcan

## Requisitos
- Python 3.14 (versión con la que se probó todo).
- Conexión a internet solo para ver el fondo del mapa en la aplicación.

## Instalación
Desde la raíz del repositorio:

```
python -m pip install -r requirements.txt
```

(Opcional, en un entorno virtual: `python -m venv .venv`, activarlo y luego el comando anterior.)

## Ejecutar la aplicación (R5)
Desde la raíz del repositorio:

```
python -m streamlit run src/app/app.py
```

Se abre en `http://localhost:8501`. La primera vez Streamlit puede pedir un correo: se puede dejar
en blanco con Enter. Páginas:

| Página | Qué muestra |
|---|---|
| Inicio | Cifras del proyecto y acceso a las demás páginas |
| Ruta más rápida (R2) | Camino de menor tiempo entre dos lugares del catálogo (Dijkstra con cola de prioridad), calculado en el momento, con mapa y tiempo |
| Envolvente convexa (R3) | Envolvente convexa de la red sobre el mapa, con verificación en vivo contra SciPy |
| Itinerario de un día (R4) | Recorrido de 6 a 8 atractivos con Held-Karp y con vecino más cercano, total de cada uno, diferencia y mapa |
| Resultados | Tablas y gráficas de `resultados/`, con la máquina de cada medición |
| Sustentación | Recorrido por R1 a R4, simulaciones paso a paso, comparaciones, decisiones y fuentes |

Las páginas de Ruta, Envolvente e Itinerario terminan con un panel «Cómo se calculó»: qué
algoritmos se usaron, por qué, su complejidad y los datos de esa ejecución.

La página de Ruta tarda unos segundos la primera vez porque carga el grafo. El tema visual está en
`.streamlit/config.toml` y `src/app/estilo.py`; su justificación, en `docs/guia_visual.md`.

## Ejecutar cada requerimiento por consola
Siempre desde la raíz del repositorio.

### R1 y R2
Estos scripts no son módulos: se ejecutan como archivo y en este orden (las mediciones de R1 y R2 tardan; la descarga necesita internet):
```
python src/red/descarga_red.py        # descarga la red de OSM del Quindío
python src/red/pesos.py               # asigna tiempo a cada arista
python src/red/guardar_grafo.py       # deja la componente conexa más grande
python src/red/asociacion.py          # asocia cada lugar del catálogo a su nodo
python src/red/componente.py          # mediciones de R1 (2/5/10/20 km y departamento)
python src/caminos/mediciones_r2.py   # mediciones de Dijkstra (lineal vs. cola)
python src/caminos/matriz_tiempos.py  # matriz de tiempos entre lugares
python src/caminos/grafica_r1.py
python src/caminos/grafica_r2.py
```
Los archivos ya generados están en `data/processed/` y `resultados/`, así que la aplicación y R3/R4 funcionan sin repetir estos pasos.

### R3
```
python -m src.envolvente.calcular_envolvente
python -m src.envolvente.mediciones_r3
python -m src.envolvente.grafica_r3
```

### R4
```
python -m src.ruta_optima.itinerario
python -m src.ruta_optima.itinerario --atractivos ATR01,ATR03,ATR05,ATR08,ATR09,ATR12
python -m src.ruta_optima.medicion --matriz data/processed/matriz_tiempos.csv --inicio CAB01
python -m src.ruta_optima.calidad --matriz data/processed/matriz_tiempos.csv --inicio CAB01
python -m src.ruta_optima.graficas
python -m src.ruta_optima.memoria_hk
```
`medicion` tarda varios minutos: la fuerza bruta con 12 atractivos se corta a los 300 s y se
reporta como "no completada".

## Pruebas
```
python -m unittest tests.test_tsp tests.test_itinerario tests.test_dijkstra tests.test_envolvente tests.test_simulaciones -v
```

## Estructura
```
data/catalogo/     catálogo de lugares y atractivos
data/processed/    grafo del Quindío y matriz de tiempos 40x40
resultados/        tablas, gráficas y datos de las mediciones (r1_, r2_, r3_, r4_)
specs/             especificaciones de cada requerimiento (Spec-Driven Development)
src/red/           R1: descarga y preparación de la red
src/caminos/       R2: grafo y Dijkstra
src/envolvente/    R3: envolvente convexa
src/ruta_optima/   R4: Held-Karp, fuerza bruta, heurística e itinerario
src/app/           R5: aplicación Streamlit (app, paginas, sustentacion, simulaciones, estilo, datos, graficas)
docs/              guía visual de la aplicación
tests/             pruebas unitarias
```

## Protocolo de medición
Cada requerimiento se mide en la misma máquina, con 5 repeticiones y la mediana (si una corrida
pasa de 1 minuto se mide una sola vez), semilla fija y límite de 5 minutos por corrida. La máquina
usada en cada requerimiento está descrita en `resultados/` (archivos `*_maquina.txt`).

## Uso de inteligencia artificial
Declarado en el Anexo A del documento técnico.