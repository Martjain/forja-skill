# Interacciones de una guía forja

## Contenido
1. La prueba de una interacción real
2. Diagrama clicable
3. Flashcards
4. Simulador con slider
5. Paso a paso guiado
6. Otras interacciones
7. Reglas técnicas

---

## 1. La prueba de una interacción real

Una interacción es real si el usuario **hace algo y ve una consecuencia que puede predecir o comprobar**. Pregunta: ¿qué aprende moviendo esto que no aprendería leyendo?

- Real: mover un slider de `timeout` y ver qué hooks alcanzan a terminar.
- Real: escribir un matcher y ver qué herramientas lo disparan.
- Falsa: un botón "Ver más" que muestra un párrafo.
- Falsa: una tarjeta que gira solo por efecto.

Una interacción por concepto. Si un concepto no gana nada con interacción, va sin ella.

Cada interacción lleva `data-interaccion="<tipo>"` en su contenedor.

## 2. Diagrama clicable — `data-interaccion="diagrama"`

Para estructuras y relaciones: partes de un sistema, flujo entre componentes, anatomía de una configuración.

- Un SVG con nodos. Cada nodo es un `<g>` con `tabindex="0"`, `role="button"` y una etiqueta.
- Al hacer clic o presionar Enter: el nodo se resalta, sus conexiones se resaltan, el resto se atenúa y un panel junto al diagrama muestra la ficha del nodo.
- Debe empezar con un nodo ya seleccionado, para que se vea qué hacer.

```js
diagrama.querySelectorAll('[data-nodo]').forEach(n => {
  const activar = () => {
    diagrama.querySelectorAll('[data-nodo]').forEach(x => x.classList.toggle('activo', x === n));
    diagrama.querySelectorAll('[data-une]').forEach(l =>
      l.classList.toggle('activo', l.dataset.une.split(' ').includes(n.dataset.nodo)));
    panel.innerHTML = fichas[n.dataset.nodo];
  };
  n.addEventListener('click', activar);
  n.addEventListener('keydown', e => (e.key === 'Enter' || e.key === ' ') && (e.preventDefault(), activar()));
});
```

## 3. Flashcards — `data-interaccion="flashcards"`

Para memorizar términos, comandos y reglas. Va casi siempre en la sección `repaso`.

- Muestra la pregunta. El usuario **intenta recordar** y luego voltea la tarjeta (ahí está el aprendizaje, no en la animación).
- Después de voltear, dos botones: "Lo sabía" y "Repasar". Las de "Repasar" vuelven al final del mazo.
- Progreso visible: "7 de 12 · 5 dominadas".
- De 8 a 15 tarjetas, con respuestas cortas.
- Voltear con clic, Enter o barra espaciadora. Respeta `prefers-reduced-motion` (sin giro 3D: solo cambio de cara).

## 4. Simulador con slider — `data-interaccion="simulador"`

Para relaciones de causa y efecto: "si cambio X, ¿qué pasa con Y?".

- Uno a tres `<input type="range">` con su valor visible y unidades.
- El resultado se **calcula** en JS y se ve: una barra que crece, un SVG que cambia, un estado que pasa de "pasa" a "bloquea".
- Los valores iniciales muestran un caso típico. Marca en el slider dónde está el punto crítico, si lo hay.
- Debajo, una frase que se actualiza y explica el resultado en palabras: "Con 45 s, el hook de pruebas no alcanza a terminar".

```js
slider.addEventListener('input', () => {
  const v = Number(slider.value);
  salida.textContent = `${v} s`;
  resultado.dataset.estado = v >= limite ? 'pasa' : 'falla';
  explicacion.textContent = explicar(v);
});
```

Si el tema no tiene ninguna variable numérica, el simulador puede ser un selector de escenarios (`<input type="range">` con pasos discretos y etiquetas), pero sigue mostrando una consecuencia calculada.

## 5. Paso a paso guiado — `data-interaccion="pasos"`

Para procedimientos: configurar algo, recorrer un proceso, resolver un problema.

- Un paso visible a la vez, con "Anterior" y "Siguiente" y una barra de progreso (`Paso 2 de 5`).
- **Cada paso cambia el estado visual**: el SVG o el bloque de código se actualiza resaltando lo nuevo. Si solo cambia el texto, es un carrusel, no un paso a paso.
- El último paso muestra el resultado completo y un "Volver a empezar".
- Flechas del teclado para avanzar y retroceder.

## 6. Otras interacciones — `data-interaccion="otra"`

Si el tema pide una interacción propia, hazla además de las principales. Ejemplos que funcionan bien:
- **Probador:** el usuario escribe algo (un patrón, un comando, una fórmula) y ve si funciona o a qué afecta.
- **Ordenar:** acomodar etapas en orden y comprobar.
- **Línea de tiempo reproducible:** un botón que reproduce un proceso evento por evento.

Siguen la prueba de la sección 1.

## 7. Reglas técnicas

- JavaScript sin librerías, en un solo `<script>` al final del `<body>`.
- Cada interacción funciona de forma independiente; si una falla, las demás siguen.
- Controles con elementos nativos (`<button>`, `<input>`), operables con teclado y con `:focus-visible`.
- Nada depende de hover: en celular no existe.
- Estado inicial con contenido: nunca una interacción que empiece vacía.
