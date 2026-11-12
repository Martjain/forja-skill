# Diseño de una guía forja

## Contenido
1. Dirección visual desde el tema
2. Familias visuales
3. Tipografía
4. Catálogo de layouts
5. Ilustraciones SVG
6. Anti-slop: qué no hacer y qué hacer en su lugar
7. Celular
8. Accesibilidad mínima
9. Ritmo y foco (para quien se distrae fácil)

---

## 1. Dirección visual desde el tema

La paleta sale de **los materiales y objetos reales del tema**, no de una paleta "bonita" genérica. Pregunta: ¿de qué color son las cosas de este mundo?

| Tema | De dónde sale la paleta |
|---|---|
| Agricultura | Verde de hoja, verde oscuro de follaje, crema de grano, tierra |
| Control de pozos | Gris acero, naranja de seguridad, café de lodo, azul de agua salada |
| Git | El ámbar de una terminal de fósforo, el gris de papel de un historial impreso, el verde y rojo de los diffs |
| Astronomía | Negro azulado de cielo, blanco de estrella, un solo acento cálido |
| Claude Code | Ver `familias/claude-code.json` |

Reglas:
- **Base clara + bloques oscuros.** El fondo general es claro y legible. Al menos una sección de cada 3 usa el fondo oscuro de la familia (`data-tono="oscuro"`) para dar ritmo.
- **Comprométete con un color dominante.** Una paleta tímida y repartida en partes iguales se ve genérica. Además del fondo, al menos una sección de ancho completo usa el color fuerte de la familia (el oscuro, o una banda del acento) para que la guía tenga carácter.
- **Un acento, dos secundarios como máximo.** El acento marca lo importante (un dato, la acción principal). Si todo es de color acento, nada lo es.
- **Fondos con atmósfera, no planos por defecto.** Un patrón sutil sacado del motivo (líneas de una cuadrícula técnica, puntos de un hilo, curvas de nivel) con un SVG en `background-image` o capas de color de la misma familia, con una opacidad de 3 a 8%. Nunca morado, nunca ruido que compita con el texto, y como máximo 2 capas.
- **El dato primero.** Cuando hay una cifra o un concepto central, va grande y con una etiqueta corta, no enterrado en un párrafo.
- **Mucho espacio en blanco.** Márgenes generosos, líneas de 60 a 75 caracteres.

## 2. Familias visuales

Una familia es la base que comparten los temas relacionados: paleta, tipografía, tono y motivos. Vive en `familias/<familia>.json`.

- **El tema pertenece a una familia existente:** usa su paleta y tipografía, y elige el motivo del tema en `motivos_por_tema`. Si el tema no está listado, inventa un motivo que represente su mecánica y agrégalo al archivo.
- **No pertenece a ninguna:** crea la familia con el esquema de `familias/claude-code.json`: `familia`, `descripcion`, `origen`, `paleta`, `bloques_oscuros`, `tipografia`, `tono`, `rasgos`, `motivos_por_tema`.
- **Dos guías de la misma familia no deben verse iguales.** Comparten colores y letras, pero cambian el motivo de las ilustraciones y la secuencia de layouts.
- **Nunca** pongas logos, wordmarks, mascotas ni ilustraciones de una marca. La relación visual sale de la paleta y la tipografía.

## 3. Tipografía

Las fuentes del sistema (y Inter, Roboto, Arial) son una señal de AI slop. Las guías **incrustan** fuentes con carácter en base64, así que siguen funcionando offline.

1. La familia indica sus fuentes en `tipografia` (ids del catálogo). Para una familia nueva, elígelas con `python3 ${CLAUDE_SKILL_DIR}/scripts/fuentes.py lista` según el carácter del tema. Lo más seguro es combinar una fuente de títulos con personalidad con una de cuerpo legible.
2. Genera el CSS y pégalo al inicio del `<style>`:
   ```bash
   python3 ${CLAUDE_SKILL_DIR}/scripts/fuentes.py css --titulos <id> --cuerpo <id> --codigo <id>
   ```
   Eso define `--f-titulos`, `--f-cuerpo` y `--f-codigo`. Añade unos 100 KB al archivo, lo cual está bien.
3. Si un tema no tiene código, omite `--codigo`.

Escala sugerida: cuerpo de 17 a 18px; h2 entre 32 y 48px con `clamp()`; cifras y títulos de portada entre 56 y 112px. **El contraste de tamaño es parte del diseño**: un título de portada grande de verdad junto a un cuerpo tranquilo. Usa dos pesos: 400 y 600.

## 4. Catálogo de layouts

Cada `<section>` declara uno con `data-layout`. No repitas el mismo en secciones seguidas y usa al menos 5 distintos por guía.

| `data-layout` | Cómo es | Úsalo para |
|---|---|---|
| `portada` | Título grande, una frase y 2-3 cifras clave, con una ilustración SVG del motivo | La primera sección |
| `dato-heroe` | Un número o término enorme a un lado y la explicación al otro | Un concepto que hay que recordar |
| `dividido` | Texto 40% e ilustración o interacción 60% (o al revés) | Explicar algo que se ve |
| `secuencia` | Etapas en fila con conectores; en celular, scroll horizontal con `scroll-snap` dentro del contenedor | Procesos, ciclos de vida, orden temporal |
| `comparacion` | Dos columnas enfrentadas con un divisor marcado | A vs B, antes/después, correcto/incorrecto |
| `lista-grande` | Elementos numerados 01, 02, 03 con números grandes en el acento | 3 a 6 ideas del mismo peso |
| `mosaico` | Rejilla asimétrica: una pieza grande y 2-3 chicas de tamaños distintos | Varias facetas de un tema |
| `enfasis` | Bloque de ancho completo con una sola idea o regla en grande | La regla que no se debe olvidar |
| `laboratorio` | La interacción ocupa el centro, con los controles debajo y el resultado visible | Simuladores y probadores |
| `repaso` | Flashcards o autoevaluación con progreso visible | El cierre de la guía |

**Prohibido:** una rejilla de tarjetas idénticas (mismo tamaño, mismo borde, ícono + título + texto) repetida sección tras sección.

## 5. Ilustraciones SVG

- **Inline**, con `viewBox` y `role="img"` + `<title>`. Usa los colores de la familia con variables CSS (`fill="var(--acento)"`) o `currentColor`.
- **Esquemáticas, no decorativas.** Dibujan el mecanismo del concepto con el motivo de la guía: capas que se abren, eventos sobre una línea de tiempo, una rama que se separa. Una mancha abstracta o un "blob" no enseña nada.
- **Simples.** Menos de 40 elementos por ilustración. Formas reconocibles antes que detalle.
- **Una por sección clave**, mínimo 3 por guía. La de `portada` presenta el motivo y las siguientes lo reutilizan.
- Íconos pequeños, si hacen falta: SVG de trazo simple, nunca emojis.

## 6. Anti-slop: qué no hacer y qué hacer en su lugar

| No | En su lugar |
|---|---|
| Degradados morados o fondos con brillo | Colores planos de la familia |
| Emojis como decoración | Ilustraciones o íconos SVG propios |
| Rejillas de tarjetas idénticas | Layouts distintos del catálogo |
| "En el mundo actual…", "Sumérgete…", "¡Vamos allá!" | Empieza con el dato o la idea |
| Animaciones que no explican nada | Una sola entrada orquestada en la portada (clase `entra` con `--i` escalonado) y animación solo cuando muestra el proceso |
| Fuentes del sistema, Inter, Roboto, Arial o Space Grotesk | Fuentes del catálogo, incrustadas con `fuentes.py` |
| Paleta tímida (crema + detalles) | Un color dominante a ancho completo y un acento marcado |
| Un botón que solo muestra más texto | Una interacción donde el usuario predice, prueba o compara (ver interacciones.md) |
| Tema oscuro genérico de "herramienta para devs" | Base clara de la familia con bloques oscuros alternados |
| Sombras grandes y difusas en todo | Bordes finos o cambio de fondo |

## 7. Celular

- Diseña primero para 390px de ancho.
- Nada puede ser más ancho que la pantalla. Lo ancho (diagramas, tablas, secuencias) va dentro de un contenedor con `overflow-x: auto`, nunca a nivel de página.
- Los bloques de código usan `overflow-x: auto` y `white-space: pre`.
- Zonas táctiles de al menos 44×44px.
- Los layouts de dos columnas pasan a una columna por debajo de 720px.
- `revisar_movil.py` verifica esto y genera capturas para que las revises.

## 8. Accesibilidad mínima

- Contraste de al menos 4.5:1 entre el texto y su fondo.
- `:focus-visible` con un contorno del color acento.
- Todo lo interactivo funciona con teclado (`<button>`, `<input>`; no `<div onclick>`).
- `@media (prefers-reduced-motion: reduce)` desactiva las animaciones.

## 9. Ritmo y foco (para quien se distrae fácil)

Las guías las lee alguien que aprende mejor viendo y haciendo, y que puede perder el hilo con bloques largos. El núcleo del esqueleto ya trae la barra de progreso, el mapa con checks, el guardado y el "Continuar donde ibas". Tú cuidas el contenido:

- **El mapa va en la portada.** Que el recorrido completo se vea desde el inicio (el `<nav data-forja-mapa>` de la portada).
- **Secciones de 3 a 8 minutos** (`data-minutos`). Si una pasa de 8, divídela.
- **Cada sección abre con su idea en una frase**, visible antes de cualquier párrafo.
- **Párrafos de 3 líneas como máximo** en celular. Si necesitas más, lo que falta es una ilustración o una interacción.
- **Algo que hacer cada 1 o 2 pantallas**: una predicción, un reto o un control. Nunca más de 2 pantallas seguidas de solo leer.
- **Feedback inmediato**: cada acción del usuario tiene una respuesta visible en menos de un segundo.
