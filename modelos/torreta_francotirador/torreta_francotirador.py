"""Torreta 8 - Francotirador (alcance enorme, crítico). Torre de vigilancia alta con rifle largo. Acento amarillo.

Objetos: Base (torre con patas + plataforma), Pivot (cabina/escudo, gira en Z), Barrel (rifle + mira).
"""
import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))
from lib_torretas import *  # noqa: E402,F403

OUT = os.path.dirname(os.path.abspath(__file__))
reset()
P = palette(armor=(0.2, 0.26, 0.12), armor_light=(0.35, 0.38, 0.2), neon=(1.0, 0.85, 0.1))
A, A2, MT, DK, LG, NE, HZ = P["ARMOR"], P["ARMOR2"], P["METAL"], P["DARK"], P["LEG"], P["NEON"], P["HAZARD"]
SAND = material("Bolsa_Arena", (0.6, 0.5, 0.32), 0.0, 0.9)
GLASS = material("Lente_Mira", (0.9, 0.2, 0.1), 0.0, 0.05, emission=(1.0, 0.15, 0.05), strength=5)

# ---------------------------------------------------------------- BASE: torre de 4 patas con travesaños
base = []
TOP = 2.2
for i in range(4):
    a = math.radians(45 + 90 * i)
    d = Vector((math.cos(a), math.sin(a), 0))
    foot, top = d * 1.1, d * 0.55 + Vector((0, 0, TOP))
    base.append(strut(foot + Vector((0, 0, 0.1)), top, 0.16, 0.16, LG, bevel=0.03))
    base.append(box((0.4, 0.4, 0.15), foot + Vector((0, 0, 0.07)), DK, rot=(0, 0, a), bevel=0.03))
    # travesaños en X entre patas vecinas
    b = math.radians(45 + 90 * (i + 1))
    e = Vector((math.cos(b), math.sin(b), 0))
    for z0, z1 in ((0.3, 1.2), (1.2, 0.3), (1.25, 2.0), (2.0, 1.25)):
        r0, r1 = 1.1 - (z0 / TOP) * 0.55, 1.1 - (z1 / TOP) * 0.55
        base.append(strut(d * r0 + Vector((0, 0, z0)), e * r1 + Vector((0, 0, z1)), 0.06, 0.06, MT, bevel=0))
# escalera
for k in range(9):
    base.append(box((0.06, 0.4, 0.05), (-0.95 + k * 0.035, 0, 0.3 + k * 0.22), MT, bevel=0))
for s in (-1, 1):
    base.append(strut((-0.97, 0.2 * s, 0.1), (-0.65, 0.2 * s, TOP), 0.05, 0.05, DK, bevel=0))
# plataforma + bolsas de arena
base.append(box((1.6, 1.6, 0.15), (0, 0, TOP + 0.07), A2, bevel=0.03))
for i in range(12):
    a = math.radians(i * 30)
    d = Vector((math.cos(a), math.sin(a), 0))
    if abs(a - 0) < 0.3 or abs(a - 2 * math.pi) < 0.3:
        continue  # hueco para el cañón
    base.append(box((0.42, 0.22, 0.18), d * 0.72 + Vector((0, 0, TOP + 0.24)), SAND, rot=(0, 0, a + math.pi / 2),
                    bevel=0.07))
base.append(cyl(0.45, 0.08, (0, 0, TOP + 0.19), NE, verts=12, bevel=0))
Base = join(base, "Base", (0, 0, 0))

# ---------------------------------------------------------------- PIVOT: soporte + escudo
PZ = TOP + 0.23
GZ = PZ + 0.55
piv = []
piv.append(cyl(0.35, 0.12, (0, 0, PZ + 0.06), DK, verts=12))
piv.append(cyl(0.1, 0.4, (0, 0, PZ + 0.3), MT, verts=8))
piv.append(box((0.35, 0.3, 0.2), (0, 0, GZ - 0.1), A, bevel=0.03))
piv.append(box((0.08, 0.75, 0.55), (0.35, 0, GZ + 0.1), A, rot=(0, -0.15, 0), bevel=0.03))    # escudo
piv.append(box((0.1, 0.2, 0.12), (0.36, 0, GZ + 0.02), DK, bevel=0))                         # ranura
piv.append(box((0.03, 0.6, 0.04), (0.4, 0, GZ + 0.33), NE, rot=(0, -0.15, 0), bevel=0))
piv.append(box((0.4, 0.25, 0.3), (-0.35, 0, GZ - 0.1), A2, bevel=0.04))                      # caja de munición
piv.append(box((0.42, 0.04, 0.06), (-0.35, 0.13, GZ), HZ, bevel=0))
Pivot = join(piv, "Pivot", (0, 0, PZ))

# ---------------------------------------------------------------- BARREL: rifle largo
brl = []
brl.append(box((0.9, 0.16, 0.2), (0.1, 0, GZ + 0.05), A, bevel=0.03))            # cajón de mecanismos
brl.append(box((0.45, 0.1, 0.22), (-0.55, 0, GZ - 0.02), A2, bevel=0.03))        # culata
brl.append(box((0.08, 0.14, 0.26), (-0.8, 0, GZ - 0.02), DK, bevel=0.02))
brl.append(cyl(0.05, 1.9, (1.45, 0, GZ + 0.07), DK, rot=(0, math.pi / 2, 0), verts=10))
brl.append(cyl(0.07, 0.7, (0.85, 0, GZ + 0.07), MT, rot=(0, math.pi / 2, 0), verts=10))
brl.append(box((0.22, 0.12, 0.1), (2.45, 0, GZ + 0.07), MT, bevel=0.02))          # freno de boca
brl.append(box((0.04, 0.02, 0.2), (1.2, 0, GZ + 0.07), NE, bevel=0))
# mira telescópica
brl.append(cyl(0.07, 0.7, (0.15, 0, GZ + 0.3), DK, rot=(0, math.pi / 2, 0), verts=12))
brl.append(cyl(0.1, 0.12, (0.5, 0, GZ + 0.3), MT, rot=(0, math.pi / 2, 0), verts=12, r2=0.08))
brl.append(cyl(0.085, 0.02, (0.57, 0, GZ + 0.3), GLASS, rot=(0, math.pi / 2, 0), verts=12, bevel=0))
brl.append(cyl(0.05, 0.1, (0.1, 0, GZ + 0.4), MT, verts=8))
brl.append(box((0.08, 0.06, 0.1), (0.15, 0, GZ + 0.18), MT, bevel=0))
# bípode plegado
for s in (-1, 1):
    brl.append(strut((1.6, 0.03 * s, GZ), (2.1, 0.08 * s, GZ - 0.05), 0.03, 0.03, MT, bevel=0))
Barrel = join(brl, "Barrel", (0, 0, GZ))

transform([Pivot, Barrel], Matrix.Scale(1.6, 4), (0, 0, PZ))
parent(Pivot, Base)
parent(Barrel, Pivot)

export(OUT, "torreta_francotirador", [Base, Pivot, Barrel])
if not os.environ.get("NO_RENDER"):
    render(OUT, target=(0.4, 0, 1.7), dist=1.0)
print("LISTO")
