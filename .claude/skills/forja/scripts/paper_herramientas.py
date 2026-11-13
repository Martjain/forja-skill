#!/usr/bin/env python3
"""Herramientas para guías de un paper (reference/papers.md).

Uso:
    python3 paper_herramientas.py anclas <paper.html>
        Lista las anclas de la versión HTML de arXiv: secciones (S3, S3.SS2), apéndices (A1…),
        ecuaciones (S3.E1), tablas (S5.T4, A4.T21) y figuras (S1.F1), con su título o pie.
        Cita con https://arxiv.org/html/<id>v<n>#<ancla>.

    python3 paper_herramientas.py numeros <guía.html> <paper.txt>
        Busca en el texto del paper (pdftotext) cada cifra que la guía muestra (porcentajes,
        decimales y números de 3 o más dígitos). Imprime las que NO aparecen en el paper, para
        revisarlas a mano: pueden ser cálculos de la guía (dilo en el texto) o errores de copia.
"""
import html as html_mod
import re
import sys
from pathlib import Path


def anclas(ruta: Path) -> int:
    s = ruta.read_text(encoding="utf-8", errors="replace")
    patron = re.compile(r'<(section|figure|table|div|h[1-6]|span)\b[^>]*\bid="((?:S|A)\d+(?:\.[A-Za-z]+\d+)*|abstract\d*)"[^>]*>', re.S)
    vistos = set()
    for m in patron.finditer(s):
        ancla = m.group(2)
        if ancla in vistos or re.search(r"\.p\d+$", ancla):
            continue
        vistos.add(ancla)
        resto = s[m.end(): m.end() + 1500]
        t = re.search(r"<(?:h[1-6]|figcaption)[^>]*>(.*?)</(?:h[1-6]|figcaption)>", resto, re.S)
        titulo = re.sub(r"<[^>]+>", " ", t.group(1)) if t else ""
        titulo = re.sub(r"\s+", " ", html_mod.unescape(titulo)).strip()[:90]
        tipo = ("tabla" if ".T" in ancla else "figura" if ".F" in ancla else "ecuación" if ".E" in ancla
                else "apéndice" if ancla.startswith("A") and "." not in ancla else "resumen" if ancla.startswith("abstract")
                else "sección")
        if tipo in ("tabla", "figura", "sección", "apéndice", "resumen") or ancla.count(".") <= 2:
            print(f"#{ancla:<14} {tipo:<9} {titulo}")
    return 0


def numeros(guia: Path, paper: Path) -> int:
    h = guia.read_text(encoding="utf-8")
    h = re.sub(r"<(script|style)\b.*?</\1>", " ", h, flags=re.S)
    h = re.sub(r"<svg\b.*?</svg>", lambda m: " " + " ".join(re.findall(r">([^<]+)<", m.group(0))) + " ", h, flags=re.S)
    texto = html_mod.unescape(re.sub(r"<[^>]+>", " ", h))
    papel = paper.read_text(encoding="utf-8", errors="replace")
    papel_norm = papel.replace(",", "").replace("−", "-")
    cifras = set(re.findall(r"(?<![\w.])\d{1,3}(?:[,.]\d{3})+(?:\.\d+)?|(?<![\w.])\d+\.\d+|(?<![\w.])\d{3,}", texto))
    faltan = []
    for c in sorted(cifras):
        sin_miles = c.replace(",", "")
        if sin_miles in papel_norm or c in papel:
            continue
        if re.fullmatch(r"(19|20)\d\d", sin_miles):  # años
            continue
        faltan.append(c)
    print(f"{len(cifras)} cifras en la guía; {len(faltan)} no aparecen tal cual en el paper:")
    for c in faltan:
        i = texto.find(c)
        print(f"  {c:<10} «…{' '.join(texto[max(0, i - 50): i + 30].split())}…»")
    print("\nCada una debe ser un cálculo de la guía (y decirlo) o corregirse contra el paper.")
    return 0


def main() -> int:
    if len(sys.argv) >= 3 and sys.argv[1] == "anclas":
        return anclas(Path(sys.argv[2]))
    if len(sys.argv) >= 4 and sys.argv[1] == "numeros":
        return numeros(Path(sys.argv[2]), Path(sys.argv[3]))
    print(__doc__)
    return 2


if __name__ == "__main__":
    sys.exit(main())
