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
    return s[:60].rstrip("-") or "guia"


def cmd_ruta(tema: str) -> int:
    raiz = raiz_repo()
    base = slug(tema)
    candidato, n = base, 1
    while (raiz / "guias" / candidato).exists():
        n += 1
        candidato = f"{base}-v{n}"
    ruta = Path("guias") / candidato / "index.html"
    (raiz / ruta).parent.mkdir(parents=True, exist_ok=True)
    print(ruta.as_posix())
    if n > 1:
        print(f"AVISO: ya existía guias/{base}/. Se creará la versión {n}; avísale al usuario.", file=sys.stderr)
    return 0


INDICE_NUEVO = """<!DOCTYPE html>
<html lang="es">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>forja · guías</title>
<style>
:root { --fondo:#FAF9F5; --tinta:#141413; --suave:#5E5D59; --borde:#E8E6DC; --acento:#D97757; }
* { box-sizing: border-box; }
body { margin:0; background:var(--fondo); color:var(--tinta); font:400 1.0625rem/1.6 ui-sans-serif, system-ui, -apple-system, "Segoe UI", sans-serif; }
main { max-width: 52rem; margin: 0 auto; padding: clamp(2rem, 8vw, 5rem) 1.25rem; }
h1 { font: 600 clamp(2.5rem, 8vw, 4rem)/1 ui-serif, Georgia, serif; margin: 0 0 .5rem; }
p.lema { color: var(--suave); margin: 0 0 3rem; }
ol { list-style: none; padding: 0; margin: 0; counter-reset: g; }
li { counter-increment: g; display: grid; grid-template-columns: 3.5rem 1fr; gap: .25rem 1rem; padding: 1.25rem 0; border-top: 1px solid var(--borde); }
li::before { content: counter(g, decimal-leading-zero); grid-row: span 2; font: 600 1.75rem/1 ui-serif, Georgia, serif; color: var(--acento); }
li a { font-weight: 600; font-size: 1.2rem; color: inherit; text-decoration-color: var(--acento); text-underline-offset: 4px; }
li span { color: var(--suave); font-size: .9rem; }
:focus-visible { outline: 3px solid var(--acento); outline-offset: 3px; }
</style>
</head>
<body>
<main>
<h1>forja</h1>
<p class="lema">Guías visuales para aprender haciendo.</p>
<ol>
<!-- forja:fin-lista -->
</ol>
</main>
</body>
</html>
"""


def cmd_indice(ruta_html: str, titulo: str, familia: str, nivel: str) -> int:
    raiz = raiz_repo()
    guia = (raiz / ruta_html) if not Path(ruta_html).is_absolute() else Path(ruta_html)
    if not guia.exists():
        print(f"ERROR: no existe {ruta_html}. Registra la guía después de crearla.")
        return 1
    rel = guia.resolve().relative_to(raiz).as_posix()
    indice = raiz / "index.html"
    if not indice.exists():
        indice.write_text(INDICE_NUEVO, encoding="utf-8")
    contenido = indice.read_text(encoding="utf-8")
    if MARCADOR not in contenido:
        print(f"ERROR: index.html no tiene el marcador {MARCADOR}. Agrégalo dentro de la lista de guías.")
        return 1
    if f'href="{rel}"' in contenido:
        print(f"Ya estaba en el índice: {rel}")
        return 0
    fecha = datetime.date.today().isoformat()
    entrada = (
        f'<li><a href="{html.escape(rel)}">{html.escape(titulo)}</a>'
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
