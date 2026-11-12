# Calificación de la línea base: hooks.html

Generada **sin** la skill, por un subagente con contexto limpio y este prompt:
"Crea una guía visual interactiva sobre los hooks de Claude Code para alguien que está empezando. Usa información de la documentación oficial."

**Resultado: 9 de 16 criterios.**

## Criterios

| # | Criterio | Resultado | Nota |
|---|---|---|---|
| 1 | Cada dato clave enlaza a una fuente oficial | ✗ | Las fuentes solo aparecen al final; no hay citas junto a los datos |
| 2 | Sección de fuentes al final | ✓ | 2 enlaces oficiales (hooks y hooks-guide) |
| 3 | Nivel declarado y adaptado | ✓ | El nivel venía en el prompt. Falta probar el caso en que hay que preguntarlo |
| 4 | Sin texto de relleno | ✓ | |
| 5 | Información correcta | ✓ | El código 2 bloquea y el 1 no; estructura evento → matcher → hooks; "más de 30 eventos" (son 33) |
| 6 | Diagrama clicable | ✓ | Ciclo de vida con "Reproducir un turno" y una ficha por evento |
| 7 | Flashcards | ✗ | No tiene |
| 8 | Simulador con slider | ✗ | Hay un simulador de entrada/salida, pero sin slider |
| 9 | Paso a paso guiado | ✓ | "Tu primer hook" en 4 pasos |
| 10 | Una interacción por concepto, ninguna falsa | ✓ | El probador de matchers es excelente: escribes un matcher y ves qué herramientas lo disparan |
| 11 | Paleta de la familia Claude Code | ✗ | Tiene acento terracota, pero el tema es oscuro genérico tipo "dev tool", con morados y verdes de relleno |
| 12 | Sin emojis decorativos | ✗ | 10 tipos: ⚓ ⚠ 💡 📝 📭 🔁 🔇 🔍 🚧 🧩 |
| 13 | Layout distinto por sección | ✗ | Todas las secciones repiten la etiqueta, el título y las tarjetas oscuras con borde |
| 14 | Ilustraciones SVG propias, sin logos | ✗ | Cero SVG; todo son cajas de texto. Sin logos (bien) |
| 15 | Un solo archivo, offline | ✓ | 84 KB, sin CDN |
| 16 | Se ve bien en el celular | ✗ | Hay desbordamiento horizontal a 390 px |

## Validador

```text
ERRORES (4):
  - Emojis en el texto: ⚓ ⚠ 💡 📝 📭 🔁 🔇 🔍 🚧 🧩
  - Solo 0 tipo(s) de interacción marcados con data-interaccion
  - Falta <meta name="forja:nivel">
  - Falta <meta name="forja:familia">
```

Los últimos 3 errores son de convenciones propias de forja; ya se esperaba que la línea base no las cumpliera.

## Conclusión para el Paso 4

**Claude ya resuelve bien:** investigar la documentación oficial, explicar con exactitud e inventar interacciones útiles (el probador de matchers es mejor que cualquier cosa que le habríamos dictado). La skill **no** debe darle instrucciones sobre el contenido, porque sería gastar tokens en algo que ya hace bien.

**La skill tiene que cubrir lo que falló, que es casi todo visual:**

1. Dirección visual a partir de `familias/*.json`, con fondo claro y bloques oscuros alternados, en vez del tema oscuro genérico
2. Ilustraciones SVG propias en cada sección clave
3. Layout distinto por sección, con un catálogo de layouts para elegir
4. Las 4 interacciones, en especial flashcards y simulador con slider, marcadas con `data-interaccion`
5. Cero emojis; usar íconos SVG si hacen falta
6. Revisar el celular y que no haya desbordamiento horizontal (agregar una verificación)
7. Citas junto a los datos clave, no solo al final
8. Preguntar el nivel cuando no viene en el pedido, y poner los metadatos `forja:*`
