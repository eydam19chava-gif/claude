"""Torreta 15 - Rociador de ácido (veneno / corroe armadura). Tanques de vidrio con líquido tóxico. Verde tóxico.

Objetos: Base (plataforma + 3 tanques de vidrio + tuberías), Pivot (bomba central, gira en Z),
Barrel (manguera + boquilla rociadora doble).
"""
import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))
from lib_torretas import *  # noqa: E402,F403

OUT = os.path.dirname(os.path.abspath(__file__))
reset()
P = palette(armor=(0.3, 0.15, 0.08), armor_light=(0.45, 0.25, 0.12), neon=(0.4, 1.0, 0.05))
A, A2, MT, DK, NE, HZ, CU = P["ARMOR"], P["ARMOR2"], P["METAL"], P["DARK"], P["NEON"], P["HAZARD"], P["COPPER"]
ACID = material("Acido", (0.35, 1.0, 0.1), 0.0, 0.1, emission=(0.3, 1.0, 0.05), strength=3)
GLASS = material("Vidrio_Verde", (0.08, 0.16, 0.1), 0.3, 0.05)

# ---------------------------------------------------------------- BASE: plataforma oxidada con 3 tanques
base = []
base.append(cyl(1.5, 0.2, (0, 0, 0.1), DK, verts=12, bevel=0.03))
base.append(cyl(1.4, 0.2, (0, 0, 0.3), A, verts=12, bevel=0.03))
for i in range(12):                                             # rejilla/franjas
    a = math.radians(i * 30)
    base.append(box((0.3, 0.06, 0.03), (1.3 * math.cos(a), 1.3 * math.sin(a), 0.41), HZ if i % 2 else DK,
                    rot=(0, 0, a), bevel=0))
for i in range(3):
    a = math.radians(60 + 120 * i)
    d = Vector((math.cos(a), math.sin(a), 0))
    c = d * 0.95
    base.append(cyl(0.38, 0.12, c + Vector((0, 0, 0.46)), MT, verts=12))
    lvl = 0.75 - i * 0.15                                       # nivel de líquido distinto en cada tanque
    base.append(cyl(0.33, lvl, c + Vector((0, 0, 0.52 + lvl / 2)), ACID, verts=12, bevel=0))
    base.append(cyl(0.33, 1.0 - lvl, c + Vector((0, 0, 0.52 + lvl + (1.0 - lvl) / 2)), GLASS, verts=12, bevel=0))
    base.append(torus(0.335, 0.02, c + Vector((0, 0, 0.52 + lvl)), NE, seg=12, minor=4))
    base.append(cyl(0.38, 0.14, c + Vector((0, 0, 1.58)), MT, verts=12))
    for k in range(4):                                          # barrotes del tanque
        b = math.radians(45 + 90 * k)
        base.append(box((0.04, 0.04, 1.0), c + Vector((0.36 * math.cos(b), 0.36 * math.sin(b), 1.02)), A2,
                        bevel=0))
    base.append(sphere(0.07, c + Vector((0.15, 0.3, 0.9)), ACID, subdiv=1))       # burbujas
    base.append(sphere(0.05, c + Vector((-0.1, 0.31, 0.75)), ACID, subdiv=1))
    # tubería al centro
    base.append(rod(c + Vector((0, 0, 1.6)), c * 0.9 + Vector((0, 0, 1.8)), 0.06, CU))
    base.append(rod(c * 0.9 + Vector((0, 0, 1.8)), Vector((0, 0, 1.8)) + d * 0.3, 0.06, CU))
    base.append(sphere(0.2, c + Vector((0, 0, 1.75)), HZ, subdiv=1, scale=(1, 1, 0.4)))  # símbolo/tapa
base.append(cyl(0.35, 1.4, (0, 0, 1.1), A2, verts=10))
base.append(cyl(0.45, 0.12, (0, 0, 1.86), MT, verts=12))
Base = join(base, "Base", (0, 0, 0))

# ---------------------------------------------------------------- PIVOT: bomba
PZ = 1.92
CZ = PZ + 0.35
piv = []
piv.append(cyl(0.42, 0.1, (0, 0, PZ + 0.05), DK, verts=12))
piv.append(sphere(0.38, (0, 0, CZ), A, subdiv=2, scale=(1.2, 1, 0.8)))
piv.append(torus(0.4, 0.04, (0, 0, CZ), NE, seg=16, minor=4))
piv.append(cyl(0.12, 0.3, (-0.2, 0, CZ + 0.35), MT, verts=8))                    # válvula de presión
piv.append(cyl(0.18, 0.05, (-0.2, 0, CZ + 0.5), CU, verts=8, bevel=0))
piv.append(cyl(0.12, 0.06, (-0.45, 0.2, CZ + 0.05), DK, rot=(0, math.pi / 2, 0), verts=10))   # manómetro
Pivot = join(piv, "Pivot", (0, 0, PZ))

# ---------------------------------------------------------------- BARREL: boquilla doble
brl = []
X0 = 0.35
brl.append(cyl(0.14, 0.3, (X0 + 0.1, 0, CZ), MT, rot=(0, math.pi / 2, 0), verts=10))
for k in range(5):                                                               # manguera corrugada
    brl.append(torus(0.1, 0.035, (X0 + 0.3 + k * 0.1, 0, CZ), CU, rot=(0, math.pi / 2, 0), seg=10, minor=4))
for s in (-1, 1):
    y = 0.12 * s
    brl.append(cyl(0.06, 0.7, (X0 + 1.05, y, CZ), MT, rot=(0, math.pi / 2, 0), verts=8))
    brl.append(cyl(0.06, 0.2, (X0 + 1.45, y, CZ), DK, rot=(0, math.pi / 2, 0), verts=8, r2=0.1))
    brl.append(cyl(0.08, 0.02, (X0 + 1.56, y, CZ), ACID, rot=(0, math.pi / 2, 0), verts=8, bevel=0))
    brl.append(sphere(0.05, (X0 + 1.7, y, CZ - 0.05), ACID, subdiv=1))              # gotas
brl.append(box((0.2, 0.36, 0.14), (X0 + 0.75, 0, CZ), A2, bevel=0.03))
Barrel = join(brl, "Barrel", (X0, 0, CZ))

transform([Pivot, Barrel], Matrix.Scale(1.2, 4), (0, 0, PZ))
parent(Pivot, Base)
parent(Barrel, Pivot)

export(OUT, "torreta_acido", [Base, Pivot, Barrel])
if not os.environ.get("NO_RENDER"):
    render(OUT, target=(0.3, 0, 1.4), dist=0.9)
print("LISTO")
