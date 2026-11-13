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
import json
import re
import sys
from html.parser import HTMLParser
from pathlib import Path

# Tipos de interacción que forja usa. Cada bloque interactivo debe marcarse con
# data-interaccion="<tipo>" para que este validador lo encuentre.
TIPOS_INTERACCION = {"diagrama", "flashcards", "simulador", "pasos"}
# "otra" se acepta (probadores, ordenar, etc.) pero no cuenta para el mínimo.
TIPOS_EXTRA = {"otra"}
# Mínimo de tipos distintos por guía: no todos los temas admiten los 4,
# pero con menos de 3 la guía se vuelve lectura pasiva.
MIN_TIPOS_INTERACCION = 3

# Catálogo de layouts de reference/diseno.md, sección 4.
LAYOUTS = {"portada", "dato-heroe", "dividido", "secuencia", "comparacion",
           "lista-grande", "mosaico", "enfasis", "laboratorio", "repaso"}
# Con menos de 5 layouts distintos la guía vuelve a verse como una plantilla repetida.
MIN_LAYOUTS = 5
# Una ilustración por sección clave; 3 es el mínimo para que la guía no sea solo cajas de texto.
MIN_SVG = 3
# Citas junto al dato (a.cita fuera de #fuentes); menos de 3 significa que las fuentes quedaron solo al final.
MIN_CITAS = 3
# Predecir antes de ver: con menos de 2, la guía vuelve a ser de mostrar resultados.
MIN_PREDICCIONES = 2
# Retos que guían la atención en las interacciones.
MIN_RETOS = 3
# Secciones de más de 8 minutos pierden a quien se distrae fácil.
MAX_MINUTOS_SECCION = 8
# Fuentes que delatan una UI genérica si son la principal (reference/diseno.md, sección 3).
FUENTES_GENERICAS = {"inter", "roboto", "arial", "helvetica", "open sans", "space grotesk", "poppins",
                     "montserrat", "system-ui", "ui-sans-serif", "ui-serif", "-apple-system", "segoe ui", "sans-serif", "serif"}

# Las fuentes incrustadas suman ~100-140 KB; por encima de ~500 KB casi siempre hay algo
# incrustado de más (imágenes en base64, pesos de fuente extra) que no aporta al aprendizaje.
TAMANO_MAX_KB = 500

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


VACIOS = {"area", "base", "br", "col", "embed", "hr", "img", "input", "link", "meta", "source", "track", "wbr", "param"}
# Flashcards: menos de 8 no alcanza para repasar; más de 15 cansa en una sola sesión.
MIN_TARJETAS, MAX_TARJETAS = 8, 15


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
        self.citas = 0
        self.svgs = 0
        self.secciones = []  # (id, data-layout) en orden
        self.oscuras = 0
        self.predicciones = 0
        self.opciones = 0
        self.tras_prediccion = 0
        self.retos = 0
        self.minutos = []  # (id, data-minutos o None)
        self.atributos = set()  # atributos data-forja-* presentes
        # Anidamiento: para saber qué hay dentro de un data-tras-prediccion o de unos pasos.
        self._abiertos = []  # (tag, dentro_de_tras, indice_de_pasos o None)
        self.tras_con_controles = []  # descripciones de controles escondidos tras una predicción
        self.pasos = []  # por cada data-interaccion="pasos": cuántas predicciones tiene dentro
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
        if tag == "a" and not self.en_fuentes and "cita" in (a.get("class") or "").split():
            self.citas += 1
        if tag == "svg":
            self.svgs += 1
        if tag == "section":
            self.secciones.append((a.get("id"), (a.get("data-layout") or "").strip().lower()))
            if (a.get("data-tono") or "").strip().lower() == "oscuro":
                self.oscuras += 1
            if a.get("id") != "fuentes":
                self.minutos.append((a.get("id"), a.get("data-minutos")))
        if "data-prediccion" in a and a.get("data-correcta"):
            self.predicciones += 1
        if "data-opcion" in a:
            self.opciones += 1
        if "data-tras-prediccion" in a:
            self.tras_prediccion += 1
        if "data-reto" in a:
            self.retos += 1
        self.atributos.update(k for k in a if k.startswith("data-forja-"))

        tras_padre = self._abiertos[-1][1] if self._abiertos else False
        pasos_padre = self._abiertos[-1][2] if self._abiertos else None
        if tras_padre and (tag in ("button", "input", "select", "textarea") or "data-nodo" in a):
            self.tras_con_controles.append(f"<{tag}{' data-nodo' if 'data-nodo' in a else ''}>")
        if "data-prediccion" in a and pasos_padre is not None:
            self.pasos[pasos_padre] += 1
        tras = tras_padre or "data-tras-prediccion" in a
        pasos = pasos_padre
        if (a.get("data-interaccion") or "").strip().lower() == "pasos":
            self.pasos.append(0)
            pasos = len(self.pasos) - 1
        if tag not in VACIOS:
            self._abiertos.append((tag, tras, pasos))
        if tag not in ("br", "img", "meta", "input", "hr", "link"):
            self._pila.append(tag)

    def handle_endtag(self, tag):
        # Cierra hasta la última apertura de esta etiqueta (tolera <p>/<li> sin cerrar).
        for i in range(len(self._abiertos) - 1, -1, -1):
            if self._abiertos[i][0] == tag:
                del self._abiertos[i:]
                break
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
    desconocidos = sorted({t for t in lector.interacciones if t not in TIPOS_INTERACCION | TIPOS_EXTRA})
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

    # 7. Layouts, tono, ilustraciones y citas
    secciones = [(i, l) for i, l in lector.secciones if i != "fuentes"]
    sin_layout = sum(1 for _, l in secciones if not l)
    if sin_layout:
        errores.append(f"{sin_layout} <section> sin data-layout (catálogo: {sorted(LAYOUTS)})")
    raros = sorted({l for _, l in secciones if l and l not in LAYOUTS})
    if raros:
        errores.append(f"Layouts fuera del catálogo: {raros}")
    seguidos = [l for (_, l), (_, s) in zip(secciones, secciones[1:]) if l and l == s]
    if seguidos:
        errores.append(f"Layout repetido en secciones seguidas: {sorted(set(seguidos))}")
    distintos = {l for _, l in secciones if l in LAYOUTS}
    if secciones and len(distintos) < MIN_LAYOUTS:
        errores.append(f"Solo {len(distintos)} layouts distintos ({sorted(distintos)}); se esperan al menos {MIN_LAYOUTS}")
    if secciones and not lector.oscuras:
        errores.append('Ninguna sección con data-tono="oscuro": falta alternar bloques claros y oscuros')
    if lector.svgs < MIN_SVG:
        errores.append(f"Solo {lector.svgs} ilustración(es) SVG; se esperan al menos {MIN_SVG}")
    if lector.citas < MIN_CITAS:
        errores.append(f'Solo {lector.citas} cita(s) junto a los datos (<a class="cita">); se esperan al menos {MIN_CITAS}')

    # 7b. Núcleo forja: progreso, mapa, predicciones y retos
    for attr in ("data-forja-progreso", "data-forja-mapa"):
        if attr not in lector.atributos:
            errores.append(f"Falta el elemento {attr} del núcleo (copia el núcleo del esqueleto sin cambios)")
    if "NÚCLEO FORJA: JS" not in html:
        errores.append("Falta el bloque «NÚCLEO FORJA: JS» del esqueleto")
    if lector.predicciones < MIN_PREDICCIONES:
        errores.append(f"Solo {lector.predicciones} predicción(es) con data-prediccion y data-correcta; se esperan al menos {MIN_PREDICCIONES}")
    elif lector.opciones < 2 * lector.predicciones:
        errores.append("Cada data-prediccion necesita al menos 2 botones data-opcion")
    if lector.predicciones and lector.tras_prediccion < lector.predicciones:
        errores.append("Cada predicción debe ocultar su resultado con data-tras-prediccion")
    if lector.retos < MIN_RETOS:
        errores.append(f"Solo {lector.retos} reto(s) con data-reto; se esperan al menos {MIN_RETOS}")
    if lector.tras_con_controles:
        errores.append(
            "data-tras-prediccion esconde controles o el diagrama "
            f"({', '.join(sorted(set(lector.tras_con_controles)))}): marca solo el resultado; los controles quedan visibles"
        )
    sin_hueco = [i + 1 for i, n in enumerate(lector.pasos) if n == 0]
    if sin_hueco:
        errores.append(f"Paso a paso sin huecos (#{sin_hueco}): desde el paso 3 el usuario completa con una data-prediccion")

    # 7b'. Flashcards del núcleo y repaso espaciado
    if "data-forja-flashcards" not in lector.atributos:
        errores.append('Falta <div data-forja-flashcards>: las flashcards las dibuja el núcleo')
    m = re.search(r'<script[^>]*id=["\']forja-tarjetas["\'][^>]*>(.*?)</script>', html, re.S)
    if not m:
        errores.append('Falta <script type="application/json" id="forja-tarjetas"> con las flashcards')
    else:
        try:
            tarjetas = json.loads(m.group(1))
            ids = [t.get("id") for t in tarjetas]
            if not MIN_TARJETAS <= len(tarjetas) <= MAX_TARJETAS:
                (errores if len(tarjetas) < MIN_TARJETAS else advertencias).append(
                    f"{len(tarjetas)} flashcards; se esperan entre {MIN_TARJETAS} y {MAX_TARJETAS}")
            if any(not (t.get("id") and t.get("q") and t.get("a")) for t in tarjetas):
                errores.append("Cada flashcard necesita id, q y a")
            if len(set(ids)) != len(ids):
                errores.append("Hay ids de flashcards repetidos (el repaso espaciado los mezclaría)")
        except (json.JSONDecodeError, AttributeError) as e:
            errores.append(f"El JSON de forja-tarjetas no es válido: {e}")
    n_sin_fuente = len(re.findall(r'class="[^"]*\bsin-fuente\b', re.sub(r"<!--.*?-->", "", html, flags=re.S)))
    if n_sin_fuente:
        advertencias.append(f"{n_sin_fuente} dato(s) marcado(s) sin fuente oficial (se muestran con †). Revisa si se pueden verificar")

    sin_min = [i or "?" for i, m in lector.minutos if not m]
    if sin_min:
        advertencias.append(f"Secciones sin data-minutos: {sin_min}")
    largas = [f"{i}={m}" for i, m in lector.minutos if m and m.isdigit() and int(m) > MAX_MINUTOS_SECCION]
    if largas:
        advertencias.append(f"Secciones de más de {MAX_MINUTOS_SECCION} min (divídelas): {largas}")

    # 7c. Tipografía incrustada y con carácter
    if not re.search(r"@font-face\s*{[^}]*data:font/woff2;base64,", css):
        errores.append("No hay fuentes incrustadas (@font-face con data:font/woff2): usa scripts/fuentes.py css")
    for var in ("--f-titulos", "--f-cuerpo"):
        m = re.search(rf"{var}\s*:\s*([^;]+);", css)
        if m:
            principal = m.group(1).split(",")[0].strip().strip("\"'").lower()
            if principal in FUENTES_GENERICAS:
                errores.append(f"{var} usa una fuente genérica como principal ({principal}); elige una del catálogo")

    # 8. Metadatos de forja
    if lector.lang is None or not lector.lang.lower().startswith("es"):
        errores.append('Falta lang="es" en <html>')
    if not lector.tiene_viewport:
        errores.append("Falta <meta name=\"viewport\">: no se verá bien en el celular")
    if not lector.metas.get("forja:nivel"):
        errores.append('Falta <meta name="forja:nivel" content="principiante|intermedio|avanzado">')
    if not lector.metas.get("forja:slug"):
        advertencias.append('Falta <meta name="forja:slug">: el guardado del progreso usará la ruta del archivo')
    if not lector.metas.get("forja:familia"):
        errores.append('Falta <meta name="forja:familia" content="<familia>">')
    else:
        familia = lector.metas["forja:familia"]
        raiz = next((p for p in [ruta.resolve(), *ruta.resolve().parents] if (p / "familias").is_dir()), None)
        if raiz and not (raiz / "familias" / f"{familia}.json").exists():
            advertencias.append(f"La familia '{familia}' no existe en familias/: créala o corrige el nombre")

    # 9. Tamaño
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
