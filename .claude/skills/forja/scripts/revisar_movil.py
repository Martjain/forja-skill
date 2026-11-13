#!/usr/bin/env python3
"""Revisa una guía en tamaño celular y escritorio.

Uso:
    python3 revisar_movil.py guias/<slug>/index.html

Qué hace:
  1. Abre la guía a 390 px de ancho (celular) y a 1280 px (escritorio).
  2. Detecta desbordamiento horizontal y lista los elementos que se salen.
  3. Reporta errores de JavaScript de la página.
  4. Guarda capturas en <FORJA_SALIDA>/forja-revision/<carpeta de la guía>/ (/tmp por omisión) para revisarlas con Read.

Código de salida: 0 si todo está bien, 1 si hay problemas, 2 si no se pudo revisar.
Requiere Playwright: pip install playwright && python3 -m playwright install chromium
"""
import shutil
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import _config  # noqa: E402  (lee .env)

ANCHO_MOVIL = _config.ancho_movil()   # 390 por omisión: iPhone 12-15, el ancho de celular más común
ALTO_MOVIL = 844
ANCHO_ESCRITORIO = 1280
ALTO_ESCRITORIO = 800
# Las capturas completas se cortan en tramos de esta altura para poder leerlas.
TRAMO_PX = 2000
SALIDA = _config.salida("forja-revision")

# Encuentra los CONTENEDORES que causan desbordamiento horizontal: el elemento más
# externo que se sale, cuyo padre todavía cabe en la pantalla. Corregir ese basta.
JS_DESBORDES = """
() => {
  const w = window.innerWidth;
  const sale = el => { const r = el.getBoundingClientRect(); return r.width > 0 && r.right > w + 1; };
  const recortado = el => {
    for (let p = el.parentElement; p && p !== document.body; p = p.parentElement) {
      const ox = getComputedStyle(p).overflowX;
      if (['auto', 'hidden', 'scroll', 'clip'].includes(ox)) return true;
    }
    return false;
  };
  const causas = new Set();
  for (const el of document.body.querySelectorAll('*')) {
    if (!sale(el) || recortado(el)) continue;
    let c = el;
    while (c.parentElement && c.parentElement !== document.body && sale(c.parentElement)
           && !['MAIN', 'SECTION', 'HTML'].includes(c.parentElement.tagName)) c = c.parentElement;
    causas.add(c);
  }
  const fuera = [...causas].slice(0, 8).map(el => {
    const r = el.getBoundingClientRect();
    const id = el.id ? '#' + el.id : '';
    const cls = el.classList.length ? '.' + [...el.classList].slice(0, 2).join('.') : '';
    const sec = el.closest('section');
    const lay = sec && sec.dataset.layout ? ` en section[data-layout=${sec.dataset.layout}]` : '';
    return `<${el.tagName.toLowerCase()}${id}${cls}> mide ${Math.round(r.width)} px y se sale ${Math.round(r.right - w)} px${lay}`;
  });
  return { scroll: document.documentElement.scrollWidth, ancho: w, fuera };
}
"""




def hojas(captura: Path, prefijo: str, escala: float, por_hoja: int):
    """Corta la captura completa en tramos y los acomoda lado a lado en pocas hojas,
    para revisar toda la página con 2-4 imágenes en vez de 15."""
    try:
        from PIL import Image
    except ImportError:
        return [captura]
    im = Image.open(captura)
    if escala != 1:
        im = im.resize((int(im.width * escala), int(im.height * escala)))
    tramos = [im.crop((0, y, im.width, min(im.height, y + TRAMO_PX))) for y in range(0, im.height, TRAMO_PX)]
    salida = []
    for n, i in enumerate(range(0, len(tramos), por_hoja)):
        grupo = tramos[i:i + por_hoja]
        separacion = 16
        hoja = Image.new("RGB", (sum(t.width for t in grupo) + separacion * (len(grupo) - 1),
                                 max(t.height for t in grupo)), "#808080")
        x = 0
        for t in grupo:
            hoja.paste(t, (x, 0))
            x += t.width + separacion
        p = SALIDA / f"{prefijo}-{n + 1}.png"
        hoja.save(p)
        salida.append(p)
    return salida


def main() -> int:
    if len(sys.argv) != 2:
        print("Uso: python3 revisar_movil.py <guia.html>")
        return 2
    guia = Path(sys.argv[1]).resolve()
    if not guia.exists():
        print(f"ERROR: no existe {guia}")
        return 2
    # Una carpeta por guía: si se revisan varias guías a la vez, no se pisan las capturas.
    global SALIDA
    SALIDA = SALIDA / guia.parent.name
    try:
        from playwright.sync_api import sync_playwright
    except ImportError:
        print("NO SE PUDO REVISAR: falta Playwright. Instálalo con:")
        print("  pip install playwright && python3 -m playwright install chromium")
        return 2

    SALIDA.mkdir(parents=True, exist_ok=True)
    problemas, capturas = [], []
    with sync_playwright() as p:
        ejecutable = _config.navegador()
        try:
            nav = p.chromium.launch(executable_path=ejecutable, args=["--no-sandbox"]) if ejecutable \
                else p.chromium.launch()
        except Exception as e:  # sin Chromium instalado
            print(f"NO SE PUDO REVISAR: no se encontró un navegador ({e.__class__.__name__}).")
            print("  Instala uno con: python3 -m playwright install chromium")
            return 2

        for nombre, ancho, alto in (("movil", ANCHO_MOVIL, ALTO_MOVIL), ("escritorio", ANCHO_ESCRITORIO, ALTO_ESCRITORIO)):
            pagina = nav.new_page(viewport={"width": ancho, "height": alto})
            errores_js = []
            pagina.on("pageerror", lambda e, lista=errores_js: lista.append(str(e)))
            pagina.goto(guia.as_uri())
            pagina.wait_for_timeout(600)
            r = pagina.evaluate(JS_DESBORDES)
            if r["scroll"] > r["ancho"] + 1:
                problemas.append(f"[{nombre}] La página mide {r['scroll']} px de ancho en una pantalla de {r['ancho']} px")
                problemas.extend(f"[{nombre}]   {f}" for f in r["fuera"])
            for e in errores_js:
                problemas.append(f"[{nombre}] Error de JavaScript: {e}")
            completa = SALIDA / f"{nombre}-completa.png"
            pagina.screenshot(path=str(completa), full_page=True)
            # Celular: 4 tramos de 390 px por hoja. Escritorio: a la mitad, 2 por hoja.
            capturas.extend(hojas(completa, nombre, 1 if nombre == "movil" else 0.5, 4 if nombre == "movil" else 2))
            pagina.close()
        nav.close()

    if problemas:
        print(f"PROBLEMAS ({len(problemas)}):")
        for x in problemas:
            print(f"  - {x}")
    else:
        print("OK: sin desbordamiento horizontal ni errores de JavaScript.")
    print("Capturas para revisar con Read:")
    for c in capturas:
        print(f"  {c}")
    return 1 if problemas else 0


if __name__ == "__main__":
    sys.exit(main())
