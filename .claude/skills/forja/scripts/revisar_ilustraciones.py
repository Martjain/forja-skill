#!/usr/bin/env python3
"""Renderiza las ilustraciones de una guía para revisarlas con la rúbrica.

Uso:
    python3 revisar_ilustraciones.py guias/<slug>/index.html

Qué hace:
  1. Captura cada <svg> de contenido en grande (escala 2x, a 1280 px de ancho).
  2. En cada animación [data-anima] fija 4 fases (0, 0.25, 0.5, 0.75) y las junta en una hoja.
  3. Detecta, a 390 px de ancho (celular):
     - etiquetas <text> que se encimen entre sí,
     - texto que se vea de menos de 11 px,
     - texto que se salga del viewBox.
  4. Advierte si un SVG usa más de 4 grosores de línea (el sistema es 2.5 / 1.25 / 1; las piezas
     gruesas, de más de 4, no cuentan).
  5. Guarda todo en /tmp/forja-ilustraciones/<carpeta de la guía>/ para abrirlo con Read.

Después: abre cada imagen y califícala con la rúbrica de reference/ilustracion.md (mínimo 8/10).

Código de salida: 0 sin problemas, 1 con problemas, 2 si no se pudo revisar.
"""
import shutil
import sys
from pathlib import Path

SALIDA = Path("/tmp/forja-ilustraciones")
TEXTO_MIN_PX = 11
MAX_GROSORES = 4
FASES = (0, 0.25, 0.5, 0.75)

# SVG de contenido: se ignoran los íconos chicos y los que el núcleo genera.
JS_SVGS = """
() => [...document.querySelectorAll('main svg, section svg')].filter(s => {
  const r = s.getBoundingClientRect();
  return r.width >= 160 && r.height >= 80 && !s.closest('.anima-ctl, [data-forja-flashcards], nav');
}).map((s, i) => { s.dataset.forjaIlus = i; return i; })
"""

JS_REVISAR = """
(minPx) => {
  const res = [];
  for (const s of document.querySelectorAll('svg[data-forja-ilus]')) {
    const sec = s.closest('section');
    const donde = (sec && sec.id ? '#' + sec.id : '(sin sección)') + ' svg ' + s.dataset.forjaIlus;
    const caja = s.getBoundingClientRect();
    if (!caja.width) continue;
    const textos = [...s.querySelectorAll('text')].filter(t => {
      const visible = t.checkVisibility ? t.checkVisibility({ opacityProperty: true, visibilityProperty: true })
        : t.getClientRects().length > 0;
      return visible && t.getClientRects().length && !t.closest('[opacity="0"]') && t.textContent.trim();
    });
    const rects = textos.map(t => ({ t, r: t.getBoundingClientRect(),
      etiqueta: t.textContent.trim().slice(0, 30) }));
    const chicos = [], fuera = [], choques = [];
    for (const { t, r, etiqueta } of rects) {
      const px = parseFloat(getComputedStyle(t).fontSize) * (caja.width / (s.viewBox.baseVal.width || caja.width));
      if (px < minPx) chicos.push(`"${etiqueta}" (${px.toFixed(1)} px)`);
      if (r.left < caja.left - 1 || r.right > caja.right + 1 || r.top < caja.top - 1 || r.bottom > caja.bottom + 1)
        fuera.push(`"${etiqueta}"`);
    }
    for (let i = 0; i < rects.length; i++) for (let j = i + 1; j < rects.length; j++) {
      const a = rects[i].r, b = rects[j].r;
      const ox = Math.min(a.right, b.right) - Math.max(a.left, b.left);
      const oy = Math.min(a.bottom, b.bottom) - Math.max(a.top, b.top);
      if (ox > 2 && oy > 2) choques.push(`"${rects[i].etiqueta}" con "${rects[j].etiqueta}"`);
    }
    const grosores = new Set();
    for (const el of s.querySelectorAll('*')) {
      const cs = getComputedStyle(el);
      // Solo trazos de línea (<= 4); los más gruesos son piezas dibujadas como dos líneas superpuestas.
      const g = parseFloat(cs.strokeWidth);
      if (cs.stroke && cs.stroke !== 'none' && el.tagName !== 'text' && g <= 4
          && !el.closest('pattern, marker, .et-num')) grosores.add(g);
    }
    res.push({ donde, chicos, fuera, choques, grosores: [...grosores].filter(g => g > 0).sort((a, b) => b - a),
      anima: !!s.closest('[data-anima]') });
  }
  return res;
}
"""


def buscar_navegador():
    for nombre in ("google-chrome", "google-chrome-stable", "chromium", "chromium-browser"):
        ruta = shutil.which(nombre)
        if ruta:
            return ruta
    return None


def hoja_fases(imagenes, destino: Path):
    from PIL import Image, ImageDraw
    ims = [Image.open(p) for p in imagenes]
    w = max(i.width for i in ims)
    h = sum(i.height for i in ims) + 34 * len(ims)
    hoja = Image.new("RGB", (w, h), "white")
    d = ImageDraw.Draw(hoja)
    y = 0
    for fase, im in zip(FASES, ims):
        d.text((12, y + 10), f"fase {fase}", fill="black")
        hoja.paste(im, (0, y + 34))
        y += im.height + 34
    hoja.save(destino)


def main() -> int:
    if len(sys.argv) != 2:
        print(__doc__)
        return 2
    guia = Path(sys.argv[1]).resolve()
    if not guia.is_file():
        print(f"No existe: {guia}")
        return 2
    try:
        from playwright.sync_api import sync_playwright
    except ImportError:
        print("Falta Playwright: pip install playwright && python3 -m playwright install chromium")
        return 2

    salida = SALIDA / guia.parent.name
    shutil.rmtree(salida, ignore_errors=True)
    salida.mkdir(parents=True)
    problemas = 0
    ejecutable = buscar_navegador()

    with sync_playwright() as p:
        nav = p.chromium.launch(executable_path=ejecutable, args=["--no-sandbox"]) if ejecutable \
            else p.chromium.launch()

        # 1 y 2. Capturas grandes (escritorio, 2x)
        pag = nav.new_page(viewport={"width": 1280, "height": 900}, device_scale_factor=2)
        pag.goto(guia.as_uri())
        pag.wait_for_timeout(600)
        pag.add_style_tag(content=".entra{animation:none!important;opacity:1!important;transform:none!important}")
        ids = pag.evaluate(JS_SVGS)
        n_anim = 0
        for i in ids:
            svg = pag.locator(f'svg[data-forja-ilus="{i}"]')
            svg.scroll_into_view_if_needed()
            caja_anima = svg.locator("xpath=ancestor::*[@data-anima][1]")
            if caja_anima.count():
                n_anim += 1
                cuadros = []
                for f in FASES:
                    caja_anima.evaluate(f"c => c.__fijar && c.__fijar({f})")
                    pag.wait_for_timeout(120)
                    destino = salida / f"ilus-{i:02d}-fase-{int(f * 100):02d}.png"
                    caja_anima.screenshot(path=str(destino))
                    cuadros.append(destino)
                try:
                    hoja_fases(cuadros, salida / f"ilus-{i:02d}-fases.png")
                    for c in cuadros:
                        c.unlink()
                except ImportError:
                    pass
            else:
                svg.screenshot(path=str(salida / f"ilus-{i:02d}.png"))
        pag.close()

        # 3 y 4. Revisión en celular
        movil = nav.new_page(viewport={"width": 390, "height": 844}, device_scale_factor=1)
        movil.goto(guia.as_uri())
        movil.wait_for_timeout(600)
        movil.evaluate(JS_SVGS)
        for c in movil.locator("[data-anima]").all():
            c.evaluate("c => c.__fijar && c.__fijar(0.25)")
        informe = movil.evaluate(JS_REVISAR, TEXTO_MIN_PX)
        nav.close()

    print(f"Ilustraciones: {len(ids)} ({n_anim} animadas)")
    if n_anim == 0:
        print("  AVISO: ninguna animación [data-anima]. Si el tema es un proceso, anima su ilustración central.")
    for r in informe:
        avisos = []
        if r["choques"]:
            avisos.append("etiquetas encimadas: " + "; ".join(r["choques"][:5]))
        if r["chicos"]:
            avisos.append(f"texto < {TEXTO_MIN_PX} px en celular: " + ", ".join(r["chicos"][:5]))
        if r["fuera"]:
            avisos.append("texto fuera del viewBox: " + ", ".join(r["fuera"][:5]))
        if len(r["grosores"]) > MAX_GROSORES:
            avisos.append(f"{len(r['grosores'])} grosores de trazo {r['grosores']} (usa 2.5 / 1.25 / 1)")
        if avisos:
            problemas += 1
            print(f"  ✗ {r['donde']}")
            for a in avisos:
                print(f"      {a}")
    if not problemas:
        print("  ✓ Sin choques de etiquetas ni texto ilegible")
    print(f"\nCapturas en {salida}/ — ábrelas con Read y califícalas con la rúbrica (mínimo 8/10).")
    return 1 if problemas else 0


if __name__ == "__main__":
    sys.exit(main())
