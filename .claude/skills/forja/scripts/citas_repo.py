#!/usr/bin/env python3
"""Comprueba las citas a código de una guía de repositorio contra el clon local.

Uso:
    python3 citas_repo.py guias/<slug>/index.html <carpeta del clon> [--mostrar]

Para cada permalink https://github.com/<dueño>/<repo>/blob/<sha>/<ruta>#L<a>-L<b> de la guía:
  - el commit debe ser el del clon (git rev-parse HEAD);
  - la ruta debe existir en el clon;
  - las líneas deben estar dentro del archivo.
Con --mostrar imprime las líneas citadas, para confirmar que dicen lo que la guía afirma.

Código de salida: 0 sin errores, 1 con errores, 2 si no se pudo revisar.
"""
import re
import subprocess
import sys
from pathlib import Path

PERMALINK = re.compile(r"https://github\.com/([\w.-]+)/([\w.-]+)/(?:blob|tree)/([0-9a-f]{7,40})/([^\"'#\s<>]+)(?:#L(\d+)(?:-L(\d+))?)?")


def main() -> int:
    args = [a for a in sys.argv[1:] if not a.startswith("--")]
    mostrar = "--mostrar" in sys.argv
    if len(args) != 2:
        print(__doc__)
        return 2
    guia, clon = Path(args[0]), Path(args[1])
    if not guia.is_file() or not (clon / ".git").exists():
        print("No encuentro la guía o el clon (debe tener .git)")
        return 2
    sha = subprocess.run(["git", "-C", str(clon), "rev-parse", "HEAD"], capture_output=True, text=True).stdout.strip()
    html = guia.read_text(encoding="utf-8")
    errores, vistos = [], set()
    citas = PERMALINK.findall(html)
    if not citas:
        print("La guía no tiene permalinks a GitHub con commit. Cita el código así: "
              "https://github.com/<dueño>/<repo>/blob/<sha>/<ruta>#L10-L25")
        return 1
    for dueno, repo, commit, ruta, a, b in citas:
        clave = (commit, ruta, a, b)
        if clave in vistos:
            continue
        vistos.add(clave)
        if not sha.startswith(commit) and not commit.startswith(sha[:len(commit)]):
            errores.append(f"{ruta}: cita el commit {commit[:7]}, pero el clon está en {sha[:7]}")
        archivo = clon / ruta.rstrip("/")
        if not archivo.exists():
            errores.append(f"{ruta}: no existe en el clon")
            continue
        if a and archivo.is_file():
            lineas = archivo.read_text(encoding="utf-8", errors="replace").splitlines()
            ini, fin = int(a), int(b or a)
            if ini < 1 or fin > len(lineas) or fin < ini:
                errores.append(f"{ruta}#L{a}{'-L' + b if b else ''}: el archivo tiene {len(lineas)} líneas")
            elif mostrar:
                print(f"\n── {ruta}  L{ini}–{fin}")
                for n in range(ini, min(fin, ini + 14) + 1):
                    print(f"{n:5} │ {lineas[n - 1]}")
    print(f"{len(vistos)} citas a código revisadas contra el commit {sha[:7]}")
    for e in errores:
        print(f"  ✗ {e}")
    if not errores:
        print("  ✓ Todas apuntan a archivos y líneas que existen")
    return 1 if errores else 0


if __name__ == "__main__":
    sys.exit(main())
