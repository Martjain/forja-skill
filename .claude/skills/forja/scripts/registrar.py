#!/usr/bin/env python3
"""Rutas y registro de guías forja.

Uso:
    python3 registrar.py ruta "<tema>"
        Imprime una ruta libre: guias/<slug>/index.html, o guias/<slug>-v2/index.html
        si ya existe. Nunca devuelve una ruta ocupada.

    python3 registrar.py indice <ruta_html> --titulo "<título>" --familia <familia> --nivel <nivel>
        Agrega la guía al índice index.html de la raíz del repo (lo crea si no existe).
        Si la guía ya está en el índice, no la duplica.
"""
import argparse
import datetime
import html
import re
import sys
import unicodedata
from pathlib import Path

MARCADOR = "<!-- forja:fin-lista -->"
# Rutas cortas se leen y se escriben mejor: "git-merge-rebase", no el título completo.
MAX_SLUG = 40
MAX_PALABRAS = 4
PLANTILLA_INDICE = Path(__file__).resolve().parent.parent / "assets" / "indice.html"


def raiz_repo() -> Path:
    """La raíz es la carpeta más cercana hacia arriba que tiene familias/ o .git."""
    aqui = Path.cwd().resolve()
    for p in [aqui, *aqui.parents]:
        if (p / "familias").is_dir() or (p / ".git").exists():
            return p
    return aqui


def slug(texto: str) -> str:
    sin_acentos = unicodedata.normalize("NFKD", texto).encode("ascii", "ignore").decode()
    s = re.sub(r"[^a-z0-9]+", "-", sin_acentos.lower()).strip("-")
    if len(s) > MAX_SLUG:
        s = s[:MAX_SLUG].rsplit("-", 1)[0]
    return s or "guia"


def cmd_ruta(tema: str) -> int:
    raiz = raiz_repo()
    if len(tema.split()) > MAX_PALABRAS:
        print(f"AVISO: el tema tiene {len(tema.split())} palabras. Usa uno corto (1 a {MAX_PALABRAS}), "
              f"por ejemplo \"git merge rebase\" en vez del título completo.", file=sys.stderr)
    base = slug(tema)
    candidato, n = base, 1
    # Una carpeta vacía (reservada por un `ruta` anterior que no llegó a escribir la guía) cuenta como libre.
    def ocupada(c):
        d = raiz / "guias" / c
        return d.exists() and (not d.is_dir() or any(d.iterdir()))
    while ocupada(candidato):
        n += 1
        candidato = f"{base}-v{n}"
    ruta = Path("guias") / candidato / "index.html"
    (raiz / ruta).parent.mkdir(parents=True, exist_ok=True)
    print(ruta.as_posix())
    if n > 1:
        print(f"AVISO: ya existía guias/{base}/. Se creará la versión {n}; avísale al usuario.", file=sys.stderr)
    return 0




def cmd_indice(ruta_html: str, titulo: str, familia: str, nivel: str) -> int:
    raiz = raiz_repo()
    guia = (raiz / ruta_html) if not Path(ruta_html).is_absolute() else Path(ruta_html)
    if not guia.exists():
        print(f"ERROR: no existe {ruta_html}. Registra la guía después de crearla.")
        return 1
    rel = guia.resolve().relative_to(raiz).as_posix()
    indice = raiz / "index.html"
    if not indice.exists():
        indice.write_text(PLANTILLA_INDICE.read_text(encoding="utf-8"), encoding="utf-8")
    contenido = indice.read_text(encoding="utf-8")
    if MARCADOR not in contenido:
        print(f"ERROR: index.html no tiene el marcador {MARCADOR}. Agrégalo dentro de la lista de guías.")
        return 1
    if f'href="{rel}"' in contenido:
        print(f"Ya estaba en el índice: {rel}")
        return 0
    fecha = datetime.date.today().isoformat()
    entrada = (
        f'<li data-slug="{html.escape(guia.parent.name)}"><a href="{html.escape(rel)}">{html.escape(titulo)}</a>'
        f"<span>{html.escape(familia)} · {html.escape(nivel)} · {fecha}</span></li>\n"
    )
    indice.write_text(contenido.replace(MARCADOR, entrada + MARCADOR), encoding="utf-8")
    print(f"Agregada al índice: {rel}")
    return 0


def main() -> int:
    p = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = p.add_subparsers(dest="cmd", required=True)
    r = sub.add_parser("ruta")
    r.add_argument("tema")
    i = sub.add_parser("indice")
    i.add_argument("ruta_html")
    i.add_argument("--titulo", required=True)
    i.add_argument("--familia", required=True)
    i.add_argument("--nivel", required=True, choices=["principiante", "intermedio", "avanzado"])
    a = p.parse_args()
    if a.cmd == "ruta":
        return cmd_ruta(a.tema)
    return cmd_indice(a.ruta_html, a.titulo, a.familia, a.nivel)


if __name__ == "__main__":
    sys.exit(main())
