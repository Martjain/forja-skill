# Ilustraciones de una guía forja

Las ilustraciones son lo primero que se juzga de una guía. Un dibujo torpe hace que toda la guía se vea amateur, aunque el contenido sea correcto. **Cada ilustración debe sacar 8 de 10 o más en la rúbrica de la sección 9** antes de darla por buena.

Referencia de nivel: [ejemplos/motor-animado.html](../assets/ejemplos/motor-animado.html). Úsalo para entender el estándar; no copies el dibujo.

## Contenido
1. Elige un lenguaje visual
2. Sistema de trazo
3. Materiales, color y profundidad
4. Geometría calculada, nunca a ojo
5. Etiquetas y composición
6. Formas orgánicas
7. Animar procesos
8. El kit
9. Rúbrica (mínimo 8 de 10)
10. Proceso de trabajo

---

## 1. Elige un lenguaje visual

Según el tema, uno de estos (y mantenlo en toda la guía):

| Lenguaje | Para | Rasgos |
|---|---|---|
| **Corte técnico** | Máquinas, dispositivos, cuerpos, instalaciones | Vista en corte; material cortado con achurado; piezas con volumen sutil |
| **Diagrama de sistema** | Software, procesos, organizaciones, flujos | Cajas con jerarquía (no todas iguales), conectores ortogonales, puertos claros |
| **Gráfica matemática** | Funciones, datos, física cuantitativa | Ejes con marcas, rejilla tenue, curvas **calculadas** de la función real |
| **Línea de tiempo o mapa** | Historia, rutas, secuencias | Un eje fuerte, eventos anclados con guías |

## 2. Sistema de trazo

- **Tres grosores, siempre los mismos:** contorno **2.5**, detalle **1.25**, guías y cotas **1**. Las piezas gruesas (una biela, un tubo) se dibujan como dos líneas superpuestas (contorno oscuro + relleno claro), no con un grosor arbitrario.
- `stroke-linejoin="round"` y `stroke-linecap="round"` en contornos.
- Ningún trazo flota: si una pieza está unida a otra (aletas a una pared, un cable a un borne), **se tocan**.
- **En gráficas** el grosor solo no basta para ordenar las líneas. Jerarquía:
  - la curva o línea protagonista: 2.5, continua;
  - las líneas que se comparan con ella (secante, tangente): 2.5, cada una de su color; si se pueden encimar, una de ellas punteada (`stroke-dasharray="6 4"`) y dibujada encima;
  - referencias y proyecciones a los ejes: 1, punteadas;
  - ejes y marcas: 1.25;
  - puntos: círculo de radio 4.5 con borde del color del fondo (`punto()` de `svg_kit`).
- Los grosores que pongas en el CSS de la guía también cuentan: ajustarlos al sistema es parte del redibujo.

## 3. Materiales, color y profundidad

- **Material cortado = achurado** (patrones `ach-*` del kit). Distingue zonas con el achurado de su color (caliente, frío, neutro).
- **Metal y piezas sólidas:** degradado vertical sutil claro → oscuro (`met` del kit). Nada de sombras difusas grandes.
- **El color significa algo y no cambia** en toda la guía. Ejemplo: naranja = caliente, azul = frío; o verde = correcto, rojo = error. Declara el significado una vez (leyenda o texto).
- **Degradado solo para una magnitud continua:** temperatura a lo largo de un gas, presión en un tubo, concentración. Nunca como decoración.
- Una sombra de piso muy tenue (elipse, opacidad 0.06–0.08) asienta el objeto.
- **Si el lenguaje no tiene materiales** (gráficas, diagramas de sistema), la profundidad sale de: rejilla tenue detrás, relleno translúcido (opacidad .1–.15) en las áreas que importan (un triángulo de pendiente, un área bajo la curva) y cajas con un fondo apenas distinto del de la página.

## 4. Geometría calculada, nunca a ojo

**Genera los dibujos con código** y calcula las coordenadas. En Python usa [svg_kit.py](../scripts/svg_kit.py): `Lienzo` (registra cada texto, conoce la letra mínima y comprueba choques y márgenes con `comprobar()`), `Plano` (mundo → viewBox, `curva`, `recta`, `rejilla`, `ejes`, `marcas`, `en_curva`), `linea`, `punto` y `biela_manivela`. La ayuda está al inicio del archivo.
- Mecanismos: usa `forja.kit.bielaManivela` o calcula la cinemática; la biela mide lo mismo en todas las posiciones.
- Curvas de funciones: muestrea la función real (`for x … y = f(x)`), no dibujes "algo que se parece".
- Proporciones reales cuando importan (un engrane de 20 dientes contra uno de 40 tiene el doble de diámetro).
- **Comprueba con `assert`** lo que no puede pasar: el pistón no sale del cilindro, dos piezas no se atraviesan, una etiqueta no sale del viewBox.

## 5. Etiquetas y composición

- **Etiqueta = título (13–14 px, peso 600) + frase corta (12 px, opacidad .75)**, con una **línea guía** de 1 px que termina en un punto sobre la pieza exacta.
- Las etiquetas van en **zonas vacías**, alineadas entre sí, nunca encima de trazos ni de otras etiquetas. En un corte o un diagrama, en los márgenes alrededor del dibujo. En una gráfica, dentro del plano donde no pasa ninguna curva (no reserves un margen que en el celular queda vacío).
- **Piezas que se mueven** (un punto que sigue a un slider, el pistón): no les pongas `g.etiqueta`. Usa una letra corta (P, Q) que el JS mueve junto con la pieza, del tamaño mínimo, y explica las letras en una leyenda dentro del SVG o en el HTML.
- El dibujo principal ocupa 60–70% del área; deja 24 px de margen en el viewBox.
- **Cada etiqueta va en su grupo** para que el núcleo la adapte al celular:
  ```html
  <g class="etiqueta" data-punto="200 196">  <!-- data-punto: el punto sobre la pieza -->
    <path d="M200 196 L200 120 H178" stroke-width="1" fill="none"/><circle cx="200" cy="196" r="3"/>
    <text x="172" y="116" font-size="13.5" font-weight="600" text-anchor="end">Gas encerrado</text>
    <text x="172" y="133" font-size="12" opacity=".75" text-anchor="end">se calienta y se expande</text>
  </g>
  ```
  En pantallas de menos de 640 px el núcleo oculta las etiquetas, pone un número sobre cada pieza y arma la leyenda debajo del dibujo. Así el dibujo puede ser ancho y seguir legible en el celular.
- **No uses la clase `etiqueta` para otra cosa en la guía.** Si la guía ya tiene un `.etiqueta` en su CSS (una pastilla, un título), acótalo (`h3 .etiqueta`) o renómbralo: si no, su estilo (mayúsculas, letra de código) se hereda a las etiquetas del SVG.
- En una sección oscura, pasa `color_sub` a `Lienzo.etiqueta` con el color de texto claro de esa sección.
- El texto que no sea etiqueta (números de los ejes, valores, letras de puntos) no debe verse de menos de 11 px en el celular. **En unidades del viewBox: al menos 11 × ancho del viewBox ÷ 350.** Un viewBox de 480 pide 16; uno de 900, 30 (con 330 px: el ancho a 390 px menos el padding de una sección). `Lienzo.letra_min` lo calcula y `revisar_ilustraciones.py` lo imprime para cada SVG. **Si el CSS le pone al SVG un `min-width` (dentro de un contenedor con scroll) o un `max-width`, el ancho real es ese:** pásalo como `Lienzo(..., ancho_movil=560)`. Si en escritorio se ve demasiado grande, haz el viewBox más angosto (más vertical) en lugar de bajar la letra. Ojo: `<figure>` trae 40 px de margen lateral por omisión, que en el celular achica el SVG; ponle `margin: 0` (o márgenes propios) a las figuras de la guía.

## 6. Formas orgánicas

Llamas, agua, órganos, hojas: curvas Bézier cúbicas **simétricas** y en **dos capas** (silueta + núcleo más claro). La llama del kit es el modelo: forma de gota con punta inclinada, núcleo amarillo al 55%. Varias copias con tamaños distintos (no idénticas).

## 7. Animar procesos

**Si el tema es un proceso, un mecanismo, un ciclo o un flujo, su ilustración central se anima.** Una animación explica lo que un dibujo fijo no puede: *cuándo* pasa cada cosa.

- **Todo sale de una fase de 0 a 1.** Usa `forja.animar(caja, fase => { … }, { periodo: 4 })`: la función recibe la fase y coloca cada pieza con la física o las matemáticas reales.
- **Sincroniza el estado con el movimiento:** lo que entra o sale (calor, corriente, datos) se enciende justo cuando pasa, no siempre.
- **Narra la fase:** un `<p class="anima-fase"><b>Fase</b><span>qué pasa y por qué</span></p>` que `dibujar` actualiza.
- **Flujos** con la clase `flujo` (líneas punteadas que avanzan) y **llamas** con `titila`. Nada se anima solo por adorno.
- El núcleo pone los controles (Pausa, **Paso a paso**, velocidad), respeta "reducir movimiento" y pausa la animación fuera de pantalla. No los programes tú.
- Contenedor: `<div data-anima id="anima-…">` con el SVG y la narración dentro.
- **Una o dos animaciones por guía**: la del proceso central. Las demás ilustraciones pueden ser fijas.
- **No reveles una predicción.** Si la animación (o cualquier dibujo) responde una pregunta de su sección, ponle `data-tras-prediccion` al SVG y a la narración `.anima-fase`, nunca al contenedor `[data-anima]` (los controles deben quedar a la vista); o usa otros valores que no den la respuesta. Revisa también el texto que acompaña al dibujo. La prueba de la fuga está en [interacciones.md](interacciones.md), sección 1.1. Si el JS reescribe el resultado con `innerHTML`, no la metas ahí: ponla después. Revisa también las ilustraciones fijas: un dibujo que muestra el resultado antes de responder también revela.
- **Si el proceso central no tiene ilustración**, créala: es la que más enseña.
- **Si la ilustración que animas ya es interactiva** (nodos clicables que se atenúan), pon las piezas que se mueven en una capa propia con `pointer-events: none`, fuera de los nodos, para que el atenuado no apague la animación.
- **Momentos clave fuera de 0, .25, .5 y .75** (un mensaje a medio viaje): ponlos en `data-fases="0 .37 .5 .83"` del `[data-anima]` para que el revisor los capture.
- Si la narración lleva espacios que importan (la salida de `git status -s`), usa `<code style="white-space:pre">`.

## 8. El kit

[kit-svg.svg](../assets/kit-svg.svg) trae achurados (neutro, caliente, frío), degradado de metal, puntas de flecha por color y la llama. En JS: `forja.kit.onda()` (flecha ondulada), `forja.kit.bielaManivela()`, `forja.kit.mezcla()`. En Python: [svg_kit.py](../scripts/svg_kit.py).

- **Pega el kit una sola vez**, en un `<svg width="0" height="0" style="position:absolute" aria-hidden="true">` al inicio del `<body>`, y úsalo desde todos los SVG con `url(#id)`. Si cada SVG pega sus propios `<defs>`, los ids se repiten y el navegador usa el primero.
- Los colores del kit se resuelven donde está definido, no donde se usa. En una sección oscura, define al lado una copia con sufijo (`pta-caliente-oscuro`) con los colores que se ven sobre fondo oscuro.
- Las definiciones propias de un SVG (un `clipPath`, un degradado) llevan el prefijo del SVG: `motor-interior`, `pend-pta`.
- Los nombres del kit (caliente, frío) son de ejemplo. Agrega las flechas que pida el significado de tu guía con el mismo marcador y otro color (`pta-gris`, `pta-azul`).
- Para un SVG que dibuja el JS, replica su geometría en el script de Python para comprobarla con `assert`, y registra con `Lienzo.registrar()` el texto más largo que el JS pueda poner.
- Diagramas de sistema: `conector([(x, y), ...])` de `svg_kit` traza líneas en ángulo recto con esquinas redondeadas.
- Un degradado sobre una línea perfectamente horizontal o vertical no se ve con las unidades por omisión (la caja de la línea mide 0 de alto o de ancho): usa `gradientUnits="userSpaceOnUse"` con coordenadas reales.

## 9. Rúbrica (mínimo 8 de 10)

| Punto | Criterio |
|---|---|
| 2 | **Correcto:** la mecánica, la física o las matemáticas son reales (piezas unidas, proporciones, curvas de la función) |
| 1 | **Trazo:** solo los tres grosores; nada flota |
| 1 | **Materiales y profundidad:** achurado en cortes y volumen sutil en piezas; si el lenguaje no tiene materiales, rejilla tenue y rellenos translúcidos (sección 3) |
| 1 | **Color con significado** y constante en la guía |
| 1 | **Etiquetas limpias:** con guía, sin choques, alineadas |
| 1 | **Composición:** proporciones, márgenes, foco claro |
| 1 | **Legible en celular:** etiquetas en `g.etiqueta` y el resto del texto ≥ 11 px a 390 px |
| 1 | **Se entiende sin leer:** el dibujo solo ya explica el mecanismo |
| 1 | **Animación** sincronizada con la física (si el tema es un proceso); si no aplica, un detalle de calidad que ayude a entender |

## 10. Proceso de trabajo

1. Escribe un script que genere cada SVG con `svg_kit.py`, geometría calculada y `assert` de lo imposible. Guárdalo fuera de la guía (por ejemplo en `/tmp/forja-gen/<slug>.py`), para poder corregir y volver a generar.
2. Insértalos en la guía y corre `python3 ${CLAUDE_SKILL_DIR}/scripts/revisar_ilustraciones.py <ruta>`: captura cada ilustración en grande (4 fases, cada una en su imagen, si está animada), revisa choques en escritorio en todas las fases, texto ilegible en el celular, e imprime la letra mínima de cada SVG.
3. **Abre cada imagen con Read** y califícala con la rúbrica. Escribe la calificación.
4. Si alguna saca menos de 8, corrígela y repite (máximo 3 vueltas).
