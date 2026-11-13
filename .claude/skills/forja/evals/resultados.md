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
