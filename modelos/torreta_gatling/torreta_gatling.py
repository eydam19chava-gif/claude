"""Torreta 10 - Gatling / minigun dorada (DPS altísimo). 6 cañones rotativos. Acento dorado.

Objetos: Base (pedestal blindado), Pivot (cuerpo + cajas de munición, gira en Z),
Barrel (soporte de elevación), Spinner (los 6 cañones, giran en X al disparar).
"""
import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))
from lib_torretas import *  # noqa: E402,F403

OUT = os.path.dirname(os.path.abspath(__file__))
reset()
P = palette(armor=(0.08, 0.08, 0.09), armor_light=(0.18, 0.18, 0.2), neon=(1.0, 0.75, 0.15))
A, A2, MT, DK, LG, NE, BR = P["ARMOR"], P["ARMOR2"], P["METAL"], P["DARK"], P["LEG"], P["NEON"], P["BRASS"]
GOLD = material("Oro", (1.0, 0.72, 0.2), 1.0, 0.22)

# ---------------------------------------------------------------- BASE
base = []
base.append(cyl(1.25, 0.25, (0, 0, 0.125), A2, verts=12, bevel=0.04))
base.append(cyl(1.1, 0.4, (0, 0, 0.45), A, verts=12, bevel=0.04, r2=0.8))
base.append(cyl(0.82, 0.05, (0, 0, 0.66), GOLD, verts=12, bevel=0))
base.append(cyl(0.6, 0.5, (0, 0, 0.9), A2, verts=12, bevel=0.03))
for i in range(6):
    a = math.radians(i * 60)
    d = Vector((math.cos(a), math.sin(a), 0))
    base.append(box((0.25, 0.35, 0.7), d * 0.95 + Vector((0, 0, 0.5)), A, rot=(0, -0.35, a), bevel=0.04))
    base.append(box((0.05, 0.12, 0.35), d * 1.08 + Vector((0, 0, 0.55)), NE, rot=(0, -0.35, a), bevel=0))
    base.append(sphere(0.06, d * 1.15 + Vector((0, 0, 0.2)), GOLD, subdiv=1))
Base = join(base, "Base", (0, 0, 0))

# ---------------------------------------------------------------- PIVOT: cuerpo con cajas de munición
PZ = 1.15
CZ = PZ + 0.7
piv = []
piv.append(cyl(0.62, 0.14, (0, 0, PZ + 0.07), GOLD, verts=16))
piv.append(cyl(0.4, 0.35, (0, 0, PZ + 0.3), A2, verts=12))
piv.append(box((1.1, 0.8, 0.65), (-0.2, 0, CZ), A, bevel=0.1))
piv.append(box((0.7, 0.82, 0.08), (-0.2, 0, CZ + 0.2), GOLD, bevel=0))
for s in (-1, 1):
    piv.append(box((0.8, 0.45, 0.55), (-0.3, 0.63 * s, CZ - 0.05), A2, bevel=0.06))    # caja de munición
    piv.append(box((0.6, 0.05, 0.1), (-0.3, 0.86 * s, CZ + 0.05), NE, bevel=0))
    for k in range(6):                                                                # cinta de balas
        x = 0.1 + k * 0.08
        piv.append(box((0.05, 0.1, 0.16), (x, 0.52 * s - 0.03 * k * s, CZ + 0.28 - k * 0.03), BR, bevel=0))
piv.append(box((0.35, 0.5, 0.25), (-0.4, 0, CZ + 0.4), A2, bevel=0.05))               # cúpula de sensores
piv.append(cyl(0.08, 0.06, (-0.22, 0, CZ + 0.42), NE, rot=(0, math.pi / 2, 0), verts=10, bevel=0))
Pivot = join(piv, "Pivot", (0, 0, PZ))

# ---------------------------------------------------------------- BARREL (motor) + SPINNER (6 cañones)
X0 = 0.35
brl = []
brl.append(cyl(0.34, 0.5, (X0 + 0.2, 0, CZ), A2, rot=(0, math.pi / 2, 0), verts=14))
brl.append(cyl(0.3, 0.05, (X0 + 0.47, 0, CZ), GOLD, rot=(0, math.pi / 2, 0), verts=14, bevel=0))
Barrel = join(brl, "Barrel", (X0, 0, CZ))

spn = []
spn.append(cyl(0.08, 1.8, (X0 + 1.4, 0, CZ), DK, rot=(0, math.pi / 2, 0), verts=8))
for x, r in ((X0 + 0.65, 0.3), (X0 + 1.4, 0.28), (X0 + 2.1, 0.3)):                   # abrazaderas
    spn.append(cyl(r, 0.1, (x, 0, CZ), GOLD if x > X0 + 2 else A2, rot=(0, math.pi / 2, 0), verts=12, bevel=0.02))
for i in range(6):
    a = math.radians(i * 60)
    off = Vector((0, math.cos(a), math.sin(a))) * 0.19
    spn.append(cyl(0.065, 1.7, Vector((X0 + 1.4, 0, CZ)) + off, MT, rot=(0, math.pi / 2, 0), verts=8, bevel=0))
    spn.append(cyl(0.035, 0.03, Vector((X0 + 2.26, 0, CZ)) + off, DK, rot=(0, math.pi / 2, 0), verts=6, bevel=0))
Spinner = join(spn, "Spinner", (X0, 0, CZ))

transform([Pivot, Barrel, Spinner], Matrix.Scale(1.1, 4), (0, 0, PZ))
parent(Pivot, Base)
parent(Barrel, Pivot)
parent(Spinner, Barrel)

export(OUT, "torreta_gatling", [Base, Pivot, Barrel, Spinner])
if not os.environ.get("NO_RENDER"):
    render(OUT, target=(0.5, 0, 1.4), dist=0.9)
print("LISTO")
