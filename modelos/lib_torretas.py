"""Utilidades compartidas para modelar torretas low-poly con bpy (Blender 4.2+).

Cada torreta se arma con piezas simples (cajas, cilindros, esferas, toroides) que
se biselan y se unen en grupos: Base (fija), Pivot (gira en Z) y Barrel (cañón,
gira en Y). Todas apuntan a +X. `export` saca .blend/.fbx/.glb/.obj y `render`
genera vistas previas.
"""
import math
import os

import bpy
from mathutils import Matrix, Vector

__all__ = [
    "math", "Vector", "Matrix", "reset", "material", "palette", "box", "cyl", "cone", "sphere", "torus",
    "strut", "rod", "join", "transform", "parent", "count_tris", "export", "render",
]


def reset():
    bpy.ops.wm.read_factory_settings(use_empty=True)


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


def palette(armor, armor_light, neon):
    """Materiales comunes + colores propios de cada torreta."""
    return {
        "ARMOR": material("Blindaje", armor, 0.55, 0.35),
        "ARMOR2": material("Blindaje_Claro", armor_light, 0.5, 0.35),
        "METAL": material("Metal_Gris", (0.20, 0.22, 0.26), 0.85, 0.35),
        "DARK": material("Metal_Oscuro", (0.035, 0.038, 0.045), 0.7, 0.5),
        "LEG": material("Estructura", (0.13, 0.14, 0.17), 0.7, 0.45),
        "BRASS": material("Dorado", (0.55, 0.40, 0.10), 0.9, 0.3),
        "COPPER": material("Cobre", (0.55, 0.22, 0.08), 0.95, 0.3),
        "NEON": material("Neon", neon, 0.0, 0.3, emission=neon, strength=8),
        "HAZARD": material("Advertencia", (0.9, 0.55, 0.03), 0.2, 0.5),
    }


def _finish(obj, mat, bevel, segments=2):
    bpy.ops.object.transform_apply(location=False, rotation=False, scale=True)
    if bevel:
        mod = obj.modifiers.new("Bevel", "BEVEL")
        mod.width = bevel
        mod.segments = segments
        mod.limit_method = "ANGLE"
        bpy.ops.object.modifier_apply(modifier=mod.name)
    obj.data.materials.append(mat)
    for p in obj.data.polygons:
        p.use_smooth = False
    return obj


def _rot(rot):
    if isinstance(rot, Vector):  # dirección -> el eje Z local apunta hacia ahí
        return rot.to_track_quat("Z", "Y").to_euler()
    return rot


def box(size, loc, mat, rot=(0, 0, 0), bevel=0.03):
    bpy.ops.mesh.primitive_cube_add(size=1, location=loc, rotation=_rot(rot))
    obj = bpy.context.active_object
    obj.scale = size
    return _finish(obj, mat, bevel)


def cyl(r, depth, loc, mat, rot=(0, 0, 0), verts=16, bevel=0.02, r2=None):
    if r2 is None:
        bpy.ops.mesh.primitive_cylinder_add(vertices=verts, radius=r, depth=depth, location=loc, rotation=_rot(rot))
    else:
        bpy.ops.mesh.primitive_cone_add(vertices=verts, radius1=r, radius2=r2, depth=depth, location=loc,
                                        rotation=_rot(rot))
    return _finish(bpy.context.active_object, mat, bevel)


def cone(r, depth, loc, mat, rot=(0, 0, 0), verts=12, r2=0.0):
    return cyl(r, depth, loc, mat, rot=rot, verts=verts, bevel=0, r2=r2)


def sphere(r, loc, mat, subdiv=2, scale=(1, 1, 1)):
    bpy.ops.mesh.primitive_ico_sphere_add(subdivisions=subdiv, radius=r, location=loc)
    obj = bpy.context.active_object
    obj.scale = scale
    return _finish(obj, mat, 0)


def torus(R, r, loc, mat, rot=(0, 0, 0), seg=24, minor=8):
    bpy.ops.mesh.primitive_torus_add(major_radius=R, minor_radius=r, major_segments=seg, minor_segments=minor,
                                     location=loc, rotation=_rot(rot))
    return _finish(bpy.context.active_object, mat, 0)


def strut(p1, p2, w, h, mat, bevel=0.03):
    """Caja alargada entre dos puntos."""
    p1, p2 = Vector(p1), Vector(p2)
    d = p2 - p1
    bpy.ops.mesh.primitive_cube_add(size=1, location=(p1 + p2) / 2)
    obj = bpy.context.active_object
    obj.rotation_mode = "QUATERNION"
    obj.rotation_quaternion = d.to_track_quat("X", "Z")
    obj.scale = (d.length, w, h)
    return _finish(obj, mat, bevel)


def rod(p1, p2, r, mat, verts=10):
    p1, p2 = Vector(p1), Vector(p2)
    d = p2 - p1
    bpy.ops.mesh.primitive_cylinder_add(vertices=verts, radius=r, depth=d.length, location=(p1 + p2) / 2)
    obj = bpy.context.active_object
    obj.rotation_mode = "QUATERNION"
    obj.rotation_quaternion = d.to_track_quat("Z", "Y")
    return _finish(obj, mat, 0)


def join(parts, name, origin):
    scene = bpy.context.scene
    bpy.ops.object.select_all(action="DESELECT")
    for p in parts:
        p.select_set(True)
    bpy.context.view_layer.objects.active = parts[0]
    if len(parts) > 1:
        bpy.ops.object.join()
    obj = bpy.context.active_object
    obj.name = obj.data.name = name
    scene.cursor.location = origin
    bpy.ops.object.origin_set(type="ORIGIN_CURSOR")
    scene.cursor.location = (0, 0, 0)
    return obj


def transform(objs, matrix, center):
    """Aplica `matrix` (rotación/escala) alrededor de `center` y la hornea."""
    c = Vector(center)
    M = Matrix.Translation(c) @ matrix @ Matrix.Translation(-c)
    for o in objs:
        o.matrix_world = M @ o.matrix_world
        bpy.ops.object.select_all(action="DESELECT")
        o.select_set(True)
        bpy.context.view_layer.objects.active = o
        bpy.ops.object.transform_apply(location=False, rotation=True, scale=True)


def parent(child, par):
    child.parent = par
    child.matrix_parent_inverse = par.matrix_world.inverted()


def count_tris(objs):
    return sum(sum(len(p.vertices) - 2 for p in o.data.polygons) for o in objs)


def _roblox_look(mat):
    """(r, g, b 0-255, Enum.Material) aproximado a partir del material de Blender."""
    bsdf = mat.node_tree.nodes["Principled BSDF"]
    glow = bsdf.inputs["Emission Strength"].default_value > 0
    col = bsdf.inputs["Emission Color" if glow else "Base Color"].default_value
    rgb = [round(255 * min(1.0, max(0.0, c)) ** (1 / 2.2)) for c in col[:3]]  # lineal -> sRGB
    if glow:
        kind = "Neon"
    elif bsdf.inputs["Metallic"].default_value >= 0.7:
        kind = "Metal"
    else:
        kind = "SmoothPlastic"
    return rgb, kind


def _split_by_material(objs):
    """Separa cada grupo en una malla por material: Base_Neon, Pivot_Blindaje, ..."""
    pieces = []
    for o in objs:
        o.select_set(True)
        bpy.context.view_layer.objects.active = o
        bpy.ops.object.parent_clear(type="CLEAR_KEEP_TRANSFORM")
    for o in objs:
        group = o.name
        bpy.ops.object.select_all(action="DESELECT")
        o.select_set(True)
        bpy.context.view_layer.objects.active = o
        bpy.ops.object.mode_set(mode="EDIT")
        bpy.ops.mesh.select_all(action="SELECT")
        bpy.ops.mesh.separate(type="MATERIAL")
        bpy.ops.object.mode_set(mode="OBJECT")
        for piece in list(bpy.context.selected_objects):
            used = {p.material_index for p in piece.data.polygons}
            mat = piece.data.materials[used.pop()]
            piece.data.materials.clear()
            piece.data.materials.append(mat)
            piece.name = piece.data.name = f"{group}_{mat.name}"
            pieces.append(piece)
    return pieces


_LUA = """-- Colores y materiales para {name} (generado automáticamente).
-- Uso: poné este Script dentro del Model importado, o seleccioná el Model
-- y pegá el código en la barra de comandos (View > Command Bar).
local COLORES = {{
{rows}
}}

local model = if script then script.Parent else game:GetService("Selection"):Get()[1]
local grupos = {{}}
for _, part in model:GetDescendants() do
\tif part:IsA("MeshPart") then
\t\tlocal c = COLORES[part.Name]
\t\tif c then
\t\t\tpart.Color = Color3.fromRGB(c[1], c[2], c[3])
\t\t\tpart.Material = c[4]
\t\tend
\t\t-- soldar cada pieza a la primera de su grupo (Base / Pivot / Barrel / Laser)
\t\tlocal grupo = string.match(part.Name, "^(%a+)_")
\t\tif grupo then
\t\t\tif grupos[grupo] then
\t\t\t\tlocal w = Instance.new("WeldConstraint")
\t\t\t\tw.Part0, w.Part1 = grupos[grupo], part
\t\t\t\tw.Parent = part
\t\t\telse
\t\t\t\tgrupos[grupo] = part
\t\t\tend
\t\tend
\tend
end
if grupos.Base then grupos.Base.Anchored = true end
print("Torreta lista:", model.Name)
"""


def export(out, name, objs):
    os.makedirs(out, exist_ok=True)
    print(f"TRIANGULOS {name}: {count_tris(objs)}")
    path = os.path.join(out, name)
    bpy.ops.wm.save_as_mainfile(filepath=path + ".blend", check_existing=False)
    for f in os.listdir(out):
        if f.endswith(".blend1"):
            os.remove(os.path.join(out, f))
    bpy.ops.object.select_all(action="DESELECT")
    bpy.ops.export_scene.gltf(filepath=path + ".glb", export_format="GLB")

    # FBX/OBJ para Roblox: una malla por material (Roblox usa un color/material por MeshPart)
    pieces = _split_by_material(objs)
    bpy.ops.object.select_all(action="DESELECT")
    for p in pieces:
        p.select_set(True)
    bpy.ops.export_scene.fbx(filepath=path + ".fbx", use_selection=True, apply_unit_scale=True,
                             object_types={"MESH"}, mesh_smooth_type="FACE", add_leaf_bones=False)
    bpy.ops.wm.obj_export(filepath=path + ".obj", export_materials=True, export_selected_objects=True,
                          forward_axis="NEGATIVE_Z", up_axis="Y")
    rows = []
    for p in sorted(pieces, key=lambda p: p.name):
        (r, g, b), kind = _roblox_look(p.data.materials[0])
        rows.append(f'\t["{p.name}"] = {{{r}, {g}, {b}, Enum.Material.{kind}}},')
    with open(os.path.join(out, "colores_roblox.lua"), "w", encoding="utf-8") as f:
        f.write(_LUA.format(name=name, rows="\n".join(rows)))
    # volver a los objetos originales para el render
    bpy.ops.wm.open_mainfile(filepath=path + ".blend")


def _light(name, loc, energy, size, target, color=(1, 1, 1)):
    data = bpy.data.lights.new(name, "AREA")
    data.energy, data.size, data.color = energy, size, color
    obj = bpy.data.objects.new(name, data)
    bpy.context.scene.collection.objects.link(obj)
    obj.location = loc
    obj.rotation_mode = "QUATERNION"
    obj.rotation_quaternion = (Vector(target) - Vector(loc)).to_track_quat("-Z", "Y")


def render(out, target=(0.4, 0, 2.2), dist=1.0, samples=None, res=None):
    """Renderiza vista frente / costado / atrás. `dist` escala la distancia de cámara."""
    scene = bpy.context.scene
    samples = int(os.environ.get("SAMPLES", samples or 64))
    res = int(os.environ.get("RES", res or 900))

    world = bpy.data.worlds.new("Mundo")
    scene.world = world
    world.use_nodes = True
    world.node_tree.nodes["Background"].inputs[0].default_value = (0.55, 0.7, 0.9, 1)
    world.node_tree.nodes["Background"].inputs[1].default_value = 0.5

    bpy.ops.mesh.primitive_plane_add(size=60, location=(0, 0, 0))
    bpy.context.active_object.data.materials.append(material("Piso", (0.75, 0.68, 0.5), 0.0, 0.9))

    t = Vector(target)
    _light("Key", t + Vector((6, -5, 6)) * dist, 1500 * dist ** 2, 5, t)
    _light("Fill", t + Vector((-6, -4, 2)) * dist, 500 * dist ** 2, 6, t, (0.7, 0.8, 1))
    _light("Rim", t + Vector((-3, 6, 4)) * dist, 800 * dist ** 2, 4, t, (0.9, 1, 0.9))

    cam = bpy.data.objects.new("Cam", bpy.data.cameras.new("Cam"))
    cam.data.lens = 50
    scene.collection.objects.link(cam)
    scene.camera = cam

    scene.render.engine = "CYCLES"
    scene.cycles.samples = samples
    scene.cycles.use_denoising = True
    scene.render.resolution_x = scene.render.resolution_y = res
    scene.view_settings.view_transform = "AgX"
    scene.view_settings.look = "AgX - Punchy"

    views = {
        "vista_frente": Vector((6.6, -8.5, 2.8)),
        "vista_costado": Vector((0.1, -11.0, 1.0)),
        "vista_atras": Vector((-8.4, 5.5, 3.3)),
    }
    for name, off in views.items():
        cam.location = t + off * dist
        cam.rotation_mode = "QUATERNION"
        cam.rotation_quaternion = (t - cam.location).to_track_quat("-Z", "Y")
        scene.render.filepath = os.path.join(out, f"{name}.png")
        bpy.ops.render.render(write_still=True)
