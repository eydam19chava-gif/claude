"""Torreta 14 - Disruptor sónico (aturde / empuja). Plato parabólico gigante con parlantes. Blanco y rosa.

Objetos: Base (trípode de brazos + consola), Pivot (brazo articulado, gira en Z), Barrel (plato + emisor).
"""
import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))
from lib_torretas import *  # noqa: E402,F403

OUT = os.path.dirname(os.path.abspath(__file__))
reset()
P = palette(armor=(0.9, 0.9, 0.92), armor_light=(0.25, 0.25, 0.3), neon=(1.0, 0.3, 0.6))
A, A2, MT, DK, NE, HZ = P["ARMOR"], P["ARMOR2"], P["METAL"], P["DARK"], P["NEON"], P["HAZARD"]
MESH = material("Rejilla", (0.08, 0.08, 0.1), 0.2, 0.8)

# ---------------------------------------------------------------- BASE: 3 patas anchas + consola
base = []
base.append(cyl(0.5, 0.9, (0, 0, 0.55), A2, verts=10, bevel=0.04, r2=0.38))
for i in range(3):
    a = math.radians(90 + 120 * i)
    d = Vector((math.cos(a), math.sin(a), 0))
    base.append(strut(d * 0.3 + Vector((0, 0, 0.7)), d * 1.4 + Vector((0, 0, 0.15)), 0.3, 0.18, A, bevel=0.06))
    base.append(box((0.55, 0.45, 0.14), d * 1.45 + Vector((0, 0, 0.07)), A2, rot=(0, 0, a), bevel=0.05))
    base.append(box((0.04, 0.32, 0.04), d * 0.9 + Vector((0, 0, 0.5)), NE, rot=(0, -0.45, a), bevel=0))
    # parlantes chicos en cada pata
    spk = d * 1.1 + Vector((0, 0, 0.42))
    base.append(box((0.3, 0.3, 0.3), spk, A2, rot=(0, 0, a), bevel=0.05))
    base.append(cyl(0.11, 0.04, spk + d * 0.16, MESH, rot=d, verts=12, bevel=0))
    base.append(torus(0.11, 0.02, spk + d * 0.17, NE, rot=d, seg=12, minor=4))
base.append(cyl(0.45, 0.1, (0, 0, 1.05), MT, verts=12))
Base = join(base, "Base", (0, 0, 0))

# ---------------------------------------------------------------- PIVOT: brazo articulado
PZ = 1.1
EZ = PZ + 1.3
piv = []
piv.append(cyl(0.4, 0.14, (0, 0, PZ + 0.07), A, verts=12))
piv.append(box((0.4, 0.5, 0.25), (-0.1, 0, PZ + 0.25), A2, bevel=0.05))
j1 = Vector((-0.2, 0, PZ + 0.35))
j2 = Vector((-0.45, 0, EZ - 0.2))
piv.append(strut(j1, j2, 0.2, 0.25, A, bevel=0.05))
piv.append(strut(j2, Vector((0, 0, EZ)), 0.18, 0.22, A, bevel=0.05))
for j in (j1, j2):
    piv.append(cyl(0.14, 0.3, j, MT, rot=(math.pi / 2, 0, 0), verts=10))
    piv.append(cyl(0.06, 0.32, j, NE, rot=(math.pi / 2, 0, 0), verts=8, bevel=0))
piv.append(rod(Vector((0.05, 0, PZ + 0.3)), j2.lerp(Vector((0, 0, EZ)), 0.5), 0.04, MT))   # pistón
for k in range(3):                                                                       # cables
    piv.append(rod(j1 + Vector((0, 0.13, 0.05 * k)), j2 + Vector((0, 0.13, 0.05 * k)), 0.02, DK, verts=5))
Pivot = join(piv, "Pivot", (0, 0, PZ))

# ---------------------------------------------------------------- BARREL: plato parabólico
brl = []
brl.append(cyl(0.18, 0.4, (0, 0, EZ), DK, rot=(math.pi / 2, 0, 0), verts=10))
brl.append(box((0.35, 0.3, 0.3), (0.15, 0, EZ), A2, bevel=0.05))
brl.append(cyl(1.0, 0.35, (0.45, 0, EZ), A, rot=(0, math.pi / 2, 0), verts=24, bevel=0.02, r2=0.3))   # plato
brl.append(cyl(0.92, 0.3, (0.49, 0, EZ), MESH, rot=(0, math.pi / 2, 0), verts=24, bevel=0, r2=0.26))
for r in (0.85, 0.6, 0.35):                                                                      # ondas
    brl.append(torus(r, 0.025, (0.62 - r * 0.12, 0, EZ), NE, rot=(0, math.pi / 2, 0), seg=24, minor=4))
brl.append(torus(1.0, 0.05, (0.64, 0, EZ), A2, rot=(0, math.pi / 2, 0), seg=24, minor=6))
for i in range(3):                                                                               # soportes
    a = math.radians(90 + 120 * i)
    rim = Vector((0.62, math.cos(a) * 0.95, EZ + math.sin(a) * 0.95))
    brl.append(rod(rim, Vector((1.25, 0, EZ)), 0.03, MT, verts=6))
brl.append(cyl(0.16, 0.3, (1.3, 0, EZ), A2, rot=(0, math.pi / 2, 0), verts=12))                    # emisor
brl.append(sphere(0.12, (1.48, 0, EZ), NE, subdiv=1))
Barrel = join(brl, "Barrel", (0, 0, EZ))
transform([Barrel], Matrix.Rotation(math.radians(-10), 4, "Y"), (0, 0, EZ))
parent(Pivot, Base)
parent(Barrel, Pivot)

export(OUT, "torreta_sonica", [Base, Pivot, Barrel])
if not os.environ.get("NO_RENDER"):
    render(OUT, target=(0.3, 0, 1.5), dist=0.95)
print("LISTO")
