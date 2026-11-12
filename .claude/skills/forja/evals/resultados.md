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

## Fallas encontradas y corregidas

1. **La ruta incluía el nivel.** `registrar.py` recibía el pedido completo (`$ARGUMENTS`), así que la carpeta quedó como `hooks-de-claude-code-nivel-principiante`. Corregido en SKILL.md (paso 2): se pasa solo el tema.

## Pendiente

- Pruebas de activación negativa (`activacion.no_debe_activar` en evals.json): falta comprobar que la skill no se dispare con "explícame rápido qué es un hook" y similares.
- El hook de protección se probó con datos simulados, pero en los evals no llegó a dispararse porque `registrar.py` evitó la colisión antes. Para probarlo de verdad hay que pedir explícitamente que se edite una guía publicada.
- Costo: cada guía toma de 9 a 14 minutos y entre 178k y 197k tokens. Vigilarlo si se agregan más pasos.
