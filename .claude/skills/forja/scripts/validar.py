#!/usr/bin/env python3
"""Validador anti-slop de forja.

Revisa una guía HTML contra las reglas que un programa puede verificar.
Las reglas que necesitan criterio humano (información correcta, interactividad
real, layout distinto por sección) se revisan a mano con evals/evals.json.

Uso:
    python3 validar.py guias/<slug>/index.html

Salida: lista de ERRORES (bloquean) y ADVERTENCIAS (revisar).
Código de salida: 1 si hay errores, 0 si no.
"""
import colorsys
import re
import sys
from html.parser import HTMLParser
from pathlib import Path

# Tipos de interacción que forja usa. Cada bloque interactivo debe marcarse con
# data-interaccion="<tipo>" para que este validador lo encuentre.
TIPOS_INTERACCION = {"diagrama", "flashcards", "simulador", "pasos"}
# Mínimo de tipos distintos por guía: no todos los temas admiten los 4,
# pero con menos de 3 la guía se vuelve lectura pasiva.
MIN_TIPOS_INTERACCION = 3

# Una guía de estudio con más de ~400 KB casi siempre trae algo incrustado de más
# (fuentes, imágenes en base64) que no aporta al aprendizaje.
TAMANO_MAX_KB = 400

# Frases de relleno típicas de texto generado (expresiones regulares, sin
# distinguir mayúsculas).
FRASES_RELLENO = [
    r"en el mundo actual",
    r"en la era digital",
    r"en el vertiginoso",
    r"sum[ée]rg(e|ete|ámonos|irnos)\b",
    r"adentr(é|e)monos",
    r"sin más preámbulos",
    r"es importante destacar",
    r"cabe destacar que",
    r"juegan? un papel (crucial|fundamental|clave)",
    r"desbloque(a|ar|e)",
    r"al siguiente nivel",
    r"(viaje fascinante|fascinante viaje)",
    r"revolucionari[oa]s?",
    r"\ben (resumen|conclusión),",
    r"¡(vamos allá|manos a la obra)",
]

# Emojis pictográficos. Los símbolos tipográficos que sí sirven en una guía
# (flechas, ✓, ✗, ×) quedan permitidos.
EMOJI = re.compile(
    "[\U0001F300-\U0001F5FF\U0001F600-\U0001F64F\U0001F680-\U0001F6FF"
    "\U0001F900-\U0001F9FF\U0001FA70-\U0001FAFF\U00002600-\U000026FF"
    "\U00002700-\U000027BF\U00002B50\U00002B55\U0001F1E6-\U0001F1FF]"
)
SIMBOLOS_PERMITIDOS = set("✓✔✗✘✕✖➜➔➤❯❮")

COLORES_MORADOS_CON_NOMBRE = {"purple", "violet", "indigo", "magenta", "fuchsia", "orchid", "plum", "rebeccapurple", "blueviolet", "mediumpurple", "darkviolet"}
HEX = re.compile(r"#([0-9a-fA-F]{6}|[0-9a-fA-F]{3})\b")
RGB = re.compile(r"rgba?\(\s*(\d+)[ ,]+(\d+)[ ,]+(\d+)")
GRADIENTE = re.compile(r"(?:linear|radial|conic)-gradient\(([^;{}]*)\)", re.I)


class Lector(HTMLParser):
    """Separa el texto visible, el CSS y los recursos de la página."""

    def __init__(self):
        super().__init__(convert_charrefs=True)
        self.texto = []
        self.css = []
        self.externos = []
        self.interacciones = []
        self.metas = {}
        self.lang = None
        self.tiene_viewport = False
        self.tiene_slider = False
        self.en_fuentes = 0
        self.links_fuentes = []
        self._pila = []
        self._ignorar = 0

    def handle_starttag(self, tag, attrs):
        a = dict(attrs)
        if tag == "html":
            self.lang = a.get("lang")
        if tag in ("script", "style"):
            self._ignorar += 1
        if tag == "script" and a.get("src"):
            self.externos.append(f'<script src="{a["src"]}">')
        if tag == "link" and a.get("href") and "stylesheet" in (a.get("rel") or ""):
            self.externos.append(f'<link href="{a["href"]}">')
        if tag in ("img", "source", "iframe", "video", "audio") and re.match(r"(https?:)?//", a.get("src") or ""):
            self.externos.append(f'<{tag} src="{a["src"]}">')
        if tag == "meta":
            if a.get("name") == "viewport":
                self.tiene_viewport = True
            if a.get("name"):
                self.metas[a["name"]] = a.get("content", "")
        if tag == "input" and a.get("type") == "range":
            self.tiene_slider = True
        if a.get("data-interaccion"):
            self.interacciones.append(a["data-interaccion"].strip().lower())
        if a.get("style"):
            self.css.append(a["style"])
        # Sección de fuentes: cualquier elemento con id="fuentes"
        if a.get("id") == "fuentes":
            self.en_fuentes = 1
        elif self.en_fuentes and tag not in ("br", "img", "meta", "input", "hr"):
            self.en_fuentes += 1
        if self.en_fuentes and tag == "a" and re.match(r"https?://", a.get("href") or ""):
            self.links_fuentes.append(a["href"])
        if tag not in ("br", "img", "meta", "input", "hr", "link"):
            self._pila.append(tag)

    def handle_endtag(self, tag):
        if tag in ("script", "style"):
            self._ignorar = max(0, self._ignorar - 1)
        if self.en_fuentes and tag not in ("br", "img", "meta", "input", "hr"):
            self.en_fuentes -= 1

    def handle_data(self, data):
        if self._ignorar:
            if self._pila and self._pila[-1] == "style":
                self.css.append(data)
            return
        self.texto.append(data)


def es_morado(r, g, b):
    h, l, s = colorsys.rgb_to_hls(r / 255, g / 255, b / 255)
    tono = h * 360
    return 255 <= tono <= 315 and s >= 0.3 and 0.15 <= l <= 0.85


def colores_de(fragmento):
    for m in HEX.finditer(fragmento):
        v = m.group(1)
        if len(v) == 3:
            v = "".join(c * 2 for c in v)
        yield int(v[0:2], 16), int(v[2:4], 16), int(v[4:6], 16)
    for m in RGB.finditer(fragmento):
        yield int(m.group(1)), int(m.group(2)), int(m.group(3))


def validar(ruta: Path):
    errores, advertencias = [], []
    html = ruta.read_text(encoding="utf-8")
    lector = Lector()
    lector.feed(html)
    texto = " ".join(" ".join(lector.texto).split())
    css = "\n".join(lector.css)

    # 1. Archivo autocontenido (offline)
    for ext in lector.externos:
        errores.append(f"Recurso externo (rompe el modo offline): {ext}")
    for m in re.finditer(r"@import\s+url\(\s*['\"]?(https?:)?//[^)]+\)", css):
        errores.append(f"@import externo en CSS: {m.group(0)}")
    if re.search(r"fonts\.googleapis|fonts\.gstatic|cdn\.|unpkg\.com|jsdelivr", html):
        errores.append("Referencia a CDN o Google Fonts: usa fuentes del sistema")

    # 2. Fuentes citadas
    if 'id="fuentes"' not in html and "id='fuentes'" not in html:
        errores.append('Falta la sección de fuentes (elemento con id="fuentes")')
    elif len(lector.links_fuentes) < 2:
        errores.append(f"La sección de fuentes tiene {len(lector.links_fuentes)} enlace(s); se esperan al menos 2")

    # 3. Texto de relleno
    bajo = texto.lower()
    encontradas = sorted({m.group(0) for p in FRASES_RELLENO for m in re.finditer(p, bajo)})
    if encontradas:
        errores.append(f"Texto de relleno: {', '.join(repr(f) for f in encontradas)}")

    # 4. Emojis decorativos
    emojis = sorted(set(EMOJI.findall(texto)) - SIMBOLOS_PERMITIDOS)
    if emojis:
        errores.append(f"Emojis en el texto: {' '.join(emojis)}")

    # 5. Degradados morados
    for m in GRADIENTE.finditer(css):
        cuerpo = m.group(1).lower()
        morado = any(n in re.findall(r"[a-z]+", cuerpo) for n in COLORES_MORADOS_CON_NOMBRE)
        morado = morado or any(es_morado(*c) for c in colores_de(cuerpo))
        if morado:
            errores.append(f"Degradado morado: {m.group(0)[:80]}")

    # 6. Interacciones reales
    tipos = {t for t in lector.interacciones if t in TIPOS_INTERACCION}
    desconocidos = sorted({t for t in lector.interacciones if t not in TIPOS_INTERACCION})
    if desconocidos:
        advertencias.append(f"Tipos de interacción no reconocidos: {desconocidos} (válidos: {sorted(TIPOS_INTERACCION)})")
    if len(tipos) < MIN_TIPOS_INTERACCION:
        errores.append(
            f"Solo {len(tipos)} tipo(s) de interacción marcados con data-interaccion "
            f"({sorted(tipos) or 'ninguno'}); se esperan al menos {MIN_TIPOS_INTERACCION} de {sorted(TIPOS_INTERACCION)}"
        )
    elif len(tipos) < len(TIPOS_INTERACCION):
        advertencias.append(f"Faltan tipos de interacción: {sorted(TIPOS_INTERACCION - tipos)}")
    if "simulador" in tipos and not lector.tiene_slider:
        errores.append('Hay data-interaccion="simulador" pero ningún <input type="range">')

    # 7. Metadatos de forja
    if lector.lang is None or not lector.lang.lower().startswith("es"):
        errores.append('Falta lang="es" en <html>')
    if not lector.tiene_viewport:
        errores.append("Falta <meta name=\"viewport\">: no se verá bien en el celular")
    if not lector.metas.get("forja:nivel"):
        errores.append('Falta <meta name="forja:nivel" content="principiante|intermedio|avanzado">')
    if not lector.metas.get("forja:familia"):
        errores.append('Falta <meta name="forja:familia" content="<familia>">')
    else:
        familia = lector.metas["forja:familia"]
        raiz = next((p for p in [ruta.resolve(), *ruta.resolve().parents] if (p / "familias").is_dir()), None)
        if raiz and not (raiz / "familias" / f"{familia}.json").exists():
            advertencias.append(f"La familia '{familia}' no existe en familias/: créala o corrige el nombre")

    # 8. Tamaño
    kb = len(html.encode("utf-8")) / 1024
    if kb > TAMANO_MAX_KB:
        advertencias.append(f"El archivo pesa {kb:.0f} KB (máximo sugerido {TAMANO_MAX_KB} KB)")

    return errores, advertencias


def main():
    if len(sys.argv) != 2:
        print("Uso: python3 validar.py <guia.html>")
        return 1
    ruta = Path(sys.argv[1])
    if not ruta.exists():
        print(f"ERROR: no existe {ruta}")
        return 1
    errores, advertencias = validar(ruta)
    if errores:
        print(f"ERRORES ({len(errores)}):")
        for e in errores:
            print(f"  - {e}")
    if advertencias:
        print(f"ADVERTENCIAS ({len(advertencias)}):")
        for a in advertencias:
            print(f"  - {a}")
    if not errores and not advertencias:
        print("OK")
    elif not errores:
        print("Sin errores. Revisa las advertencias.")
    return 1 if errores else 0


if __name__ == "__main__":
    sys.exit(main())
