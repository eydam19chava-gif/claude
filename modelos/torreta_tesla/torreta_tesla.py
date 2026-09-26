"""Torreta 5 - Bobina Tesla (rayos en cadena). Torre de bobinas con orbe. Acento violeta eléctrico.

Objetos: Base (cimiento + contrafuertes + columna con bobinas), Pivot (orbe + garras, gira en Z).
No tiene cañón: el rayo sale del orbe (usar Beam/partículas en Roblox).
"""
import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))
from lib_torretas import *  # noqa: E402,F403

OUT = os.path.dirname(os.path.abspath(__file__))
reset()
P = palette(armor=(0.025, 0.012, 0.06), armor_light=(0.06, 0.03, 0.13), neon=(0.65, 0.25, 1.0))
A, A2, MT, DK, NE, CU = P["ARMOR"], P["ARMOR2"], P["METAL"], P["DARK"], P["NEON"], P["COPPER"]
for m in (A, A2):  # blindaje violeta mate para que no se vea lavado
    m.node_tree.nodes["Principled BSDF"].inputs["Metallic"].default_value = 0.15
    m.node_tree.nodes["Principled BSDF"].inputs["Roughness"].default_value = 0.45
NE.node_tree.nodes["Principled BSDF"].inputs["Emission Strength"].default_value = 4
ORB = material("Orbe", (0.55, 0.25, 1.0), 0.0, 0.05, emission=(0.55, 0.2, 1.0), strength=6)

# ---------------------------------------------------------------- BASE
base = []
base.append(cyl(1.35, 0.25, (0, 0, 0.125), DK, verts=8, bevel=0.05))
base.append(cyl(1.15, 0.3, (0, 0, 0.4), A, verts=8, bevel=0.05, r2=1.0))
base.append(cyl(1.02, 0.04, (0, 0, 0.57), NE, verts=8, bevel=0))
for i in range(4):                                                   # contrafuertes
    a = math.radians(22.5 + 90 * i)
    d = Vector((math.cos(a), math.sin(a), 0))
    base.append(strut(d * 1.05 + Vector((0, 0, 0.6)), d * 0.45 + Vector((0, 0, 1.7)), 0.22, 0.2, A2, bevel=0.04))
    base.append(box((0.35, 0.3, 0.25), d * 1.05 + Vector((0, 0, 0.65)), MT, rot=(0, 0, a), bevel=0.04))
    base.append(strut(d * 0.95 + Vector((0, 0, 0.8)), d * 0.55 + Vector((0, 0, 1.5)), 0.06, 0.24, NE, bevel=0))
    # aisladores laterales
    for k in range(3):
        base.append(cyl(0.1 - k * 0.015, 0.06, d * 1.2 + Vector((0, 0, 0.62 + k * 0.1)), P["BRASS"], verts=8,
                        bevel=0))
# columna central con bobinas de cobre
base.append(cyl(0.45, 0.4, (0, 0, 0.75), MT, verts=12))
base.append(cyl(0.22, 2.6, (0, 0, 2.0), DK, verts=12))
for k in range(9):
    z = 1.0 + k * 0.24
    base.append(torus(0.36 - k * 0.012, 0.07, (0, 0, z), CU, seg=16, minor=6))
    if k % 3 == 1:
        base.append(torus(0.4 - k * 0.012, 0.025, (0, 0, z + 0.12), NE, seg=16, minor=4))
base.append(cyl(0.55, 0.12, (0, 0, 3.25), A, verts=12, bevel=0.03))
base.append(cyl(0.6, 0.04, (0, 0, 3.33), NE, verts=12, bevel=0))
Base = join(base, "Base", (0, 0, 0))

# ---------------------------------------------------------------- PIVOT: orbe + 3 garras
PZ = 3.35
OZ = PZ + 0.75
piv = []
piv.append(cyl(0.45, 0.16, (0, 0, PZ + 0.08), MT, verts=12))
piv.append(cyl(0.2, 0.3, (0, 0, PZ + 0.3), DK, verts=8))
piv.append(torus(0.62, 0.08, (0, 0, OZ), A2, seg=24, minor=6))       # anillo ecuatorial
piv.append(torus(0.62, 0.035, (0, 0, OZ + 0.06), NE, seg=24, minor=4))
piv.append(sphere(0.42, (0, 0, OZ), ORB, subdiv=2))
for i in range(3):                                                   # garras curvas
    a = math.radians(120 * i)
    d = Vector((math.cos(a), math.sin(a), 0))
    p0 = d * 0.35 + Vector((0, 0, PZ + 0.2))
    p1 = d * 0.75 + Vector((0, 0, OZ - 0.15))
    p2 = d * 0.6 + Vector((0, 0, OZ + 0.45))
    p3 = d * 0.25 + Vector((0, 0, OZ + 0.7))
    piv.append(strut(p0, p1, 0.16, 0.2, A, bevel=0.04))
    piv.append(strut(p1, p2, 0.14, 0.18, A, bevel=0.04))
    piv.append(strut(p2, p3, 0.1, 0.12, MT, bevel=0.03))
    piv.append(sphere(0.07, p3, NE, subdiv=1))
    piv.append(box((0.2, 0.2, 0.2), p1, A2, rot=(0, 0, a), bevel=0.04))
# chispas (zigzags emisivos) alrededor del orbe
for i in range(3):
    a = math.radians(60 + 120 * i)
    d = Vector((math.cos(a), math.sin(a), 0))
    pts = [d * 0.45 + Vector((0, 0, OZ + 0.1)), d * 0.7 + Vector((0, 0, OZ + 0.25)),
           d * 0.62 + Vector((0, 0, OZ + 0.4)), d * 0.9 + Vector((0, 0, OZ + 0.55))]
    for k in range(3):
        piv.append(rod(pts[k], pts[k + 1], 0.02, NE, verts=4))
Pivot = join(piv, "Pivot", (0, 0, PZ))
parent(Pivot, Base)

export(OUT, "torreta_tesla", [Base, Pivot])
if not os.environ.get("NO_RENDER"):
    render(OUT, target=(0, 0, 2.2), dist=1.05)
print("LISTO")
