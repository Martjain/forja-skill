#!/usr/bin/env python3
"""Hook PreToolUse: impide modificar guías ya publicadas.

Una guía está "publicada" cuando su archivo ya está en git (commit hecho).
Las guías nuevas que todavía no tienen commit se pueden escribir y corregir libremente.

Recibe el evento como JSON por stdin. Sale con:
  0 -> permitir
  2 -> bloquear (el motivo va por stderr y Claude lo ve)
"""
import json
import re
import subprocess
import sys
from pathlib import Path

GUIA = re.compile(r"(^|/)guias/[^/]+/index\.html$")


def main() -> int:
    try:
        evento = json.load(sys.stdin)
    except json.JSONDecodeError:
        return 0  # sin datos válidos no se bloquea nada
    ruta = (evento.get("tool_input") or {}).get("file_path") or ""
    if not GUIA.search(ruta.replace("\\", "/")):
        return 0
    archivo = Path(ruta)
    if not archivo.is_absolute():
        archivo = Path(evento.get("cwd") or ".") / archivo
    if not archivo.exists():
        return 0
    publicada = subprocess.run(
        ["git", "ls-files", "--error-unmatch", str(archivo)],
        cwd=archivo.parent, capture_output=True,
    ).returncode == 0
    if publicada:
        print(
            f"Bloqueado: {ruta} es una guía ya publicada (está en git). "
            "Si estás generando una guía nueva, crea otra versión con: "
            "python3 .claude/skills/forja/scripts/registrar.py ruta \"<tema>\". "
            "Si el usuario pidió explícitamente cambiar ESTA guía, aplica solo ese cambio con un script "
            "que inserte o reemplace los bloques pedidos y muéstrale el diff (ver CLAUDE.md).",
            file=sys.stderr,
        )
        return 2
    return 0


if __name__ == "__main__":
    sys.exit(main())
