# R5. Aplicación demostrativa

**Estado:** En curso

## Objetivo
Aplicación web local que permita usar y mostrar lo construido en R1 a R4 sin tocar el código.
Se ejecuta con `python -m streamlit run src/app/app.py` siguiendo el README.

## Funciones requeridas
1. **Ruta:** el usuario elige origen y destino del catálogo y la aplicación calcula en el momento
   el camino de menor tiempo con Dijkstra y cola de prioridad (sin librerías para el algoritmo),
   mostrándolo en un mapa con el tiempo estimado.
2. **Envolvente convexa:** muestra la envolvente convexa sobre el mapa del departamento
   (puede usar un resultado precalculado de R3).
3. **Itinerario:** punto de partida (por defecto Armenia) y de 6 a 8 atractivos. Muestra el
   recorrido con Held-Karp y con la heurística del vecino más cercano, el total de cada uno y la
   diferencia. Aplica la jornada de 11 h y el criterio de exclusión de atractivos de R4.
4. **Resultados:** tablas y gráficas de R1 a R4 tomadas de `resultados/`.

## Decisiones
- Tecnología: Streamlit, con Folium para los mapas. Las librerías se usan solo para la interfaz y
  el mapa; los algoritmos (Dijkstra, Held-Karp, vecino más cercano, envolvente) son propios.
- La comparación Held-Karp contra heurística se hace sobre los mismos atractivos finales (los que
  deja Held-Karp tras aplicar la jornada), para que la diferencia sea solo de recorrido.
- El criterio de exclusión depende del algoritmo usado para calcular el total; si la heurística
  decide sola qué quitar, puede conservar otros atractivos. Se muestra aparte, sin compararla.
- Los tiempos son estimaciones del modelo, de nodo a nodo, no tiempos reales de viaje.

## Criterios de aceptación
- La ruta CAB01 a CAB02 da 47 min 11 s, igual que `matriz_tiempos.csv`.
- El itinerario de Held-Karp coincide con `python -m src.ruta_optima.itinerario` para los mismos
  atractivos.
- Con los atractivos por defecto la heurística nunca da menos que Held-Karp.
- La aplicación arranca en una máquina limpia siguiendo solo el README.

## Añadido después de las funciones requeridas
- Tema visual propio (`.streamlit/config.toml`, `src/app/estilo.py`), justificado en `docs/guia_visual.md`.
- Panel «Cómo se calculó» al final de Ruta, Envolvente e Itinerario.
- Página de Sustentación: recorrido por R1 a R4, simulaciones paso a paso (`src/app/simulaciones.py`,
  comprobadas en `tests/test_simulaciones.py`), comparaciones generadas desde `resultados/`,
  decisiones, limitaciones y fuentes.
- Toda cifra que muestra la aplicación sale de `resultados/`, de `data/` o de un cálculo en vivo.

## Pendiente
- Nada.