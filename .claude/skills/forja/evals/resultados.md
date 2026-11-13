# Resultados de evaluación: forja v1

Fecha: 2026-11-12. Cada caso corrió en un subagente con contexto limpio. Todo lo revisé de nuevo por mi cuenta: validador, revisión en celular, capturas y el contenido contra la documentación oficial.

## Comparación con la línea base (hooks de Claude Code, principiante)

| | Sin skill | Con forja |
|---|---|---|
| Criterios cumplidos | 9 / 16 | **16 / 16** |
| Errores del validador | 9 | 0 |
| Layouts distintos | 0 (una sola plantilla) | 10 |
| Ilustraciones SVG | 0 | 10 |
| Citas junto al dato | 0 | 17 |
| Emojis | 10 | 0 |
| Interacciones (de 4) | 2 + probador | 4 + probador |
| Desborde en celular | Sí (650 px en pantalla de 390) | No |
| Paleta | Oscura genérica | Familia claude-code |
| Tiempo / tokens | ~8 min / 164k | ~9 min / 178k |

## Casos

| # | Caso | Resultado | Evidencia |
|---|---|---|---|
| 1 | Tema en familia existente (hooks) | ✓ 16/16 | `guias/hooks-de-claude-code/` |
| 2 | Tema nuevo sin nivel (git) | ✓ 5/5 | Preguntó el nivel sin crear archivos; creó la familia `control-de-versiones` con una paleta del tema; 11 fuentes de git-scm.com y 47 citas |
| 3 | La guía ya existe | ✓ 4/4 | La v1 quedó intacta (mismo hash y sin diff); creó `hooks-de-claude-code-v2` y avisó; agregó la v2 al índice sin quitar la v1; usó un motivo nuevo (`hooks-v2`) para que no se viera igual |

| 4 | Segunda guía de una familia creada por la skill (git intermedio) | ✓ | Usó `control-de-versiones` sin cambiar la paleta ni la tipografía. Le agregó un motivo nuevo (cinta perforada horizontal en vez de cuentas en un hilo), cambió la secuencia de layouts y le dio otro significado a los colores (verde para copias del rebase, rojo para abandonados). Se ve de la misma familia sin ser igual |

## Fallas encontradas y corregidas

1. **La ruta incluía el nivel.** `registrar.py` recibía el pedido completo (`$ARGUMENTS`), así que la carpeta quedó como `hooks-de-claude-code-nivel-principiante`. Corregido en SKILL.md (paso 2): se pasa solo el tema.

## Observaciones del caso 4

- **Ruta demasiado larga:** `git-ramas-merge-vs-rebase-y-resolucion-de-conflictos`. El subagente pasó el título completo como tema. Conviene pedirle un tema corto, por ejemplo `git-merge-rebase`.
- **Avisó con honestidad de 2 datos sin fuente consultada:** la etiqueta de diff3 durante un rebase y un detalle del estilo `merge`. El criterio de "cada dato clave citado" se cumplió en parte. Conviene que la skill pida marcar en la guía los datos que no tienen fuente.

## Pendiente

- Pruebas de activación negativa (`activacion.no_debe_activar` en evals.json): falta comprobar que la skill no se dispare con "explícame rápido qué es un hook" y similares.
- El hook de protección se probó con datos simulados, pero en los evals no llegó a dispararse porque `registrar.py` evitó la colisión antes. Para probarlo de verdad hay que pedir explícitamente que se edite una guía publicada.
- Costo: cada guía toma de 9 a 14 minutos y entre 178k y 197k tokens. Vigilarlo si se agregan más pasos.

---

# forja v2, ronda 1: predecir, progreso y tipografía

Misma petición (hooks de Claude Code, principiante), en un subagente limpio y sin ver las guías anteriores. Resultado: `guias/hooks-de-claude-code-v3/`.

| | v1 | v2 |
|---|---|---|
| Validador v2 | 8 errores (no tiene núcleo, predicciones, retos ni fuentes) | OK |
| Predicciones antes de ver | 0 | 3 (eventos, matcher, exit 1), con errores plausibles como distractores |
| Retos | 0 | 9, que se cumplen haciendo |
| Progreso, mapa y guardado | No | Barra, mapa en la portada con minutos, "Continuar donde ibas" |
| Tipografía | Del sistema | Newsreader, Instrument Sans y JetBrains Mono incrustadas |
| Color dominante | Crema + bloques oscuros | Además, una banda terracota a ancho completo ("exit 1 no bloquea.") |
| Fondo | Plano | Patrón sutil de circuito (motivo "cable") |
| Peso | 68 KB | 185 KB (las fuentes suman ~100 KB) |
| Tokens / tiempo | 178k / 9 min | 230k / 15 min |

Verificado a mano: el dato de que "Claude Code anula un Stop hook tras 8 bloqueos seguidos" viene de la guía oficial de hooks.

## Por corregir en la ronda 2

- **El borroso tapa demasiado.** En algunas secciones el diagrama completo queda ilegible antes de predecir y se ve como una zona muerta. Hay que difuminar solo el **resultado** y dejar visible la estructura y los controles.
- **Ruta corta** (del caso 4) y **marcar los datos sin fuente** (del caso 4).
- Siguen pendientes las mejoras 3 (repaso espaciado entre guías) y 4 (ejemplos que se desvanecen).

---

# forja v2, ronda 2: borroso acotado, repaso espaciado, ejemplos que se desvanecen

Prueba: "subagentes de Claude Code: qué son, cómo delegar tareas y cuándo conviene usarlos, nivel principiante". Pedido largo a propósito, para comprobar la ruta corta. Subagente limpio, sin ver otras guías.

| Criterio nuevo | Resultado |
|---|---|
| Ruta corta | ✓ `subagentes-de-claude-code` (tema pasado: "subagentes de Claude Code") |
| Borroso solo en el resultado | ✓ Los 5 objetivos son paneles de resultado; diagrama y sliders visibles desde el inicio |
| Paso a paso que se desvanece | ✓ Pasos 1-2 resueltos, huecos en 3, 4 y 5, y "¿Por qué funciona?" después de revelar |
| Flashcards del núcleo | ✓ 14 tarjetas en JSON que se suman al repaso del índice |
| Núcleo copiado sin cambios | ✓ CSS y JS idénticos al esqueleto (comprobado con diff) |
| Datos sin fuente | No marcó ninguno; el simulador declara que sus cantidades son ilustrativas |
| Retos | 9, incluido un clasificador de 6 situaciones ("¿subagente o principal?") |
| Validador / celular | OK / OK |

Verificado a mano contra la documentación oficial: límite de 20 subagentes simultáneos, fork con `/subtask`, `claude --agent`, `@"nombre (agent)"`.

Costo: 209k tokens, 11.5 min (la v2 ronda 1 usó 230k y 15 min, porque las flashcards ya no se programan a mano).

---

## Limpieza (2026-11-12)

Se quitaron las guías hechas con versiones anteriores de la skill, para dejar una por tema con la versión actual. La evidencia de los evals sigue en el historial de git:
- `guias/hooks-de-claude-code/` (eval 1, v1) y `guias/hooks-de-claude-code-v2/` (eval 3, v1): commit `e2d15aa`
- `guias/git/` (eval 2, v1): commit `e2d15aa`
- `guias/git-ramas-merge-vs-rebase-y-resolucion-de-conflictos/` (eval 4, v1): commit `77f7711`
- `guias/hooks-de-claude-code-v3/` (v2 ronda 1): commit `00846a1`

---

## Pruebas de activación (D)

Cada frase corrió en un subagente limpio, con todas las skills de la sesión disponibles. El subagente se detenía al cargar una skill. **10 de 10 correctas.**

| # | Frase | Esperado | Resultado |
|---|---|---|---|
| 1 | hazme una guía visual de los hooks de Claude Code | forja | ✓ forja (y preguntó el nivel) |
| 2 | quiero aprender git, hazme una guía | forja | ✓ forja (preguntó el nivel con temario por nivel) |
| 3 | /forja subagentes | forja | ✓ forja (preguntó el nivel) |
| 4 | créame una guía interactiva para estudiar control de pozos | forja | ✓ forja (preguntó el nivel) |
| 5 | explícame rápido qué es un hook | ninguna | ✓ respondió en el chat |
| 6 | resume este PDF | no forja | ✓ pidió el archivo; dijo que forja no es para resúmenes |
| 7 | hazme una presentación de ventas… | no forja | ✓ cargó pptx, no forja |
| 8 | corrige este archivo HTML… | no forja | ✓ ninguna; citó que forja excluye editar HTML |
| 9 | dame una tabla con los comandos de git (ambiguo) | no forja | ✓ tabla en el chat; ofreció forja como opción |
| 10 | explícame con un diagrama cómo funciona un hook (ambiguo) | no forja | ✓ cargó product-self-knowledge, no forja |

Conclusión: la description no se activa de más ni de menos, y no le quita trabajo a otras skills (pptx, product-self-knowledge). No hay que cambiarla.

## Regeneración con la skill actual (A)

| Guía | Motivo | Predicciones (huecos) | Retos | Tarjetas | Sin fuente |
|---|---|---|---|---|---|
| `hooks-de-claude-code` | banda transportadora con estaciones (nuevo: `hooks-v4`) | 8 (4) | 10 | 14 | 0 |
| `git` | cuentas en un hilo de papel continuo | 9 (4) | 7 | 14 | 1 (que muchos servicios crean `main` por defecto) |
| `git-merge-rebase` | cinta perforada | 9 (4) | 9 | 14 | 0 (zdiff3 desde 2.35 se verificó en las release notes oficiales y se citó) |

Las 3 pasan el validador y la revisión en celular.

### Fallas encontradas al regenerar

1. **Bug en el núcleo:** la API `forja` se definía después de dibujar las flashcards. Con el reto `flashcards` cumplido, al recargar fallaba todo el núcleo. Corregido en el esqueleto y propagado a las 4 guías con el script nuevo `scripts/actualizar_nucleo.py`, que solo reemplaza los bloques del núcleo. Probado: dominar el mazo y recargar ya no da errores.
2. **`revisar_movil.py` compartía la carpeta de capturas** entre procesos paralelos. Ahora usa una carpeta por guía.

## Prueba fuera de Claude Code: derivadas (Cálculo I, principiante)

- **Familia nueva `matematicas`:** papel milimétrico crema con cuadrícula, grafito para el texto, rojo de profesor como acento, azul de bolígrafo para las curvas y pizarrón verde con gis en los bloques oscuros. Fuentes: Source Serif 4 (libro de texto), Atkinson Hyperlegible (distingue 1, l e I en texto con símbolos) e IBM Plex Mono.
- **Motivo:** la secante que gira hasta volverse tangente.
- **Fuentes:** OpenStax Calculus Vol. 1 (Rice University), Paul's Online Notes (Lamar University), MAA Convergence y MacTutor (St Andrews). Un dato sin fuente: el consejo de no "tachar las d" en dy/dx.
- **Matemáticas verificadas a mano:** pendiente de (0,5) a (2,1) = −2; f(x)=x²+3x da f′(x)=2x+3; simulador con a=1 y h=0.1 da Δy=0.21 y pendiente 2.1; f(x)=x²−2x tiene f′(1)=0 en su mínimo; la regla de la potencia maneja n=0.
- **Distractores pedagógicos:** "f′(1) = −1, lo mismo que f(1)" (confundir altura con inclinación), "0/0" y "2x + h + 3" (olvidar el límite).
- Validador: sin errores (1 advertencia †). Celular: OK. 234k tokens, 16.5 min.

## "Explícamelo paso a paso" (pedido por el usuario)

Botón en el núcleo para cuando el usuario no puede resolver algo. Muestra el razonamiento **un paso por clic**, con "Ya entendí, lo intento" para volver a intentarlo, y la respuesta solo al final. Si se abre antes de responder, el veredicto dice "Acertaste con ayuda.", sin castigo. Para ejercicios generados por JS existe `forja.ayuda(el, pasos, respuesta)`.

- Núcleo propagado a las 5 guías.
- **Derivadas:** ayuda escrita para las 6 predicciones y ayuda dinámica en el probador (cambia con cada ejercicio; para n = 0 explica la constante). Probado en Chrome: un paso por clic, cerrar y retomar ("Seguir con la explicación"), "Acertaste con ayuda", reinicio con "Otro ejercicio", sin errores de JS.
- **Pendiente:** hooks, git, git-merge-rebase y subagentes tienen el botón en su núcleo, pero no tienen los pasos escritos. El validador ahora lo marca como error. Hay que escribir sus ayudas o regenerarlas.
- **Hecho (2026-11-12):** ayudas agregadas a las 4 guías restantes, solo con líneas nuevas y sin borrar ninguna:
  - hooks: 9 (8 de predicciones + probador de matchers)
  - git: 10 (9 + laboratorio de zonas)
  - git-merge-rebase: 11 (9 + terminal + **ayuda dinámica en el probador de ours/theirs**, que solo aparece después de responder `pred-swap` para no dar la respuesta antes de tiempo)
  - subagentes: 7 (5 + 2 clasificadores; dan el criterio y un caso de ejemplo, no las 6 respuestas)

  Las 5 guías pasan el validador sin errores de ayuda y no tienen errores de JS.
- **Aclaración de regla:** un subagente creó `git-v2` en vez de editar la original, porque la regla "nunca sobrescribir" era ambigua. Se aplicó el cambio a la original y se quitó la copia. Ahora CLAUDE.md y el mensaje del hook distinguen entre *generar* una guía (nunca sobrescribir) y un *cambio pedido por el usuario* (se edita la original, solo lo pedido, mostrando el diff).
- **Nota:** el hook de protección no corre en sesiones que no se abren desde el repo (como los subagentes de esta sesión). En las sesiones de Claude Code abiertas en `forja-skill` sí se aplica.

## Prueba con pedido natural: "quiero una guía del proceso de un motor de combustión externa"

- **Activación y preguntas:** cargó forja sola y, antes de crear nada, preguntó el **nivel** y además **qué motor** (Stirling, vapor o los dos). La segunda pregunta no está en la skill; salió del criterio de Claude ante un tema ambiguo. Respuesta del usuario: principiante, los dos.
- **Familia nueva `maquinas-termicas`:** crema de plano técnico, negro de hierro fundido, naranja de brasa como acento y azul acero del agua fría. Regla fija: naranja = caliente y azul = frío en toda la guía. Fuentes: Fraunces, IBM Plex Sans e IBM Plex Mono.
- **Motivo:** la pared que separa el fuego del fluido.
- **Estructura:** 3 partes (lo común, Stirling, vapor), 9 secciones, 6 predicciones (3 son huecos del paso a paso), 8 ayudas (2 dinámicas), 7 retos, 13 flashcards.
- **Fuentes:** NASA (science.nasa.gov y NTRS), DOE, OpenStax, Ohio University, FAMU-FSU, Penn State, MSU, HyperPhysics y ASME. Dos datos con †: volumen ×1,600 del vapor y que bombear líquido cuesta menos que comprimir vapor.
- **Física verificada a mano:** Carnot con T en kelvin (30 °C de lado frío: 47 % → 65 % al subir de 300 a 600 °C: "sube, pero no al doble"); regenerador con modelo de gas ideal (68 % = Carnot entre 850 y 90 °C; sin regenerador, 20 % con aire y 27 % con helio, reproducido con cv/R = 2.5 y 1.5). La guía aclara que son cálculos de modelo, no datos publicados.
- Validador sin errores, celular OK, sin errores de JS.

## Ilustraciones técnicas y animación

- **Punto de partida:** el usuario calificó las ilustraciones de la guía del motor con **2/10**. Un redibujo técnico (corte con achurado, sistema de trazo, geometría calculada) llegó a **6/10**, y animado con la física real a **8/10**. El usuario aprobó integrarlo a la skill.
- **Integrado:**
  - `reference/ilustracion.md` con reglas y una rúbrica de 10 puntos (mínimo 8);
  - `forja.animar` y `forja.kit` en el núcleo;
  - etiquetas `g.etiqueta` que en el celular se cambian por números y leyenda;
  - `assets/kit-svg.svg`, `scripts/svg_kit.py` y `scripts/revisar_ilustraciones.py`;
  - nuevo paso 8 en SKILL.md y avisos en `validar.py`.
- **Hallazgo del revisor nuevo:** en el celular, el ejemplo del motor mostraba el texto de unos 5 px. Por eso se agregaron las etiquetas adaptables.
- **Prueba de generalización (derivadas, en una copia):** un subagente limpio rehízo los 9 SVG y agregó la animación de la secante que se vuelve tangente.
  - Se calificó de 8 a 9 en cada dibujo.
  - Matemáticas verificadas en el navegador: 0 px de error; la pendiente medida es 3 + h en cada fase.
  - Corrigió 2 errores de los dibujos anteriores: las barras de f(a) y f(a+h) estaban corridas 18–20 px de P y Q, y el pico de |x| estaba fuera del eje.
- **Mejoras a partir de los reportes de esa prueba:**
  - Letra mínima en unidades del viewBox (11 × ancho ÷ 350), calculada por `Lienzo` e impresa por el revisor.
  - Etiquetas en las zonas vacías del plano para gráficas; letras móviles para las piezas que se mueven.
  - Profundidad alternativa cuando el lenguaje no tiene materiales.
  - Jerarquía de líneas en gráficas.
  - Kit pegado una sola vez, con prefijos por SVG y copia para secciones oscuras.
  - La animación no debe revelar una predicción.
  - El número de la etiqueta en el celular se corre para no tapar la pieza.
  - El revisor guarda cada fase por separado y revisa choques en escritorio en las 4 fases.
  - "Velocidad" ya no se parte en dos líneas.

## Redibujo de las 6 guías con la skill nueva

Lo pidió el usuario. Un agente por guía, en paralelo, editando la guía original y cambiando solo las ilustraciones (más su JS/CSS). Las 6 pasan el validador, la revisión en celular y el revisor de ilustraciones, sin errores de JS.

| Guía | SVG | Animación | Calificación |
|---|---|---|---|
| derivadas | 9 + 1 nueva | la secante se vuelve tangente (h → 0) | 8–9 |
| git | 8 | editar → git add → git commit (tres zonas) | 8–9 |
| git-merge-rebase | 8 | merge (dos padres) contra rebase (copias con hash nuevo) | 8–9 |
| hooks | 7 | ciclo de una sesión con el bucle agéntico | 8–9 |
| subagentes | 7 + 1 nueva | delegación: elegir por description → trabajar aparte → solo vuelve el resultado | 8–9 |
| motor | 13 | Stirling de dos pistones a 90° y ciclo de vapor | 8–9 |

- **Errores encontrados al calcular la geometría:**
  - en derivadas, barras desalineadas y el pico de |x| fuera del eje;
  - en hooks, Notification aparecía entre PostToolUse y Stop.
- **Respuestas que se revelaban antes de tiempo** (las 4 se corrigieron):
  - en hooks, "exit 1 → sigue + aviso";
  - en merge-rebase, el laboratorio dibujaba el rebase y el fast-forward se veía;
  - en motor, dos etiquetas.
- **Mejoras a la skill a partir de los reportes:** el número de etiqueta en el celular se mide con el ancho real; `svg_kit` suma `registrar`, `conector`, `color_sub`, `em` y atributos del svg; el revisor tiene `data-fases` y captura sin el desenfoque; `onda` termina recta; se documentaron la clase `.etiqueta` reservada, `ancho_movil` con min-width, cómo animar ilustraciones interactivas y los degradados con `userSpaceOnUse`.
