"""Torreta 13 - Ballesta de plasma. Arco gigante con cuerda de energía sobre un pilar de piedra. Magenta.

Objetos: Base (pilar de piedra con runas), Pivot (soporte giratorio), Barrel (ballesta: riel, brazos, cuerda, virote).
"""
import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))
from lib_torretas import *  # noqa: E402,F403

OUT = os.path.dirname(os.path.abspath(__file__))
reset()
P = palette(armor=(0.18, 0.07, 0.2), armor_light=(0.35, 0.12, 0.35), neon=(1.0, 0.1, 0.75))
A, A2, MT, DK, NE, BR = P["ARMOR"], P["ARMOR2"], P["METAL"], P["DARK"], P["NEON"], P["BRASS"]
STONE = material("Piedra", (0.42, 0.4, 0.38), 0.0, 0.85)
STONE2 = material("Piedra_Oscura", (0.25, 0.24, 0.23), 0.0, 0.9)
WOOD = material("Madera", (0.3, 0.16, 0.07), 0.0, 0.7)

# ---------------------------------------------------------------- BASE: pilar de bloques de piedra
base = []
base.append(box((2.0, 2.0, 0.3), (0, 0, 0.15), STONE2, bevel=0.08))
for layer in range(4):
    z = 0.45 + layer * 0.32
    w = 1.5 - layer * 0.1
    for k in range(4):                                      # bloques con juntas
        a = math.radians(90 * k + layer * 45)
        d = Vector((math.cos(a), math.sin(a), 0))
        base.append(box((w * 0.52, w * 0.52, 0.3), d * w * 0.24 + Vector((0, 0, z)),
                        STONE if (k + layer) % 2 else STONE2, rot=(0, 0, a), bevel=0.06))
for i in range(4):                                          # runas brillantes
    a = math.radians(45 + 90 * i)
    d = Vector((math.cos(a), math.sin(a), 0))
    base.append(box((0.04, 0.2, 0.35), d * 0.73 + Vector((0, 0, 0.75)), NE, rot=(0, 0, a), bevel=0))
    base.append(box((0.04, 0.08, 0.08), d * 0.73 + Vector((0, 0, 1.0)), NE, rot=(0, 0, a + 0.78), bevel=0))
    # antorchas
    base.append(cyl(0.05, 0.4, d * 1.05 + Vector((0, 0, 0.5)), WOOD, verts=6))
    base.append(cone(0.07, 0.18, d * 1.05 + Vector((0, 0, 0.79)), NE, verts=6))
base.append(cyl(0.6, 0.15, (0, 0, 1.55), A, verts=8, bevel=0.03))
Base = join(base, "Base", (0, 0, 0))

# ---------------------------------------------------------------- PIVOT: soporte en Y
PZ = 1.62
BZ = PZ + 0.6
piv = []
piv.append(cyl(0.5, 0.12, (0, 0, PZ + 0.06), BR, verts=12))
piv.append(cyl(0.18, 0.4, (0, 0, PZ + 0.3), DK, verts=8))
for s in (-1, 1):
    piv.append(box((0.25, 0.1, 0.45), (0, 0.18 * s, BZ - 0.1), A, bevel=0.03))
Pivot = join(piv, "Pivot", (0, 0, PZ))

# ---------------------------------------------------------------- BARREL: la ballesta
brl = []
brl.append(box((2.0, 0.22, 0.16), (0.3, 0, BZ), WOOD, bevel=0.04))              # riel
brl.append(box((1.8, 0.06, 0.03), (0.35, 0, BZ + 0.09), NE, bevel=0))           # canal de plasma
brl.append(box((0.35, 0.3, 0.3), (-0.6, 0, BZ - 0.05), A, bevel=0.05))          # mecanismo
brl.append(cyl(0.18, 0.35, (-0.6, 0, BZ - 0.05), BR, rot=(math.pi / 2, 0, 0), verts=12))  # manivela
for s in (-1, 1):
    brl.append(box((0.06, 0.06, 0.3), (-0.6, 0.2 * s, BZ - 0.25), BR, bevel=0))
# brazos curvos (3 segmentos cada uno) y cuerda de energía
FX = 1.05
tips = []
for s in (-1, 1):
    pts = [Vector((FX, 0.1 * s, BZ)), Vector((FX + 0.05, 0.6 * s, BZ)), Vector((FX - 0.08, 1.05 * s, BZ)),
           Vector((FX - 0.35, 1.35 * s, BZ))]
    for k in range(3):
        brl.append(strut(pts[k], pts[k + 1], 0.14 - k * 0.03, 0.22 - k * 0.04, A2, bevel=0.03))
        brl.append(strut(pts[k] + Vector((0.07, 0, 0)), pts[k + 1] + Vector((0.07, 0, 0)), 0.03, 0.05, NE, bevel=0))
    brl.append(sphere(0.07, pts[3], BR, subdiv=1))
    tips.append(pts[3])
nock = Vector((0.0, 0, BZ + 0.02))
for t in tips:
    brl.append(rod(t, nock, 0.02, NE, verts=5))
brl.append(box((0.3, 0.3, 0.2), (FX, 0, BZ), MT, bevel=0.04))                    # prod central
# virote de energía cargado
brl.append(cyl(0.035, 1.5, (0.75, 0, BZ + 0.15), BR, rot=(0, math.pi / 2, 0), verts=6, bevel=0))
brl.append(cone(0.1, 0.3, (1.62, 0, BZ + 0.15), NE, rot=(0, math.pi / 2, 0), verts=4))
for s in (-1, 1):
    brl.append(box((0.18, 0.02, 0.1), (0.08, 0.05 * s, BZ + 0.15), NE, bevel=0))
Barrel = join(brl, "Barrel", (0, 0, BZ))

transform([Pivot, Barrel], Matrix.Scale(1.55, 4), (0, 0, PZ))
parent(Pivot, Base)
parent(Barrel, Pivot)

export(OUT, "torreta_ballesta", [Base, Pivot, Barrel])
if not os.environ.get("NO_RENDER"):
    render(OUT, target=(0.4, 0, 1.8), dist=1.0)
print("LISTO")
