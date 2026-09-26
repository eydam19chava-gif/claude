"""Torreta ametralladora low-poly sci-fi para Tower Defense (Roblox).

Uso:
  - Headless:  python torreta_ametralladora.py [carpeta_salida]
  - Blender:   pegar en la pestaña Scripting y darle a Run Script.

Genera 4 objetos: Base (patas), Pivot (gira en Z), Barrel (cañón) y Laser.
El cañón apunta a +X. Exporta .blend, .fbx, .glb y .obj y renderiza vistas previas.
"""
import math
import os
import sys

import bpy
from mathutils import Matrix, Vector

OUT = sys.argv[-1] if len(sys.argv) > 1 and not sys.argv[-1].endswith(".py") else os.path.dirname(os.path.abspath(__file__))

# ---------------------------------------------------------------- escena
bpy.ops.wm.read_factory_settings(use_empty=True)
scene = bpy.context.scene


def material(name, color, metallic=0.6, rough=0.4, emission=None, strength=6.0):
    mat = bpy.data.materials.new(name)
    mat.use_nodes = True
    bsdf = mat.node_tree.nodes["Principled BSDF"]
    bsdf.inputs["Base Color"].default_value = (*color, 1)
    bsdf.inputs["Metallic"].default_value = metallic
    bsdf.inputs["Roughness"].default_value = rough
    if emission:
        bsdf.inputs["Emission Color"].default_value = (*emission, 1)
        bsdf.inputs["Emission Strength"].default_value = strength
    return mat


NAVY = material("Blindaje_Azul", (0.045, 0.05, 0.19), 0.55, 0.35)
NAVY_LIGHT = material("Blindaje_Azul_Claro", (0.09, 0.11, 0.36), 0.5, 0.35)
GUNMETAL = material("Metal_Gris", (0.20, 0.22, 0.26), 0.85, 0.35)
DARK = material("Metal_Oscuro", (0.035, 0.038, 0.045), 0.7, 0.5)
LEG = material("Patas_Gris", (0.13, 0.14, 0.17), 0.7, 0.45)
BRASS = material("Marco_Dorado", (0.55, 0.40, 0.10), 0.9, 0.3)
NEON = material("Neon_Verde", (0.1, 1.0, 0.25), 0.0, 0.3, emission=(0.1, 1.0, 0.2), strength=8)
LENS = material("Lente", (0.02, 0.3, 0.05), 0.0, 0.05, emission=(0.2, 1.0, 0.3), strength=3)


def finish(obj, mat, bevel):
    bpy.ops.object.transform_apply(location=False, rotation=False, scale=True)
    if bevel:
        mod = obj.modifiers.new("Bevel", "BEVEL")
        mod.width = bevel
        mod.segments = 2
        mod.limit_method = "ANGLE"
        bpy.ops.object.modifier_apply(modifier=mod.name)
    obj.data.materials.append(mat)
    for p in obj.data.polygons:
        p.use_smooth = False
    return obj


def box(size, loc, mat, rot=(0, 0, 0), bevel=0.03):
    bpy.ops.mesh.primitive_cube_add(size=1, location=loc, rotation=rot)
    obj = bpy.context.active_object
    obj.scale = size
    return finish(obj, mat, bevel)


def cyl(r, depth, loc, mat, rot=(0, 0, 0), verts=16, bevel=0.02, r2=None):
    if r2 is None:
        bpy.ops.mesh.primitive_cylinder_add(vertices=verts, radius=r, depth=depth, location=loc, rotation=rot)
    else:
        bpy.ops.mesh.primitive_cone_add(vertices=verts, radius1=r, radius2=r2, depth=depth, location=loc, rotation=rot)
    return finish(bpy.context.active_object, mat, bevel)


def strut(p1, p2, w, h, mat, bevel=0.03, up=Vector((0, 0, 1))):
    """Caja alargada entre dos puntos (su eje largo = X local)."""
    p1, p2 = Vector(p1), Vector(p2)
    d = p2 - p1
    bpy.ops.mesh.primitive_cube_add(size=1, location=(p1 + p2) / 2)
    obj = bpy.context.active_object
    obj.rotation_mode = "QUATERNION"
    obj.rotation_quaternion = d.to_track_quat("X", "Z")
    obj.scale = (d.length, w, h)
    return finish(obj, mat, bevel)


def rod(p1, p2, r, mat, verts=10):
    p1, p2 = Vector(p1), Vector(p2)
    d = p2 - p1
    bpy.ops.mesh.primitive_cylinder_add(vertices=verts, radius=r, depth=d.length, location=(p1 + p2) / 2)
    obj = bpy.context.active_object
    obj.rotation_mode = "QUATERNION"
    obj.rotation_quaternion = d.to_track_quat("Z", "Y")
    return finish(obj, mat, 0)


def join(parts, name, origin):
    bpy.ops.object.select_all(action="DESELECT")
    for p in parts:
        p.select_set(True)
    bpy.context.view_layer.objects.active = parts[0]
    bpy.ops.object.join()
    obj = bpy.context.active_object
    obj.name = obj.data.name = name
    scene.cursor.location = origin
    bpy.ops.object.origin_set(type="ORIGIN_CURSOR")
    scene.cursor.location = (0, 0, 0)
    return obj


# ---------------------------------------------------------------- BASE (trípode de 4 patas)
base = []
HUB_Z = 1.55
base.append(cyl(0.55, 0.55, (0, 0, HUB_Z), GUNMETAL, verts=12))
base.append(cyl(0.45, 0.35, (0, 0, HUB_Z - 0.42), DARK, verts=12, r2=0.2))
base.append(cyl(0.72, 0.14, (0, 0, HUB_Z + 0.33), NAVY, verts=16))
base.append(cyl(0.6, 0.06, (0, 0, HUB_Z + 0.03), NEON, verts=16, bevel=0))

for i in range(4):
    a = math.radians(45 + 90 * i)
    radial = Vector((math.cos(a), math.sin(a), 0))
    tangent = Vector((-math.sin(a), math.cos(a), 0))

    hip = radial * 0.5 + Vector((0, 0, HUB_Z + 0.05))
    knee = radial * 1.35 + Vector((0, 0, HUB_Z + 0.45))
    ankle = radial * 1.95 + Vector((0, 0, 0.4))

    # muslo: dos placas paralelas (look mecánico)
    for s in (-1, 1):
        off = tangent * 0.13 * s
        base.append(strut(hip + off, knee + off, 0.08, 0.26, LEG))
    base.append(cyl(0.2, 0.42, hip, GUNMETAL, rot=tangent.to_track_quat("Z", "X").to_euler(), verts=12))
    base.append(cyl(0.21, 0.44, knee, GUNMETAL, rot=tangent.to_track_quat("Z", "X").to_euler(), verts=12))
    base.append(cyl(0.1, 0.46, knee, NEON, rot=tangent.to_track_quat("Z", "X").to_euler(), verts=10, bevel=0))
    # canilla gruesa
    base.append(strut(knee, ankle, 0.28, 0.3, LEG, bevel=0.05))
    base.append(strut(knee.lerp(ankle, 0.25), knee.lerp(ankle, 0.7), 0.32, 0.34, NAVY, bevel=0.04))
    # pistón hidráulico
    p_top = radial * 0.45 + Vector((0, 0, HUB_Z - 0.35))
    p_bot = knee.lerp(ankle, 0.55) - radial * 0.12
    base.append(rod(p_top, p_top.lerp(p_bot, 0.55), 0.07, GUNMETAL))
    base.append(rod(p_top.lerp(p_bot, 0.5), p_bot, 0.045, DARK))
    # pie con dedos
    yaw = (0, 0, a)
    base.append(cyl(0.16, 0.4, ankle, GUNMETAL, rot=tangent.to_track_quat("Z", "X").to_euler(), verts=10))
    foot_c = radial * 2.05 + Vector((0, 0, 0.13))
    base.append(box((0.75, 0.5, 0.2), foot_c, DARK, rot=yaw, bevel=0.05))
    base.append(box((0.5, 0.38, 0.12), foot_c + Vector((0, 0, 0.15)), LEG, rot=yaw, bevel=0.03))
    for s in (-1, 1):
        toe = foot_c + radial * 0.45 + tangent * 0.15 * s + Vector((0, 0, -0.03))
        base.append(box((0.3, 0.16, 0.13), toe, DARK, rot=(0, math.radians(12), a), bevel=0.03))
    heel = foot_c - radial * 0.45 + Vector((0, 0, -0.03))
    base.append(box((0.22, 0.2, 0.12), heel, DARK, rot=yaw, bevel=0.03))

Base = join(base, "Base", (0, 0, 0))

# ---------------------------------------------------------------- PIVOT (gira en Z)
PIV_Z = HUB_Z + 0.4
BODY_Z = PIV_Z + 1.05
piv = []
piv.append(cyl(0.68, 0.16, (0, 0, PIV_Z + 0.08), GUNMETAL, verts=20))
piv.append(cyl(0.7, 0.025, (0, 0, PIV_Z + 0.17), NEON, verts=20, bevel=0))
piv.append(cyl(0.45, 0.4, (0, 0, PIV_Z + 0.4), DARK, verts=12))
# horquilla
for s in (-1, 1):
    piv.append(box((0.5, 0.16, 0.8), (0.0, 0.52 * s, PIV_Z + 0.62), NAVY, bevel=0.04))
    piv.append(box((0.3, 0.2, 0.3), (0.0, 0.5 * s, PIV_Z + 0.25), GUNMETAL, bevel=0.03))
# cuerpo principal
piv.append(box((1.7, 0.84, 0.72), (0, 0, BODY_Z), NAVY, bevel=0.07))
piv.append(box((1.3, 0.7, 0.2), (-0.05, 0, BODY_Z + 0.44), NAVY_LIGHT, bevel=0.05))
piv.append(box((0.6, 0.86, 0.3), (0.62, 0, BODY_Z + 0.35), NAVY, rot=(0, math.radians(-22), 0), bevel=0.05))
piv.append(box((1.5, 0.9, 0.12), (-0.05, 0, BODY_Z - 0.38), GUNMETAL, bevel=0.03))
# placas laterales con franjas neón
for s in (-1, 1):
    piv.append(box((1.3, 0.08, 0.52), (0.1, 0.46 * s, BODY_Z + 0.04), NAVY_LIGHT, bevel=0.03))
    piv.append(cyl(0.2, 0.1, (-0.1, 0.52 * s, BODY_Z - 0.08), GUNMETAL, rot=(math.pi / 2, 0, 0), verts=12))
    piv.append(cyl(0.08, 0.12, (-0.1, 0.53 * s, BODY_Z - 0.08), DARK, rot=(math.pi / 2, 0, 0), verts=8, bevel=0))
    for k in range(3):
        piv.append(box((0.08, 0.04, 0.36), (0.3 + k * 0.16, 0.51 * s, BODY_Z + 0.05), NEON,
                       rot=(0, math.radians(-25), 0), bevel=0))
    piv.append(cyl(0.06, 0.04, (-0.42, 0.51 * s, BODY_Z + 0.2), NEON, rot=(math.pi / 2, 0, 0), verts=12, bevel=0))
    for k in range(3):
        piv.append(box((0.05, 0.05, 0.14), (-0.62 + k * 0.08, 0.5 * s, BODY_Z - 0.12), DARK, bevel=0))
# mantelete frontal
piv.append(box((0.3, 0.72, 0.62), (0.92, 0, BODY_Z), GUNMETAL, bevel=0.06))
piv.append(cyl(0.3, 0.12, (1.1, 0, BODY_Z), DARK, rot=(0, math.pi / 2, 0), verts=16))
# tambor de munición trasero con marco dorado
piv.append(cyl(0.44, 0.78, (-0.95, 0, BODY_Z), GUNMETAL, rot=(math.pi / 2, 0, 0), verts=18, bevel=0.03))
piv.append(cyl(0.3, 0.82, (-0.95, 0, BODY_Z), DARK, rot=(math.pi / 2, 0, 0), verts=12, bevel=0))
for s in (-1, 1):
    piv.append(box((0.9, 0.08, 0.1), (-1.0, 0.42 * s, BODY_Z + 0.4), BRASS, bevel=0.02))
    piv.append(box((0.9, 0.08, 0.1), (-1.0, 0.42 * s, BODY_Z - 0.4), BRASS, bevel=0.02))
    piv.append(box((0.1, 0.08, 0.9), (-1.45, 0.42 * s, BODY_Z), BRASS, bevel=0.02))
piv.append(box((0.12, 0.72, 0.62), (-1.46, 0, BODY_Z), NAVY, bevel=0.03))
# manguera de alimentación (arco del tambor al cuerpo)
hose_pts = []
N = 14
for t in range(N + 1):
    u = t / N
    x = -1.05 + u * 1.25
    y = 0.28 + u * 0.22
    z = BODY_Z + 0.38 + math.sin(u * math.pi) * 0.75 - u * 0.35
    hose_pts.append((x, y, z))
for k in range(len(hose_pts) - 1):
    piv.append(rod(hose_pts[k], hose_pts[k + 1], 0.1 if k % 2 == 0 else 0.085, GUNMETAL if k % 2 == 0 else DARK, verts=10))
for end in (hose_pts[0], hose_pts[-1]):
    piv.append(cyl(0.13, 0.12, end, BRASS, verts=10))
# mira / scope
SC = Vector((0.15, -0.28, BODY_Z + 0.68))
piv.append(box((0.3, 0.14, 0.14), SC - Vector((0, 0, 0.12)), DARK, bevel=0.02))
piv.append(cyl(0.1, 0.6, SC, GUNMETAL, rot=(0, math.pi / 2, 0), verts=12))
piv.append(cyl(0.12, 0.08, SC + Vector((0.32, 0, 0)), DARK, rot=(0, math.pi / 2, 0), verts=12))
piv.append(cyl(0.08, 0.02, SC + Vector((0.37, 0, 0)), LENS, rot=(0, math.pi / 2, 0), verts=12, bevel=0))
# antena
piv.append(rod((-0.6, 0.3, BODY_Z + 0.5), (-0.7, 0.3, BODY_Z + 1.2), 0.02, DARK, verts=6))
piv.append(cyl(0.045, 0.06, (-0.7, 0.3, BODY_Z + 1.22), NEON, verts=8, bevel=0))

Pivot = join(piv, "Pivot", (0, 0, PIV_Z))

# ---------------------------------------------------------------- BARREL (cañón)
brl = []
X0 = 1.15
brl.append(cyl(0.25, 1.3, (X0 + 0.65, 0, BODY_Z), NAVY, rot=(0, math.pi / 2, 0), verts=12))
for k in range(7):
    brl.append(cyl(0.29, 0.06, (X0 + 0.12 + k * 0.18, 0, BODY_Z), GUNMETAL, rot=(0, math.pi / 2, 0), verts=12, bevel=0.01))
brl.append(box((1.1, 0.06, 0.08), (X0 + 0.65, 0, BODY_Z + 0.27), NEON, bevel=0))
brl.append(cyl(0.13, 0.7, (X0 + 1.6, 0, BODY_Z), GUNMETAL, rot=(0, math.pi / 2, 0), verts=12))
brl.append(cyl(0.22, 0.4, (X0 + 2.08, 0, BODY_Z), DARK, rot=(0, math.pi / 2, 0), verts=8, bevel=0.03))
for s in (-1, 1):
    brl.append(box((0.22, 0.05, 0.1), (X0 + 2.08, 0.22 * s, BODY_Z), GUNMETAL, bevel=0))
brl.append(cyl(0.09, 0.03, (X0 + 2.29, 0, BODY_Z), DARK, rot=(0, math.pi / 2, 0), verts=10, bevel=0))

Barrel = join(brl, "Barrel", (X0, 0, BODY_Z))

# ---------------------------------------------------------------- LASER
LASER_LEN = 6.0
Laser = cyl(0.018, LASER_LEN, SC + Vector((0.4 + LASER_LEN / 2, 0, 0)), NEON, rot=(0, math.pi / 2, 0), verts=6, bevel=0)
Laser.name = Laser.data.name = "Laser"

# cabeza más grande (escala alrededor del eje de giro)
HEAD_SCALE = 1.22
M = Matrix.Translation((0, 0, PIV_Z)) @ Matrix.Scale(HEAD_SCALE, 4) @ Matrix.Translation((0, 0, -PIV_Z))
for o in (Pivot, Barrel, Laser):
    o.matrix_world = M @ o.matrix_world
    bpy.ops.object.select_all(action="DESELECT")
    o.select_set(True)
    bpy.context.view_layer.objects.active = o
    bpy.ops.object.transform_apply(location=False, rotation=False, scale=True)

# jerarquía: Base > Pivot > Barrel / Laser
for child, parent in ((Pivot, Base), (Barrel, Pivot), (Laser, Pivot)):
    child.parent = parent
    child.matrix_parent_inverse = parent.matrix_world.inverted()

tris = sum(sum(len(p.vertices) - 2 for p in o.data.polygons) for o in (Base, Pivot, Barrel, Laser))
print(f"TRIANGULOS: {tris}")

# ---------------------------------------------------------------- exportar + render
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))
import lib_torretas as L  # noqa: E402

L.export(OUT, "torreta_ametralladora", [Base, Pivot, Barrel, Laser])
if not os.environ.get("NO_RENDER"):
    L.render(OUT, target=(0.5, 0, 2.2))
print("LISTO")
