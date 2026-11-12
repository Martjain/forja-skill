# forja-skill

**forja** es una skill de Claude Code que convierte un tema en una guía visual interactiva: un solo archivo HTML que funciona offline, investigado en fuentes oficiales y con una UI acorde al tema.

```text
/forja hooks de Claude Code
```

## Qué incluye cada guía

- Diagramas clicables, flashcards, simuladores con slider y recorridos paso a paso
- Una dirección visual que sale del tema, sin AI slop (nada de degradados morados, emojis decorativos ni texto de relleno)
- Fuentes oficiales citadas
- Profundidad ajustada a tu nivel: principiante, intermedio o avanzado

## Estado

En construcción, siguiendo un proceso en el que las pruebas se escriben primero:

- [x] Paso 1: definir la tarea
- [x] Paso 2: ficha de diseño
- [x] Paso 3: línea base y pruebas (`evals/`, `scripts/validar.py`). Línea base: 9/16
- [x] Paso 4: skill mínima (`SKILL.md`, `reference/`, scripts, hook de protección)
- [ ] Paso 5: probar, comparar e iterar

## Piezas de la skill

| Pieza | Para qué |
|---|---|
| `SKILL.md` | Flujo de 9 pasos con checklist |
| `reference/diseno.md` | Dirección visual, familias, catálogo de 10 layouts, SVG, anti-slop, celular |
| `reference/interacciones.md` | Diagrama, flashcards, simulador, paso a paso: cómo debe ser cada uno |
| `assets/esqueleto.html` | Estructura mínima: metadatos, variables de la familia, sección de fuentes |
| `scripts/validar.py` | Validador anti-slop (lo que se puede revisar con un programa) |
| `scripts/revisar_movil.py` | Desbordamiento en celular, errores de JS y capturas (requiere Playwright) |
| `scripts/registrar.py` | Ruta libre (nunca sobrescribe) y registro en el índice |
| `.claude/hooks/proteger_guias.py` | Hook que bloquea editar guías que ya tienen commit |

Para `revisar_movil.py`, en tu equipo:

```bash
pip install playwright && python3 -m playwright install chromium
```

## Estructura

```text
.claude/skills/forja/   la skill
familias/               bases visuales compartidas (ej. claude-code.json)
guias/                  guías generadas
linea-base/             guías generadas sin la skill, para comparar
```
