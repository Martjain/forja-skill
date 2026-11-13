"""Ayudante para generar ilustraciones SVG de forja con geometría calculada y comprobada.

Uso en tu script generador:

    import sys; sys.path.insert(0, "<CLAUDE_SKILL_DIR>/scripts")
    from svg_kit import Lienzo, Plano, linea, W_C, W_D, W_G

    lz = Lienzo("pendiente", 480, 320)          # viewBox 0 0 480 320
    P = Plano(-1, 5, -1, 9, L=48, R=456, T=24, B=288)   # mundo -> viewBox
    partes = [P.rejilla(range(0, 6), range(0, 10, 2)), P.ejes("pend"),
              P.marcas(lz, range(1, 6), range(2, 10, 2)),
              f'<path d="{P.curva(lambda x: x * x)}" stroke="var(--azul)" stroke-width="{W_C}" fill="none"/>',
              lz.etiqueta((P.X(1), P.Y(1)), [(P.X(1) + 30, P.Y(1) - 40)], "Punto P", "aquí medimos", "var(--tinta)")]
    lz.comprobar()                               # assert: nada sale del viewBox ni choca
    svg = lz.svg("".join(partes), titulo="Pendiente de y = x²")

Qué comprueba:
  - El texto que NO es etiqueta (ejes, valores) mide al menos `lz.letra_min` unidades,
    que equivale a 11 px cuando el SVG se ve a ANCHO_MOVIL px en el celular.
  - Las etiquetas (g.etiqueta) se miden contra el viewBox y entre sí, pero no contra el
    mínimo: en el celular el núcleo las cambia por números + leyenda.
  - Ningún texto sale del viewBox ni choca con otro.
El ancho del texto es una estimación (0.56 em por carácter; 0.6 en monoespaciada), suficiente
para detectar choques. La revisión final la hace revisar_ilustraciones.py con el render real.
"""
import math

W_C, W_D, W_G = 2.5, 1.25, 1      # contorno, detalle, guías y cotas
ANCHO_MOVIL = 350                  # ancho real aproximado de un SVG a todo lo ancho en un celular de 390 px
LETRA_MIN_PX = 11


def r1(v):
    """Redondea a 1 decimal sin ceros sobrantes ni '-0'."""
    s = f"{v:.1f}".rstrip("0").rstrip(".")
    return "0" if s in ("-0", "") else s


def ancho_texto(txt, size, mono=False):
    return len(txt) * size * (0.6 if mono else 0.56)


class Lienzo:
    """Un SVG que registra la caja de cada texto para comprobar márgenes y choques."""

    def __init__(self, nombre, w, h, ancho_movil=ANCHO_MOVIL):
        self.nombre, self.w, self.h = nombre, w, h
        # Letra mínima en unidades del viewBox para que se vea de 11 px en el celular.
        self.letra_min = math.ceil(LETRA_MIN_PX * w / ancho_movil * 2) / 2
        self.cajas = []   # (x0, y0, x1, y1, texto)

    def _caja(self, x, y, txt, size, anchor, mono):
        a = ancho_texto(txt, size, mono)
        x0 = x - a if anchor == "end" else x - a / 2 if anchor == "middle" else x
        self.cajas.append((x0, y - size * 0.74, x0 + a, y + size * 0.24, txt))

    def texto(self, x, y, txt, size=None, color="var(--tinta)", anchor="start", mono=False, extra=""):
        """Texto que se ve también en el celular (ejes, valores). Por omisión, del tamaño mínimo."""
        size = size or self.letra_min
        assert size >= self.letra_min - 1e-9, \
            f"{self.nombre}: '{txt}' mide {size} y el mínimo en este viewBox es {self.letra_min}"
        self._caja(x, y, txt, size, anchor, mono)
        a = f' text-anchor="{anchor}"' if anchor != "start" else ""
        m = ' font-family="var(--f-codigo)"' if mono else ""
        return f'<text x="{r1(x)}" y="{r1(y)}" font-size="{size}" fill="{color}"{a}{m}{extra}>{txt}</text>'

    def etiqueta(self, punto, ruta, titulo, sub, color, anchor="start"):
        """Etiqueta forja: punto sobre la pieza, guía de 1 px por `ruta`, título 13.5 + frase 12.

        punto: (x, y) sobre la pieza. ruta: puntos de la guía; el texto va junto al último.
        """
        px, py = punto
        d = f"M{r1(px)} {r1(py)}" + "".join(f" L{r1(x)} {r1(y)}" for x, y in ruta)
        ex, ey = ruta[-1]
        tx = ex + 6 if anchor == "start" else ex - 6
        partes = [f'<g class="etiqueta" data-punto="{r1(px)} {r1(py)}">',
                  f'<path d="{d}" stroke="{color}" stroke-width="{W_G}" fill="none" opacity=".7"/>',
                  f'<circle cx="{r1(px)}" cy="{r1(py)}" r="3" fill="{color}"/>']
        a = f' text-anchor="{anchor}"' if anchor != "start" else ""
        for txt, size, y, extra in ((titulo, 13.5, ey + 4.5, f' font-weight="600" fill="{color}"'),
                                    (sub, 12, ey + 21.5, ' fill="var(--tinta)" opacity=".75"')):
            if not txt:
                continue
            self._caja(tx, y, txt, size, anchor, False)
            partes.append(f'<text x="{r1(tx)}" y="{r1(y)}" font-size="{size}"{extra}{a}>{txt}</text>')
        partes.append("</g>")
        return "".join(partes)

    def comprobar(self, margen=2):
        for (x0, y0, x1, y1, t) in self.cajas:
            assert x0 >= margen and x1 <= self.w - margen and y0 >= margen and y1 <= self.h - margen, \
                f"{self.nombre}: '{t}' sale del viewBox ({x0:.0f},{y0:.0f})-({x1:.0f},{y1:.0f})"
        for i, a in enumerate(self.cajas):
            for b in self.cajas[i + 1:]:
                ox = min(a[2], b[2]) - max(a[0], b[0])
                oy = min(a[3], b[3]) - max(a[1], b[1])
                assert not (ox > 1 and oy > 1), f"{self.nombre}: '{a[4]}' choca con '{b[4]}'"

    def svg(self, contenido, titulo, id_svg=None, defs=""):
        i = f' id="{id_svg}"' if id_svg else ""
        d = f"<defs>{defs}</defs>" if defs else ""
        return (f'<svg{i} viewBox="0 0 {self.w} {self.h}" role="img" xmlns="http://www.w3.org/2000/svg">'
                f"<title>{titulo}</title>{d}{contenido}</svg>")


class Plano:
    """Convierte coordenadas del mundo (x0..x1, y0..y1) a la caja L..R, T..B del viewBox."""

    def __init__(self, x0, x1, y0, y1, L, R, T, B):
        self.x0, self.x1, self.y0, self.y1 = x0, x1, y0, y1
        self.L, self.R, self.T, self.B = L, R, T, B

    def X(self, x):
        return self.L + (x - self.x0) / (self.x1 - self.x0) * (self.R - self.L)

    def Y(self, y):
        return self.B - (y - self.y0) / (self.y1 - self.y0) * (self.B - self.T)

    def curva(self, f, n=200, xa=None, xb=None):
        """Path de la función real muestreada en n tramos (corta donde sale del rango y)."""
        xa = self.x0 if xa is None else xa
        xb = self.x1 if xb is None else xb
        d, dentro = [], False
        for i in range(n + 1):
            x = xa + (xb - xa) * i / n
            y = f(x)
            ok = self.y0 - 1 <= y <= self.y1 + 1
            if ok:
                d.append(("L" if dentro else "M") + f"{self.X(x):.1f},{self.Y(y):.1f}")
            dentro = ok
        assert len(d) > 10, "la curva casi no entra en el plano"
        return " ".join(d)

    def recta(self, xa, ya, m):
        """Recta por (xa, ya) con pendiente m de borde a borde: (x1, y1, x2, y2). Recórtala con clipPath."""
        return (self.X(self.x0), self.Y(ya + m * (self.x0 - xa)), self.X(self.x1), self.Y(ya + m * (self.x1 - xa)))

    def en_curva(self, f, x, px, py, tol=0.05):
        assert abs(self.X(x) - px) < tol and abs(self.Y(f(x)) - py) < tol, "el punto no está sobre la curva"

    def rejilla(self, xs, ys, color="var(--rejilla, rgba(0,0,0,.08))"):
        d = "".join(f"M{r1(self.X(x))} {r1(self.T)}V{r1(self.B)}" for x in xs)
        d += "".join(f"M{r1(self.L)} {r1(self.Y(y))}H{r1(self.R)}" for y in ys)
        return f'<path d="{d}" stroke="{color}" stroke-width="{W_G}" fill="none"/>'

    def ejes(self, prefijo, color="var(--tinta-suave)"):
        """Ejes con punta de flecha. `prefijo` evita ids duplicados entre SVG (incluye su <marker>)."""
        mk = (f'<marker id="{prefijo}-pta" viewBox="0 0 10 10" refX="6" refY="5" markerWidth="5" markerHeight="5" '
              f'orient="auto"><path d="M1 1 L8 5 L1 9 Z" style="fill:{color}"/></marker>')
        out = [f"<defs>{mk}</defs>"]
        if self.y0 <= 0 <= self.y1:
            y = self.Y(0)
            out.append(f'<line x1="{r1(self.L)}" y1="{r1(y)}" x2="{r1(self.R + 4)}" y2="{r1(y)}" stroke="{color}" '
                       f'stroke-width="{W_D}" marker-end="url(#{prefijo}-pta)"/>')
        if self.x0 <= 0 <= self.x1:
            x = self.X(0)
            out.append(f'<line x1="{r1(x)}" y1="{r1(self.B)}" x2="{r1(x)}" y2="{r1(self.T - 4)}" stroke="{color}" '
                       f'stroke-width="{W_D}" marker-end="url(#{prefijo}-pta)"/>')
        return "".join(out)

    def marcas(self, lz, xs, ys, size=None, color="var(--tinta-suave)"):
        """Marcas de 6 unidades sobre los ejes y sus números, del tamaño mínimo legible."""
        size = size or lz.letra_min
        y0 = self.Y(0) if self.y0 <= 0 <= self.y1 else self.B
        x0 = self.X(0) if self.x0 <= 0 <= self.x1 else self.L
        d, txt = "", []
        for x in xs:
            d += f"M{r1(self.X(x))} {r1(y0 - 3)}V{r1(y0 + 3)}"
            txt.append(lz.texto(self.X(x), y0 + size + 4, r1(x).replace("-", "−"), size, color, "middle", mono=True))
        for y in ys:
            d += f"M{r1(x0 - 3)} {r1(self.Y(y))}H{r1(x0 + 3)}"
            txt.append(lz.texto(x0 - 7, self.Y(y) + size * 0.35, r1(y).replace("-", "−"), size, color, "end", mono=True))
        return f'<path d="{d}" stroke="{color}" stroke-width="{W_D}" fill="none"/>' + "".join(txt)


def linea(x1, y1, x2, y2, color, w=W_C, extra=""):
    return f'<line x1="{r1(x1)}" y1="{r1(y1)}" x2="{r1(x2)}" y2="{r1(y2)}" stroke="{color}" stroke-width="{w}"{extra}/>'


def punto(x, y, color, r=4.5):
    """Punto de una gráfica: relleno de color con borde del fondo para que se separe de las líneas."""
    return f'<circle cx="{r1(x)}" cy="{r1(y)}" r="{r}" fill="{color}" stroke="var(--fondo)" stroke-width="{W_D}"/>'


def biela_manivela(cx, cy, r, L, a, lado=-1):
    """Mecanismo biela-manivela: (px, py) perno de la manivela, (wx, wy) perno del pistón (igual que forja.kit)."""
    px, py = cx + r * math.cos(a), cy + r * math.sin(a)
    return px, py, px + lado * math.sqrt(L * L - (py - cy) ** 2), cy


if __name__ == "__main__":
    # Prueba rápida
    lz = Lienzo("prueba", 480, 320)
    P = Plano(-1, 5, -1, 9, L=48, R=456, T=24, B=288)
    partes = [P.rejilla(range(0, 6), range(0, 10, 2)), P.ejes("prueba"), P.marcas(lz, range(1, 6), range(2, 10, 2)),
              f'<path d="{P.curva(lambda x: x * x)}" stroke="var(--azul)" stroke-width="{W_C}" fill="none"/>',
              lz.etiqueta((P.X(2), P.Y(4)), [(P.X(2) - 40, P.Y(4) - 50)], "Punto P", "aquí medimos", "black", "end")]
    lz.comprobar()
    print(f"letra mínima: {lz.letra_min} unidades ·", len(lz.svg("".join(partes), "prueba")), "bytes · ok")
