"""Escudos de energía de panal hexagonal (modelos 1, 2 y 4 de la referencia), sin base ni palito.

Cada escudo es una cáscara curva (un pedazo de esfera) cubierta de hexágonos chicos en relieve, con el borde roto:
algunos hexágonos sueltos y marcos de hexágonos más grandes que sobresalen. La cara convexa mira hacia -Y.
El pivote está en el centro del escudo.

Uso: python escudos.py [escudo_1_esfera | escudo_2_ovalado | escudo_4_racimo]
"""
import math
import os
import random
import sys

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))
import bpy  # noqa: E402
import lib_torretas as L  # noqa: E402
from lib_torretas import Vector  # noqa: E402

HERE = os.path.dirname(os.path.abspath(__file__))
SQ3 = math.sqrt(3)
LIFT = 3.0                                     # altura del centro (para que no toque el piso en las vistas)


class Shell:
    """Arma la malla directamente con from_pydata (miles de hexágonos, mucho más rápido que un objeto por pieza)."""

    def __init__(self, R):
        self.R = R
        self.verts, self.faces, self.mats = [], [], []

    def surf(self, x, z, h=0.0):
        """Punto (x, z) del plano (medido en largo de arco) llevado a la esfera de radio R, subido h por la normal."""
        th, ph = x / self.R, z / self.R
        n = Vector((math.sin(th) * math.cos(ph), -math.cos(th) * math.cos(ph), math.sin(ph)))
        return Vector((0, self.R, LIFT)) + n * (self.R + h)

    def prism(self, poly, h0, h1, mat, bottom=False, sides=True):
        """Prisma sobre la superficie: polígono 2D `poly`, de la altura h0 a h1 (sobre la normal)."""
        b = len(self.verts)
        n = len(poly)
        self.verts += [self.surf(x, z, h0) for x, z in poly] + [self.surf(x, z, h1) for x, z in poly]
        # cara de arriba (hacia afuera, -Y): sentido horario visto desde afuera
        self.faces.append(tuple(b + n + k for k in reversed(range(n))))
        self.mats.append(mat)
        if bottom:
            self.faces.append(tuple(b + k for k in range(n)))
            self.mats.append(mat)
        for k in range(n if sides else 0):
            j = (k + 1) % n
            self.faces.append((b + k, b + j, b + n + j, b + n + k))
            self.mats.append(mat)

    def build(self, name, materials):
        me = bpy.data.meshes.new(name)
        me.from_pydata([tuple(v) for v in self.verts], [], self.faces)
        for m in materials:
            me.materials.append(m)
        for p, m in zip(me.polygons, self.mats):
            p.material_index = m
            p.use_smooth = False
        me.validate()
        me.update()
        ob = bpy.data.objects.new(name, me)
        bpy.context.scene.collection.objects.link(ob)
        bpy.context.view_layer.objects.active = ob
        bpy.ops.object.select_all(action="DESELECT")
        ob.select_set(True)
        bpy.ops.object.mode_set(mode="EDIT")
        bpy.ops.mesh.select_all(action="SELECT")
        bpy.ops.mesh.normals_make_consistent(inside=False)
        bpy.ops.object.mode_set(mode="OBJECT")
        return ob


def hexagon(cx, cz, r, rot=0.0):
    """Hexágono de punta plana (vértice en +x)."""
    return [(cx + r * math.cos(rot + k * math.pi / 3), cz + r * math.sin(rot + k * math.pi / 3)) for k in range(6)]


def lattice(s, half_w, half_h):
    """Centros de una grilla de hexágonos de tamaño s (centro a vértice) que cubre el rectángulo dado."""
    pts = []
    for i in range(-int(half_w / (1.5 * s)) - 2, int(half_w / (1.5 * s)) + 3):
        for j in range(-int(half_h / (SQ3 * s)) - 2, int(half_h / (SQ3 * s)) + 3):
            pts.append((i * 1.5 * s, (j + 0.5 * (i % 2)) * SQ3 * s))
    return pts


def shield(name, R, a, b, s, seed, lobes=(), wobble=0.08):
    """a, b: semiejes de la forma (en largo de arco). lobes: [(x, z, radio)] bultos extra en el borde."""
    rng = random.Random(seed)
    ph = [rng.uniform(0, 6.28) for _ in range(3)]

    def m(x, z):                                                                # < 1 adentro, > 1 afuera
        ang = math.atan2(z, x)
        d = math.hypot(x / a, z / b) / (1 + wobble * math.sin(3 * ang + ph[0]) + 0.6 * wobble * math.sin(7 * ang + ph[1]))
        for lx, lz, lr in lobes:
            d = min(d, math.hypot(x - lx, z - lz) / lr)
        return d

    tile = L.material("Panal", (0.35, 0.8, 1.0), 0.1, 0.35, emission=(0.2, 0.65, 1.0), strength=1.2)
    base = L.material("Fondo_Escudo", (0.04, 0.18, 0.38), 0.3, 0.4)
    frame = L.material("Borde_Hex", (0.8, 0.97, 1.0), 0.2, 0.3, emission=(0.5, 0.9, 1.0), strength=2.5)
    S = Shell(R)
    big = 2.0 * s
    ext = max(a, b) * 1.4 + max([lr + abs(lx) + abs(lz) for lx, lz, lr in lobes] or [0])
    # panal: hexágonos chicos en relieve sobre un fondo continuo (el fondo tapa los huecos y se ve desde atrás)
    for x, z in lattice(s, ext, ext):
        d = m(x, z)
        if d < 0.86 or (d < 1.0 and rng.random() < 0.75):
            S.prism(hexagon(x, z, s * 1.04), -0.05, 0.0, 1, bottom=True, sides=d > 0.7)   # paredes solo en el borde
            S.prism(hexagon(x, z, s * 0.8), 0.0, 0.03, 0)
    # borde roto: marcos de hexágonos grandes que sobresalen y algunos hexágonos grandes sueltos
    for x, z in lattice(big, ext, ext):
        d = m(x, z)
        if 0.9 < d < 1.22 and rng.random() < 0.6:
            hx = hexagon(x, z, big)
            hi = hexagon(x, z, big * 0.78)
            for k in range(6):                                                  # 6 barras del marco
                j = (k + 1) % 6
                S.prism([hx[k], hx[j], hi[j], hi[k]], -0.05, 0.05, 2, bottom=True)
            if rng.random() < 0.3:                                              # algunos rellenos
                S.prism(hexagon(x, z, big * 0.7), -0.03, 0.02, 0, bottom=True)
    ob = S.build(name, [tile, base, frame])
    return [ob]


SHIELDS = {
    "escudo_1_esfera": lambda: shield("escudo_1_esfera", R=2.4, a=1.9, b=1.9, s=0.1, seed=1),
    "escudo_2_ovalado": lambda: shield("escudo_2_ovalado", R=3.6, a=3.1, b=1.55, s=0.11, seed=2, wobble=0.06),
    "escudo_4_racimo": lambda: shield("escudo_4_racimo", R=2.2, a=0.75, b=0.8, s=0.1, seed=4, wobble=0.12,
                                      lobes=[(0.75, 0.45, 0.45), (-0.7, 0.55, 0.4), (0.1, 0.95, 0.42), (-0.55, -0.6, 0.35)]),
}


if __name__ == "__main__":
    for nm in [x for x in sys.argv[1:] if x in SHIELDS] or list(SHIELDS):
        L.reset()
        objs = SHIELDS[nm]()
        bpy.context.scene.cursor.location = (0, 0, LIFT)                        # pivote en el centro del escudo
        bpy.ops.object.select_all(action="DESELECT")
        objs[0].select_set(True)
        bpy.ops.object.origin_set(type="ORIGIN_CURSOR")
        out = os.path.join(HERE, nm)
        dist = max(0.85, max(objs[0].dimensions) / 5.0)                         # alejar la cámara en los grandes
        L.export(out, nm, objs)
        if not os.environ.get("NO_RENDER"):
            L.render(out, target=(0, 0, LIFT), dist=dist,
                     views={"vista_frente": (0.0, -11.0, 1.0), "vista_tres_cuartos": (6.5, -8.5, 2.0), "vista_atras": (-6.0, 8.5, 2.0)})
        print("LISTO", nm)
