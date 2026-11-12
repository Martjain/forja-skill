# Línea base

Guías generadas **sin** la skill forja, para compararlas contra las que se generan con ella.

## Cómo generar una línea base

1. Abre una sesión **nueva** de Claude Code en la raíz del repo, con la skill apagada.
   En `.claude/settings.local.json`:
   ```json
   { "skillOverrides": { "forja": "off" } }
   ```
2. Pega el prompt sin agregar reglas:
   ```text
   Crea una guía visual interactiva sobre los hooks de Claude Code para alguien
   que está empezando. Usa información de la documentación oficial.
   Guárdala en un solo archivo: linea-base/hooks.html
   ```
3. Califícala:
   ```bash
   python3 .claude/skills/forja/scripts/validar.py linea-base/hooks.html
   ```
   y revisa a mano los criterios sin `[script]` de `.claude/skills/forja/evals/evals.json`.

La línea base va a fallar en las convenciones propias de forja (por ejemplo `data-interaccion` o `forja:familia`), y eso es lo esperado. Lo que importa son las fallas de fondo: información incorrecta, interactividad falsa, AI slop y dependencias externas.
