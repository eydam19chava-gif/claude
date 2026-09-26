"""Torreta 3 - Lanzamisiles con radar. Base hexagonal con estabilizadores. Acento rojo.

Objetos: Base (pedestal + estabilizadores), Pivot (cuello + radar, gira en Z), Barrel (dos pods de misiles).
"""
import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))
from lib_torretas import *  # noqa: E402,F403

OUT = os.path.dirname(os.path.abspath(__file__))
reset()
P = palette(armor=(0.75, 0.76, 0.78), armor_light=(0.55, 0.57, 0.6), neon=(1.0, 0.06, 0.05))
A, A2, MT, DK, LG, NE, HZ = P["ARMOR"], P["ARMOR2"], P["METAL"], P["DARK"], P["LEG"], P["NEON"], P["HAZARD"]
RED = material("Punta_Roja", (0.7, 0.03, 0.03), 0.3, 0.35)
WHITE = material("Misil_Blanco", (0.85, 0.85, 0.82), 0.1, 0.4)

# ---------------------------------------------------------------- BASE: pedestal hexagonal escalonado
base = []
base.append(cyl(1.3, 0.3, (0, 0, 0.15), DK, verts=6, bevel=0.05))
base.append(cyl(1.1, 0.35, (0, 0, 0.47), A2, verts=6, bevel=0.05, r2=0.95))
base.append(cyl(0.98, 0.04, (0, 0, 0.66), NE, verts=6, bevel=0))
base.append(cyl(0.85, 0.5, (0, 0, 0.9), A, verts=6, bevel=0.05, r2=0.7))
for i in range(6):                                                    # paneles y ventilas del pedestal
    a = math.radians(30 + 60 * i)
    d = Vector((math.cos(a), math.sin(a), 0))
    base.append(box((0.08, 0.5, 0.3), d * 0.8 + Vector((0, 0, 0.9)), DK, rot=(0, -0.29, a), bevel=0.02))
for i in range(3):                                                    # estabilizadores
    a = math.radians(60 + 120 * i)
    d = Vector((math.cos(a), math.sin(a), 0))
    t = Vector((-d.y, d.x, 0))
    hinge = d * 1.0 + Vector((0, 0, 0.45))
    foot = d * 2.0 + Vector((0, 0, 0.12))
    base.append(box((0.35, 0.5, 0.35), hinge, MT, rot=(0, 0, a), bevel=0.04))
    base.append(strut(hinge, foot + Vector((0, 0, 0.15)), 0.26, 0.22, LG, bevel=0.04))
    base.append(rod(d * 0.7 + Vector((0, 0, 0.75)), d * 1.55 + Vector((0, 0, 0.35)), 0.06, MT))
    base.append(cyl(0.38, 0.14, foot, DK, verts=8, bevel=0.03))
    base.append(cyl(0.2, 0.1, foot + Vector((0, 0, 0.1)), HZ, verts=8, bevel=0.01))
    base.append(box((0.06, 0.2, 0.08), hinge + d * 0.18 + Vector((0, 0, 0.1)), NE, rot=(0, 0, a), bevel=0))
Base = join(base, "Base", (0, 0, 0))

# ---------------------------------------------------------------- PIVOT: cuello, horquilla, radar
PZ = 1.15
HZ_ = PZ + 1.0  # altura del eje de elevación
piv = []
piv.append(cyl(0.72, 0.16, (0, 0, PZ + 0.08), MT, verts=16))
piv.append(cyl(0.5, 0.55, (0, 0, PZ + 0.43), A, verts=8))
piv.append(torus(0.52, 0.04, (0, 0, PZ + 0.5), NE, seg=16, minor=6))
piv.append(box((0.8, 0.9, 0.3), (0, 0, PZ + 0.75), A2, bevel=0.05))
for s in (-1, 1):                                                     # horquilla
    piv.append(box((0.5, 0.14, 0.55), (0, 0.38 * s, HZ_ - 0.05), A, bevel=0.04))
    piv.append(cyl(0.16, 0.2, (0, 0.44 * s, HZ_), DK, rot=(math.pi / 2, 0, 0), verts=10))
# cabeza de sensores entre los pods
piv.append(box((0.7, 0.58, 0.5), (0.05, 0, HZ_ + 0.05), A, bevel=0.07))
piv.append(box((0.08, 0.4, 0.14), (0.42, 0, HZ_ + 0.08), NE, bevel=0))
piv.append(cyl(0.1, 0.08, (0.42, 0.18, HZ_ - 0.1), DK, rot=(0, math.pi / 2, 0), verts=10, bevel=0))
# mástil + radar
piv.append(cyl(0.05, 0.5, (-0.2, 0, HZ_ + 0.55), MT, verts=8))
piv.append(cyl(0.42, 0.14, (-0.2, 0, HZ_ + 0.85), A2, rot=(0, -1.1, 0), verts=16, r2=0.1))
piv.append(sphere(0.07, (-0.08, 0, HZ_ + 0.9), NE, subdiv=1))
Pivot = join(piv, "Pivot", (0, 0, PZ))

# ---------------------------------------------------------------- BARREL: 2 pods de 2x3 misiles
brl = []
for s in (-1, 1):
    y = 0.9 * s
    brl.append(box((1.3, 0.72, 0.95), (0.05, y, HZ_), A, bevel=0.07))
    brl.append(box((0.08, 0.76, 0.99), (0.68, y, HZ_), A2, bevel=0.03))          # marco frontal
    brl.append(box((1.1, 0.04, 0.12), (0.0, y + 0.37 * s, HZ_ + 0.3), NE, bevel=0))
    brl.append(box((0.5, 0.05, 0.3), (-0.2, y + 0.37 * s, HZ_ - 0.15), HZ, bevel=0.01))
    brl.append(box((0.35, 0.3, 0.2), (-0.45, y, HZ_ + 0.55), MT, bevel=0.03))    # cabezal de carga
    for r in range(3):
        for c in range(2):
            tz = HZ_ + 0.28 - r * 0.28
            ty = y + (c - 0.5) * 0.32
            brl.append(cyl(0.12, 0.1, (0.72, ty, tz), DK, rot=(0, math.pi / 2, 0), verts=12, bevel=0))
            brl.append(cyl(0.085, 0.3, (0.8, ty, tz), WHITE, rot=(0, math.pi / 2, 0), verts=10, bevel=0))
            brl.append(cone(0.085, 0.2, (1.05, ty, tz), RED, rot=(0, math.pi / 2, 0), verts=10))
    brl.append(box((0.25, 0.15, 0.4), (0.05, 0.4 * s, HZ_), MT, bevel=0.02))      # brazo al eje
Barrel = join(brl, "Barrel", (0, 0, HZ_))

transform([Barrel], Matrix.Rotation(math.radians(-18), 4, "Y"), (0, 0, HZ_))
parent(Pivot, Base)
parent(Barrel, Pivot)

export(OUT, "torreta_misiles", [Base, Pivot, Barrel])
if not os.environ.get("NO_RENDER"):
    render(OUT, target=(0.3, 0, 1.4), dist=0.9)
print("LISTO")
