"""Exporta modelos "con color" para Roblox, sin depender de texturas.

Roblox a veces importa los .glb/.obj sin la textura de paleta y quedan grises. Esta versión separa cada parte
(Head, Torso, ...) en una pieza por color y le pone el color en el nombre: `Torso__1A6BFF` (o `Torso__1A6BFF_N`
si brilla). Después, en Roblox Studio, `pintar_colores.lua` lee ese nombre y pinta cada pieza (y pone Neon a las
que brillan). Todas las piezas de una parte comparten el pivote de su articulación.

Uso: python exportar_con_color.py zombi_basico jefe_comandante_escudo ...
Sale en modelos/con_color/<nombre>.glb, .obj y .mtl.
"""
import os
import sys

import bpy

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import lib_torretas as L  # noqa: E402

OUT = os.path.join(HERE, "con_color")


def find_blend(name):
    for root, _, files in os.walk(HERE):
        if name + ".blend" in files and "con_color" not in root:
            return os.path.join(root, name + ".blend")
    raise FileNotFoundError(name)


def glows(m):
    bsdf = m.node_tree.nodes["Principled BSDF"]
    return bsdf.inputs["Emission Strength"].default_value > 0 and max(bsdf.inputs["Emission Color"].default_value[:3]) > 0


def _fix_mtl(path):
    """Blender escribe Kd en valores lineales (salen muy oscuros): poner el color real RRGGBB/255 de cada material."""
    out, key = [], None
    for ln in open(path).read().split("\n"):
        if ln.startswith("newmtl C_"):
            key = ln.split("C_", 1)[1]
            out.append(ln)
            continue
        if key and ln.split(" ")[0] in ("Kd", "Ka", "Ke"):
            rgb = [int(key[i:i + 2], 16) / 255 for i in (0, 2, 4)]
            val = {"Kd": rgb, "Ka": [0, 0, 0], "Ke": rgb if key.endswith("_N") else [0, 0, 0]}[ln.split(" ")[0]]
            ln = ln.split(" ")[0] + " " + " ".join(f"{v:.6f}" for v in val)
        out.append(ln)
    open(path, "w").write("\n".join(out))


def export(name):
    bpy.ops.wm.open_mainfile(filepath=find_blend(name))
    meshes = [o for o in bpy.data.objects if o.type == "MESH"]
    cache = {}
    for ob in meshes:
        joint = ob.name
        bpy.ops.object.select_all(action="DESELECT")
        ob.select_set(True)
        bpy.context.view_layer.objects.active = ob
        if len(ob.data.materials) > 1:
            bpy.ops.mesh.separate(type="MATERIAL")
        pieces = [o for o in bpy.context.selected_objects]
        groups = {}
        for p in pieces:                                                       # agrupar piezas del mismo color
            m = p.data.materials[p.data.polygons[0].material_index] if p.data.polygons else p.data.materials[0]
            r, g, b = L._mat_rgb(m)
            key = "%02X%02X%02X" % (round(r * 255), round(g * 255), round(b * 255)) + ("_N" if glows(m) else "")
            groups.setdefault(key, []).append(p)
            if key not in cache:                                               # material plano con ese color
                flat = bpy.data.materials.new("C_" + key)
                flat.use_nodes = True
                bsdf = flat.node_tree.nodes["Principled BSDF"]
                lin = [c ** 2.2 for c in (r, g, b)]                             # sRGB -> lineal para el baseColorFactor
                bsdf.inputs["Base Color"].default_value = (*lin, 1)
                bsdf.inputs["Roughness"].default_value = 0.6
                cache[key] = flat
        for key, ps in groups.items():
            bpy.ops.object.select_all(action="DESELECT")
            for p in ps:
                p.select_set(True)
            bpy.context.view_layer.objects.active = ps[0]
            if len(ps) > 1:
                bpy.ops.object.join()
            o = bpy.context.view_layer.objects.active
            o.name = o.data.name = f"{joint}__{key}"
            o.data.materials.clear()
            o.data.materials.append(cache[key])
            # color por vértice (va adentro del mismo .obj como "v x y z r g b")
            hx = key[:6]
            rgb = tuple(int(hx[i:i + 2], 16) / 255 for i in (0, 2, 4))
            ca = o.data.color_attributes.new(name="Color", type="BYTE_COLOR", domain="POINT")
            for d in ca.data:
                d.color_srgb = (*rgb, 1.0)
            o.data.color_attributes.active_color = ca
    objs = [o for o in bpy.data.objects if o.type == "MESH"]
    os.makedirs(OUT, exist_ok=True)
    path = os.path.join(OUT, name)
    bpy.ops.object.select_all(action="DESELECT")
    bpy.ops.export_scene.gltf(filepath=path + ".glb", export_format="GLB")
    # export_object_groups: cada pieza sale como "g Nombre"; Roblox separa las mallas por grupo (sin esto junta
    # todo en una sola malla "default" y se pierden los nombres con el color)
    bpy.ops.wm.obj_export(filepath=path + ".obj", export_materials=True, path_mode="STRIP",
                          forward_axis="NEGATIVE_Z", up_axis="Y", export_object_groups=True, export_colors=True)
    lines = open(path + ".obj").read().split("\n")                           # "g X_X" (objeto_malla) -> "g X"
    for i, ln in enumerate(lines):
        if ln.startswith("g "):
            g = ln[2:]
            half = (len(g) - 1) // 2
            if len(g) % 2 == 1 and g[:half] == g[half + 1:]:
                lines[i] = "g " + g[:half]
    open(path + ".obj", "w").write("\n".join(lines))
    _fix_mtl(path + ".mtl")
    print(f"LISTO {name}: {len(objs)} piezas, {L.count_tris(objs)} triángulos")


if __name__ == "__main__":
    for n in sys.argv[1:]:
        export(n)
