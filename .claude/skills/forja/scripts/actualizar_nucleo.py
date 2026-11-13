#!/usr/bin/env python3
"""Actualiza el núcleo forja (CSS y JS) de guías ya creadas.

El núcleo (progreso, mapa, predicciones, retos, flashcards, repaso) se copia
sin cambios del esqueleto a cada guía. Cuando el núcleo del esqueleto se
corrige o mejora, este script reemplaza SOLO los bloques entre los marcadores
"NÚCLEO FORJA: CSS/JS" y "FIN NÚCLEO FORJA: CSS/JS". No toca el contenido, el
diseño ni las interacciones propias de la guía.

Es mantenimiento de código compartido, no una reescritura de la guía: por eso
es la forma permitida de cambiar una guía ya publicada.

Uso:
    python3 actualizar_nucleo.py                 # todas las guías en guias/
    python3 actualizar_nucleo.py --revisar       # solo dice cuáles están desactualizadas
    python3 actualizar_nucleo.py guias/x/index.html [...]
"""
import re
import sys
from pathlib import Path

ESQUELETO = Path(__file__).resolve().parent.parent / "assets" / "esqueleto.html"
BLOQUE = r"(/\* ===== NÚCLEO FORJA: {m} \(copiar sin cambios\) ===== \*/)(.*?)(/\* ===== FIN NÚCLEO FORJA: {m} ===== \*/)"


def bloques(texto):
    return {m: re.search(BLOQUE.format(m=m), texto, re.S) for m in ("CSS", "JS")}


def main(args):
    revisar = "--revisar" in args
    rutas = [Path(a) for a in args if a != "--revisar"]
    if not rutas:
        raiz = next((p for p in [Path.cwd(), *Path.cwd().parents] if (p / "guias").is_dir()), Path.cwd())
        rutas = sorted((raiz / "guias").glob("*/index.html"))
    nuevo = bloques(ESQUELETO.read_text(encoding="utf-8"))
    desactualizadas = 0
    for ruta in rutas:
        texto = ruta.read_text(encoding="utf-8")
        actual = bloques(texto)
        if not all(actual.values()):
            print(f"  -  {ruta}: sin núcleo forja (guía de una versión anterior), se omite")
            continue
        cambia = [m for m in ("CSS", "JS") if actual[m].group(2).strip() != nuevo[m].group(2).strip()]
        if not cambia:
            print(f"  =  {ruta}: al día")
            continue
        desactualizadas += 1
        if revisar:
            print(f"  !  {ruta}: núcleo {'+'.join(cambia)} desactualizado")
            continue
        for m in cambia:
            patron = re.compile(BLOQUE.format(m=m), re.S)
            texto = patron.sub(lambda x, m=m: x.group(1) + nuevo[m].group(2) + x.group(3), texto, count=1)
        ruta.write_text(texto, encoding="utf-8")
        print(f"  ✓  {ruta}: núcleo {'+'.join(cambia)} actualizado")
    return 1 if (revisar and desactualizadas) else 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
