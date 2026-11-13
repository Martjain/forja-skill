#!/usr/bin/env python3
"""Recorre una guía como lo haría una persona y revisa que lo importante funcione.

Uso:
    python3 probar_guia.py guias/<slug>/index.html [--celular]

validar.py revisa la estructura (que haya predicciones, retos, citas…). Este script revisa
que funcionen y que enseñen bien:

  Errores (hay que corregirlos):
  - errores de JavaScript en cualquier momento del recorrido;
  - una predicción cuyo resultado se ve antes de contestar (no está borroso ni oculto);
  - una predicción que no muestra su veredicto, o «Volver a predecir» que no funciona;
  - una ayuda «Explícamelo paso a paso» que no llega a la respuesta;
  - un diagrama, simulador o ejercicio que no cambia nada al tocarlo;
  - una animación sin controles o cuyo «Paso a paso ›» no avanza la narración;
  - flashcards que no se voltean o no cuentan «Lo sabía»;
  - un reto cuyo id no aparece en ningún forja.reto(…) del JS (nunca se podría cumplir).

  Advertencias (revísalas con criterio):
  - el texto de la opción correcta aparece a la vista ANTES de la predicción (posible fuga);
  - la opción correcta es mucho más larga que las demás;
  - el primer paso de una ayuda ya contiene la respuesta;
  - texto con contraste insuficiente (WCAG AA: 4.5:1, o 3:1 en texto grande);
  - párrafos de más de 90 palabras (muro de texto);
  - retos que el recorrido automático no cumplió (normal si piden algo específico: compruébalos a mano).

Fugas que el texto no delata (un dibujo que ya muestra el resultado): el script guarda en
<FORJA_SALIDA>/forja-prueba/<carpeta>/ (/tmp por omisión; ver .env.example) antes-<predicción>.png lo que se ve antes de cada pregunta, para revisarlo
con Read. En las guías anteriores hubo 4 fugas así; ninguna se habría encontrado comparando texto.

Código de salida: 0 sin errores, 1 con errores, 2 si no se pudo correr.
"""
import re
import shutil
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import _config  # noqa: E402  (lee .env)

MAX_PALABRAS_PARRAFO = 90

JS_OBSERVAR = """
(sel) => {
  const el = document.querySelector(sel);
  window.__cambios = 0;
  if (window.__obs) window.__obs.disconnect();
  window.__obs = new MutationObserver(m => { window.__cambios += m.length; });
  window.__obs.observe(el || document.body, { subtree: true, childList: true, attributes: true, characterData: true });
}
"""

JS_OCULTO = """
(id) => {
  const objetivos = [...document.querySelectorAll(`[data-tras-prediccion="${id}"]`)];
  return objetivos.map(o => {
    const cs = getComputedStyle(o);
    const r = o.getBoundingClientRect();
    const oculto = cs.display === 'none' || cs.visibility === 'hidden' || +cs.opacity < 0.2
      || /blur\\(/.test(cs.filter) || o.hidden || r.height === 0 || !!o.closest('[hidden]');
    return { oculto, revelado: o.classList.contains('revelado'), texto: (o.innerText || '').slice(0, 60) };
  });
}
"""

# Texto visible antes de un elemento (en orden del documento), sin contar lo que está oculto.
JS_TEXTO_ANTES = """
(id) => {
  const p = document.getElementById(id);
  const caminante = document.createTreeWalker(document.body, NodeFilter.SHOW_TEXT);
  let txt = '';
  while (caminante.nextNode()) {
    const n = caminante.currentNode;
    if (p.compareDocumentPosition(n) & Node.DOCUMENT_POSITION_FOLLOWING) break;
    const el = n.parentElement;
    if (!el || el.closest('script, style, title, [hidden], [data-tras-prediccion], .forja-uso, nav')) continue;
    const cs = getComputedStyle(el);
    if (cs.display === 'none' || cs.visibility === 'hidden' || /blur\\(/.test(cs.filter)) continue;
    txt += ' ' + n.textContent;
  }
  return txt.replace(/\\s+/g, ' ').toLowerCase();
}
"""

JS_CONTRASTE = """
() => {
  const lum = c => { const [r, g, b] = c.map(v => { v /= 255; return v <= .03928 ? v / 12.92 : ((v + .055) / 1.055) ** 2.4; });
    return .2126 * r + .7152 * g + .0722 * b; };
  const rgba = s => { const m = s.match(/rgba?\\(([^)]+)\\)/); if (!m) return null;
    const p = m[1].split(/[ ,\\/]+/).filter(Boolean).map(Number); return [p[0], p[1], p[2], p.length > 3 ? p[3] : 1]; };
  const fondo = el => {
    let capas = [];
    for (let e = el; e; e = e.parentElement) {
      const c = rgba(getComputedStyle(e).backgroundColor);
      if (c && c[3] > 0) { capas.push(c); if (c[3] >= 1) break; }
      if (getComputedStyle(e).backgroundImage !== 'none' && !capas.length) return null;  // imagen o degradado: no se puede medir
    }
    let res = [255, 255, 255];
    for (const c of capas.reverse()) res = res.map((v, i) => v * (1 - c[3]) + c[i] * c[3]);
    return res;
  };
  const malos = [];
  const vistos = new Set();
  for (const el of document.querySelectorAll('main p, main li, main h1, main h2, main h3, main label, main button, main td, main th, main figcaption, main small')) {
    if (!el.innerText || !el.innerText.trim() || el.closest('[hidden], [data-tras-prediccion]')) continue;
    const cs = getComputedStyle(el);
    if (cs.visibility === 'hidden' || +cs.opacity < .5 || el.getClientRects().length === 0) continue;
    const c = rgba(cs.color), f = fondo(el);
    if (!c || !f) continue;
    const col = c.slice(0, 3).map((v, i) => v * c[3] + f[i] * (1 - c[3]));
    const [a, b] = [lum(col), lum(f)].sort((x, y) => y - x);
    const ratio = (a + .05) / (b + .05);
    const px = parseFloat(cs.fontSize), grande = px >= 24 || (px >= 18.66 && +cs.fontWeight >= 700);
    const minimo = grande ? 3 : 4.5;
    if (ratio < minimo) {
      const sec = el.closest('section[id]');
      const clave = (sec ? sec.id : '') + el.tagName + el.className;
      if (vistos.has(clave)) continue;
      vistos.add(clave);
      malos.push(`#${sec ? sec.id : '?'} ${el.tagName.toLowerCase()}${el.className ? '.' + String(el.className).split(' ')[0] : ''} ` +
        `«${el.innerText.trim().slice(0, 40)}» ${ratio.toFixed(1)}:1 (mínimo ${minimo}:1)`);
    }
  }
  return malos;
}
"""




def main() -> int:
    args = [a for a in sys.argv[1:] if not a.startswith("--")]
    celular = "--celular" in sys.argv
    if len(args) != 1:
        print(__doc__)
        return 2
    guia = Path(args[0]).resolve()
    if not guia.is_file():
        print(f"No existe: {guia}")
        return 2
    try:
        from playwright.sync_api import sync_playwright
    except ImportError:
        print("Falta Playwright: pip install playwright && python3 -m playwright install chromium")
        return 2

    html = guia.read_text(encoding="utf-8")
    salida = _config.salida("forja-prueba") / guia.parent.name
    shutil.rmtree(salida, ignore_errors=True)
    salida.mkdir(parents=True)
    errores, avisos, info = [], [], []
    js_errores = []

    # Retos que ningún código puede cumplir (estático)
    ids_reto = set(re.findall(r'data-reto="([^"]+)"', html))
    llamados = set(re.findall(r"""reto\(\s*['"`]([^'"`]+)['"`]\s*\)""", html))
    dinamicos = re.search(r"reto\(\s*[a-zA-Z_$][\w$.]*\s*\)", re.sub(r"reto\(id\)", "", html))
    sin_llamada = sorted(ids_reto - llamados)
    if sin_llamada and not dinamicos:
        errores.append(f"Retos que ningún forja.reto(…) cumple: {sin_llamada}")
    elif sin_llamada:
        avisos.append(f"Retos sin forja.reto('id') literal (se cumplen con un id calculado; compruébalos): {sin_llamada}")

    ejecutable = _config.navegador()
    with sync_playwright() as p:
        nav = p.chromium.launch(executable_path=ejecutable, args=["--no-sandbox"]) if ejecutable else p.chromium.launch()
        vp = {"width": _config.ancho_movil(), "height": 844} if celular else {"width": 1280, "height": 900}
        ctx = nav.new_context(viewport=vp)
        pag = ctx.new_page()
        pag.on("pageerror", lambda e: js_errores.append(str(e)))
        pag.set_default_timeout(3000)

        def mostrar(loc):
            """Lleva el elemento a la vista; False si está oculto (detrás de otra acción)."""
            try:
                if not loc.is_visible():
                    return False
                loc.scroll_into_view_if_needed(timeout=1500)
                return True
            except Exception:
                return False
        pag.goto(guia.as_uri())
        pag.wait_for_timeout(500)

        def cambio(selector, accion, espera=250):
            pag.evaluate(JS_OBSERVAR, selector)
            accion()
            pag.wait_for_timeout(espera)
            return pag.evaluate("() => window.__cambios")

        # 1. Predicciones
        preds = pag.evaluate("() => [...document.querySelectorAll('[data-prediccion][data-correcta]')].map(p => p.id || p.dataset.prediccion).filter(Boolean)")
        pendientes_pred = []

        def probar_prediccion(pid):
            caja = pag.locator(f'[id="{pid}"][data-prediccion], [data-prediccion="{pid}"]').first
            mostrar(caja)
            correcta = caja.get_attribute("data-correcta")
            botones = caja.locator("[data-opcion]")
            if botones.count() < 2:
                return
            if not caja.is_visible():
                pendientes_pred.append(pid)
                return
            # Captura de lo que se ve ANTES de contestar, para revisar fugas que el texto no delata
            # (un dibujo que ya muestra el resultado). Ver «Fugas» en el docstring.
            try:
                sec = caja.locator("xpath=ancestor::section[1]")
                sec.screenshot(path=str(salida / f"antes-{pid}.png"))
            except Exception:
                pass
            # Dibujos o tablas a la vista después de la pregunta, en la misma sección, que no esperan a la respuesta
            sueltos = pag.evaluate("""(id) => {
              const p = document.getElementById(id), sec = p.closest('section');
              return [...sec.querySelectorAll('svg, table, figure, pre')].filter(e =>
                (p.compareDocumentPosition(e) & Node.DOCUMENT_POSITION_FOLLOWING) && !p.contains(e)
                && !e.closest('[data-tras-prediccion], [data-prediccion], .forja-uso, [hidden]') && e.getBoundingClientRect().height > 60
                && !e.parentElement.closest('svg, figure, table'))
                .map(e => (e.getAttribute('aria-label') || e.querySelector('title')?.textContent || e.tagName.toLowerCase()).slice(0, 50));
            }""", pid)
            if sueltos:
                avisos.append(f"{pid}: después de la pregunta se ven sin contestar: {sueltos[:3]}. "
                              f"Si muestran la respuesta, ponlos detrás de la predicción (mira antes-{pid}.png)")
            # ¿El resultado está oculto antes de contestar?
            for o in pag.evaluate(JS_OCULTO, pid):
                if not o["oculto"]:
                    errores.append(f"{pid}: su resultado se ve antes de contestar: «{o['texto']}…»")
            # ¿La opción correcta destaca por su largo?
            largos = {b.get_attribute("data-opcion"): len(b.inner_text().strip()) for b in botones.all()}
            otros = [n for k, n in largos.items() if k != correcta]
            if otros and largos.get(correcta, 0) > 1.6 * (sum(otros) / len(otros)) and largos.get(correcta, 0) - max(otros) > 12:
                avisos.append(f"{pid}: la opción correcta es mucho más larga que las demás (se adivina por eso)")
            # ¿La opción correcta ya se lee antes de la pregunta?
            txt_correcta = caja.locator(f'[data-opcion="{correcta}"]').inner_text().strip().lower()
            if len(txt_correcta) >= 12 and txt_correcta in pag.evaluate(JS_TEXTO_ANTES, pid):
                avisos.append(f"{pid}: el texto de la respuesta correcta («{txt_correcta[:40]}») ya aparece antes de la pregunta")
            # Ayuda
            ayuda = pag.locator(f'[data-ayuda="{pid}"] .ayuda-abrir, [id="{pid}"] .ayuda-abrir').first
            if ayuda.count():
                ayuda.click()
                pag.wait_for_timeout(150)
                cont = ayuda.locator("xpath=ancestor::*[contains(@class,'ayuda-ui')][1]")
                primer = cont.locator("li:visible").first
                if primer.count() and len(txt_correcta) >= 6 and txt_correcta in primer.inner_text().lower():
                    avisos.append(f"{pid}: el primer paso de la ayuda ya dice la respuesta")
                for _ in range(8):
                    sig = cont.locator(".ayuda-siguiente:visible")
                    if not sig.count():
                        break
                    sig.first.click()
                    pag.wait_for_timeout(80)
                if not cont.locator("li.respuesta:visible").count():
                    errores.append(f"{pid}: la ayuda paso a paso no llega a la respuesta")
                cerrar = cont.locator(".ayuda-cerrar:visible")
                if cerrar.count():
                    cerrar.first.click()
            # Contestar mal, volver a predecir, contestar bien
            incorrecta = [b for b in botones.all() if b.get_attribute("data-opcion") != correcta][0]
            incorrecta.click()
            pag.wait_for_timeout(250)
            ver = caja.locator(".veredicto")
            if not ver.count() or not ver.first.is_visible():
                errores.append(f"{pid}: al contestar no aparece el veredicto")
                return
            if any(not o["revelado"] for o in pag.evaluate(JS_OCULTO, pid)):
                errores.append(f"{pid}: al contestar, el resultado sigue oculto")
            reh = ver.locator(".rehacer")
            if reh.count():
                reh.first.click()
                pag.wait_for_timeout(150)
                if not caja.locator(f'[data-opcion="{correcta}"]').is_enabled():
                    errores.append(f"{pid}: «Volver a predecir» no reactiva las opciones")
                    return
            caja.locator(f'[data-opcion="{correcta}"]').click()
            pag.wait_for_timeout(250)
            if "Acertaste" not in ver.first.inner_text():
                errores.append(f"{pid}: contestar la opción correcta no dice «Acertaste»")
        for pid in preds:
            try:
                probar_prediccion(pid)
            except Exception as e:
                avisos.append(f"{pid}: no se pudo recorrer automáticamente ({str(e).splitlines()[0][:90]})")
        info.append(f"{len(preds)} predicciones recorridas")

        # 2. Diagramas: cada pieza clicable cambia algo
        nodos = pag.locator("[data-interaccion='diagrama'] [data-nodo]")
        muertos = []
        for i in range(nodos.count()):
            n = nodos.nth(i)
            if not mostrar(n):
                continue
            try:
                c = cambio("main", lambda: n.click(force=True))
            except Exception:
                continue
            if c == 0:
                muertos.append(n.get_attribute("data-nodo"))
        if muertos:
            errores.append(f"Piezas de diagrama que no hacen nada al tocarlas: {muertos[:8]}")
        info.append(f"{nodos.count()} piezas de diagrama tocadas")

        # 3. Simuladores y ejercicios: cada control cambia algo
        # Pasos guiados: contestar la predicción visible (bien) o pulsar «Siguiente», hasta el final
        for caja in pag.locator("[data-interaccion='pasos']").all():
            if not mostrar(caja):
                continue
            nombre = caja.get_attribute("id") or "pasos"
            total = 0
            for _ in range(20):
                hecho = False
                for pr in caja.locator("[data-prediccion][data-correcta]").all():
                    if pr.is_visible():
                        op = pr.locator(f'[data-opcion="{pr.get_attribute("data-correcta")}"]')
                        if op.count() and op.is_enabled():
                            total += cambio("main", lambda op=op: op.click())
                            pid = pr.get_attribute("id")
                            if pid in pendientes_pred:
                                pendientes_pred.remove(pid)
                            hecho = True
                            break
                if hecho:
                    continue
                libres = [b for b in caja.locator("button:visible").all() if b.is_enabled() and not b.locator(
                    "xpath=ancestor-or-self::*[@data-prediccion or contains(@class,'ayuda') or contains(@class,'anima-ctl')]").count()]
                prim = [b for b in libres if "primario" in (b.get_attribute("class") or "")]
                actual = [i for i, b in enumerate(libres) if b.get_attribute("aria-current") in ("step", "true")]
                if prim:
                    boton = prim[-1]
                elif actual and actual[0] + 1 < len(libres):
                    boton = libres[actual[0] + 1]   # pestañas de pasos: la siguiente a la actual
                elif libres and not actual:
                    boton = libres[-1]
                else:
                    break
                c = cambio("main", lambda: boton.click())
                total += c
                if c == 0:
                    break
            if total == 0:
                errores.append(f"pasos «{nombre}»: sus controles no cambian nada")

        for tipo in ("simulador", "otra"):
            cajas = pag.locator(f"[data-interaccion='{tipo}']")
            for k in range(cajas.count()):
                caja = cajas.nth(k)
                if not caja.is_visible():
                    continue
                mostrar(caja)
                nombre = caja.get_attribute("id") or f"{tipo} {k + 1}"
                total = 0
                for r in caja.locator("input[type=range]:visible").all():
                    mn, mx = r.get_attribute("min") or "0", r.get_attribute("max") or "100"
                    for v in (mn, mx):
                        total += cambio("main", lambda r=r, v=v: r.evaluate(
                            "(e, v) => { e.value = v; e.dispatchEvent(new Event('input', {bubbles: true})); "
                            "e.dispatchEvent(new Event('change', {bubbles: true})); }", v))
                botones = [b for b in caja.locator("button:visible, [role=button]:visible, input[type=checkbox]:visible, input[type=radio]:visible, [tabindex='0']:visible, select:visible").all()
                           if not b.locator("xpath=ancestor-or-self::*[@data-prediccion or contains(@class,'ayuda') or contains(@class,'anima-ctl')]").count()]
                for b in botones[:12]:
                    try:
                        if b.is_enabled():
                            total += cambio("main", lambda b=b: b.click(timeout=1500))
                    except Exception:
                        pass
                if caja.get_attribute("data-prediccion") is not None or (
                        not botones and not caja.locator("input[type=range]").count()
                        and caja.locator("[data-prediccion]").count()):
                    continue  # solo contiene una predicción: ya se probó como tal
                if total == 0 and (botones or caja.locator("input[type=range]").count()):
                    errores.append(f"{tipo} «{nombre}»: sus controles no cambian nada")
                elif total == 0:
                    avisos.append(f"{tipo} «{nombre}»: no se encontró ningún control para probarlo")

        # Segunda pasada: predicciones que aparecieron después de otra acción (pasos guiados)
        for pid in pendientes_pred[:]:
            try:
                if pag.locator(f'[id="{pid}"]').first.is_visible():
                    pendientes_pred.remove(pid)
                    probar_prediccion(pid)
            except Exception as e:
                avisos.append(f"{pid}: no se pudo recorrer automáticamente ({str(e).splitlines()[0][:90]})")
        for pid in pendientes_pred:
            avisos.append(f"{pid}: nunca se hizo visible en el recorrido (¿depende de una acción concreta?); pruébala a mano")

        # 4. Animaciones
        def probar_animacion(k, a):
            nombre = a.get_attribute("id") or f"animación {k + 1}"
            mostrar(a)
            if not a.locator(".anima-ctl").count():
                errores.append(f"{nombre}: sin controles (¿no llama a forja.animar?)")
                return
            fase = a.locator(".anima-fase")
            antes = fase.inner_text() if fase.count() else ""
            paso = a.locator(".anima-paso")
            textos = {antes}
            for _ in range(6):
                paso.click()
                pag.wait_for_timeout(120)
                if fase.count():
                    textos.add(fase.inner_text())
            if fase.count() and len(textos) < 2:
                errores.append(f"{nombre}: «Paso a paso ›» no cambia la narración (.anima-fase)")
            elif not fase.count():
                avisos.append(f"{nombre}: sin narración .anima-fase")

        for k, a in enumerate(pag.locator("[data-anima]").all()):
            try:
                probar_animacion(k, a)
            except Exception as e:
                avisos.append(f"animación {k + 1}: no se pudo recorrer ({str(e).splitlines()[0][:90]})")

        # 5. Flashcards
        fc = pag.locator("[data-forja-flashcards]")
        if fc.count():
            mostrar(fc.first)
            t = fc.locator(".fc-tarjeta")
            if t.count():
                t.first.click()
                pag.wait_for_timeout(120)
                if not fc.locator(".fc-sabia").count():
                    errores.append("Flashcards: al tocar la tarjeta no se voltea")
                else:
                    antes = fc.locator(".fc-progreso").inner_text()
                    fc.locator(".fc-sabia").click()
                    pag.wait_for_timeout(120)
                    if fc.locator(".fc-progreso").count() and fc.locator(".fc-progreso").inner_text() == antes:
                        errores.append("Flashcards: «Lo sabía» no cambia el conteo")

        # 6. Retos cumplidos por el recorrido
        cumplidos = pag.evaluate("() => [...document.querySelectorAll('[data-reto]')].filter(r => r.classList.contains('logrado') || r.getAttribute('aria-checked') === 'true' || r.querySelector('input:checked')).map(r => r.dataset.reto)")
        pendientes = sorted(ids_reto - set(cumplidos))
        info.append(f"retos cumplidos por el recorrido: {len(set(cumplidos))} de {len(ids_reto)}")
        if pendientes:
            avisos.append(f"Retos que el recorrido automático no cumplió (compruébalos a mano): {pendientes}")

        # 7. Contraste y muros de texto
        for m in pag.evaluate(JS_CONTRASTE)[:10]:
            avisos.append(f"Contraste bajo: {m}")
        largos = pag.evaluate(f"""() => [...document.querySelectorAll('main p')].filter(p => !p.closest('[data-forja-flashcards], #fuentes'))
            .map(p => [p.closest('section[id]')?.id || '?', p.innerText.trim().split(/\\s+/).length])
            .filter(([, n]) => n > {MAX_PALABRAS_PARRAFO})""")
        for sec, n in largos[:6]:
            avisos.append(f"Muro de texto en #{sec}: un párrafo de {n} palabras (divídelo, o cámbialo por una lista o un dibujo)")
        nav.close()

    for e in dict.fromkeys(js_errores):
        errores.insert(0, f"Error de JavaScript: {e[:200]}")

    print(f"Recorrido de {guia.parent.name} ({'celular' if celular else 'escritorio'}): " + "; ".join(info))
    if errores:
        print("ERRORES:")
        for e in errores:
            print(f"  ✗ {e}")
    if avisos:
        print("ADVERTENCIAS:")
        for a in avisos:
            print(f"  ! {a}")
    if not errores and not avisos:
        print("  ✓ Todo funciona")
    print(f"\nFugas: en {salida}/antes-<predicción>.png está lo que se ve antes de cada pregunta. "
          "Ábrelas con Read (o pídeselo a un subagente que no conozca las respuestas) y comprueba que "
          "ningún dibujo, tabla o texto ya muestre la respuesta.")
    return 1 if errores else 0


if __name__ == "__main__":
    sys.exit(main())
