# Rutas del Paisaje Cultural Cafetero

Proyecto final de Análisis de Algoritmos, 2026-2, Universidad del Quindío.
Planificación de rutas turísticas sobre la red vial del Quindío: construcción de la red (R1),
caminos de menor tiempo con Dijkstra (R2), envolvente convexa (R3), itinerario de un día con
Held-Karp y heurística del vecino más cercano (R4) y aplicación demostrativa (R5).

Integrantes: Meller, Jefferson Rodríguez y Cesar (completar apellidos).

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
| Ruta (R2) | Camino de menor tiempo entre dos lugares del catálogo (Dijkstra con cola de prioridad), calculado en el momento, con mapa y tiempo |
| Envolvente (R3) | Envolvente convexa de la red |
| Itinerario (R4) | Recorrido de 6 a 8 atractivos con Held-Karp y con vecino más cercano, total de cada uno y diferencia |
| Resultados R1-R4 | Tablas y gráficas de `resultados/` |
| Sustentación | Ayudas para la sustentación |

La página de Ruta tarda unos segundos la primera vez porque carga el grafo.

## Ejecutar cada requerimiento por consola
Siempre desde la raíz del repositorio.

### R1 y R2
(Cesar completa: comandos para construir la red, la matriz de tiempos y las mediciones de Dijkstra.)

### R3
(Meller completa: comando para calcular la envolvente convexa.)

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
python -m unittest tests.test_tsp tests.test_itinerario -v
```

## Estructura
```
data/catalogo/     catálogo de lugares y atractivos
data/processed/    grafo del Quindío y matriz de tiempos 40x40
resultados/        tablas, gráficas y datos de las mediciones (r1_, r2_, r3_, r4_)
specs/             especificaciones de cada requerimiento (Spec-Driven Development)
src/caminos/       R1 y R2: grafo y Dijkstra
src/ruta_optima/   R4: Held-Karp, fuerza bruta, heurística e itinerario
src/app/           R5: aplicación Streamlit
tests/             pruebas unitarias
```

## Protocolo de medición
Cada requerimiento se mide en la misma máquina, con 5 repeticiones y la mediana (si una corrida
pasa de 1 minuto se mide una sola vez), semilla fija y límite de 5 minutos por corrida. La máquina
usada en R4 está descrita en `resultados/r4_maquina.txt`.

## Uso de inteligencia artificial
Declarado en el Anexo A del documento técnico.