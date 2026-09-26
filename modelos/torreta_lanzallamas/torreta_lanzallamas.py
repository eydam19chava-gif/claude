"""Torreta 6 - Lanzallamas (daño por quemadura). Tanques de combustible y boquilla ancha. Acento naranja fuego.

Objetos: Base (plataforma con barriles), Pivot (cuerpo + tanques, gira en Z), Barrel (lanza + boquilla).
"""
import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))
from lib_torretas import *  # noqa: E402,F403

OUT = os.path.dirname(os.path.abspath(__file__))
reset()
P = palette(armor=(0.35, 0.05, 0.03), armor_light=(0.55, 0.12, 0.04), neon=(1.0, 0.45, 0.02))
A, A2, MT, DK, LG, NE, HZ = P["ARMOR"], P["ARMOR2"], P["METAL"], P["DARK"], P["LEG"], P["NEON"], P["HAZARD"]
TANK = material("Tanque_Amarillo", (0.85, 0.6, 0.05), 0.3, 0.4)
FIRE = material("Llama", (1.0, 0.35, 0.02), 0.0, 0.2, emission=(1.0, 0.3, 0.02), strength=10)

# ---------------------------------------------------------------- BASE: plataforma cuadrada con barriles
base = []
base.append(box((2.4, 2.4, 0.3), (0, 0, 0.15), DK, bevel=0.08))
base.append(box((2.1, 2.1, 0.3), (0, 0, 0.45), A, bevel=0.08))
for i in range(4):                                               # franjas de peligro en el borde
    a = math.radians(90 * i)
    d, t = Vector((math.cos(a), math.sin(a), 0)), Vector((-math.sin(a), math.cos(a), 0))
    for k in range(7):
        base.append(box((0.16, 0.05, 0.12), d * 1.06 + t * (-0.75 + k * 0.25) + Vector((0, 0, 0.45)),
                        HZ if k % 2 == 0 else DK, rot=(0, 0.6, a + math.pi / 2), bevel=0))
for i in range(4):                                               # barriles en las esquinas
    a = math.radians(45 + 90 * i)
    c = Vector((math.cos(a), math.sin(a), 0)) * 1.25
    base.append(cyl(0.26, 0.6, c + Vector((0, 0, 0.6)), TANK, verts=12, bevel=0.03))
    for z in (0.42, 0.78):
        base.append(torus(0.265, 0.03, c + Vector((0, 0, z)), DK, seg=12, minor=4))
    base.append(cyl(0.2, 0.04, c + Vector((0, 0, 0.91)), NE, verts=12, bevel=0))
base.append(cyl(0.7, 0.55, (0, 0, 0.87), MT, verts=12))
base.append(cyl(0.75, 0.04, (0, 0, 1.1), NE, verts=16, bevel=0))
Base = join(base, "Base", (0, 0, 0))

# ---------------------------------------------------------------- PIVOT: cuerpo + tanques gemelos
PZ = 1.14
CZ = PZ + 0.75
piv = []
piv.append(cyl(0.65, 0.16, (0, 0, PZ + 0.08), DK, verts=16))
piv.append(box((0.8, 0.8, 0.4), (0, 0, PZ + 0.35), A2, bevel=0.06))
piv.append(box((1.3, 0.9, 0.7), (0.05, 0, CZ), A, bevel=0.12))
piv.append(box((0.9, 0.95, 0.12), (0.05, 0, CZ + 0.2), NE, bevel=0))
for s in (-1, 1):                                                # tanques de combustible
    y = 0.72 * s
    piv.append(cyl(0.3, 1.3, (-0.25, y, CZ + 0.05), TANK, rot=(0, math.pi / 2, 0), verts=14, bevel=0.03))
    piv.append(sphere(0.3, (-0.9, y, CZ + 0.05), TANK, subdiv=2, scale=(0.5, 1, 1)))
    piv.append(sphere(0.3, (0.4, y, CZ + 0.05), TANK, subdiv=2, scale=(0.5, 1, 1)))
    for k in range(3):
        piv.append(torus(0.305, 0.035, (-0.65 + k * 0.4, y, CZ + 0.05), DK, rot=(0, math.pi / 2, 0), seg=14,
                         minor=4))
    piv.append(box((0.25, 0.06, 0.25), (-0.25, y + 0.3 * s, CZ + 0.05), HZ, bevel=0.01))   # símbolo
    piv.append(cyl(0.06, 0.2, (-0.25, y, CZ + 0.4), MT, verts=8))                          # válvula
    piv.append(cyl(0.12, 0.05, (-0.25, y, CZ + 0.5), P["COPPER"], verts=8, bevel=0))
    piv.append(rod((0.35, y, CZ + 0.2), (0.6, 0.2 * s, CZ + 0.3), 0.05, DK))              # manguera
Pivot = join(piv, "Pivot", (0, 0, PZ))

# ---------------------------------------------------------------- BARREL: lanza + boquilla + piloto
brl = []
X0 = 0.7
brl.append(box((0.45, 0.6, 0.5), (X0 + 0.15, 0, CZ), MT, bevel=0.06))
brl.append(cyl(0.15, 1.2, (X0 + 0.9, 0, CZ), DK, rot=(0, math.pi / 2, 0), verts=12))
for k in range(5):                                               # aletas de disipación
    brl.append(cyl(0.22, 0.05, (X0 + 0.5 + k * 0.15, 0, CZ), A2, rot=(0, math.pi / 2, 0), verts=10, bevel=0))
brl.append(cyl(0.16, 0.4, (X0 + 1.65, 0, CZ), MT, rot=(0, math.pi / 2, 0), verts=12, r2=0.28))   # boquilla
brl.append(cyl(0.2, 0.03, (X0 + 1.86, 0, CZ), FIRE, rot=(0, math.pi / 2, 0), verts=12, bevel=0))
brl.append(cyl(0.035, 0.9, (X0 + 1.2, 0, CZ - 0.24), MT, rot=(0, math.pi / 2, 0), verts=6, bevel=0))  # piloto
brl.append(cone(0.06, 0.18, (X0 + 1.72, 0, CZ - 0.24), FIRE, rot=(0, math.pi / 2, 0), verts=8))
Barrel = join(brl, "Barrel", (X0, 0, CZ))

transform([Pivot, Barrel], Matrix.Scale(1.1, 4), (0, 0, PZ))
parent(Pivot, Base)
parent(Barrel, Pivot)

export(OUT, "torreta_lanzallamas", [Base, Pivot, Barrel])
if not os.environ.get("NO_RENDER"):
    render(OUT, target=(0.4, 0, 1.3), dist=0.85)
print("LISTO")
