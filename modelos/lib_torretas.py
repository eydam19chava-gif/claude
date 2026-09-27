"""Utilidades compartidas para modelar torretas low-poly con bpy (Blender 4.2+).

Cada torreta se arma con piezas simples (cajas, cilindros, esferas, toroides) que
se biselan y se unen en grupos: Base (fija), Pivot (gira en Z) y Barrel (cañón,
gira en Y). Todas apuntan a +X. `export` saca .blend/.fbx/.glb/.obj y `render`
genera vistas previas.
"""
import math
import os
import shutil

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


def _mat_rgb(mat):
    """Color sRGB (0-1) de un material: su emisión si brilla, si no su color base."""
    bsdf = mat.node_tree.nodes["Principled BSDF"]
    glow = bsdf.inputs["Emission Strength"].default_value > 0
    col = bsdf.inputs["Emission Color" if glow else "Base Color"].default_value
    # lineal -> casi sRGB (gamma 1.8) y un poco más de saturación, para que en Roblox se parezca al render
    c = [min(1.0, max(0.0, v)) ** (1 / 1.8) for v in col[:3]]
    lum = 0.3 * c[0] + 0.59 * c[1] + 0.11 * c[2]
    return [min(1.0, max(0.0, lum + (v - lum) * 1.25)) for v in c]


def _bake_palette(objs, png_path, cells=None, cell_px=16):
    """Pinta todos los materiales en una textura de paleta y deja un solo material con esa imagen.

    Así el color viaja dentro de la textura (y dentro del .glb), que es lo que Roblox respeta.
    """
    mats = []
    for o in objs:
        for m in o.data.materials:
            if m not in mats:
                mats.append(m)
    cells = cells or max(8, math.ceil(math.sqrt(len(mats))))
    size = cells * cell_px
    img = bpy.data.images.new("Paleta", size, size, alpha=False)
    px = [0.0] * (size * size * 4)
    for i, m in enumerate(mats):
        cx, cy = i % cells, i // cells
        r, g, b = _mat_rgb(m)
        for y in range(cy * cell_px, (cy + 1) * cell_px):
            for x in range(cx * cell_px, (cx + 1) * cell_px):
                j = (y * size + x) * 4
                px[j:j + 4] = [r, g, b, 1.0]
    img.pixels = px
    img.filepath_raw = png_path
    img.file_format = "PNG"
    img.save()

    pal = bpy.data.materials.new("Paleta")
    pal.use_nodes = True
    nodes = pal.node_tree.nodes
    bsdf = nodes["Principled BSDF"]
    bsdf.inputs["Metallic"].default_value = 0.3
    bsdf.inputs["Roughness"].default_value = 0.5
    tex = nodes.new("ShaderNodeTexImage")
    tex.image = img
    tex.interpolation = "Closest"
    pal.node_tree.links.new(tex.outputs["Color"], bsdf.inputs["Base Color"])

    for o in objs:
        me = o.data
        uv = me.uv_layers.active or me.uv_layers.new(name="UVMap")
        for poly in me.polygons:
            i = mats.index(me.materials[poly.material_index])
            u = ((i % cells) + 0.5) / cells
            v = ((i // cells) + 0.5) / cells
            for li in poly.loop_indices:
                uv.data[li].uv = (u, v)
        me.materials.clear()
        me.materials.append(pal)


def export(out, name, objs):
    """Guarda el .blend original y exporta para Roblox con color en textura de paleta.

    - <name>.glb : UN solo archivo con la textura adentro (recomendado para Roblox).
    - <name>.obj + <name>.mtl + <name>_paleta.png : versión OBJ (el color va en el PNG).
    - <name>.fbx : con la textura incrustada.
    """
    os.makedirs(out, exist_ok=True)
    print(f"TRIANGULOS {name}: {count_tris(objs)}")
    path = os.path.join(out, name)
    bpy.ops.wm.save_as_mainfile(filepath=path + ".blend", check_existing=False)
    for f in os.listdir(out):
        if f.endswith(".blend1") or f == "colores_roblox.lua":
            os.remove(os.path.join(out, f))

    _bake_palette(objs, path + "_paleta.png")
    bpy.ops.object.select_all(action="DESELECT")
    bpy.ops.export_scene.gltf(filepath=path + ".glb", export_format="GLB")
    bpy.ops.export_scene.fbx(filepath=path + ".fbx", apply_unit_scale=True, object_types={"MESH"},
                             mesh_smooth_type="FACE", add_leaf_bones=False, path_mode="COPY", embed_textures=True)
    bpy.ops.wm.obj_export(filepath=path + ".obj", export_materials=True, path_mode="STRIP",
                          forward_axis="NEGATIVE_Z", up_axis="Y")
    # copia de un solo archivo por torreta en modelos/roblox/
    roblox_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "roblox")
    os.makedirs(roblox_dir, exist_ok=True)
    shutil.copy(path + ".glb", os.path.join(roblox_dir, name + ".glb"))
    # volver a los materiales originales para el render
    bpy.ops.wm.open_mainfile(filepath=path + ".blend")


def _light(name, loc, energy, size, target, color=(1, 1, 1)):
    data = bpy.data.lights.new(name, "AREA")
    data.energy, data.size, data.color = energy, size, color
    obj = bpy.data.objects.new(name, data)
    bpy.context.scene.collection.objects.link(obj)
    obj.location = loc
    obj.rotation_mode = "QUATERNION"
    obj.rotation_quaternion = (Vector(target) - Vector(loc)).to_track_quat("-Z", "Y")


def render(out, target=(0.4, 0, 2.2), dist=1.0, samples=None, res=None, views=None):
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

    views = {k: Vector(v) for k, v in views.items()} if views else {
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
