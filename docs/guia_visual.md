# Guía visual de la aplicación (R5)

Esta guía explica cómo se ve la aplicación y por qué. Todo lo que aquí se describe está
implementado en dos lugares: `.streamlit/config.toml` (tema base) y `src/app/estilo.py`
(colores, CSS y componentes). Las páginas no escriben colores ni CSS sueltos.

## 1. Criterio general

Estilo plano, minimalista y sobrio, pensado para un trabajo académico que se proyecta en una
sustentación:

- Fondo blanco y mucho espacio en blanco; el contenido tiene un ancho máximo de lectura (1180 px).
- Sin sombras, sin degradados y sin emojis. La separación se logra con líneas de 1 px y espacio.
- Un solo color de acento para las acciones y dos colores de datos con significado fijo.
- Una sola jerarquía tipográfica, igual en todas las páginas.

## 2. Paleta

### Interfaz

Los neutros y el acento salen de la paleta del sistema de diseño Carbon (IBM), que está pensada
para productos con mucha información. El acento es un verde azulado oscuro: remite al paisaje
cafetero sin recurrir a un marrón o a un verde saturado, y deja libres el azul y el naranja para
los datos.

| Uso | Color | Contraste sobre blanco | Contraste sobre gris #F4F4F4 |
|---|---|---|---|
| Texto principal | `#161616` | 18,10:1 | 16,45:1 |
| Texto secundario | `#525252` | 7,81:1 | 7,10:1 |
| Texto de apoyo | `#6F6F6F` | 5,02:1 | 4,57:1 |
| Acento (botón principal, enlaces, selección) | `#005D5D` | 7,71:1 | 7,01:1 |
| Borde que comunica (foco, estados vacíos) | `#8D8D8D` | 3,32:1 | 3,02:1 |
| Separador decorativo | `#E0E0E0` | 1,32:1 | no aplica |
| Superficie | `#F4F4F4` | no aplica | no aplica |
| Éxito | `#198038` | 5,02:1 | 4,56:1 |
| Aviso | `#8E6A00` | 4,99:1 | 4,53:1 |
| Error | `#DA1E28` | 5,00:1 | 4,55:1 |

El texto blanco sobre el acento (botón principal) tiene 7,71:1.

### Datos

Para las gráficas, los mapas y las simulaciones se usa la paleta de Okabe e Ito, diseñada para que
las categorías se distingan también con daltonismo y recomendada para figuras científicas
(Wong, 2011). El mismo color significa lo mismo en toda la aplicación:

| Significado | Color | Contraste sobre blanco |
|---|---|---|
| Método principal del proyecto: cola de prioridad, Held-Karp, envolvente propia, ruta calculada | `#0072B2` azul | 5,19:1 |
| La alternativa con la que se compara: búsqueda lineal, heurística, SciPy, fuerza bruta | `#D55E00` bermellón | 3,87:1 |
| Tercera categoría | `#009E73` verde azulado | 3,42:1 |

En el mapa del itinerario cada tramo cambia de color. Como hacen falta seis colores que se
distingan y que tengan al menos 3:1 sobre el fondo claro, a los tres anteriores se suman dos tonos
de la paleta de Paul Tol, `#332288` (12,17:1) y `#882255` (8,73:1), y el gris `#525252`. El amarillo,
el naranja y el azul claro de Okabe-Ito no se usan para trazos porque no llegan a 3:1 sobre blanco.

El color nunca es la única señal: en las gráficas cada método tiene además una forma distinta
(círculo o cuadrado), en los mapas las paradas llevan letra o número, y en las simulaciones las
aristas que no mejoran van punteadas.

### Cómo se calculó el contraste

Con la fórmula de luminancia relativa de WCAG 2.1. Los criterios aplicados son:

- 1.4.3 Contraste mínimo (AA): 4,5:1 para texto normal y 3:1 para texto grande.
- 1.4.11 Contraste de elementos no textuales (AA): 3:1 para componentes de la interfaz y para las
  partes de una gráfica necesarias para entenderla.

Todo el texto de la interfaz cumple 4,5:1 o más. Los colores de datos se usan en trazos, puntos y
rellenos (3:1 o más); cuando hay texto junto a ellos, el texto va en `#161616` o `#525252`.

## 3. Tipografía

Un par de la misma familia, la del sistema Carbon:

- **IBM Plex Sans** para todo el texto y los títulos.
- **IBM Plex Mono** para el código y las cifras de las tarjetas y las tablas. En una fuente
  monoespaciada los dígitos ocupan el mismo ancho, así que los números se comparan mejor en columna.

Se eligieron porque fueron diseñadas para interfaces técnicas, tienen tildes y eñe bien resueltas
y distinguen con claridad caracteres como `0`/`O` y `1`/`l`, importante cuando se muestran
identificadores (`CAB01`, `ATR10`) y complejidades (`O(n log n)`).

Las fuentes se cargan de Google Fonts desde `config.toml`. Sin conexión, la aplicación usa la
fuente sin serifa del sistema; nada deja de funcionar.

### Jerarquía

Tomada de la escala tipográfica de Carbon (12, 14, 16, 18, 20, 24, 28, 32...), en su versión
«productiva», pensada para pantallas de trabajo:

| Nivel | Tamaño / interlínea | Peso | Dónde |
|---|---|---|---|
| Ceja | 12 / 16 px, mayúsculas espaciadas | 600 | A qué requerimiento pertenece la página |
| Título de página | 32 / 40 px | 500 | Uno por página |
| Entrada | 18 / 28 px | 400 | Una frase que dice para qué sirve la página |
| Sección | 24 / 32 px | 500 | Bloques principales |
| Subsección | 20 / 28 px | 600 | Dentro de una sección |
| Cuerpo | 16 / 24 px | 400 | Texto corrido |
| Apoyo | 14 / 20 px | 400 | Notas y leyendas |
| Cifra de tarjeta | 24 / 32 px, monoespaciada | 500 | Métricas |

## 4. Componentes

Todos están en `src/app/estilo.py`:

| Componente | Función | Para qué |
|---|---|---|
| Encabezado | `encabezado()` | Ceja, título y entrada; igual en todas las páginas |
| Tarjetas de métricas | `tarjetas()` | Las cifras clave de un resultado; la principal lleva una línea de acento |
| Estado vacío | `estado_vacio()` | Qué hacer cuando todavía no hay resultado |
| Archivo faltante | `falta_archivo()` | Qué archivo falta, para qué sirve y con qué comando se genera |
| Panel «Cómo se calculó» | `como_se_calculo()` | Algoritmos usados, por qué, complejidad y datos de la ejecución |
| Ficha | `ficha()` | Bloque de texto con etiqueta |
| Tabla de simulación | `tabla_html()` | Tablas con la fila actual y las celdas que cambiaron resaltadas |
| Mapa | `mapa_base()`, `marcador()`, `mostrar_mapa()` | Fondo de OpenStreetMap atenuado y marcadores planos con letra o número |
| Gráfica | `grafica()` | Tema común para las gráficas de Altair |

Los avisos de Streamlit (información, éxito, advertencia, error) se aplanan: fondo gris y una barra
de color a la izquierda, en lugar de un bloque de color saturado.

El fondo del mapa usa las teselas estándar de OpenStreetMap con transparencia. Se probó el fondo
gris de CARTO, pero ahora muestra una marca de agua que pide clave de acceso.

## 5. Principios aplicados

### Leyes de la Gestalt

- **Proximidad:** cada resultado agrupa sus cifras en una fila de tarjetas pegadas; los bloques
  distintos se separan con espacio, no con cajas.
- **Similitud:** todas las métricas usan la misma tarjeta y todas las secciones, el mismo título.
  Lo que se ve igual se comporta igual.
- **Cierre:** las tarjetas comparten bordes de 1 px y forman una sola unidad sin dibujar una caja
  alrededor de cada una.
- **Figura y fondo:** fondo blanco, un solo color de acento y el fondo del mapa atenuado, para que
  la ruta sea la figura.
- **Continuidad:** en las simulaciones, el recorrido se lee como una secuencia (`A → B → C`) y la
  barra de progreso indica en qué paso se está.

### Diseño centrado en el usuario e interacción (HCI)

Heurísticas de Nielsen:

- **Visibilidad del estado del sistema:** indicador de carga mientras se calcula; si la selección
  cambia después de calcular, un aviso dice que el resultado es de la consulta anterior; «Paso 4 de 9»
  en las simulaciones.
- **Prevención de errores:** el botón de calcular se desactiva si el origen y el destino coinciden,
  si hay menos de 6 o más de 8 atractivos, o si la partida está entre los atractivos, y se explica
  por qué.
- **Reconocer antes que recordar:** los selectores muestran el nombre del lugar y su municipio, no
  solo el código, y permiten buscar escribiendo. Los valores por defecto ya producen un resultado.
- **Consistencia y estándares:** mismo encabezado, mismas tarjetas, mismos colores con el mismo
  significado y el mismo panel final en todas las páginas.
- **Ayuda para reconocer y recuperarse de errores:** si falta un archivo, el mensaje dice cuál, para
  qué se usa y con qué comando se genera.

Otras leyes:

- **Ley de Fitts:** los botones miden al menos 44 px de alto y la acción principal está junto a los
  campos que la alimentan.
- **Ley de Hick:** el menú tiene seis opciones en dos grupos; cada página tiene una sola acción
  principal; el detalle va en desplegables.
- **Carga cognitiva:** primero el resultado, después el mapa y al final la explicación. Las cifras
  van con su unidad y una nota corta.

### Accesibilidad

- Contraste AA en todo el texto (sección 2).
- Foco visible de 2 px en botones, enlaces, pestañas y campos, para navegar con teclado.
- El color no es la única señal (formas, letras, números y trazos punteados).
- Los dibujos de las simulaciones llevan texto alternativo con la descripción del paso.
- Los números usan el formato del español (punto para miles y coma decimal).
- La página se adapta a pantallas angostas: las tarjetas y las columnas se apilan y las tablas
  anchas se desplazan dentro de su caja.

## 6. Fuentes consultadas

- IBM. *Carbon Design System*, tipografía, escala y conjuntos de estilos «productivo» y «expresivo».
  https://carbondesignsystem.com/elements/typography/overview/ y
  https://carbondesignsystem.com/elements/typography/type-sets/
- Okabe, M. e Ito, K. (2008). *Color Universal Design: how to make figures and presentations that are
  friendly to colorblind people.* https://jfly.uni-koeln.de/color/
- Wong, B. (2011). Points of view: Color blindness. *Nature Methods*, 8, 441.
- Tol, P. *Colour schemes* (nota técnica). https://personal.sron.nl/~pault/
- W3C. *Web Content Accessibility Guidelines (WCAG) 2.1*, criterios 1.4.3 y 1.4.11.
  https://www.w3.org/TR/WCAG21/ ; explicación del criterio 1.4.3:
  https://www.w3.org/WAI/WCAG21/Understanding/contrast-minimum.html
- WebAIM. *Contrast and Color Accessibility.* https://webaim.org/articles/contrast/
- Nielsen, J. (1994). *10 Usability Heuristics for User Interface Design.*
  https://www.nngroup.com/articles/ten-usability-heuristics/
- Streamlit. *Theming* y *Customize fonts in your Streamlit app.*
  https://docs.streamlit.io/develop/concepts/configuration/theming
