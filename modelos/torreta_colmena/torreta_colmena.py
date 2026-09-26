"""Torreta 11 - Colmena de drones. Panal hexagonal que lanza mini-drones. Negro y amarillo.

Objetos: Base (panal + hangar), Pivot (anillo con 3 drones que orbitan, gira en Z). No tiene cañón.
"""
import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))
from lib_torretas import *  # noqa: E402,F403

OUT = os.path.dirname(os.path.abspath(__file__))
reset()
P = palette(armor=(0.03, 0.03, 0.035), armor_light=(0.12, 0.12, 0.13), neon=(1.0, 0.7, 0.0))
A, A2, MT, DK, NE = P["ARMOR"], P["ARMOR2"], P["METAL"], P["DARK"], P["NEON"]
HONEY = material("Miel", (0.95, 0.62, 0.02), 0.2, 0.35)
HONEY_GLOW = material("Miel_Brillo", (1.0, 0.65, 0.05), 0.0, 0.2, emission=(1.0, 0.55, 0.0), strength=4)
GLASS = material("Vidrio", (0.2, 0.9, 1.0), 0.0, 0.05, emission=(0.2, 0.8, 1.0), strength=4)

# ---------------------------------------------------------------- BASE: panal de celdas hexagonales
base = []
base.append(cyl(1.45, 0.25, (0, 0, 0.125), A, verts=6, bevel=0.04))
R = 0.36
cells = [(0, 0)] + [(math.cos(math.radians(30 + 60 * i)) * R * 1.75,
                     math.sin(math.radians(30 + 60 * i)) * R * 1.75) for i in range(6)]
heights = [2.1, 1.4, 1.7, 1.2, 1.55, 1.3, 1.8]
for (x, y), h in zip(cells, heights):
    base.append(cyl(R, h, (x, y, 0.25 + h / 2), HONEY, verts=6, bevel=0.03))
    base.append(cyl(R * 0.72, 0.1, (x, y, 0.25 + h), HONEY_GLOW if h < 2 else DK, verts=6, bevel=0))
    base.append(cyl(R * 1.02, 0.06, (x, y, 0.25 + h - 0.12), A, verts=6, bevel=0))
# hangar (plataforma de despegue) sobre la celda central
TOP = 0.25 + heights[0]
base.append(cyl(0.55, 0.12, (0, 0, TOP + 0.06), A2, verts=6, bevel=0.03))
for i in range(6):
    a = math.radians(i * 60)
    base.append(box((0.12, 0.04, 0.02), (0.4 * math.cos(a), 0.4 * math.sin(a), TOP + 0.13), NE, rot=(0, 0, a),
                    bevel=0))
# antena de control
base.append(rod((0.55, -0.3, 1.9), (0.7, -0.4, 2.6), 0.03, MT, verts=6))
base.append(sphere(0.06, (0.7, -0.4, 2.62), NE, subdiv=1))
Base = join(base, "Base", (0, 0, 0))

# ---------------------------------------------------------------- PIVOT: anillo orbital + 3 drones
PZ = TOP + 0.12
OZ = PZ + 0.55
piv = []
piv.append(cyl(0.12, 0.6, (0, 0, PZ + 0.3), MT, verts=8))
piv.append(torus(1.35, 0.04, (0, 0, OZ), A2, seg=36, minor=4))
for i in range(3):
    a = math.radians(i * 120)
    d = Vector((math.cos(a), math.sin(a), 0))
    piv.append(strut(Vector((0, 0, OZ)), d * 1.35 + Vector((0, 0, OZ)), 0.04, 0.04, MT, bevel=0))
    c = d * 1.35 + Vector((0, 0, OZ))
    t = Vector((-d.y, d.x, 0))
    # dron: cuerpo, ojo, 4 brazos con hélices
    piv.append(sphere(0.2, c, HONEY, subdiv=2, scale=(1.2, 1, 0.7)))
    piv.append(box((0.22, 0.28, 0.08), c + Vector((0, 0, 0.12)), A, rot=(0, 0, a), bevel=0.03))
    piv.append(sphere(0.07, c + t * 0.22, GLASS, subdiv=1))
    for k in range(4):
        b = a + math.radians(45 + 90 * k)
        arm = Vector((math.cos(b), math.sin(b), 0))
        tip = c + arm * 0.38 + Vector((0, 0, 0.06))
        piv.append(strut(c, tip, 0.05, 0.04, A, bevel=0))
        piv.append(cyl(0.14, 0.015, tip + Vector((0, 0, 0.05)), NE, verts=10, bevel=0))
        piv.append(cyl(0.035, 0.08, tip + Vector((0, 0, 0.02)), DK, verts=6, bevel=0))
    piv.append(cone(0.08, 0.15, c - Vector((0, 0, 0.2)), A, rot=(math.pi, 0, 0), verts=6))    # aguijón
Pivot = join(piv, "Pivot", (0, 0, PZ))
transform([Pivot], Matrix.Scale(1.35, 4), (0, 0, PZ))
parent(Pivot, Base)

export(OUT, "torreta_colmena", [Base, Pivot])
if not os.environ.get("NO_RENDER"):
    render(OUT, target=(0, 0, 1.7), dist=1.05)
print("LISTO")
