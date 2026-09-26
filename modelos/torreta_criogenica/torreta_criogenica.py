"""Torreta 7 - Criogénica (ralentiza / congela). Base con cristales de hielo y cañón de 3 puntas. Acento celeste.

Objetos: Base (pedestal + cristales), Pivot (tanque criogénico, gira en Z), Barrel (proyector de frío).
"""
import os
import random
import sys

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))
from lib_torretas import *  # noqa: E402,F403

OUT = os.path.dirname(os.path.abspath(__file__))
reset()
random.seed(7)
P = palette(armor=(0.78, 0.86, 0.95), armor_light=(0.25, 0.45, 0.7), neon=(0.35, 0.85, 1.0))
A, A2, MT, DK, LG, NE = P["ARMOR"], P["ARMOR2"], P["METAL"], P["DARK"], P["LEG"], P["NEON"]
ICE = material("Hielo", (0.55, 0.85, 1.0), 0.0, 0.08, emission=(0.3, 0.7, 1.0), strength=1.5)
FROST = material("Escarcha", (0.92, 0.97, 1.0), 0.0, 0.6)

# ---------------------------------------------------------------- BASE
base = []
base.append(cyl(1.3, 0.25, (0, 0, 0.125), A2, verts=10, bevel=0.04))
base.append(cyl(1.25, 0.08, (0, 0, 0.28), FROST, verts=10, bevel=0.02))
base.append(cyl(0.7, 0.8, (0, 0, 0.7), A, verts=10, bevel=0.04, r2=0.55))
base.append(cyl(0.72, 0.05, (0, 0, 0.55), NE, verts=10, bevel=0))
for i in range(5):                                               # tubos de refrigerante
    a = math.radians(36 + 72 * i)
    d = Vector((math.cos(a), math.sin(a), 0))
    base.append(rod(d * 0.62 + Vector((0, 0, 0.35)), d * 0.5 + Vector((0, 0, 1.05)), 0.07, MT))
    base.append(rod(d * 0.66 + Vector((0, 0, 0.5)), d * 0.53 + Vector((0, 0, 0.95)), 0.075, NE))
for i in range(7):                                               # cristales de hielo alrededor
    a = math.radians(i * 51 + random.uniform(-10, 10))
    d = Vector((math.cos(a), math.sin(a), 0))
    h = random.uniform(0.45, 0.85)
    tilt = d * 0.35 + Vector((0, 0, 1))
    c = d * random.uniform(0.95, 1.15) + Vector((0, 0, 0.3 + h / 2))
    base.append(cyl(random.uniform(0.1, 0.16), h, c, ICE, rot=tilt, verts=6, bevel=0, r2=0.0))
    base.append(cyl(0.07, h * 0.6, c + d * 0.15 - Vector((0, 0, h * 0.2)), ICE, rot=tilt + d * 0.4, verts=6,
                    bevel=0, r2=0.0))
Base = join(base, "Base", (0, 0, 0))

# ---------------------------------------------------------------- PIVOT: tanque criogénico
PZ = 1.1
CZ = PZ + 0.75
piv = []
piv.append(cyl(0.6, 0.16, (0, 0, PZ + 0.08), MT, verts=16))
piv.append(cyl(0.35, 0.4, (0, 0, PZ + 0.35), A2, verts=10))
piv.append(box((1.3, 0.85, 0.6), (-0.05, 0, CZ), A, bevel=0.15))
piv.append(cyl(0.34, 0.9, (-0.3, 0, CZ + 0.45), A2, rot=(math.pi / 2, 0, 0), verts=14, bevel=0.03))
piv.append(cyl(0.26, 0.92, (-0.3, 0, CZ + 0.45), ICE, rot=(math.pi / 2, 0, 0), verts=14, bevel=0))   # ventana
for s in (-1, 1):
    piv.append(cyl(0.36, 0.08, (-0.3, 0.42 * s, CZ + 0.45), MT, rot=(math.pi / 2, 0, 0), verts=14, bevel=0.01))
    piv.append(box((0.8, 0.05, 0.08), (0.05, 0.44 * s, CZ - 0.1), NE, bevel=0))
    piv.append(cyl(0.14, 0.12, (0.2, 0.45 * s, CZ + 0.1), DK, rot=(math.pi / 2, 0, 0), verts=10))   # manómetro
    piv.append(cyl(0.1, 0.13, (0.2, 0.45 * s, CZ + 0.1), FROST, rot=(math.pi / 2, 0, 0), verts=10, bevel=0))
piv.append(box((0.3, 0.7, 0.4), (-0.75, 0, CZ - 0.05), A2, bevel=0.05))
for k in range(4):
    piv.append(box((0.04, 0.6, 0.05), (-0.91, 0, CZ - 0.18 + k * 0.1), NE, bevel=0))
Pivot = join(piv, "Pivot", (0, 0, PZ))

# ---------------------------------------------------------------- BARREL: proyector con 3 puntas
brl = []
X0 = 0.6
brl.append(cyl(0.28, 0.35, (X0 + 0.15, 0, CZ), A2, rot=(0, math.pi / 2, 0), verts=12))
brl.append(cyl(0.2, 1.0, (X0 + 0.8, 0, CZ), A, rot=(0, math.pi / 2, 0), verts=12))
for k in range(4):
    brl.append(torus(0.21, 0.03, (X0 + 0.45 + k * 0.22, 0, CZ), NE, rot=(0, math.pi / 2, 0), seg=14, minor=4))
brl.append(cyl(0.24, 0.15, (X0 + 1.35, 0, CZ), MT, rot=(0, math.pi / 2, 0), verts=12))
for i in range(3):                                               # puntas de emisión
    a = math.radians(90 + 120 * i)
    off = Vector((0, math.cos(a), math.sin(a))) * 0.2
    p0 = Vector((X0 + 1.4, 0, CZ)) + off
    brl.append(strut(p0, p0 + Vector((0.45, 0, 0)) + off * 0.5, 0.08, 0.08, A2, bevel=0.02))
    brl.append(cone(0.06, 0.2, p0 + Vector((0.55, 0, 0)) + off * 0.55, ICE, rot=(0, math.pi / 2, 0), verts=6))
brl.append(sphere(0.13, (X0 + 1.55, 0, CZ), ICE, subdiv=1))
Barrel = join(brl, "Barrel", (X0, 0, CZ))

transform([Pivot, Barrel], Matrix.Scale(1.15, 4), (0, 0, PZ))
parent(Pivot, Base)
parent(Barrel, Pivot)

export(OUT, "torreta_criogenica", [Base, Pivot, Barrel])
if not os.environ.get("NO_RENDER"):
    render(OUT, target=(0.4, 0, 1.3), dist=0.85)
print("LISTO")
