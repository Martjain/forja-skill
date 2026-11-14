# Interacciones de una guía forja

## Contenido
1. La prueba de una interacción real
   - 1.1 Predecir antes de ver
   - 1.2 Retos que guían la atención
   - 1.3 "Explícamelo paso a paso"
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

### 1.1 Predecir antes de ver

Cuando alguien adivina antes de ver la respuesta (aunque se equivoque) y recibe la corrección de inmediato, recuerda más que si solo lee. Por eso **al menos 2 interacciones por guía empiezan con una predicción**: normalmente el simulador y el diagrama o los pasos.

- Una pregunta concreta sobre lo que va a pasar, con 2 a 4 opciones. Las opciones incorrectas deben ser errores **plausibles**, los que comete un principiante de verdad.
- **Solo el resultado** lleva `data-tras-prediccion="<id de la predicción>"`: el panel de salida, la lectura del simulador, la ficha del nodo. El núcleo lo deja borroso hasta que el usuario elige. **Los controles y el diagrama quedan a la vista**, porque ver la estructura ayuda a predecir. Si escondes un bloque grande, se convierte en una zona muerta. El validador marca como error un `data-tras-prediccion` que contenga botones, inputs o `data-nodo`.
- Al elegir, el núcleo muestra "Acertaste" o "Predijiste X; mira qué pasa en realidad", más la explicación de `data-explicacion` (una o dos frases con el **porqué**).
- No escribas JS para esto: el núcleo del esqueleto lo resuelve con el marcado:

```html
<div data-interaccion="simulador">
  <div data-prediccion id="pred-exit" data-correcta="b"
       data-explicacion="Con exit 2, PreToolUse cancela la herramienta y Claude lee tu stderr.">
    <p><strong>Antes de mover nada:</strong> si tu hook termina con exit 2 en PreToolUse, ¿qué pasa?</p>
    <div class="opciones">
      <button type="button" data-opcion="a">La herramienta corre igual</button>
      <button type="button" data-opcion="b">La herramienta se cancela</button>
      <button type="button" data-opcion="c">Claude Code se cierra</button>
    </div>
    <p class="veredicto" hidden></p>
  </div>
  … sliders y SVG (visibles) …
  <p data-tras-prediccion="pred-exit"> … resultado y frase que lo explica … </p>
</div>
```

**La prueba de la fuga.** Tapa con la mano todo lo que está detrás de la predicción y pregúntate: con lo que queda a la vista en esa sección (el subtítulo, los párrafos, los dibujos, la tabla, la lista de abajo), ¿alguien puede contestar sin pensar? Si sí, hay una fuga. Una revisión ciega de las 7 primeras guías encontró **20 fugas en 27 predicciones**, todas **en la misma sección que la pregunta**:
- un subtítulo que ya dice la respuesta («Git solo mueve el puntero hacia adelante», «El que más te van a preguntar: convencer»);
- un dibujo o una tabla debajo de la pregunta que muestra el resultado (el fast-forward ya hecho, la flecha resaltada hacia «Convencer»);
- un texto explicativo junto a una animación que sí está borrosa («Primero la introducción, con la tesis en amarillo»).
- el mismo ejemplo que se pregunta, ya anotado más arriba en la sección (el borrador literario con sus etiquetas «tono subjetivo», «intención estética»);
- etiquetas de un diagrama que repiten las palabras de la opción correcta («el repositorio» en la caja `.git`);
- un reto o un pie de figura que descarta las opciones incorrectas.
- **otra sección o un reto**: un dato dicho antes que descarta opciones, o un reto que describe la respuesta. Lee los retos y las secciones anteriores con la pregunta en mente.
- **la opción correcta destaca**: es la más larga, la más técnica o la única con matices. Iguala el largo y el detalle de las opciones.

Cómo corregirlas, en este orden:
1. Reescribe el subtítulo o el párrafo para que plantee la pregunta en lugar de responderla.
2. Pon **también** detrás de la predicción (`data-tras-prediccion`) el dibujo, la tabla o el texto que la responden. Sigue sin tapar controles: en un `[data-anima]`, el atributo va en el SVG y en la narración `.anima-fase`, no en el contenedor, para que los controles queden a la vista.
3. Si el bloque es grande y quedaría una zona muerta, cambia la pregunta por otra que ese bloque no responda.

Mostrar la **estructura** (las piezas, el orden de las etapas) no es fuga si la pregunta es sobre el **comportamiento** (qué pasa, cuánto da, qué gana). Sí es fuga si la pregunta es justamente sobre esa estructura.

`probar_guia.py` marca los dibujos, tablas y bloques de código que quedan a la vista después de una pregunta y guarda una captura de cada sección antes de contestar. Revísalas con esta prueba.

### 1.2 Retos que guían la atención

Una interacción sin dirección es un juguete. Cada interacción principal lleva **1 a 3 retos**: tareas concretas que llevan al usuario al fenómeno que importa ("Mueve el código a 2 en PostToolUse: ¿por qué ya no bloquea?"). **Mínimo 3 retos por guía.**

```html
<ul data-retos>
  <li data-reto="reto-post">Encuentra un evento donde exit 2 <em>no</em> bloquea</li>
</ul>
```

El JS de la interacción llama a `forja.reto('reto-post')` cuando el usuario llega a ese estado. El núcleo lo marca, lo guarda y actualiza el progreso. El reto se cumple haciendo, no con un botón de "listo".

### 1.3 "Explícamelo paso a paso"

Si alguien no puede resolver algo, no debe quedarse atorado ni adivinar al azar. **Cada predicción y cada ejercicio** lleva un botón "Explícamelo paso a paso" que muestra el razonamiento **un paso a la vez**. Después de cada paso, el usuario puede decir "Ya entendí, lo intento" y volver a intentarlo él mismo. La respuesta llega al final, solo si la pide.

```html
<div data-ayuda="pred-limite">
  <ol>
    <li>Fija a = 1. La pendiente de la secante es (f(1+h) − f(1)) / h.</li>
    <li>Con f(x) = x²: (1 + 2h + h² − 1) / h = (2h + h²) / h.</li>
    <li>Divide entre h (h no es 0, solo se acerca): queda 2 + h.</li>
    <li data-respuesta>Cuando h se acerca a 0, 2 + h se acerca a <strong>2</strong>.</li>
  </ol>
</div>
```

Cómo escribir los pasos:
- **De 2 a 5 pasos**, cada uno con **una sola** idea u operación. El primero arranca desde lo que el usuario ya sabe ("¿qué te piden?", "¿qué fórmula aplica?").
- **Ningún paso antes del último dice la respuesta.** Cada uno acerca, pero deja que el usuario la termine.
- **El que lleva `data-respuesta` cierra** con la respuesta y una frase del porqué.
- **Va dentro del bloque `data-prediccion`**, después de `.veredicto`, y su valor es el id de la predicción. Si el usuario abre la ayuda antes de responder, el veredicto dice "Acertaste con ayuda.", sin castigo.
- **Ejercicios que se generan con JS** (probadores, ejercicios al azar): pon `<div data-ayuda data-ayuda-dinamica></div>` en el ejercicio y, cada vez que cambie, llama a `forja.ayuda(div, ['paso 1', 'paso 2'], 'respuesta')` con los pasos de **ese** ejercicio.
- Puedes cambiar el texto del botón con `data-ayuda-texto="…"` cuando otro encaje mejor, por ejemplo "¿Cómo se resuelve?".

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

Para memorizar términos, comandos y reglas. Van en la sección `repaso`.

**No escribas JS para las flashcards.** El núcleo las dibuja a partir de un JSON, guarda el avance y las suma al **repaso espaciado** del índice, que mezcla tarjetas de todas las guías y las vuelve a mostrar en 1, 3, 7, 16 y 35 días según cuánto las domines:

```html
<div data-interaccion="flashcards" data-forja-flashcards></div>
<script type="application/json" id="forja-tarjetas">
[
  {"id": "exit-2", "q": "¿Qué código de salida bloquea la acción?", "a": "<code>exit 2</code>. El <code>exit 1</code> es un error que no bloquea."},
  …
]
</script>
```

Cómo escribir buenas tarjetas:
- **De 8 a 15**, una idea por tarjeta. Respuestas de una o dos líneas.
- **Que se respondan recordando, no reconociendo**: "¿Qué evento corre antes de la herramienta?" sirve; "¿PreToolUse corre antes?" no, porque la respuesta es sí o no.
- Incluye **las confusiones típicas** del tema (exit 1 contra exit 2, *ours* contra *theirs*): son las que más vale repasar.
- El `id` debe ser estable y corto. Si cambias el `id`, la tarjeta pierde su historial de repaso.
- Puedes cambiar su aspecto con CSS (clases `.fc-*`) para que combine con la guía.

## 4. Simulador con slider — `data-interaccion="simulador"`

Un simulador cambia un resultado al mover sus controles. Lo normal es un `<input type="range">`, pero si el tema no tiene una magnitud continua (elegir argumentos, prender y apagar piezas), valen 2 o más botones, casillas o un `select`: no inventes un slider sin sentido.

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


**Transiciones.** Cuando el usuario mueve un control o elige otro caso, las piezas **se deslizan** a su nuevo valor en lugar de saltar: así se ve qué cambió y cuánto. Usa el núcleo, no lo programes:
- `forja.deslizar(el, { width: 120, y: 40 }, 450)` mueve atributos numéricos de un SVG (también propiedades CSS como `'--avance'`).
- `forja.contar(elNumero, 15.2, { decimales: 2, sufijo: ' %' })` hace que un número cuente hasta su nuevo valor.
- **Duraciones (las mismas en toda la skill):** mientras se arrastra un control, **120 ms**; con un botón que carga un caso o corre algo, **450 ms** (máximo 600).
- `forja.transitar(estado, { h: 0.5 }, 450, e => redibujar(e))` para lo que se **calcula y redibuja** (una curva, una figura con geometría): anima los números del estado y redibuja en cada cuadro con la fórmula real. Así una curva cambia de forma en lugar de saltar.
- `forja.escalonar(lista, (el, i) => …, 45)` marca cosas una tras otra (una cadena de pasos, filas que se llenan): así se ve el orden. El total no debe pasar de unos 600 ms.
- Cada atributo lleva su propia animación: puedes deslizar `x` y luego `width` del mismo elemento sin que se pisen. Si una animación se reapunta a medio camino (al arrastrar), sigue sin volver a arrancar desde cero.
- `forja.contar` no anima la primera vez. Si el número se crea con `innerHTML`, ponle `data-valor` con el valor de partida.
- **Ángulos y giros:** `deslizar` no mueve `transform`. Desliza una propiedad CSS (`forja.deslizar(el, {'--ang': 120})`) y úsala en el CSS: `transform: rotate(calc(var(--ang) * 1deg)); transform-box: view-box; transform-origin: 200px 150px;`.
- `forja.reducir` dice si el usuario pidió menos movimiento, por si necesitas decidir algo a mano.
- Ambas respetan «reducir movimiento»: ahí el cambio es inmediato.

## 5. Paso a paso guiado — `data-interaccion="pasos"`

Para procedimientos: configurar algo, recorrer un proceso, resolver un problema.

- Un paso visible a la vez, con "Anterior" y "Siguiente" y una barra de progreso (`Paso 2 de 5`).
- **Cada paso cambia el estado visual**: el SVG o el bloque de código se actualiza resaltando lo nuevo. Si solo cambia el texto, es un carrusel, no un paso a paso.
- El último paso muestra el resultado completo y un "Volver a empezar".
- Flechas del teclado para avanzar y retroceder.

**Ejemplo que se desvanece.** Para un principiante, ver un ejemplo resuelto enseña más que resolverlo solo desde cero. Pero si todo viene resuelto, solo lee. Por eso la ayuda se va retirando:

1. **Los pasos 1 y 2 vienen resueltos**: se muestra qué se hace y por qué.
2. **Desde el paso 3, cada paso tiene un hueco**: antes de mostrar la línea o la acción nueva, el usuario elige cuál va. Es una `data-prediccion` dentro del paso, y la línea nueva lleva `data-tras-prediccion="<id>"`. Las opciones incorrectas son los errores reales de un principiante.
3. **Después de revelar, un "¿Por qué?"**: un `<details>` con `<summary>¿Por qué funciona? Piénsalo y luego ábrelo</summary>`. Explicar el porqué con tus propias palabras es lo que fija el paso.
4. **El último paso lo arma el usuario**, con un hueco que reúne lo de los pasos anteriores.

El validador exige al menos una `data-prediccion` dentro de cada `data-interaccion="pasos"`.

## 6. Otras interacciones — `data-interaccion="otra"`

Si el tema pide una interacción propia, hazla además de las principales. Ejemplos que funcionan bien:
- **Probador:** el usuario escribe algo (un patrón, un comando, una fórmula) y ve si funciona o a qué afecta.
- **Ordenar:** acomodar etapas en orden y comprobar.
- **Línea de tiempo reproducible:** un botón que reproduce un proceso evento por evento.

Siguen la prueba de la sección 1.

## 7. Reglas técnicas

- JavaScript sin librerías, en un solo `<script>` al final del `<body>`, **después** del núcleo forja, que se copia sin cambios.
- Usa la API del núcleo: `forja.reto(id)`, `forja.guardar(clave, valor)` y `forja.leer(clave)`. No uses `localStorage` directamente.
- Cada interacción funciona de forma independiente; si una falla, las demás siguen.
- Controles con elementos nativos (`<button>`, `<input>`), operables con teclado y con `:focus-visible`.
- Nada depende de hover: en celular no existe.
- Estado inicial con contenido: nunca una interacción que empiece vacía.
- Cada reto `data-reto="x"` necesita un `forja.reto('x')` en el JS, con el id escrito tal cual: `probar_guia.py` marca como error un reto que ningún código cumple.
- En una cuadrícula (`display: grid`) con una columna que se desplaza de lado (una fila de pasos, un SVG con `min-width`), pon `min-width: 0` en esa columna: sin eso desborda en el celular.
- Los botones con fondo de acento los resuelve el núcleo (elige texto claro u oscuro según el contraste). Si haces tus propios botones de color, comprueba el contraste: `probar_guia.py` avisa cuando el texto queda por debajo de 4.5:1.
