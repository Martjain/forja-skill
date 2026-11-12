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
- [ ] Paso 3: línea base y pruebas (`evals/`, `scripts/validar.py`)
- [ ] Paso 4: skill mínima
- [ ] Paso 5: probar, comparar e iterar

## Estructura

```text
.claude/skills/forja/   la skill
familias/               bases visuales compartidas (ej. claude-code.json)
guias/                  guías generadas
linea-base/             guías generadas sin la skill, para comparar
```
