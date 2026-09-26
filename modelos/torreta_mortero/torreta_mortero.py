"""Torreta 9 - Mortero (disparo parabólico, área grande). Búnker bajo con tubo grueso inclinado. Acento verde lima.

Objetos: Base (búnker + bolsas de arena), Pivot (plato giratorio con montaje), Barrel (tubo, elevación).
"""
import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))
from lib_torretas import *  # noqa: E402,F403

OUT = os.path.dirname(os.path.abspath(__file__))
reset()
P = palette(armor=(0.22, 0.2, 0.16), armor_light=(0.4, 0.36, 0.28), neon=(0.6, 1.0, 0.05))
A, A2, MT, DK, LG, NE, HZ = P["ARMOR"], P["ARMOR2"], P["METAL"], P["DARK"], P["LEG"], P["NEON"], P["HAZARD"]
SAND = material("Bolsa_Arena", (0.6, 0.5, 0.32), 0.0, 0.9)
SHELL = material("Proyectil", (0.25, 0.3, 0.12), 0.4, 0.4)

# ---------------------------------------------------------------- BASE: búnker octogonal
base = []
base.append(cyl(1.5, 0.3, (0, 0, 0.15), DK, verts=8, bevel=0.04))
base.append(cyl(1.35, 0.55, (0, 0, 0.55), A, verts=8, bevel=0.05, r2=1.15))
for i in range(8):                                               # anillo de bolsas de arena
    for layer in range(2):
        a = math.radians(i * 45 + layer * 22.5)
        d = Vector((math.cos(a), math.sin(a), 0))
        base.append(box((0.55, 0.3, 0.2), d * 1.5 + Vector((0, 0, 0.12 + layer * 0.2)), SAND,
                        rot=(0, 0, a + math.pi / 2), bevel=0.08))
for i in range(8):                                               # remaches y luces
    a = math.radians(22.5 + i * 45)
    d = Vector((math.cos(a), math.sin(a), 0))
    base.append(box((0.05, 0.2, 0.08), d * 1.26 + Vector((0, 0, 0.6)), NE if i % 2 else DK, rot=(0, -0.35, a),
                    bevel=0))
# proyectiles de reserva en un soporte
for k in range(4):
    p = Vector((-0.75 + k * 0.18, -0.85, 0.95))
    base.append(cyl(0.07, 0.35, p, SHELL, verts=8, bevel=0))
    base.append(cone(0.07, 0.12, p + Vector((0, 0, 0.23)), NE, verts=8))
base.append(box((0.8, 0.25, 0.12), (-0.48, -0.85, 0.8), MT, bevel=0.02))
base.append(cyl(1.0, 0.12, (0, 0, 0.88), MT, verts=16))
Base = join(base, "Base", (0, 0, 0))

# ---------------------------------------------------------------- PIVOT: plato + horquilla
PZ = 0.94
TZ = PZ + 0.55
piv = []
piv.append(cyl(0.95, 0.14, (0, 0, PZ + 0.07), A2, verts=16))
piv.append(torus(0.9, 0.035, (0, 0, PZ + 0.15), NE, seg=24, minor=4))
for s in (-1, 1):
    piv.append(box((0.4, 0.14, 0.6), (0, 0.42 * s, PZ + 0.45), A, bevel=0.04))
    piv.append(cyl(0.16, 0.2, (0, 0.46 * s, TZ), MT, rot=(math.pi / 2, 0, 0), verts=12))
    piv.append(box((0.5, 0.25, 0.3), (-0.55, 0.45 * s, PZ + 0.3), A2, bevel=0.04))       # cajas laterales
    piv.append(box((0.3, 0.26, 0.04), (-0.55, 0.45 * s, PZ + 0.35), HZ, bevel=0))
# placa base del tubo + tornillos de elevación
piv.append(box((0.5, 0.6, 0.12), (-0.25, 0, PZ + 0.2), DK, bevel=0.03))
piv.append(rod((0.3, 0, PZ + 0.15), (0.35, 0, TZ - 0.05), 0.05, MT))
piv.append(cyl(0.12, 0.06, (0.33, 0, PZ + 0.45), P["COPPER"], verts=10, bevel=0))
Pivot = join(piv, "Pivot", (0, 0, PZ))

# ---------------------------------------------------------------- BARREL: tubo grueso
brl = []
brl.append(cyl(0.3, 0.3, (0, 0, TZ), MT, rot=(math.pi / 2, 0, 0), verts=12))          # muñón
brl.append(cyl(0.3, 1.8, (0.6, 0, TZ), A, rot=(0, math.pi / 2, 0), verts=14, bevel=0.03))
brl.append(cyl(0.36, 0.3, (-0.35, 0, TZ), DK, rot=(0, math.pi / 2, 0), verts=14))    # recámara
brl.append(sphere(0.3, (-0.5, 0, TZ), DK, subdiv=2, scale=(0.5, 1, 1)))
for k in range(3):
    brl.append(torus(0.31, 0.04, (0.3 + k * 0.45, 0, TZ), MT, rot=(0, math.pi / 2, 0), seg=14, minor=4))
brl.append(torus(0.31, 0.02, (0.52, 0, TZ), NE, rot=(0, math.pi / 2, 0), seg=14, minor=4))
brl.append(cyl(0.36, 0.2, (1.5, 0, TZ), A2, rot=(0, math.pi / 2, 0), verts=14))      # boca reforzada
brl.append(cyl(0.24, 0.05, (1.61, 0, TZ), DK, rot=(0, math.pi / 2, 0), verts=12, bevel=0))
Barrel = join(brl, "Barrel", (0, 0, TZ))

transform([Barrel], Matrix.Rotation(math.radians(-50), 4, "Y"), (0, 0, TZ))
parent(Pivot, Base)
parent(Barrel, Pivot)

export(OUT, "torreta_mortero", [Base, Pivot, Barrel])
if not os.environ.get("NO_RENDER"):
    render(OUT, target=(0.2, 0, 1.1), dist=0.85)
print("LISTO")
