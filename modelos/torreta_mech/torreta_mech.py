"""Torreta 12 - Mech bípedo. Robot de patas invertidas (tipo pollo) con cañones en los hombros. Verde azulado.

Objetos: Base (patas + cadera), Pivot (torso/cabina, gira en Z), Barrel (dos cañones de hombro).
"""
import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))
from lib_torretas import *  # noqa: E402,F403

OUT = os.path.dirname(os.path.abspath(__file__))
reset()
P = palette(armor=(0.05, 0.28, 0.26), armor_light=(0.12, 0.45, 0.4), neon=(1.0, 0.2, 0.3))
A, A2, MT, DK, LG, NE, HZ = P["ARMOR"], P["ARMOR2"], P["METAL"], P["DARK"], P["LEG"], P["NEON"], P["HAZARD"]
VISOR = material("Visor", (1.0, 0.25, 0.3), 0.0, 0.05, emission=(1.0, 0.15, 0.2), strength=6)

# ---------------------------------------------------------------- BASE: dos patas de articulación invertida
base = []
HIP = 2.2
base.append(box((0.7, 1.0, 0.45), (0, 0, HIP), MT, bevel=0.08))                # cadera
for s in (-1, 1):
    y = 0.62 * s
    hip = Vector((0, y, HIP))
    knee = Vector((0.45, y, HIP - 0.75))      # rodilla adelante
    ankle = Vector((-0.35, y, 0.55))          # tobillo atrás (articulación invertida)
    foot = Vector((0.05, y, 0.12))
    base.append(cyl(0.26, 0.3, hip, DK, rot=(math.pi / 2, 0, 0), verts=12))
    base.append(strut(hip, knee, 0.32, 0.36, A, bevel=0.07))                   # muslo blindado
    base.append(box((0.5, 0.36, 0.1), hip.lerp(knee, 0.5) + Vector((0, 0, 0.2)), A2,
                    rot=(0, -0.9, 0), bevel=0.03))
    base.append(cyl(0.2, 0.36, knee, MT, rot=(math.pi / 2, 0, 0), verts=12))
    base.append(cyl(0.08, 0.38, knee, NE, rot=(math.pi / 2, 0, 0), verts=8, bevel=0))
    base.append(strut(knee, ankle, 0.22, 0.24, LG, bevel=0.05))                # canilla
    base.append(rod(hip + Vector((-0.2, 0, -0.1)), ankle.lerp(knee, 0.4), 0.05, MT))   # pistón
    base.append(cyl(0.15, 0.3, ankle, MT, rot=(math.pi / 2, 0, 0), verts=10))
    base.append(strut(ankle, foot + Vector((0, 0, 0.12)), 0.16, 0.18, LG, bevel=0.04))  # empeine
    # pie de 3 dedos + espolón
    for k, ang in enumerate((-0.45, 0, 0.45)):
        d = Vector((math.cos(ang), math.sin(ang), 0))
        base.append(strut(foot, foot + d * 0.55 + Vector((0, 0, -0.04)), 0.12, 0.1, DK, bevel=0.03))
        base.append(cone(0.07, 0.15, foot + d * 0.62, A2, rot=(0, math.pi / 2, ang), verts=6))
    base.append(strut(foot, foot + Vector((-0.4, 0, -0.02)), 0.1, 0.08, DK, bevel=0.02))
    base.append(box((0.3, 0.3, 0.12), foot + Vector((0, 0, 0.02)), A, bevel=0.03))
Base = join(base, "Base", (0, 0, 0))

# ---------------------------------------------------------------- PIVOT: torso/cabina
PZ = HIP + 0.22
CZ = PZ + 0.5
piv = []
piv.append(cyl(0.35, 0.2, (0, 0, PZ + 0.1), DK, verts=10))
piv.append(box((1.1, 1.0, 0.75), (0, 0, CZ), A, bevel=0.14))
piv.append(box((0.5, 0.9, 0.3), (0.45, 0, CZ + 0.18), A2, rot=(0, 0.35, 0), bevel=0.06))   # frente inclinado
piv.append(box((0.08, 0.7, 0.12), (0.67, 0, CZ + 0.12), VISOR, rot=(0, 0.35, 0), bevel=0))  # visor
piv.append(box((0.4, 0.7, 0.45), (-0.6, 0, CZ + 0.05), A2, bevel=0.06))                    # mochila
for k in range(3):
    piv.append(cyl(0.07, 0.35, (-0.75, -0.2 + k * 0.2, CZ + 0.4), MT, verts=8))          # escapes
piv.append(box((0.5, 0.06, 0.08), (0.0, 0.52, CZ - 0.2), HZ, bevel=0))
piv.append(box((0.5, 0.06, 0.08), (0.0, -0.52, CZ - 0.2), HZ, bevel=0))
piv.append(rod((-0.3, 0.35, CZ + 0.35), (-0.4, 0.4, CZ + 1.0), 0.02, DK, verts=6))       # antena
piv.append(sphere(0.05, (-0.4, 0.4, CZ + 1.02), NE, subdiv=1))
Pivot = join(piv, "Pivot", (0, 0, PZ))

# ---------------------------------------------------------------- BARREL: cañones de hombro
brl = []
SZ = CZ + 0.3
for s in (-1, 1):
    y = 0.72 * s
    brl.append(box((0.5, 0.35, 0.45), (0.05, y, SZ), A2, bevel=0.07))              # hombrera
    brl.append(box((0.52, 0.04, 0.08), (0.05, y + 0.18 * s, SZ + 0.1), NE, bevel=0))
    for k in (-1, 1):                                                              # dos cañones por lado
        brl.append(cyl(0.08, 1.1, (0.75, y, SZ + 0.1 * k), MT, rot=(0, math.pi / 2, 0), verts=10))
        brl.append(cyl(0.1, 0.18, (1.3, y, SZ + 0.1 * k), DK, rot=(0, math.pi / 2, 0), verts=10))
    brl.append(box((0.12, 0.2, 0.4), (0.4, y, SZ), DK, bevel=0.02))
brl.append(cyl(0.1, 1.5, (0.05, 0, SZ), MT, rot=(math.pi / 2, 0, 0), verts=10))      # eje entre hombros
Barrel = join(brl, "Barrel", (0.05, 0, SZ))
parent(Pivot, Base)
parent(Barrel, Pivot)

export(OUT, "torreta_mech", [Base, Pivot, Barrel])
if not os.environ.get("NO_RENDER"):
    render(OUT, target=(0.2, 0, 1.6), dist=0.95)
print("LISTO")
