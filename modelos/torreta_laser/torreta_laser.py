"""Torreta 4 - Láser / railgun de energía. Base flotante con aletas y anillo. Acento cian.

Objetos: Base (pedestal + aletas + anillo), Pivot (cuerpo con cristal de energía, gira en Z),
Barrel (emisor con anillos de enfoque y rieles).
"""
import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))
from lib_torretas import *  # noqa: E402,F403

OUT = os.path.dirname(os.path.abspath(__file__))
reset()
P = palette(armor=(0.85, 0.87, 0.9), armor_light=(0.12, 0.14, 0.2), neon=(0.05, 0.85, 1.0))
A, A2, MT, DK, LG, NE = P["ARMOR"], P["ARMOR2"], P["METAL"], P["DARK"], P["LEG"], P["NEON"]
CRYSTAL = material("Cristal", (0.2, 0.9, 1.0), 0.0, 0.05, emission=(0.1, 0.8, 1.0), strength=12)

# ---------------------------------------------------------------- BASE
base = []
base.append(cyl(1.15, 0.2, (0, 0, 0.1), A2, verts=12, bevel=0.04))
base.append(cyl(0.6, 1.0, (0, 0, 0.7), A, verts=12, bevel=0.04, r2=0.42))
base.append(cyl(0.44, 0.08, (0, 0, 1.23), NE, verts=12, bevel=0))
for i in range(4):                                                   # aletas curvas
    a = math.radians(45 + 90 * i)
    d = Vector((math.cos(a), math.sin(a), 0))
    for k, (r0, z0, r1, z1) in enumerate(((0.45, 1.1, 0.95, 0.75), (0.95, 0.75, 1.2, 0.2))):
        base.append(strut(d * r0 + Vector((0, 0, z0)), d * r1 + Vector((0, 0, z1)), 0.12, 0.36, A, bevel=0.04))
    base.append(box((0.3, 0.16, 0.12), d * 1.2 + Vector((0, 0, 0.14)), DK, rot=(0, 0, a), bevel=0.03))
    base.append(strut(d * 0.7 + Vector((0, 0, 0.95)), d * 1.08 + Vector((0, 0, 0.52)), 0.14, 0.05, NE, bevel=0))
# anillo flotante
base.append(torus(1.0, 0.07, (0, 0, 0.55), NE, seg=32, minor=8))
base.append(torus(1.0, 0.1, (0, 0, 0.55), A2, seg=32, minor=6))
Base = join(base, "Base", (0, 0, 0))

# ---------------------------------------------------------------- PIVOT
PZ = 1.27
CZ = PZ + 0.75
piv = []
piv.append(cyl(0.55, 0.14, (0, 0, PZ + 0.07), MT, verts=16))
piv.append(cyl(0.3, 0.4, (0, 0, PZ + 0.34), A2, verts=8))
# cuerpo alargado tipo cápsula, facetado
piv.append(box((1.6, 0.9, 0.62), (-0.2, 0, CZ), A, bevel=0.18))
piv.append(box((1.2, 0.95, 0.2), (-0.35, 0, CZ + 0.3), A2, bevel=0.06))
piv.append(box((0.9, 0.96, 0.06), (-0.1, 0, CZ - 0.05), NE, bevel=0))
# cámara del cristal (visible arriba)
piv.append(cyl(0.3, 0.2, (-0.45, 0, CZ + 0.48), DK, verts=8))
piv.append(sphere(0.25, (-0.45, 0, CZ + 0.72), CRYSTAL, subdiv=1, scale=(0.8, 0.8, 1.4)))
for i in range(4):
    a = math.radians(45 + 90 * i)
    piv.append(box((0.08, 0.08, 0.5), (-0.45 + 0.3 * math.cos(a), 0.3 * math.sin(a), CZ + 0.7), MT,
                   rot=(0.3 * math.sin(a), -0.3 * math.cos(a), 0), bevel=0.01))
# alas de refrigeración traseras
for s in (-1, 1):
    for k in range(3):
        piv.append(box((0.5, 0.05, 0.5 - k * 0.08), (-1.0 + k * 0.12, (0.55 + k * 0.1) * s, CZ + 0.05), A2,
                       rot=(0.25 * s, 0, 0), bevel=0.02))
    piv.append(box((0.5, 0.05, 0.05), (-0.2, 0.47 * s, CZ + 0.18), NE, bevel=0))
piv.append(box((0.3, 0.6, 0.3), (-1.05, 0, CZ), DK, bevel=0.05))
piv.append(box((0.04, 0.4, 0.06), (-1.21, 0, CZ), NE, bevel=0))
Pivot = join(piv, "Pivot", (0, 0, PZ))

# ---------------------------------------------------------------- BARREL: emisor
brl = []
X0 = 0.55
brl.append(cyl(0.26, 0.5, (X0 + 0.2, 0, CZ), A2, rot=(0, math.pi / 2, 0), verts=12))
brl.append(cyl(0.14, 1.6, (X0 + 1.1, 0, CZ), MT, rot=(0, math.pi / 2, 0), verts=12))
for k in range(3):                                                   # anillos de enfoque
    x = X0 + 0.65 + k * 0.42
    brl.append(torus(0.25 - k * 0.02, 0.05, (x, 0, CZ), A, rot=(0, math.pi / 2, 0), seg=16, minor=6))
    brl.append(torus(0.25 - k * 0.02, 0.025, (x + 0.05, 0, CZ), NE, rot=(0, math.pi / 2, 0), seg=16, minor=4))
for s in (-1, 1):                                                    # rieles superior/inferior
    brl.append(box((1.7, 0.14, 0.08), (X0 + 1.2, 0, CZ + 0.3 * s), A, bevel=0.03))
    brl.append(box((1.5, 0.05, 0.03), (X0 + 1.25, 0, CZ + 0.25 * s), NE, bevel=0))
    brl.append(box((0.25, 0.14, 0.2), (X0 + 2.05, 0, CZ + 0.24 * s), A2, rot=(0, 0.3 * s, 0), bevel=0.03))
brl.append(cyl(0.18, 0.12, (X0 + 1.95, 0, CZ), DK, rot=(0, math.pi / 2, 0), verts=12))
brl.append(sphere(0.1, (X0 + 2.02, 0, CZ), CRYSTAL, subdiv=1))
Barrel = join(brl, "Barrel", (X0, 0, CZ))

transform([Pivot, Barrel], Matrix.Scale(1.3, 4), (0, 0, PZ))
parent(Pivot, Base)
parent(Barrel, Pivot)

export(OUT, "torreta_laser", [Base, Pivot, Barrel])
if not os.environ.get("NO_RENDER"):
    render(OUT, target=(0.6, 0, 1.45), dist=0.95)
print("LISTO")
