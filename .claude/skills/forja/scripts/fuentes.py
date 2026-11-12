#!/usr/bin/env python3
"""Tipografías incrustadas para guías forja.

Uso:
    python3 fuentes.py lista
        Muestra el catálogo: id, roles, pesos y carácter de cada fuente.

    python3 fuentes.py css --titulos <id> --cuerpo <id> [--codigo <id>]
        Imprime el CSS listo para pegar al inicio del <style> de la guía:
        @font-face con las fuentes en base64 (funciona offline) y las variables
        --f-titulos, --f-cuerpo y --f-codigo con su pila de respaldo.

Pesos que se incrustan (los mínimos, para que el archivo no crezca de más):
    titulos: 600 (o 400 si la fuente solo tiene 400)
    cuerpo:  400 y 600 (o 700 si no hay 600)
    codigo:  400
"""
import argparse
import base64
import json
import sys
from pathlib import Path

DIR = Path(__file__).resolve().parent.parent / "assets" / "fuentes"
RESPALDO = {
    "titulos": "Georgia, serif",
    "cuerpo": "system-ui, sans-serif",
    "codigo": "ui-monospace, Menlo, Consolas, monospace",
}


def catalogo():
    return json.loads((DIR / "catalogo.json").read_text(encoding="utf-8"))["fuentes"]


def peso_mas_cercano(pesos, deseado):
    return deseado if deseado in pesos else min(pesos, key=lambda p: (abs(p - deseado), -p))


def font_face(fid, info, peso):
    archivo = DIR / fid / f"{peso}.woff2"
    datos = base64.b64encode(archivo.read_bytes()).decode()
    return (
        f"@font-face{{font-family:\"{info['nombre']}\";font-style:normal;font-weight:{peso};"
        f"font-display:swap;src:url(data:font/woff2;base64,{datos}) format(\"woff2\");}}"
    )


def cmd_lista():
    for fid, info in catalogo().items():
        print(f"{fid:24} {'/'.join(info['rol']):18} {info['pesos']}  {info['caracter']}")
    return 0


def cmd_css(titulos, cuerpo, codigo):
    cat = catalogo()
    pedidos = {"titulos": titulos, "cuerpo": cuerpo, "codigo": codigo}
    faltan = [f for f in pedidos.values() if f and f not in cat]
    if faltan:
        print(f"ERROR: no están en el catálogo: {faltan}. Opciones: {sorted(cat)}", file=sys.stderr)
        return 1
    caras = {}  # (fid, peso) -> css, para no repetir si una fuente cumple dos roles
    variables = []
    for rol, fid in pedidos.items():
        if not fid:
            variables.append(f"--f-{rol}:{RESPALDO[rol]};")
            continue
        info = cat[fid]
        if rol == "titulos":
            pesos = [peso_mas_cercano(info["pesos"], 600)]
        elif rol == "cuerpo":
            pesos = sorted({peso_mas_cercano(info["pesos"], 400), peso_mas_cercano(info["pesos"], 600)})
        else:
            pesos = [peso_mas_cercano(info["pesos"], 400)]
        for p in pesos:
            caras.setdefault((fid, p), font_face(fid, info, p))
        variables.append(f"--f-{rol}:\"{info['nombre']}\",{RESPALDO[rol]};")
    salida = "\n".join(caras.values()) + "\n:root{" + "".join(variables) + "}"
    print(f"/* forja:fuentes titulos={titulos} cuerpo={cuerpo} codigo={codigo or '-'} · licencia SIL OFL 1.1 */")
    print(salida)
    kb = len(salida.encode()) / 1024
    print(f"Fuentes: {len(caras)} archivo(s), {kb:.0f} KB de CSS", file=sys.stderr)
    return 0


def main():
    p = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = p.add_subparsers(dest="cmd", required=True)
    sub.add_parser("lista")
    c = sub.add_parser("css")
    c.add_argument("--titulos", required=True)
    c.add_argument("--cuerpo", required=True)
    c.add_argument("--codigo")
    a = p.parse_args()
    return cmd_lista() if a.cmd == "lista" else cmd_css(a.titulos, a.cuerpo, a.codigo)


if __name__ == "__main__":
    sys.exit(main())
