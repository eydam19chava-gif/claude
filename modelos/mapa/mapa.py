"""Mapa del Tower Defense: 6 islas (una por jugador) alrededor de una isla central con la palanca.

Cada isla tiene su tema, un camino en zigzag desde el portal de los enemigos hasta la casa base,
bordillos, faroles, decoración, un monumento y waypoints (Isla<N>_Waypoint_<k>) para que los
enemigos sigan el camino en Roblox. La isla local apunta con -X hacia el centro.

Salida: mapa.blend, mapa_completo.glb (todo) y un .glb por isla + centro, y vistas previas.
"""
import os
import random
import sys

import bpy
from mathutils import noise

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))
import lib_torretas as L  # noqa: E402
from lib_torretas import Matrix, Vector, box, cone, cyl, join, math, rod, sphere, strut, torus  # noqa: E402

OUT = os.path.dirname(os.path.abspath(__file__))
L.reset()

R = 40.0         # radio de cada isla
TOP = 3.0        # altura de la meseta
D = 100.0        # distancia del centro a cada isla
HUB_R = 22.0     # radio de la isla central
PW = 2.2         # medio ancho del camino

# ------------------------------------------------------------------ materiales (con caché)
_MATS = {}


def M(name, color, metallic=0.0, rough=0.8, emission=None, strength=3.0):
    if name not in _MATS:
        _MATS[name] = L.material(name, color, metallic, rough, emission, strength)
    return _MATS[name]


WATER = M("Agua", (0.05, 0.45, 0.7), 0.0, 0.1)
STONE = M("Piedra", (0.5, 0.5, 0.52))
STONE_D = M("Piedra_Oscura", (0.28, 0.28, 0.3))
WOOD = M("Madera", (0.38, 0.22, 0.1))
WOOD_D = M("Madera_Oscura", (0.2, 0.11, 0.05))
PLASTER = M("Revoque", (0.92, 0.86, 0.72))
ROOF = M("Tejas", (0.65, 0.15, 0.1))
WINDOW = M("Ventana_Luz", (1.0, 0.8, 0.4), emission=(1.0, 0.7, 0.3), strength=4)
GOLD = M("Oro", (1.0, 0.72, 0.2), 1.0, 0.25)
IRON = M("Hierro", (0.12, 0.12, 0.14), 0.8, 0.4)
PORTAL = M("Portal", (0.35, 0.03, 0.7), emission=(0.4, 0.02, 0.9), strength=2.5)
PORTAL2 = M("Portal_Borde", (1.0, 0.2, 0.7), emission=(1.0, 0.1, 0.55), strength=3)
VOID = M("Vacio", (0.02, 0.0, 0.04))
LAMP = M("Farol_Luz", (1.0, 0.85, 0.5), emission=(1.0, 0.75, 0.35), strength=6)
WAYPOINT = M("Waypoint", (1.0, 1.0, 1.0))
LEAF = M("Hoja_Palmera", (0.2, 0.6, 0.15))
COCO = M("Coco", (0.35, 0.2, 0.08))
RED = M("Rojo", (0.85, 0.08, 0.06), 0.1, 0.4)
WHITE = M("Blanco", (0.95, 0.95, 0.95))

THEMES = [
    dict(name="Tropical", grass=(0.35, 0.72, 0.2), grass2=(0.3, 0.62, 0.17), dirt=(0.66, 0.45, 0.24),
         sand=(0.95, 0.85, 0.58), rock=(0.62, 0.3, 0.2), rock2=(0.52, 0.24, 0.17), accent=(0.1, 0.8, 0.9),
         trees="palm", landmark="windmill"),
    dict(name="Bosque", grass=(0.2, 0.5, 0.15), grass2=(0.16, 0.42, 0.12), dirt=(0.42, 0.28, 0.14),
         sand=(0.7, 0.65, 0.45), rock=(0.4, 0.4, 0.38), rock2=(0.32, 0.32, 0.3), accent=(0.2, 0.9, 0.2),
         trees="forest", landmark="bigtree"),
    dict(name="Nieve", grass=(0.92, 0.95, 1.0), grass2=(0.85, 0.9, 0.97), dirt=(0.5, 0.42, 0.34),
         sand=(0.75, 0.82, 0.9), rock=(0.45, 0.5, 0.6), rock2=(0.36, 0.4, 0.5), accent=(0.3, 0.7, 1.0),
         trees="snowpine", landmark="igloo"),
    dict(name="Desierto", grass=(0.9, 0.72, 0.42), grass2=(0.85, 0.65, 0.36), dirt=(0.6, 0.38, 0.18),
         sand=(0.95, 0.8, 0.5), rock=(0.75, 0.4, 0.2), rock2=(0.65, 0.32, 0.16), accent=(1.0, 0.6, 0.1),
         trees="cactus", landmark="pyramid"),
    dict(name="Volcan", grass=(0.2, 0.17, 0.17), grass2=(0.26, 0.2, 0.18), dirt=(0.45, 0.2, 0.12),
         sand=(0.18, 0.16, 0.16), rock=(0.12, 0.1, 0.1), rock2=(0.2, 0.12, 0.1), accent=(1.0, 0.3, 0.02),
         trees="dead", landmark="volcano"),
    dict(name="Cristal", grass=(0.45, 0.3, 0.72), grass2=(0.38, 0.25, 0.62), dirt=(0.25, 0.2, 0.42),
         sand=(0.75, 0.7, 0.9), rock=(0.18, 0.2, 0.4), rock2=(0.14, 0.15, 0.32), accent=(0.8, 0.3, 1.0),
         trees="crystal", landmark="bigcrystal"),
]

# Camino en zigzag (unidades de R): portal -> casa. La casa queda del lado del centro (-X).
PATH = [(0.66, 0.0), (0.45, 0.0), (0.45, 0.45), (0.15, 0.45), (0.15, -0.45), (-0.15, -0.45), (-0.15, 0.35),
        (-0.4, 0.35), (-0.4, 0.0), (-0.44, 0.0)]


# ------------------------------------------------------------------ utilidades
def dist_seg(p, a, b):
    ab = b - a
    t = max(0.0, min(1.0, (p - a).dot(ab) / ab.length_squared))
    return (p - (a + ab * t)).length


def dist_path(p, pts):
    return min(dist_seg(p, pts[i], pts[i + 1]) for i in range(len(pts) - 1))


def prism(length, width, height, base_loc, mat):
    """Prisma triangular a lo largo de X (para techos a dos aguas). base_loc = centro de la base."""
    bpy.ops.mesh.primitive_cylinder_add(vertices=3, radius=1, depth=length, rotation=(0, -math.pi / 2, 0))
    o = bpy.context.active_object
    bpy.ops.object.transform_apply(location=False, rotation=True, scale=False)
    o.scale = (1, width / 1.732, height / 1.5)
    bpy.ops.object.transform_apply(location=False, rotation=False, scale=True)
    o.location = Vector(base_loc) + Vector((0, 0, 0.5 * height / 1.5))
    return L._finish(o, mat, 0)


def rock(p, s, mat, rng):
    return sphere(s, p, mat, subdiv=1, scale=(rng.uniform(0.8, 1.3), rng.uniform(0.8, 1.2), rng.uniform(0.5, 0.9)))


def join_chunks(parts, name, maxtris=15000):
    """Une piezas en varios objetos de menos de `maxtris` triángulos (límite de Roblox: 20.000)."""
    out, cur, tris = [], [], 0
    for p in parts:
        t = L.count_tris([p])
        if cur and tris + t > maxtris:
            out.append(join(cur, f"{name}_{len(out) + 1}", (0, 0, 0)))
            cur, tris = [], 0
        cur.append(p)
        tris += t
    if cur:
        out.append(join(cur, f"{name}_{len(out) + 1}" if out else name, (0, 0, 0)))
    return out


def place(objs, angle, offset):
    Mx = Matrix.Translation(offset) @ Matrix.Rotation(angle, 4, "Z")
    for o in objs:
        o.matrix_world = Mx @ o.matrix_world
        bpy.ops.object.select_all(action="DESELECT")
        o.select_set(True)
        bpy.context.view_layer.objects.active = o
        bpy.ops.object.transform_apply(location=False, rotation=True, scale=True)


def to_collection(objs, name):
    col = bpy.data.collections.new(name)
    bpy.context.scene.collection.children.link(col)
    for o in objs:
        for c in o.users_collection:
            c.objects.unlink(o)
        col.objects.link(o)
    return col


# ------------------------------------------------------------------ terreno
def terrain(th, pts, seed, name):
    N = 80
    half = 1.15 * R
    step = 2 * half / N
    verts, heights = [], {}

    def rim(x, y):
        a = math.atan2(y, x)
        return R * (1 + 0.1 * noise.noise(Vector((math.cos(a) * 1.5, math.sin(a) * 1.5, seed))))

    for j in range(N + 1):
        for i in range(N + 1):
            x, y = -half + i * step, -half + j * step
            p = Vector((x, y, 0))
            d = p.length / rim(x, y)
            if d < 0.8:
                h = TOP + 0.3 * noise.noise(Vector((x * 0.08, y * 0.08, seed)))
            elif d < 0.9:
                t = (d - 0.8) / 0.1
                h = TOP * (1 - t) + 0.8 * t + 0.25 * noise.noise(Vector((x * 0.3, y * 0.3, seed + 3)))
            elif d < 1.0:
                t = (d - 0.9) / 0.1
                h = 0.8 * (1 - t) + 0.15 * t
            elif d < 1.1:
                h = 0.15 - (d - 1.0) * 8
            else:
                h = -1.2
            dp = dist_path(p, pts)
            if d < 0.8 and dp < PW + 1.2:
                k = max(0.0, min(1.0, (dp - PW) / 1.2))
                h = (TOP - 0.15) * (1 - k) + h * k
            verts.append((x, y, h))
    faces = []
    for j in range(N):
        for i in range(N):
            a = j * (N + 1) + i
            faces.append((a, a + 1, a + N + 2, a + N + 1))
    me = bpy.data.meshes.new(name)
    me.from_pydata(verts, [], faces)
    mats = [M(f"{th['name']}_Pasto", th["grass"]), M(f"{th['name']}_Pasto2", th["grass2"]),
            M(f"{th['name']}_Tierra", th["dirt"]), M(f"{th['name']}_Arena", th["sand"]),
            M(f"{th['name']}_Roca", th["rock"]), M(f"{th['name']}_Roca2", th["rock2"]),
            M(f"{th['name']}_Arena_Mojada", tuple(c * 0.7 for c in th["sand"]))]
    for m in mats:
        me.materials.append(m)
    for f in me.polygons:
        vs = [Vector(verts[v]) for v in f.vertices]
        c = sum(vs, Vector()) / 4
        hs = [v.z for v in vs]
        slope = max(hs) - min(hs)
        if c.z > TOP - 0.6 and dist_path(Vector((c.x, c.y, 0)), pts) < PW:
            f.material_index = 2
        elif c.z > TOP - 0.6 and slope < 0.9:
            f.material_index = 0 if noise.noise(Vector((c.x * 0.1, c.y * 0.1, seed + 7))) > -0.1 else 1
        elif c.z > 0.9:
            f.material_index = 4 if int(c.z * 1.3) % 2 == 0 else 5
        elif c.z > -0.3:
            f.material_index = 3
        else:
            f.material_index = 6
        f.use_smooth = False
    o = bpy.data.objects.new(name, me)
    bpy.context.scene.collection.objects.link(o)
    return o


# ------------------------------------------------------------------ piezas del camino
def curbs(pts, mat):
    parts = []
    z = TOP - 0.15 + 0.15
    for i in range(len(pts) - 1):
        a, b = pts[i], pts[i + 1]
        d = (b - a).normalized()
        for s in (-1, 1):
            n = Vector((-d.y, d.x, 0)) * s
            e0 = e1 = 0.0
            if i > 0:
                dp = (a - pts[i - 1]).normalized()
                turn = dp.x * d.y - dp.y * d.x
                e0 = -(PW + 0.2) if turn * s > 0 else (PW + 0.2)
            if i < len(pts) - 2:
                dn = (pts[i + 2] - b).normalized()
                turn = d.x * dn.y - d.y * dn.x
                e1 = -(PW + 0.2) if turn * s > 0 else (PW + 0.2)
            p0 = a - d * e0 + n * (PW + 0.2) + Vector((0, 0, z))
            p1 = b + d * e1 + n * (PW + 0.2) + Vector((0, 0, z))
            if (p1 - p0).dot(d) > 0.3:
                parts.append(strut(p0, p1, 0.4, 0.35, mat, bevel=0.08))
    return parts


def lamp(p, h=3.2):
    parts = [cyl(0.3, 0.2, p + Vector((0, 0, 0.1)), STONE_D, verts=8),
             cyl(0.08, h, p + Vector((0, 0, h / 2)), IRON, verts=8, bevel=0),
             box((0.45, 0.45, 0.55), p + Vector((0, 0, h + 0.2)), LAMP, bevel=0.05),
             cone(0.4, 0.3, p + Vector((0, 0, h + 0.62)), IRON, verts=4)]
    return parts


# ------------------------------------------------------------------ casa base
def house(c, accent_mat, flag_mat, roof_mat):
    """Casa de 2 aguas con la puerta hacia +X. c = centro en el piso."""
    P = []
    g = c + Vector((0, 0, TOP - 0.15))
    P.append(box((9.5, 8.5, 0.6), g + Vector((0, 0, 0.3)), STONE, bevel=0.12))
    for k in range(3):                                                          # escalones
        P.append(box((0.6, 3.0, 0.2), g + Vector((5.0 + k * 0.5, 0, 0.5 - k * 0.2)), STONE_D, bevel=0.04))
    W, Dp, H = 7.0, 6.2, 3.4
    base = g + Vector((0, 0, 0.6))
    P.append(box((W, Dp, H), base + Vector((0, 0, H / 2)), PLASTER, bevel=0.05))
    for sx in (-1, 1):                                                          # vigas de esquina
        for sy in (-1, 1):
            P.append(box((0.35, 0.35, H + 0.1), base + Vector((sx * W / 2, sy * Dp / 2, H / 2)), WOOD_D, bevel=0.04))
    for z in (0.15, H - 0.1):
        P.append(box((W + 0.3, 0.3, 0.3), base + Vector((0, Dp / 2, z)), WOOD_D, bevel=0.03))
        P.append(box((W + 0.3, 0.3, 0.3), base + Vector((0, -Dp / 2, z)), WOOD_D, bevel=0.03))
        P.append(box((0.3, Dp + 0.3, 0.3), base + Vector((W / 2, 0, z)), WOOD_D, bevel=0.03))
        P.append(box((0.3, Dp + 0.3, 0.3), base + Vector((-W / 2, 0, z)), WOOD_D, bevel=0.03))
    for sy in (-1, 1):                                                          # diagonales de entramado
        P.append(strut(base + Vector((-W / 2, sy * Dp / 2, 0.2)), base + Vector((-0.6, sy * Dp / 2, H - 0.2)),
                       0.2, 0.2, WOOD_D, bevel=0))
        P.append(strut(base + Vector((W / 2, sy * Dp / 2, 0.2)), base + Vector((0.6, sy * Dp / 2, H - 0.2)),
                       0.2, 0.2, WOOD_D, bevel=0))
    # puerta
    fx = base + Vector((W / 2 + 0.05, 0, 0))
    P.append(box((0.2, 1.6, 2.4), fx + Vector((0, 0, 1.2)), WOOD, bevel=0.04))
    P.append(box((0.25, 2.0, 0.25), fx + Vector((0, 0, 2.5)), WOOD_D, bevel=0.03))
    for sy in (-1, 1):
        P.append(box((0.25, 0.25, 2.5), fx + Vector((0, sy * 0.95, 1.25)), WOOD_D, bevel=0.03))
    P.append(sphere(0.08, fx + Vector((0.15, 0.5, 1.2)), GOLD, subdiv=1))
    P.append(box((1.2, 2.6, 0.15), fx + Vector((0.6, 0, 2.85)), roof_mat, rot=(0, -0.3, 0), bevel=0.03))   # alero
    for sy in (-1, 1):                                                          # faroles de la puerta
        P.append(box((0.3, 0.3, 0.4), fx + Vector((0.25, sy * 1.35, 2.0)), LAMP, bevel=0.04))
    # ventanas
    def window(p, rot):
        P.append(box((0.12, 1.2, 1.1), p, WINDOW, rot=rot, bevel=0))
        P.append(box((0.2, 1.45, 0.15), p + Vector((0, 0, -0.62)), WOOD_D, rot=rot, bevel=0.02))
        P.append(box((0.18, 0.1, 1.2), p, WOOD_D, rot=rot, bevel=0))
        P.append(box((0.18, 1.3, 0.1), p, WOOD_D, rot=rot, bevel=0))
    for sy in (-1, 1):
        for x in (-1.8, 1.8):
            window(base + Vector((x, sy * (Dp / 2 + 0.03), 1.9)), (0, 0, math.pi / 2))
    for sy in (-1, 1):
        window(base + Vector((W / 2 + 0.03, sy * 2.1, 1.9)), (0, 0, 0))
    # techo
    rz = base.z + H
    P.append(prism(W + 0.1, Dp, 2.6, Vector((base.x, base.y, rz)), PLASTER))
    ang = math.atan2(2.6, Dp / 2)
    slab = math.hypot(2.6, Dp / 2) + 0.6
    for s in (-1, 1):
        cen = Vector((base.x, base.y + s * Dp / 4, rz + 1.3)) + Vector((0, s * 0.18, 0.15))
        P.append(box((W + 1.2, slab, 0.3), cen, roof_mat, rot=(-s * ang, 0, 0), bevel=0.06))
        for k in range(4):                                                      # filas de tejas
            t = (k + 0.5) / 4
            q = Vector((base.x, base.y + s * (Dp / 2 + 0.3) * (1 - t), rz + 2.6 * t + 0.33))
            P.append(box((W + 1.25, 0.12, 0.1), q, WOOD_D, rot=(-s * ang, 0, 0), bevel=0))
    P.append(cyl(0.2, W + 1.3, Vector((base.x, base.y, rz + 2.75)), WOOD_D, rot=(0, math.pi / 2, 0), verts=8))
    ch = Vector((base.x - 1.8, base.y + 1.6, rz + 2.0))                         # chimenea
    P.append(box((0.9, 0.9, 2.4), ch, STONE, bevel=0.06))
    P.append(box((1.1, 1.1, 0.25), ch + Vector((0, 0, 1.25)), STONE_D, bevel=0.04))
    for k in range(3):                                                          # humo
        P.append(sphere(0.35 + k * 0.12, ch + Vector((0.2 * k, 0.1 * k, 1.8 + k * 0.6)), WHITE, subdiv=1))
    # cerca de madera (3 lados)
    fence = []
    fz = g.z
    for x in [i * 1.0 - 5.5 for i in range(12)]:
        for sy in (-1, 1):
            fence.append(Vector((c.x + x, c.y + sy * 5.6, fz)))
    for y in [i * 1.0 - 5.0 for i in range(11)]:
        fence.append(Vector((c.x - 5.8, c.y + y, fz)))
    for p in fence:
        P.append(box((0.18, 0.18, 1.1), p + Vector((0, 0, 0.55)), WOOD, bevel=0.03))
    for sy in (-1, 1):
        for z in (0.45, 0.85):
            P.append(box((11.5, 0.1, 0.12), Vector((c.x - 0.25, c.y + sy * 5.6, fz + z)), WOOD, bevel=0))
    for z in (0.45, 0.85):
        P.append(box((0.1, 11.2, 0.12), Vector((c.x - 5.8, c.y, fz + z)), WOOD, bevel=0))
    # mástil con bandera del jugador
    fp = Vector((c.x + 4.2, c.y - 4.6, fz))
    P.append(cyl(0.1, 7.0, fp + Vector((0, 0, 3.5)), IRON, verts=8, bevel=0))
    P.append(sphere(0.18, fp + Vector((0, 0, 7.05)), GOLD, subdiv=1))
    P.append(box((0.08, 2.0, 1.2), fp + Vector((0, 1.05, 6.2)), flag_mat, bevel=0))
    # cristal de vida flotando sobre el techo (lo que atacan los enemigos)
    cz = rz + 4.6
    P.append(cone(0.7, 1.3, Vector((base.x, base.y, cz + 0.65)), accent_mat, verts=6))
    P.append(cone(0.7, 1.0, Vector((base.x, base.y, cz - 0.5)), accent_mat, rot=(math.pi, 0, 0), verts=6))
    P.append(torus(1.1, 0.06, Vector((base.x, base.y, cz)), GOLD, seg=20, minor=4))
    return P


# ------------------------------------------------------------------ portal de los enemigos
def portal(c, rng, rock_mat):
    """Cueva con portal mirando a -X. c = centro en el piso."""
    P = []
    g = c + Vector((0, 0, TOP - 0.15))
    P.append(cyl(5.5, 0.12, g + Vector((0, 0, 0.06)), VOID, verts=16, bevel=0))
    Rr, cz = 3.4, g.z + 3.6
    for k in range(14):                                                         # arco de piedra
        a = math.radians(k * (360 / 14))
        p = Vector((c.x, c.y + math.cos(a) * Rr, cz + math.sin(a) * Rr))
        if p.z < g.z + 0.3:
            continue
        P.append(box((1.3, 1.2, 0.9), p, STONE_D, rot=(a + math.pi / 2, 0, 0), bevel=0.15))
        P.append(cone(0.25, 0.9, p + Vector((0, math.cos(a), math.sin(a))) * 0.9, IRON, rot=Vector((0, math.cos(a), math.sin(a))), verts=5))
    for s in (-1, 1):                                                           # pilares
        P.append(box((1.6, 1.4, 3.2), Vector((c.x, c.y + s * 3.6, g.z + 1.6)), STONE_D, bevel=0.15))
        P.append(box((0.08, 0.6, 1.5), Vector((c.x - 0.82, c.y + s * 3.6, g.z + 1.8)), PORTAL2, bevel=0))
    P.append(cyl(3.0, 0.2, Vector((c.x + 0.1, c.y, cz)), PORTAL, rot=(0, math.pi / 2, 0), verts=24, bevel=0))
    for r in (2.4, 1.6, 0.8):
        P.append(torus(r, 0.1, Vector((c.x - 0.05, c.y, cz)), PORTAL2 if r != 1.6 else VOID,
                       rot=(0, math.pi / 2, 0), seg=24, minor=4))
    P.append(sphere(0.45, Vector((c.x - 0.1, c.y, cz)), VOID, subdiv=1))
    # montaña/cueva de rocas detrás
    for k in range(9):
        a = math.radians(-100 + k * 25)
        p = Vector((c.x + 2.5 + math.cos(a) * 1.5, c.y + math.sin(a) * 5.5, g.z + rng.uniform(1.5, 3.5)))
        P.append(rock(p, rng.uniform(2.2, 3.2), rock_mat, rng))
    P.append(rock(Vector((c.x + 3.5, c.y, g.z + 5.5)), 3.5, rock_mat, rng))
    # antorchas violetas
    for s in (-1, 1):
        t = Vector((c.x - 2.0, c.y + s * 5.0, g.z))
        P.append(cyl(0.12, 2.2, t + Vector((0, 0, 1.1)), WOOD_D, verts=6, bevel=0))
        P.append(cone(0.25, 0.3, t + Vector((0, 0, 2.3)), IRON, rot=(math.pi, 0, 0), verts=6))
        P.append(cone(0.2, 0.7, t + Vector((0, 0, 2.7)), PORTAL2, verts=6))
    # huesos / pinchos en el suelo
    for k in range(6):
        p = Vector((c.x - rng.uniform(1.5, 4.5), c.y + rng.uniform(-4.5, 4.5), g.z))
        if abs(p.y - c.y) < PW + 0.3:
            continue
        P.append(cone(0.2, rng.uniform(0.6, 1.2), p + Vector((0, 0, 0.4)), IRON, rot=(rng.uniform(-0.4, 0.4), rng.uniform(-0.4, 0.4), 0), verts=5))
    return P


# ------------------------------------------------------------------ vegetación y decoración
def palm(p, rng, ground):
    P, lean = [], Vector((rng.uniform(-0.5, 0.5), rng.uniform(-0.5, 0.5), 0))
    q = p + Vector((0, 0, ground))
    for k in range(5):
        q2 = q + Vector((0, 0, 1.3)) + lean * (k * 0.15)
        P.append(strut(q, q2, 0.45 - k * 0.04, 0.45 - k * 0.04, M("Tronco_Palmera", (0.55, 0.4, 0.25)), bevel=0.06))
        q = q2
    for k in range(7):
        a = math.radians(k * 360 / 7 + rng.uniform(-10, 10))
        d = Vector((math.cos(a), math.sin(a), 0))
        mid = q + d * 1.4 + Vector((0, 0, 0.35))
        P.append(strut(q, mid, 0.9, 0.08, LEAF, bevel=0))
        P.append(strut(mid, q + d * 2.8 - Vector((0, 0, 0.6)), 0.7, 0.08, LEAF, bevel=0))
    for k in range(3):
        P.append(sphere(0.22, q + Vector((0.25 * math.cos(k * 2.1), 0.25 * math.sin(k * 2.1), -0.3)), COCO, subdiv=1))
    return P


def pine(p, rng, ground, snow=False, dark=False):
    s = rng.uniform(0.8, 1.3)
    g = p + Vector((0, 0, ground))
    col = M("Pino_Oscuro", (0.08, 0.3, 0.12)) if dark else M("Pino", (0.12, 0.42, 0.16))
    P = [cyl(0.25 * s, 1.2 * s, g + Vector((0, 0, 0.6 * s)), WOOD_D, verts=6, bevel=0)]
    for k in range(3):
        z = (1.2 + k * 1.1) * s
        P.append(cone((1.6 - k * 0.4) * s, 1.8 * s, g + Vector((0, 0, z + 0.6 * s)), col, verts=7))
        if snow:
            P.append(cone((1.0 - k * 0.25) * s, 0.8 * s, g + Vector((0, 0, z + 1.2 * s)), WHITE, verts=7))
    return P


def round_tree(p, rng, ground):
    s = rng.uniform(0.9, 1.4)
    g = p + Vector((0, 0, ground))
    P = [cyl(0.3 * s, 2.2 * s, g + Vector((0, 0, 1.1 * s)), WOOD, verts=6, bevel=0)]
    for k in range(3):
        o = Vector((rng.uniform(-0.6, 0.6), rng.uniform(-0.6, 0.6), 2.4 + k * 0.5)) * s
        P.append(sphere((1.3 - k * 0.2) * s, g + o, M("Copa", (0.2, 0.55, 0.15)), subdiv=1))
    return P


def cactus(p, rng, ground):
    s = rng.uniform(0.8, 1.3)
    g = p + Vector((0, 0, ground))
    C = M("Cactus", (0.25, 0.55, 0.2))
    P = [cyl(0.35 * s, 3.0 * s, g + Vector((0, 0, 1.5 * s)), C, verts=8, bevel=0.05),
         sphere(0.35 * s, g + Vector((0, 0, 3.0 * s)), C, subdiv=1)]
    for side in (-1, 1):
        if rng.random() < 0.8:
            h = rng.uniform(1.0, 1.8) * s
            a = g + Vector((0, 0, h))
            b = a + Vector((side * 0.8 * s, 0, 0))
            P.append(strut(a, b, 0.4 * s, 0.4 * s, C, bevel=0.05))
            P.append(cyl(0.2 * s, 1.0 * s, b + Vector((0, 0, 0.5 * s)), C, verts=8, bevel=0.05))
    P.append(sphere(0.15, g + Vector((0, 0, 3.3 * s)), M("Flor_Rosa", (1.0, 0.35, 0.6)), subdiv=1))
    return P


def dead_tree(p, rng, ground):
    g = p + Vector((0, 0, ground))
    C = M("Madera_Quemada", (0.08, 0.06, 0.05))
    P = [strut(g, g + Vector((0.2, 0, 3.0)), 0.4, 0.4, C, bevel=0.05)]
    for k in range(4):
        a = math.radians(k * 90 + rng.uniform(-30, 30))
        b0 = g + Vector((0.1, 0, 1.6 + k * 0.35))
        P.append(strut(b0, b0 + Vector((math.cos(a) * 1.2, math.sin(a) * 1.2, 0.8)), 0.15, 0.15, C, bevel=0))
    return P


def crystal(p, rng, ground, mat):
    g = p + Vector((0, 0, ground))
    P = []
    for k in range(rng.randint(3, 5)):
        tilt = Vector((rng.uniform(-0.5, 0.5), rng.uniform(-0.5, 0.5), 1))
        h = rng.uniform(1.2, 3.0)
        P.append(cyl(rng.uniform(0.25, 0.45), h, g + tilt.normalized() * h / 2, mat, rot=tilt, verts=6, bevel=0, r2=0.0))
    return P


def mushroom(p, rng, ground, cap):
    g = p + Vector((0, 0, ground))
    s = rng.uniform(0.6, 1.2)
    return [cyl(0.15 * s, 0.8 * s, g + Vector((0, 0, 0.4 * s)), WHITE, verts=6, bevel=0),
            sphere(0.5 * s, g + Vector((0, 0, 0.85 * s)), cap, subdiv=1, scale=(1, 1, 0.55))]


def bush(p, rng, ground, mat):
    g = p + Vector((0, 0, ground))
    return [sphere(rng.uniform(0.5, 0.9), g + Vector((rng.uniform(-0.4, 0.4), rng.uniform(-0.4, 0.4), 0.3)), mat,
                   subdiv=1, scale=(1, 1, 0.7)) for _ in range(3)]


def flowers(p, rng, ground):
    g = p + Vector((0, 0, ground))
    cols = [M("Flor_Roja", (0.95, 0.15, 0.2)), M("Flor_Amarilla", (1.0, 0.85, 0.1)), M("Flor_Blanca", (1, 1, 1)),
            M("Flor_Rosa", (1.0, 0.35, 0.6))]
    return [sphere(0.18, g + Vector((rng.uniform(-0.8, 0.8), rng.uniform(-0.8, 0.8), 0.15)), rng.choice(cols),
                   subdiv=1) for _ in range(6)]


# ------------------------------------------------------------------ monumentos
def landmark(kind, c, th, rng, accent):
    g = c + Vector((0, 0, TOP - 0.1))
    P = []
    if kind == "windmill":
        P.append(cyl(2.4, 7.0, g + Vector((0, 0, 3.5)), M("Molino", (0.9, 0.88, 0.8)), verts=10, r2=1.7))
        P.append(cone(2.2, 2.2, g + Vector((0, 0, 8.1)), ROOF, verts=10))
        P.append(box((0.2, 1.2, 2.0), g + Vector((2.2, 0, 1.0)), WOOD, rot=(0, 0.1, 0), bevel=0.03))
        hub = g + Vector((2.3, 0, 6.8))
        P.append(cyl(0.4, 0.8, hub, WOOD_D, rot=(0, math.pi / 2, 0), verts=8))
        for k in range(4):
            a = math.radians(45 + k * 90)
            tip = hub + Vector((0.2, math.cos(a) * 5, math.sin(a) * 5))
            P.append(strut(hub + Vector((0.2, 0, 0)), tip, 0.2, 0.2, WOOD_D, bevel=0))
            P.append(strut(hub + Vector((0.3, math.cos(a) * 1.2, math.sin(a) * 1.2)), tip, 0.1, 1.0, WHITE, bevel=0))
    elif kind == "bigtree":
        P.append(cyl(1.4, 9.0, g + Vector((0, 0, 4.5)), WOOD, verts=8, r2=0.8))
        for k in range(5):
            a = math.radians(k * 72)
            P.append(strut(g + Vector((0, 0, 0.3)), g + Vector((math.cos(a) * 2.6, math.sin(a) * 2.6, -0.2)), 0.6, 0.5, WOOD, bevel=0.05))
        for k in range(6):
            o = Vector((rng.uniform(-2.5, 2.5), rng.uniform(-2.5, 2.5), 9 + rng.uniform(0, 3)))
            P.append(sphere(rng.uniform(2.5, 3.5), g + o, M("Copa_Grande", (0.15, 0.45, 0.12)), subdiv=1))
        P.append(box((0.15, 1.2, 1.8), g + Vector((1.2, 0, 1.0)), WOOD_D, bevel=0.03))         # puertita
        P.append(box((0.1, 0.4, 0.4), g + Vector((1.1, 0, 4.0)), WINDOW, bevel=0))
    elif kind == "igloo":
        ice = M("Hielo_Bloque", (0.85, 0.93, 1.0))
        P.append(sphere(3.2, g, ice, subdiv=2, scale=(1, 1, 0.85)))
        P.append(box((2.4, 1.8, 1.8), g + Vector((3.2, 0, 0.9)), ice, bevel=0.3))
        P.append(box((0.1, 1.2, 1.3), g + Vector((4.42, 0, 0.7)), VOID, bevel=0))
        for k in range(3):
            P.append(sphere(1.0 - k * 0.25, g + Vector((-1.5, 4.5, 0.8 + k * 1.3)), WHITE, subdiv=2))      # muñeco
        P.append(cone(0.12, 0.6, g + Vector((-1.5, 4.0, 3.4)), M("Zanahoria", (1, 0.45, 0.05)), rot=(math.pi / 2, 0, 0), verts=6))
    elif kind == "pyramid":
        for k in range(5):
            s = 7.0 - k * 1.4
            P.append(box((s, s, 1.2), g + Vector((0, 0, 0.6 + k * 1.2)), M("Arenisca", (0.85, 0.68, 0.4)), bevel=0.08))
        P.append(box((1.4, 1.4, 1.2), g + Vector((0, 0, 6.6)), GOLD, bevel=0.1))
        P.append(box((0.3, 1.4, 1.8), g + Vector((3.5, 0, 0.9)), VOID, bevel=0))
        for s in (-1, 1):
            P.append(box((0.8, 0.8, 5.0), g + Vector((4.5, s * 4.5, 2.5)), M("Arenisca", (0.85, 0.68, 0.4)), bevel=0.1))
            P.append(cone(0.55, 1.2, g + Vector((4.5, s * 4.5, 5.6)), GOLD, verts=4))
    elif kind == "volcano":
        lava = M("Lava", (1.0, 0.35, 0.02), emission=(1.0, 0.3, 0.0), strength=10)
        P.append(cyl(6.0, 7.0, g + Vector((0, 0, 3.5)), M("Roca_Volcanica", (0.12, 0.1, 0.1)), verts=10, r2=2.2))
        P.append(cyl(1.9, 0.3, g + Vector((0, 0, 7.0)), lava, verts=10, bevel=0))
        for k in range(4):
            a = math.radians(k * 90 + 20)
            P.append(strut(g + Vector((math.cos(a) * 2.0, math.sin(a) * 2.0, 6.9)),
                           g + Vector((math.cos(a) * 5.6, math.sin(a) * 5.6, 0.4)), 0.5, 0.15, lava, bevel=0))
        for k in range(3):
            P.append(sphere(0.6 + k * 0.3, g + Vector((0, 0, 8.5 + k * 1.2)), M("Humo", (0.25, 0.23, 0.23)), subdiv=1))
    elif kind == "bigcrystal":
        P.append(cyl(2.5, 0.6, g + Vector((0, 0, 0.3)), STONE_D, verts=6, bevel=0.1))
        cz = g.z + 6.5
        P.append(cone(1.6, 4.0, Vector((c.x, c.y, cz + 2.0)), accent, verts=6))
        P.append(cone(1.6, 2.5, Vector((c.x, c.y, cz - 1.25)), accent, rot=(math.pi, 0, 0), verts=6))
        for k, r in enumerate((3.0, 3.8)):
            P.append(torus(r, 0.1, Vector((c.x, c.y, cz)), GOLD, rot=(0.4 * (k * 2 - 1), 0.3, 0), seg=24, minor=4))
    return P


# ------------------------------------------------------------------ isla completa
def island(idx, th):
    rng = random.Random(100 + idx)
    seed = idx * 10.0
    pts = [Vector((x * R, y * R, 0)) for x, y in PATH]
    objs = []
    name = f"Isla{idx + 1}_{th['name']}"
    accent = M(f"{th['name']}_Acento", th["accent"], emission=th["accent"], strength=2)
    flat = M(f"{th['name']}_Color", th["accent"], 0.0, 0.6)
    rock_mat = M(f"{th['name']}_Roca", th["rock"])
    objs.append(terrain(th, pts, seed, f"{name}_Terreno"))
    # bordillos + faroles en las esquinas
    part = curbs(pts, STONE)
    for i in range(1, len(pts) - 1):
        a, b, c2 = pts[i - 1], pts[i], pts[i + 1]
        out = ((b - a).normalized() - (c2 - b).normalized()).normalized()
        if i % 2 == 1:
            part += lamp(b + out * (PW + 1.4) + Vector((0, 0, TOP - 0.15)))
    objs.append(join(part, f"{name}_Bordes", (0, 0, 0)))
    # casa y portal
    hc = pts[-1] + Vector((-5.5, 0, 0))
    objs.append(join(house(hc, accent, flat, M(f"{th['name']}_Techo", tuple(c * 0.8 for c in th["accent"]))
                           if th["name"] in ("Cristal",) else ROOF), f"{name}_Casa", hc))
    L.transform([objs[-1]], Matrix.Scale(1.3, 4), hc + Vector((0, 0, TOP - 0.15)))
    pc = pts[0] + Vector((2.5, 0, 0))
    objs.append(join(portal(pc, rng, rock_mat), f"{name}_Portal", pc))
    lm = Vector((0.3 * R, -0.66 * R, 0))
    objs.append(join(landmark(th["landmark"], lm, th, rng, accent), f"{name}_Monumento", lm))

    # decoración esparcida en la meseta
    taken = [(hc, 10.5), (pc, 8.0), (lm, 8.0)]
    trees, rocks, small = [], [], []

    def free(p, r):
        if p.length > 0.72 * R or dist_path(p, pts) < PW + 3.0 + r:  # deja lugar para torretas
            return False
        return all((p - q).length > rr + r for q, rr in taken)

    ground = TOP - 0.2
    tries = 0
    trees_n = 0
    while trees_n < 26 and tries < 3000:
        tries += 1
        p = Vector((rng.uniform(-R, R), rng.uniform(-R, R), 0))
        if not free(p, 1.8):
            continue
        taken.append((p, 1.8))
        t = th["trees"]
        if t == "palm":
            trees += palm(p, rng, ground)
        elif t == "forest":
            trees += pine(p, rng, ground, dark=True) if rng.random() < 0.5 else round_tree(p, rng, ground)
        elif t == "snowpine":
            trees += pine(p, rng, ground, snow=True)
        elif t == "cactus":
            trees += cactus(p, rng, ground)
        elif t == "dead":
            trees += dead_tree(p, rng, ground)
        elif t == "crystal":
            trees += crystal(p, rng, ground, accent) if rng.random() < 0.6 else mushroom(p, rng, ground, accent)
        trees_n += 1
    tries = 0
    count = 0
    while count < 40 and tries < 3000:
        tries += 1
        p = Vector((rng.uniform(-R, R), rng.uniform(-R, R), 0))
        if not free(p, 0.8):
            continue
        taken.append((p, 0.8))
        count += 1
        kind = count % 3
        if kind == 0:
            rocks.append(rock(p + Vector((0, 0, ground + 0.2)), rng.uniform(0.6, 1.3), rock_mat, rng))
        elif kind == 1:
            bm = M(f"{th['name']}_Arbusto", tuple(c * 0.8 for c in th["grass"]))
            small += bush(p, rng, ground, bm)
        else:
            if th["name"] in ("Tropical", "Bosque"):
                small += flowers(p, rng, ground)
            elif th["name"] == "Bosque" or th["name"] == "Cristal":
                small += mushroom(p, rng, ground, accent)
            else:
                rocks.append(rock(p + Vector((0, 0, ground + 0.1)), rng.uniform(0.3, 0.6), rock_mat, rng))
    # playa: rocas en el agua y (tropical) palmeras en la arena
    for k in range(10):
        a = rng.uniform(0, 2 * math.pi)
        if abs(math.atan2(math.sin(a), math.cos(a)) - math.pi) < 0.5:
            continue  # lado del puente
        p = Vector((math.cos(a), math.sin(a), 0)) * R * rng.uniform(1.02, 1.12)
        rocks.append(rock(p + Vector((0, 0, 0.1)), rng.uniform(0.8, 1.8), rock_mat, rng))
    if th["trees"] == "palm":
        for k in range(8):
            a = rng.uniform(-2.4, 2.4)
            p = Vector((math.cos(a), math.sin(a), 0)) * R * 0.95
            trees += palm(p, rng, 0.4)
    if trees:
        objs += join_chunks(trees, f"{name}_Arboles")
    if rocks:
        objs += join_chunks(rocks, f"{name}_Rocas")
    if small:
        objs += join_chunks(small, f"{name}_Plantas")

    # waypoints (el enemigo va del 1 al último)
    for k, p in enumerate(pts):
        w = box((0.6, 0.6, 0.6), p + Vector((0, 0, TOP + 0.4)), WAYPOINT, bevel=0)
        w.name = w.data.name = f"Isla{idx + 1}_Waypoint_{k + 1:02d}"
        objs.append(w)
    return objs


# ------------------------------------------------------------------ isla central con la palanca
def hub():
    P, deco = [], []
    rng = random.Random(7)
    P.append(cyl(HUB_R + 1.5, TOP + 3, Vector((0, 0, (TOP - 3) / 2 - 0.5)), M("Centro_Roca", (0.55, 0.3, 0.22)), verts=24, bevel=0.2, r2=HUB_R))
    P.append(cyl(HUB_R, 0.4, Vector((0, 0, TOP - 0.3)), M("Centro_Pasto", (0.35, 0.72, 0.2)), verts=24, bevel=0.1))
    P.append(cyl(HUB_R + 3.5, 0.3, Vector((0, 0, 0.15)), M("Centro_Arena", (0.95, 0.85, 0.58)), verts=24, bevel=0.1))
    P.append(cyl(13.0, 0.25, Vector((0, 0, TOP - 0.05)), STONE, verts=24, bevel=0.05))
    for k in range(24):                                                      # baldosas radiales
        a = math.radians(k * 15)
        P.append(box((5.5, 0.15, 0.06), Vector((math.cos(a) * 9.5, math.sin(a) * 9.5, TOP + 0.09)), STONE_D,
                     rot=(0, 0, a), bevel=0))
    P.append(torus(13.0, 0.15, Vector((0, 0, TOP + 0.1)), GOLD, seg=48, minor=4))
    g = Vector((0, 0, TOP + 0.08))
    # ---- máquina de la palanca (gacha)
    P.append(box((7.0, 5.0, 0.6), g + Vector((0, 0, 0.3)), STONE_D, bevel=0.1))
    P.append(box((6.0, 4.0, 0.5), g + Vector((0, 0, 0.85)), GOLD, bevel=0.1))
    body = g + Vector((0, 0, 4.0))
    P.append(box((5.0, 3.2, 5.8), body, RED, bevel=0.35))
    P.append(box((5.2, 3.4, 0.4), body + Vector((0, 0, 3.0)), GOLD, bevel=0.1))
    P.append(cyl(1.6, 3.4, body + Vector((0, 0, 3.2)), RED, rot=(math.pi / 2, 0, 0), verts=16))  # techo redondo
    P.append(torus(1.6, 0.12, body + Vector((0, 1.72, 3.2)), GOLD, rot=(math.pi / 2, 0, 0), seg=16, minor=4))
    P.append(torus(1.6, 0.12, body + Vector((0, -1.72, 3.2)), GOLD, rot=(math.pi / 2, 0, 0), seg=16, minor=4))
    P.append(sphere(0.7, body + Vector((0, 0, 5.0)), M("Estrella", (1, 0.9, 0.2), emission=(1, 0.8, 0.1), strength=5), subdiv=1))
    for face in (-1, 1):                                                     # pantalla con 3 rodillos en ambos lados
        fy = body.y + face * 1.62
        P.append(box((4.0, 0.1, 2.0), Vector((body.x, fy, body.z + 0.9)), VOID, bevel=0))
        for k, col in enumerate(((0.1, 0.8, 1.0), (1.0, 0.8, 0.1), (0.9, 0.2, 1.0))):
            m = M(f"Rodillo_{k}", col, emission=col, strength=3)
            P.append(box((1.1, 0.12, 1.6), Vector((body.x - 1.3 + k * 1.3, fy + face * 0.02, body.z + 0.9)), m, bevel=0.05))
        P.append(box((4.3, 0.15, 0.2), Vector((body.x, fy, body.z + 2.0)), GOLD, bevel=0))
        P.append(box((4.3, 0.15, 0.2), Vector((body.x, fy, body.z - 0.2)), GOLD, bevel=0))
        P.append(box((2.2, 0.3, 0.6), Vector((body.x, fy, body.z - 1.5)), GOLD, bevel=0.1))      # bandeja
        for k in range(8):                                                   # luces de feria
            col = [(1, 0.2, 0.2), (1, 0.9, 0.1), (0.2, 1, 0.3), (0.2, 0.6, 1)][k % 4]
            m = M(f"Luz_Feria_{k % 4}", col, emission=col, strength=5)
            P.append(sphere(0.14, Vector((body.x - 2.2 + k * 0.63, fy, body.z + 2.4)), m, subdiv=1))
    # palanca a un costado (+X)
    lx = body + Vector((2.6, 0, 0.5))
    P.append(cyl(0.6, 0.8, lx, GOLD, rot=(0, math.pi / 2, 0), verts=12))
    P.append(strut(lx + Vector((0.4, 0, 0)), lx + Vector((0.9, 0, 3.2)), 0.3, 0.3, IRON, bevel=0.05))
    P.append(sphere(0.6, lx + Vector((0.95, 0, 3.5)), RED, subdiv=2))
    # carteles hacia cada puente + faroles
    for i in range(6):
        a = math.radians(90 + 60 * i)
        d = Vector((math.cos(a), math.sin(a), 0))
        acc = M(f"{THEMES[i]['name']}_Color", THEMES[i]["accent"], 0.0, 0.6)
        pole = d * 15.5 + Vector((0, 0, TOP))
        P.append(cyl(0.12, 5.0, pole + Vector((0, 0, 2.5)), IRON, verts=8, bevel=0))
        P.append(box((0.1, 1.6, 2.4), pole + Vector((0, 0, 3.6)) + Vector((-d.y, d.x, 0)) * 0.9, acc,
                     rot=(0, 0, a), bevel=0))
        for s in (-1, 1):
            t = Vector((-d.y, d.x, 0)) * 4.2 * s
            P += lamp(d * 18.0 + t + Vector((0, 0, TOP)))
    # árboles del centro
    for k in range(10):
        a = math.radians(k * 36 + 18)
        p = Vector((math.cos(a), math.sin(a), 0)) * 19.0
        deco += palm(p, rng, TOP - 0.1) if k % 2 else round_tree(p, rng, TOP - 0.1)
    return [join(P, "Centro_Plaza", (0, 0, 0)), join(deco, "Centro_Arboles", (0, 0, 0))]


def bridge(i):
    a = math.radians(90 + 60 * i)
    d = Vector((math.cos(a), math.sin(a), 0))
    t = Vector((-d.y, d.x, 0))
    y_off = 8.0
    start = d * (HUB_R - 1.0) + t * 0.0
    end = d * (D - 0.78 * R) + t * y_off
    P = []
    L_ = (end - start).length
    u = (end - start).normalized()
    side = Vector((-u.y, u.x, 0))
    n = int(L_ / 1.0)
    z = TOP - 0.05
    for k in range(n):
        p = start + u * (k + 0.5) + Vector((0, 0, z))
        P.append(box((0.85, 3.6, 0.2), p, WOOD, rot=(0, 0, math.atan2(u.y, u.x)), bevel=0.03))
    for k in range(0, n + 1, 4):
        for s in (-1, 1):
            p = start + u * k + side * 1.9 * s
            P.append(cyl(0.15, 1.4, p + Vector((0, 0, z + 0.6)), WOOD_D, verts=6, bevel=0))
            P.append(cyl(0.25, z + 1.5, p + Vector((0, 0, (z - 1.5) / 2)), WOOD_D, verts=6, bevel=0))
    for s in (-1, 1):
        P.append(strut(start + side * 1.9 * s + Vector((0, 0, z + 1.2)), end + side * 1.9 * s + Vector((0, 0, z + 1.2)),
                       0.08, 0.08, M("Soga", (0.7, 0.55, 0.3)), bevel=0))
    return join(P, f"Puente_{i + 1}", start)


# ------------------------------------------------------------------ armar todo
groups = {}
water = cyl(D + R * 1.6, 0.1, Vector((0, 0, 0.0)), WATER, verts=48, bevel=0)
water.name = water.data.name = "Agua"
groups["Centro"] = hub() + [water]
for i, th in enumerate(THEMES):
    objs = island(i, th)
    ang = math.radians(90 + 60 * i)
    place(objs, ang, Vector((math.cos(ang), math.sin(ang), 0)) * D)
    br = bridge(i)
    groups[f"Isla{i + 1}_{th['name']}"] = objs + [br]
    print(f"isla {i + 1} {th['name']} lista")

for name, objs in groups.items():
    to_collection(objs, name)
    for o in objs:
        t = L.count_tris([o])
        if t > 20000:
            print(f"AVISO {o.name}: {t} triangulos (> 20000)")
allobjs = [o for objs in groups.values() for o in objs]
print("TRIANGULOS mapa:", L.count_tris(allobjs), "objetos:", len(allobjs))

# ------------------------------------------------------------------ exportar
blend = os.path.join(OUT, "mapa.blend")
bpy.ops.wm.save_as_mainfile(filepath=blend)
for f in os.listdir(OUT):
    if f.endswith(".blend1"):
        os.remove(os.path.join(OUT, f))
L._bake_palette(allobjs, os.path.join(OUT, "mapa_paleta.png"), cell_px=4)
bpy.ops.object.select_all(action="DESELECT")
bpy.ops.export_scene.gltf(filepath=os.path.join(OUT, "mapa_completo.glb"), export_format="GLB")
for name in groups:
    bpy.ops.object.select_all(action="DESELECT")
    for o in bpy.data.collections[name].objects:
        o.select_set(True)
    bpy.ops.export_scene.gltf(filepath=os.path.join(OUT, f"{name}.glb"), export_format="GLB", use_selection=True)
bpy.ops.wm.open_mainfile(filepath=blend)

# ------------------------------------------------------------------ render
if os.environ.get("NO_RENDER"):
    print("LISTO")
    sys.exit(0)
scene = bpy.context.scene
for o in scene.objects:
    if "Waypoint" in o.name:
        o.hide_render = True
world = bpy.data.worlds.new("Cielo")
scene.world = world
world.use_nodes = True
world.node_tree.nodes["Background"].inputs[0].default_value = (0.45, 0.65, 0.95, 1)
world.node_tree.nodes["Background"].inputs[1].default_value = 0.8
sun = bpy.data.objects.new("Sol", bpy.data.lights.new("Sol", "SUN"))
sun.data.energy = 3.5
sun.data.angle = math.radians(3)
sun.rotation_euler = (math.radians(40), math.radians(15), math.radians(30))
scene.collection.objects.link(sun)
cam = bpy.data.objects.new("Cam", bpy.data.cameras.new("Cam"))
scene.collection.objects.link(cam)
scene.camera = cam
scene.render.engine = "CYCLES"
scene.cycles.samples = int(os.environ.get("SAMPLES", 48))
scene.cycles.use_denoising = True
scene.render.resolution_x = int(os.environ.get("RES", 1400))
scene.render.resolution_y = int(scene.render.resolution_x * 0.62)
scene.view_settings.view_transform = "AgX"
scene.view_settings.look = "AgX - Punchy"


def shot(name, loc, target, lens=35):
    cam.location = loc
    cam.data.lens = lens
    cam.rotation_mode = "QUATERNION"
    cam.rotation_quaternion = (Vector(target) - Vector(loc)).to_track_quat("-Z", "Y")
    scene.render.filepath = os.path.join(OUT, f"{name}.png")
    bpy.ops.render.render(write_still=True)


isla1 = Vector((0, D, 0))
shot("vista_mapa_completo", (0, -250, 230), (0, 10, 0), lens=30)
shot("vista_isla_tropical", isla1 + Vector((55, -60, 55)), isla1 + Vector((0, 0, 3)), lens=32)
# isla 1 rota 90°: local (x, y) -> mundo (-y, x) + (0, D)
shot("vista_casa", isla1 + Vector((16, -8, 15)), isla1 + Vector((0, -0.44 * R - 5.5, 4)), lens=35)
shot("vista_portal", isla1 + Vector((6, 13, 12)), isla1 + Vector((0, 0.66 * R + 2.5, 4)), lens=40)
shot("vista_centro", (30, -35, 25), (0, 0, 5), lens=35)
print("LISTO")
