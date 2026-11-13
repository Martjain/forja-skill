"""Configuración local de los scripts de forja.

Lee, en este orden (gana el primero que tenga el valor):
  1. Variables de entorno.
  2. El archivo `.env` de la raíz del repo (no se sube a GitHub: está en .gitignore).
  3. Los valores por omisión de abajo.

Copia `.env.example` a `.env` y cambia lo que necesites. Sin `.env`, todo funciona igual.
No necesita instalar nada: el `.env` se lee con este módulo, sin python-dotenv.
"""
import os
import shutil
import tempfile
from pathlib import Path

POR_OMISION = {
    # Navegador para Playwright. Vacío = buscar Chrome o Chromium en el PATH, y si no, el de Playwright.
    "FORJA_NAVEGADOR": "",
    # Carpeta donde los scripts guardan capturas e informes (una subcarpeta por guía).
    "FORJA_SALIDA": str(Path(tempfile.gettempdir())),
    # Ancho del celular para las revisiones (px).
    "FORJA_ANCHO_MOVIL": "390",
}


def _raiz() -> Path:
    p = Path(__file__).resolve()
    for padre in p.parents:
        if (padre / "familias").is_dir() or (padre / ".git").exists():
            return padre
    return p.parents[3]


def _leer_env(ruta: Path) -> dict:
    valores = {}
    if not ruta.is_file():
        return valores
    for linea in ruta.read_text(encoding="utf-8").splitlines():
        linea = linea.strip()
        if not linea or linea.startswith("#") or "=" not in linea:
            continue
        clave, valor = linea.split("=", 1)
        valor = valor.strip()
        if len(valor) >= 2 and valor[0] == valor[-1] and valor[0] in "\"'":
            valor = valor[1:-1]
        valores[clave.strip().removeprefix("export ").strip()] = valor
    return valores


_ENV = _leer_env(_raiz() / ".env")


def leer(clave: str) -> str:
    return os.environ.get(clave) or _ENV.get(clave) or POR_OMISION.get(clave, "")


def salida(nombre: str) -> Path:
    """Carpeta de salida de un script, p. ej. salida('forja-prueba') → /tmp/forja-prueba."""
    return Path(leer("FORJA_SALIDA")).expanduser() / nombre


def navegador():
    """Ruta del navegador para Playwright, o None para usar el que trae Playwright."""
    elegido = leer("FORJA_NAVEGADOR")
    if elegido:
        return elegido
    for nombre in ("google-chrome", "google-chrome-stable", "chromium", "chromium-browser"):
        ruta = shutil.which(nombre)
        if ruta:
            return ruta
    return None


def ancho_movil() -> int:
    try:
        return int(leer("FORJA_ANCHO_MOVIL"))
    except ValueError:
        return 390
