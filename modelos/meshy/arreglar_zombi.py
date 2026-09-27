"""Arregla el Inferno Zombie de Meshy: piernas que salen por la espalda, textura de la espalda, y lo baja a <20k triángulos."""
import os
import sys

import bpy
import numpy as np
from mathutils import Matrix, Vector
from PIL import Image, ImageDraw

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

# 1) piernas: la parte de arriba sobresalía por detrás del torso (los "cubitos")
BACK = 0.275
for v in me.vertices:
    c = v.co
    if abs(c.x) < 0.5 and c.y > BACK and -0.52 < c.z < -0.18:
        t = min(1.0, max(0.0, (c.z + 0.52) / 0.24))
        c.y = c.y - (c.y - (BACK - 0.01)) * t
    # pierna derecha (-X): el bloque de arriba sobresalía hacia atrás de la pierna
    if -0.6 < c.x < 0.0 and c.y > 0.135 and -0.47 < c.z < (-0.225 if c.x < -0.28 else -0.295):
        c.y = 0.135
    if -0.62 < c.x < -0.36 and c.y > 0.1 and -0.36 < c.z < -0.18:                # bultito de la esquina
        c.z = max(c.z, -0.19)
        c.y = min(c.y, 0.2)

# 2) espalda de la camisa: pintar limpio (sin la R rota ni la mancha)
mat = me.materials[0]
img = next(n.image for n in mat.node_tree.nodes if n.type == "TEX_IMAGE" and n.outputs[0].links
           and n.outputs[0].links[0].to_socket.name == "Base Color")
W, H = img.size
px = np.array(img.pixels[:], dtype=np.float32).reshape(H, W, 4)
uv = me.uv_layers.active.data
polys = []
for f in me.polygons:
    c, n = f.center, f.normal
    if -0.46 < c.x < 0.55 and c.y > 0.16 and -0.26 < c.z < 0.46 and n.y > 0.3:
        polys.append([(uv[li].uv.x * W, (1 - uv[li].uv.y) * H) for li in f.loop_indices])
mask_img = Image.new("L", (W, H), 0)
d = ImageDraw.Draw(mask_img)
for p in polys:
    d.polygon(p, fill=255)
mask = np.array(mask_img)[::-1] > 0              # Blender guarda las filas de abajo hacia arriba
front = Image.new("L", (W, H), 0)                 # color de referencia: frente de la camisa
df = ImageDraw.Draw(front)
for f in me.polygons:
    c, n = f.center, f.normal
    if -0.45 < c.x < 0.0 and -0.25 < c.z < 0.1 and n.y < -0.8:
        df.polygon([(uv[li].uv.x * W, (1 - uv[li].uv.y) * H) for li in f.loop_indices], fill=255)
region = px[np.array(front)[::-1] > 0][:, :3]
lum = region.mean(axis=1)
yellowish = region[(region[:, 0] > region[:, 2] * 1.6) & (lum > np.percentile(lum, 55))]
base = np.median(yellowish, axis=0)
print("pixeles de la espalda:", mask.sum(), "color base:", base)
px[mask, :3] = base
img.pixels = px.ravel().tolist()
for node in mat.node_tree.nodes:                    # el relieve (normal map) también tenía la R: aplanarlo
    if node.type == "TEX_IMAGE" and any(l.to_node.type == "NORMAL_MAP" for l in node.outputs[0].links):
        nimg = node.image
        npx = np.array(nimg.pixels[:], dtype=np.float32).reshape(nimg.size[1], nimg.size[0], 4)
        m2 = mask if npx.shape[:2] == mask.shape else np.array(mask_img.resize(nimg.size))[::-1] > 0
        npx[m2, :3] = (0.5, 0.5, 1.0)
        nimg.pixels = npx.ravel().tolist()
        nimg.pack()
        print("normal map aplanado en la espalda")
img.filepath_raw = os.path.join(HERE, "inferno_zombie_textura.png")
img.file_format = "PNG"
img.save()

# 3) pies en el piso, altura 6 studs, y bajar a <20k triángulos
zmin = min(v.co.z for v in me.vertices)
s = 6.0 / (max(v.co.z for v in me.vertices) - zmin)
o.matrix_world = Matrix.Scale(s, 4) @ Matrix.Translation((0, 0, -zmin))
bpy.ops.object.transform_apply(location=True, rotation=True, scale=True)
tris = sum(len(p.vertices) - 2 for p in me.polygons)
mod = o.modifiers.new("Decimate", "DECIMATE")
mod.ratio = 19000 / tris
bpy.ops.object.modifier_apply(modifier=mod.name)
for p in me.polygons:
    p.use_smooth = True
print("TRIANGULOS:", sum(len(p.vertices) - 2 for p in me.polygons))

out = os.path.join(HERE, "inferno_zombie")
bpy.ops.wm.obj_export(filepath=out + ".obj", export_materials=True, path_mode="COPY", forward_axis="NEGATIVE_Z", up_axis="Y")
bpy.ops.export_scene.gltf(filepath=out + ".glb", export_format="GLB")
bpy.ops.wm.save_as_mainfile(filepath=out + ".blend")
if not os.environ.get("NO_RENDER"):
    L.render(os.path.join(HERE, "arreglado"), target=(0, 0, 3.0), dist=0.95,
             views={"frente": (0, -10, 1.5), "atras": (0, 10, 1.5), "nalgas": (1.2, 4.5, 0.2)})
print("LISTO")
