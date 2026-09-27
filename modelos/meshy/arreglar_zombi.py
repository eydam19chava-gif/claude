"""Arregla el Inferno Zombie de Meshy: piernas que salen por la espalda, textura de la espalda, y lo baja a <20k triángulos."""
import math
import os
import sys

import bpy
import bmesh  # noqa: E402  (bmesh necesita bpy cargado antes)
import numpy as np
from mathutils import Matrix, Vector
from PIL import Image, ImageDraw, ImageFilter

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))
import lib_torretas as L  # noqa: E402

HERE = os.path.dirname(os.path.abspath(__file__))
L.reset()
bpy.ops.import_scene.gltf(filepath=os.path.join(HERE, "inferno_zombie_original.glb"))
o = bpy.data.objects["Mesh_0"]
o.name = o.data.name = "InfernoZombie"
bpy.context.view_layer.objects.active = o
o.select_set(True)
bpy.ops.object.transform_apply(location=True, rotation=True, scale=True)
me = o.data

# La espalda del torso de Meshy es una malla rota (R mal hecha, mancha, grietas, y la parte de arriba de las
# piernas asomando como 2 cubitos). En vez de parcharla: se borra la mitad de atrás del torso y se pone una
# caja limpia con el mismo amarillo. El torso está girado ~14.6° en Z, así que se trabaja en su sistema local.
mat = me.materials[0]
img = next(n.image for n in mat.node_tree.nodes if n.type == "TEX_IMAGE" and n.outputs[0].links
           and n.outputs[0].links[0].to_socket.name == "Base Color")
W, H = img.size
px = np.array(img.pixels[:], dtype=np.float32).reshape(H, W, 4)
uv = me.uv_layers.active.data
vcol = np.zeros((len(me.vertices), 3), dtype=np.float32)
for l in me.loops:
    u, v = uv[l.index].uv
    vcol[l.vertex_index] = px[min(H - 1, max(0, int(v * H))), min(W - 1, max(0, int(u * W))), :3]
vmax = vcol.max(1)
gris = ((vmax - vcol.min(1)) / (vmax + 1e-6) < 0.15) & (vmax > 0.3)
oscuro = vmax < 0.22                                   # brazo de corrupción

YAW = math.atan(0.26)
CY, SY = math.cos(YAW), math.sin(YAW)
def local(p):                                          # (ancho, profundidad hacia atrás, alto)
    return p.x * CY + p.y * SY, -p.x * SY + p.y * CY, p.z
X0, X1, MID, BACK, Z0, Z1 = -0.385, 0.405, 0.02, 0.228, -0.30, 0.52

bm = bmesh.new()
bm.from_mesh(me)
bm.faces.ensure_lookup_table()
borrar, tex_mask = [], Image.new("L", (W, H), 0)
dm = ImageDraw.Draw(tex_mask)
uvl = bm.loops.layers.uv.active
for f in bm.faces:
    if any(oscuro[v.index] for v in f.verts):
        continue
    if all(X0 - 0.01 < local(v.co)[0] < X1 + 0.01 and local(v.co)[1] > MID and Z0 - 0.01 < v.co.z < Z1 + 0.01
           for v in f.verts):
        borrar.append(f)
        dm.polygon([(l[uvl].uv.x * W, (1 - l[uvl].uv.y) * H) for l in f.loops], fill=255)
bmesh.ops.delete(bm, geom=borrar, context="FACES")
# lo que queda de las piernas asomando por arriba del borde del torso: aplastarlo al borde de abajo
aplast = 0
for v in bm.verts:
    if gris[v.index] and Z0 < v.co.z < -0.1 and local(v.co)[1] > 0.1 and X0 - 0.1 < local(v.co)[0] < X1 + 0.1:
        v.co.z = Z0
        aplast += 1
bm.to_mesh(me)
bm.free()
print("caras borradas de la espalda:", len(borrar), "| vertices de piernas aplastados:", aplast)

# color: el amarillo del frente de la camisa
front = Image.new("L", (W, H), 0)
df = ImageDraw.Draw(front)
for f in me.polygons:
    c, n = f.center, f.normal
    if -0.3 < c.x < 0.0 and -0.2 < c.z < 0.1 and n.y < -0.8:
        df.polygon([(uv[li].uv.x * W, (1 - uv[li].uv.y) * H) for li in f.loop_indices], fill=255)
region = px[np.array(front)[::-1] > 0][:, :3]
lum = region.mean(axis=1)
base = np.median(region[(region[:, 0] > region[:, 2] * 1.6) & (lum > np.percentile(lum, 60))], axis=0)
# las islas de textura de lo borrado quedan libres: se pintan de amarillo y la caja nueva usa un pixel del medio
libre = np.array(tex_mask)[::-1] > 0
px[libre, :3] = base
img.pixels = px.ravel().tolist()
er = tex_mask
for _ in range(6):
    nxt = er.filter(ImageFilter.MinFilter(9))
    if not np.array(nxt).any():
        break
    er = nxt
ys, xs = np.nonzero(np.array(er))
PU, PV = (xs[len(xs) // 2] + 0.5) / W, 1 - (ys[len(ys) // 2] + 0.5) / H
print("color base:", base, "| pixel de la caja:", PU, PV)
for node in mat.node_tree.nodes:                        # relieve plano en esa zona
    if node.type == "TEX_IMAGE" and any(l.to_node.type == "NORMAL_MAP" for l in node.outputs[0].links):
        nimg = node.image
        npx = np.array(nimg.pixels[:], dtype=np.float32).reshape(nimg.size[1], nimg.size[0], 4)
        m2 = libre if npx.shape[:2] == libre.shape else np.array(tex_mask.resize(nimg.size))[::-1] > 0
        npx[m2, :3] = (0.5, 0.5, 1.0)
        nimg.pixels = npx.ravel().tolist()
        nimg.pack()
img.filepath_raw = os.path.join(HERE, "inferno_zombie_textura.png")
img.file_format = "PNG"
img.save()

# caja nueva de la espalda (con borde redondeado)
bpy.ops.mesh.primitive_cube_add(size=1)
caja = bpy.context.active_object
ZB = Z0 - 0.025                                        # un poquito más abajo: tapa el borde de las piernas
caja.scale = (X1 - X0, BACK - MID, Z1 - ZB)
caja.location = ((X0 + X1) / 2, (MID + BACK) / 2, (ZB + Z1) / 2)
bpy.ops.object.transform_apply(location=True, rotation=False, scale=True)
bev = caja.modifiers.new("Bevel", "BEVEL")
bev.width, bev.segments = 0.035, 3
bpy.ops.object.modifier_apply(modifier=bev.name)
caja.matrix_world = Matrix.Rotation(YAW, 4, "Z")
bpy.ops.object.transform_apply(location=True, rotation=True, scale=True)
caja.data.materials.append(mat)
cuv = caja.data.uv_layers.active.data
for d in cuv:
    d.uv = (PU, PV)
for p in caja.data.polygons:
    p.use_smooth = False
bpy.ops.object.select_all(action="DESELECT")
o.select_set(True)
bpy.context.view_layer.objects.active = o

# 3) pies en el piso, altura 6 studs, y bajar a <20k triángulos
zmin = min(v.co.z for v in me.vertices)
s = 6.0 / (max(v.co.z for v in me.vertices) - zmin)
o.matrix_world = Matrix.Scale(s, 4) @ Matrix.Translation((0, 0, -zmin))
bpy.ops.object.transform_apply(location=True, rotation=True, scale=True)
tris = sum(len(p.vertices) - 2 for p in me.polygons)
mod = o.modifiers.new("Decimate", "DECIMATE")
mod.ratio = 18700 / tris
bpy.ops.object.modifier_apply(modifier=mod.name)
for p in me.polygons:
    p.use_smooth = True
caja.matrix_world = Matrix.Scale(s, 4) @ Matrix.Translation((0, 0, -zmin))
bpy.ops.object.select_all(action="DESELECT")
caja.select_set(True)
o.select_set(True)
bpy.context.view_layer.objects.active = o
bpy.ops.object.join()
print("TRIANGULOS:", sum(len(p.vertices) - 2 for p in me.polygons))

out = os.path.join(HERE, "inferno_zombie")
bpy.ops.wm.obj_export(filepath=out + ".obj", export_materials=True, path_mode="COPY", forward_axis="NEGATIVE_Z", up_axis="Y")
bpy.ops.export_scene.gltf(filepath=out + ".glb", export_format="GLB")
bpy.ops.wm.save_as_mainfile(filepath=out + ".blend")
if not os.environ.get("NO_RENDER"):
    L.render(os.path.join(HERE, "arreglado"), target=(0, 0, 3.0), dist=0.95,
             views={"frente": (0, -10, 1.5), "atras": (0, 10, 1.5), "nalgas": (1.2, 4.5, 0.2),
                    "costado": (10, 2, 1.5), "tres_cuartos": (-7, 7, 2.5)})
print("LISTO")
