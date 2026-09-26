"""Torreta 2 - Cañón pesado (artillería de área) sobre orugas. Acento naranja.

Objetos: Base (orugas + chasis), Pivot (torreta blindada, gira en Z), Barrel (doble cañón, eleva en Y).
"""
import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))
from lib_torretas import *  # noqa: E402,F403

OUT = os.path.dirname(os.path.abspath(__file__))
reset()
P = palette(armor=(0.16, 0.17, 0.12), armor_light=(0.28, 0.29, 0.2), neon=(1.0, 0.35, 0.02))
A, A2, MT, DK, LG, NE, HZ = P["ARMOR"], P["ARMOR2"], P["METAL"], P["DARK"], P["LEG"], P["NEON"], P["HAZARD"]

# ---------------------------------------------------------------- BASE: orugas + chasis
base = []
for s in (-1, 1):
    y = 1.05 * s
    base.append(box((3.2, 0.62, 0.62), (0, y, 0.42), DK, bevel=0.12))            # banda de oruga
    for k in range(13):                                                        # tacos de la oruga
        base.append(box((0.1, 0.66, 0.06), (-1.45 + k * 0.242, y, 0.75), LG, bevel=0))
        base.append(box((0.1, 0.66, 0.06), (-1.45 + k * 0.242, y, 0.08), LG, bevel=0))
    for k in range(5):                                                         # ruedas
        base.append(cyl(0.27, 0.66, (-1.2 + k * 0.6, y, 0.42), MT, rot=(math.pi / 2, 0, 0), verts=12))
        base.append(cyl(0.12, 0.7, (-1.2 + k * 0.6, y, 0.42), NE if k == 2 else DK, rot=(math.pi / 2, 0, 0),
                        verts=8, bevel=0))
    base.append(box((3.35, 0.7, 0.16), (0, y, 0.84), A, bevel=0.05))            # guardabarros
    for k in range(6):                                                         # franjas de peligro
        base.append(box((0.14, 0.02, 0.12), (1.0 + k * 0.1, y + 0.36 * s, 0.84), HZ if k % 2 == 0 else DK,
                        rot=(0.5 * s, 0, 0), bevel=0))
base.append(box((2.6, 1.5, 0.55), (0, 0, 0.7), A, bevel=0.08))                   # chasis
base.append(box((0.4, 1.3, 0.4), (1.4, 0, 0.68), A2, rot=(0, 0.5, 0), bevel=0.05))  # frente inclinado
base.append(box((0.3, 1.2, 0.45), (-1.4, 0, 0.72), A2, bevel=0.05))
for s in (-1, 1):                                                              # escapes
    base.append(cyl(0.09, 0.5, (-1.5, 0.4 * s, 1.1), MT, verts=10))
    base.append(cyl(0.11, 0.08, (-1.5, 0.4 * s, 1.36), DK, verts=10))
    base.append(box((0.08, 0.06, 0.2), (1.55, 0.45 * s, 0.85), NE, bevel=0))    # faros
base.append(cyl(1.0, 0.18, (0, 0, 1.05), MT, verts=24))
base.append(cyl(1.02, 0.04, (0, 0, 1.15), NE, verts=24, bevel=0))
Base = join(base, "Base", (0, 0, 0))

# ---------------------------------------------------------------- PIVOT: torreta blindada
PZ = 1.17
TZ = PZ + 0.55
piv = []
piv.append(cyl(0.95, 0.2, (0, 0, PZ + 0.1), DK, verts=24))
piv.append(cyl(1.15, 0.7, (-0.15, 0, TZ), A, verts=8, r2=0.95))                  # casco octogonal
piv.append(cyl(0.95, 0.14, (-0.15, 0, TZ + 0.42), A2, verts=8, r2=0.8))
piv.append(cyl(0.45, 0.25, (-0.45, 0.3, TZ + 0.6), MT, verts=10))              # escotilla
piv.append(cyl(0.35, 0.05, (-0.45, 0.3, TZ + 0.74), DK, verts=10, bevel=0))
piv.append(box((0.5, 0.15, 0.15), (-0.2, -0.35, TZ + 0.56), DK, bevel=0.02))    # periscopio
piv.append(box((0.04, 0.12, 0.08), (0.06, -0.35, TZ + 0.56), NE, bevel=0))
for s in (-1, 1):                                                              # faldones laterales
    piv.append(box((1.4, 0.12, 0.55), (-0.15, 1.02 * s, TZ - 0.05), A2, rot=(0.18 * s, 0, 0), bevel=0.04))
    for k in range(4):
        piv.append(cyl(0.05, 0.05, (-0.65 + k * 0.33, 1.1 * s, TZ + 0.08), MT, rot=(math.pi / 2, 0, 0),
                       verts=6, bevel=0))
    piv.append(box((0.9, 0.04, 0.06), (-0.15, 1.1 * s, TZ - 0.12), NE, rot=(0.18 * s, 0, 0), bevel=0))
    # lanzahumo
    for k in range(3):
        piv.append(cyl(0.07, 0.25, (0.35 - k * 0.14, 0.82 * s, TZ + 0.5), DK, rot=(0.6 * s, 0.4, 0), verts=8))
# caja de munición trasera
piv.append(box((0.7, 1.5, 0.6), (-1.3, 0, TZ + 0.05), A, bevel=0.06))
for k in range(5):
    piv.append(box((0.72, 0.1, 0.62), (-1.3, -0.6 + k * 0.3, TZ + 0.05), DK, bevel=0.02))
piv.append(box((0.04, 1.2, 0.1), (-1.66, 0, TZ + 0.2), NE, bevel=0))
# mantelete
piv.append(box((0.5, 1.2, 0.75), (0.9, 0, TZ), MT, bevel=0.08))
piv.append(box((0.3, 1.25, 0.12), (0.95, 0, TZ - 0.42), HZ, bevel=0.02))
Pivot = join(piv, "Pivot", (0, 0, PZ))

# ---------------------------------------------------------------- BARREL: doble cañón con freno de boca
brl = []
X0 = 1.1
for s in (-1, 1):
    y = 0.3 * s
    brl.append(cyl(0.2, 0.5, (X0 + 0.2, y, TZ), DK, rot=(0, math.pi / 2, 0), verts=12))
    brl.append(cyl(0.16, 2.1, (X0 + 1.35, y, TZ), A, rot=(0, math.pi / 2, 0), verts=12))
    brl.append(cyl(0.19, 0.35, (X0 + 0.9, y, TZ), MT, rot=(0, math.pi / 2, 0), verts=12))   # evacuador
    brl.append(cyl(0.2, 0.06, (X0 + 1.9, y, TZ), NE, rot=(0, math.pi / 2, 0), verts=12, bevel=0))
    brl.append(box((0.5, 0.36, 0.3), (X0 + 2.55, y, TZ), DK, bevel=0.05))                  # freno de boca
    for k in range(3):
        brl.append(box((0.08, 0.4, 0.12), (X0 + 2.4 + k * 0.14, y, TZ), MT, bevel=0))
    brl.append(cyl(0.1, 0.04, (X0 + 2.81, y, TZ), P["DARK"], rot=(0, math.pi / 2, 0), verts=10, bevel=0))
    brl.append(cyl(0.06, 1.2, (X0 + 0.7, y, TZ - 0.24), MT, rot=(0, math.pi / 2, 0), verts=8))  # recuperador
Barrel = join(brl, "Barrel", (X0, 0, TZ))

# cabeza un poco más grande y cañón elevado 8°
transform([Pivot, Barrel], Matrix.Scale(1.1, 4), (0, 0, PZ))
transform([Barrel], Matrix.Rotation(math.radians(-8), 4, "Y"), (X0 * 1.1, 0, PZ + (TZ - PZ) * 1.1))
parent(Pivot, Base)
parent(Barrel, Pivot)

export(OUT, "torreta_canon", [Base, Pivot, Barrel])
if not os.environ.get("NO_RENDER"):
    render(OUT, target=(0.6, 0, 1.3), dist=0.95)
print("LISTO")
