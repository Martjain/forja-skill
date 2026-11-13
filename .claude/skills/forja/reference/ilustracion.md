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

## 3. Materiales, color y profundidad

- **Material cortado = achurado** (patrones `ach-*` del kit). Distingue zonas con el achurado de su color (caliente, frío, neutro).
- **Metal y piezas sólidas:** degradado vertical sutil claro → oscuro (`met` del kit). Nada de sombras difusas grandes.
- **El color significa algo y no cambia** en toda la guía. Ejemplo: naranja = caliente, azul = frío; o verde = correcto, rojo = error. Declara el significado una vez (leyenda o texto).
- **Degradado solo para una magnitud continua:** temperatura a lo largo de un gas, presión en un tubo, concentración. Nunca como decoración.
- Una sombra de piso muy tenue (elipse, opacidad 0.06–0.08) asienta el objeto.

## 4. Geometría calculada, nunca a ojo

**Genera los dibujos con código** (Python o JS) y calcula las coordenadas:
- Mecanismos: usa `forja.kit.bielaManivela` o calcula la cinemática; la biela mide lo mismo en todas las posiciones.
- Curvas de funciones: muestrea la función real (`for x … y = f(x)`), no dibujes "algo que se parece".
- Proporciones reales cuando importan (un engrane de 20 dientes contra uno de 40 tiene el doble de diámetro).
- **Comprueba con `assert`** lo que no puede pasar: el pistón no sale del cilindro, dos piezas no se atraviesan, una etiqueta no sale del viewBox.

## 5. Etiquetas y composición

- **Etiqueta = título (13–14 px, peso 600) + frase corta (12 px, opacidad .75)**, con una **línea guía** de 1 px que termina en un punto sobre la pieza exacta.
- Las etiquetas van **fuera** del dibujo, en los márgenes, alineadas entre sí. Nunca encima de trazos ni de otras etiquetas.
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
- El texto que no sea etiqueta (ejes, valores) no debe verse de menos de 11 px a 390 px de ancho.

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

## 8. El kit

[kit-svg.svg](../assets/kit-svg.svg) trae, listos para pegar en `<defs>`: achurados (neutro, caliente, frío), degradado de metal, puntas de flecha por color, la llama y la flecha ondulada. En JS: `forja.kit.onda()`, `forja.kit.bielaManivela()`, `forja.kit.mezcla()`.

## 9. Rúbrica (mínimo 8 de 10)

| Punto | Criterio |
|---|---|
| 2 | **Correcto:** la mecánica, la física o las matemáticas son reales (piezas unidas, proporciones, curvas de la función) |
| 1 | **Trazo:** solo los tres grosores; nada flota |
| 1 | **Materiales y profundidad:** achurado en cortes, volumen sutil en piezas |
| 1 | **Color con significado** y constante en la guía |
| 1 | **Etiquetas limpias:** con guía, sin choques, alineadas |
| 1 | **Composición:** proporciones, márgenes, foco claro |
| 1 | **Legible en celular:** etiquetas en `g.etiqueta` y el resto del texto ≥ 11 px a 390 px |
| 1 | **Se entiende sin leer:** el dibujo solo ya explica el mecanismo |
| 1 | **Animación** sincronizada con la física (si el tema es un proceso); si no aplica, un detalle de calidad que ayude a entender |

## 10. Proceso de trabajo

1. Escribe un script (Python o JS) que genere cada SVG con geometría calculada y `assert` de lo imposible.
2. Insértalos en la guía y corre `python3 ${CLAUDE_SKILL_DIR}/scripts/revisar_ilustraciones.py <ruta>`: renderiza cada ilustración en grande (4 cuadros si está animada) y marca choques de etiquetas y texto ilegible.
3. **Abre cada imagen con Read** y califícala con la rúbrica. Escribe la calificación.
4. Si alguna saca menos de 8, corrígela y repite (máximo 3 vueltas).
