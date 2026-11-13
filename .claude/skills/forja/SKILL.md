---
name: forja
description: Crea guías visuales interactivas de estudio sobre cualquier tema, en un solo archivo HTML offline con diagramas clicables, flashcards, simuladores con slider y pasos guiados, investigadas en fuentes oficiales y con una UI que sale del propio tema. Usar cuando se pida una guía visual, una guía interactiva, una guía para estudiar o aprender un tema, o con /forja <tema>. No usar para explicaciones rápidas en el chat, resúmenes de documentos, presentaciones ni para editar un HTML existente.
argument-hint: [tema]
allowed-tools: Bash(python3 *), WebFetch, WebSearch
---

# forja

Reglas que no se rompen:
- **Nunca sobrescribas una guía.** La ruta la decide `registrar.py`.
- **Un solo archivo HTML, sin CDN ni recursos externos.** Debe funcionar offline.
- **Cero emojis.** Si necesitas un ícono, dibújalo en SVG.
- **No termines hasta que `validar.py` no marque errores y `revisar_movil.py` pase.**

El contenido (investigar y explicar con exactitud) hazlo como lo harías normalmente. Esta skill agrega reglas de **forma**: dirección visual, layouts, interacciones y verificación.

## Flujo

Copia esta lista y márcala conforme avances:

```
- [ ] 1. Nivel
- [ ] 2. Ruta
- [ ] 3. Familia visual
- [ ] 4. Investigar
- [ ] 5. Plan de secciones
- [ ] 6. Construir
- [ ] 7. Validar
- [ ] 8. Revisar en celular
- [ ] 9. Registrar en el índice
```

**1. Nivel.** Si el pedido no dice el nivel, pregunta *principiante, intermedio o avanzado* y espera la respuesta antes de seguir.

**2. Ruta.** Pasa **solo el tema, en 1 a 4 palabras**, sin el nivel ni el título completo (de "/forja hooks de Claude Code, nivel principiante" el tema es "hooks de Claude Code"; de "git: ramas, merge vs rebase y conflictos" es "git merge rebase"):
```bash
python3 ${CLAUDE_SKILL_DIR}/scripts/registrar.py ruta "<tema>"
```
Usa exactamente la ruta que imprime. Si dice que ya existía una versión, avísale al usuario cuál creaste. El nombre de la carpeta es el `forja:slug` de la guía.

**3. Familia visual.** Revisa `familias/`. Si el tema pertenece a una familia existente, usa su paleta y tipografía, y elige el motivo del tema en `motivos_por_tema` (agrégalo si falta). Si no pertenece a ninguna, crea `familias/<familia>.json` con el mismo esquema que `familias/claude-code.json`. Cómo derivar la paleta y elegir las fuentes del tema: [diseno.md](reference/diseno.md), secciones 1 y 3. Genera el CSS de las fuentes de la familia:
```bash
python3 ${CLAUDE_SKILL_DIR}/scripts/fuentes.py css --titulos <id> --cuerpo <id> --codigo <id>
```

**4. Investigar.** Solo fuentes oficiales (documentación oficial, estándares, sitios .gov/.edu, papers). Anota la URL de cada dato clave. Si un dato no lo encontraste en una fuente oficial, márcalo en la guía con `<span class="sin-fuente">…</span>`. **Nunca lo presentes como verificado.**

**5. Plan de secciones.** Antes de escribir HTML, muéstrale al usuario una tabla corta con 5 a 9 secciones. Para cada una: concepto, layout del catálogo, interacción (con su predicción y sus retos, si los tiene), ilustración SVG y minutos. Layouts e interacciones: [diseno.md](reference/diseno.md) sección 4 e [interacciones.md](reference/interacciones.md).

**6. Construir.** Parte de [esqueleto.html](assets/esqueleto.html). Copia **sin cambios** los bloques "NÚCLEO FORJA" (progreso, mapa, predicciones, retos, guardado) y pega el CSS de las fuentes. Reglas:
- **Predecir antes de ver:** al menos 2 interacciones empiezan con `data-prediccion`. **Solo el resultado** lleva `data-tras-prediccion="<id>"`; los controles y el diagrama quedan visibles.
- **"Explícamelo paso a paso":** cada predicción lleva su `data-ayuda` con 2 a 5 pasos, y la respuesta solo en el último (`data-respuesta`). Los ejercicios generados por JS usan `forja.ayuda(...)`.
- **Paso a paso que se desvanece:** los pasos 1 y 2 vienen resueltos, desde el 3 el usuario completa un hueco y después ve un "¿Por qué?".
- **Flashcards:** solo el JSON `forja-tarjetas` (8 a 15 tarjetas) y `<div data-forja-flashcards>`. El núcleo las dibuja y las suma al repaso del índice.
- **Retos:** al menos 3 `data-reto` en total, que se cumplen haciendo (tu JS llama a `forja.reto(id)`).
- **Portada:** incluye el mapa (`<nav data-forja-mapa>`) y la entrada escalonada (`class="entra"` con `--i`). Cada `<section>` lleva `id` y `data-minutos`.
- Cada `<section>` lleva `data-layout="<layout del catálogo>"`. No repitas un layout en secciones seguidas y usa al menos 5 distintos.
- Al menos una sección con `data-tono="oscuro"` para alternar claro y oscuro.
- Cada interacción lleva `data-interaccion="diagrama|flashcards|simulador|pasos|otra"`. Usa al menos 3 de los 4 tipos principales. Si el tema pide una interacción propia, como un probador, agrégala como `otra`.
- Una ilustración SVG propia en cada sección clave (mínimo 3), dibujada con los colores de la familia.
- Cita junto al dato: `<a class="cita" href="URL">[n]</a>`, con la lista completa en `<section id="fuentes">`.

**7. Validar.**
```bash
python3 ${CLAUDE_SKILL_DIR}/scripts/validar.py <ruta>
```
Si marca errores, corrígelos y vuelve a correrlo. **No sigas mientras haya errores.**

**8. Revisar en celular.**
```bash
python3 ${CLAUDE_SKILL_DIR}/scripts/revisar_movil.py <ruta>
```
Abre con Read las capturas que genera y revisa que se lea bien. Corrige cualquier desbordamiento que reporte.

**9. Registrar.**
```bash
python3 ${CLAUDE_SKILL_DIR}/scripts/registrar.py indice <ruta> --titulo "<título>" --familia <familia> --nivel <nivel>
```
Termina diciendo la ruta de la guía y qué interacciones tiene.
