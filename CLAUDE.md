# forja-skill

Repositorio de **forja**, una skill de Claude Code que crea guías visuales interactivas (HTML + CSS + JS sin librerías) sobre cualquier tema, con una UI acorde al tema.

## Estructura

- `.claude/skills/forja/`: la skill (SKILL.md, reference/, scripts/, evals/)
- `familias/<familia>.json`: base visual compartida por temas relacionados (paleta, tipografía, tono, motivos)
- `guias/<slug>/index.html`: una guía por carpeta, en un solo archivo
- `linea-base/`: guías generadas SIN la skill, para comparar
- `index.html`: índice de todas las guías

## Reglas del repo

- Todo en español. Los términos técnicos van como aparecen en la documentación oficial.
- Una guía = un solo archivo `guias/<slug>/index.html`, sin CDN ni recursos externos. Tiene que funcionar offline.
- Al **generar** una guía, nunca sobrescribir una existente: si `guias/<slug>/` ya existe, crear `guias/<slug>-v2/` (o el siguiente número).
- Cuando el **usuario pide explícitamente un cambio en una guía publicada** (por ejemplo, agregar ayudas o corregir un dato), se edita la guía original: no se crea una `-v2`. Se aplica solo lo pedido, con un script que inserte o reemplace esos bloques, y se muestra el diff. El hook de protección bloquea Edit/Write sobre guías con commit para evitar sobrescrituras accidentales; no está pensado para impedir cambios que el usuario pidió.
- Al agregar una guía, agregarla también a `index.html`.
- Antes de dar una guía por terminada, correr el validador y corregir hasta que no marque errores:
  `python3 .claude/skills/forja/scripts/validar.py guias/<slug>/index.html`
- Los cambios van en ramas, nunca directo a `main`.
- Si cambias el núcleo en `assets/esqueleto.html` (bloques "NÚCLEO FORJA"), propágalo a las guías publicadas con
  `python3 .claude/skills/forja/scripts/actualizar_nucleo.py`. Solo toca esos bloques; el contenido de las guías no se modifica.
