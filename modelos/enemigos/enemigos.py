"""Enemigos del Tower Defense: zombis estilo bloque (tipo Roblox R6) con variantes y jefes.

Cada enemigo se exporta separado en partes con el pivote en su articulación, para animarlo
con Motor6D en Roblox:  Head (cuello), Torso (centro), LeftArm / RightArm (hombros),
LeftLeg / RightLeg (caderas). Los accesorios van pegados a la parte que corresponde.
El enemigo mira hacia -Y. Pies en z = 0.

Uso: python enemigos.py [nombre ...]   (sin nombres arma todos)
"""
import os
import random
import shutil
import sys

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))
import bpy  # noqa: E402
import lib_torretas as L  # noqa: E402
import rbxmx  # noqa: E402
from lib_torretas import Matrix, Vector, box, cone, cyl, join, math, rod, sphere, strut, torus  # noqa: E402

HERE = os.path.dirname(os.path.abspath(__file__))


def mat(name, color, metallic=0.0, rough=0.7, emission=None, strength=3.0):
    return bpy.data.materials.get(name) or L.material(name, color, metallic, rough, emission, strength)


def base_mats():
    return dict(
        BLACK=mat("Negro", (0.02, 0.02, 0.02)),
        WHITE=mat("Hueso", (0.9, 0.88, 0.8)),
        TEETH=mat("Dientes", (0.85, 0.8, 0.55)),
        MOUTH=mat("Boca", (0.25, 0.02, 0.03)),
        SHOE=mat("Zapato", (0.12, 0.08, 0.06)),
        METAL=mat("Metal", (0.45, 0.47, 0.5), 0.8, 0.35),
        DARKM=mat("Metal_Oscuro", (0.1, 0.1, 0.12), 0.7, 0.45),
        GOLD=mat("Oro", (1.0, 0.72, 0.2), 1.0, 0.25),
        BLOOD=mat("Sangre", (0.35, 0.02, 0.02)),
        WOOD=mat("Madera", (0.35, 0.2, 0.1)),
    )


# ------------------------------------------------------------------ cuerpo base
def humanoid(skin, shirt, pants, eye, K, s=1.0, w=1.0, arms="forward", legs="stand", rng=None, torn=True,
             no_legs=False, hunch=0.0, hand=None, hand_size=1.0, hair=None, arm_len=1.0):
    """Devuelve (partes por articulación, pivotes). s = escala general, w = ancho de brazos/piernas."""
    rng = rng or random.Random(1)
    P = {k: [] for k in ("Head", "Torso", "LeftArm", "RightArm", "LeftLeg", "RightLeg")}
    hip_z, sh_z, neck_z = 2.0 * s, 3.8 * s, 4.0 * s
    piv = dict(Torso=Vector((0, 0, 3.0 * s)), Head=Vector((0, -hunch * s, neck_z)),
               LeftArm=Vector((-1.5 * s, 0, sh_z)), RightArm=Vector((1.5 * s, 0, sh_z)),
               LeftLeg=Vector((-0.5 * s, 0, hip_z)), RightLeg=Vector((0.5 * s, 0, hip_z)))
    # torso con camisa rota
    T = P["Torso"]
    T.append(box((2.0 * s, 1.0 * s, 2.0 * s), piv["Torso"], shirt, rot=(-hunch * 0.3, 0, 0), bevel=0.08 * s))
    if torn:
        for k in range(5):                                                      # borde desgarrado
            x = (-0.8 + k * 0.4) * s
            T.append(cone(0.18 * s, 0.35 * s, Vector((x, -0.3 * s, hip_z - 0.05 * s)), shirt, rot=(math.pi, 0, 0), verts=3))
        T.append(box((0.6 * s, 0.05 * s, 0.5 * s), piv["Torso"] + Vector((0.45 * s, -0.51 * s, -0.2 * s)), skin,
                     bevel=0))                                                  # piel a la vista
        for k in range(3):                                                      # costillas
            T.append(box((0.45 * s, 0.03 * s, 0.07 * s), piv["Torso"] + Vector((0.45 * s, -0.54 * s, (-0.05 - k * 0.15) * s)),
                         K["WHITE"], bevel=0))
        T.append(box((0.3 * s, 0.05 * s, 0.25 * s), piv["Torso"] + Vector((-0.5 * s, -0.51 * s, 0.4 * s)), K["BLOOD"], bevel=0))
    T.append(box((2.05 * s, 1.05 * s, 0.2 * s), Vector((0, 0, hip_z + 0.1 * s)), K["SHOE"], bevel=0.03 * s))  # cinturón
    # cabeza
    H = P["Head"]
    hc = piv["Head"] + Vector((0, 0, 0.62 * s))
    H.append(box((1.25 * s, 1.2 * s, 1.2 * s), hc, skin, bevel=0.14 * s))
    for sx in (-1, 1):
        H.append(box((0.32 * s, 0.06 * s, 0.26 * s), hc + Vector((sx * 0.3 * s, -0.6 * s, 0.12 * s)), K["BLACK"], bevel=0))
        H.append(box((0.16 * s, 0.07 * s, 0.14 * s), hc + Vector((sx * 0.3 * s, -0.62 * s, 0.12 * s)), eye, bevel=0))
    H.append(box((0.6 * s, 0.06 * s, 0.22 * s), hc + Vector((0, -0.6 * s, -0.28 * s)), K["MOUTH"], bevel=0))
    for k in range(4):
        H.append(box((0.1 * s, 0.07 * s, 0.1 * s), hc + Vector(((-0.22 + k * 0.15) * s, -0.62 * s, -0.2 * s)), K["TEETH"], bevel=0))
    H.append(box((0.05 * s, 0.07 * s, 0.4 * s), hc + Vector((-0.5 * s, -0.6 * s, 0.0)), K["BLACK"], rot=(0, 0.5, 0), bevel=0))  # cicatriz
    if hair:
        for k in range(7):                                                      # mechones
            H.append(box((0.3 * s, 0.3 * s, 0.25 * s), hc + Vector((rng.uniform(-0.45, 0.45) * s, rng.uniform(-0.4, 0.45) * s, 0.62 * s)),
                         hair, rot=(rng.uniform(-0.3, 0.3), rng.uniform(-0.3, 0.3), rng.uniform(0, 1)), bevel=0.05 * s))
    # brazos
    for side, name in ((-1, "LeftArm"), (1, "RightArm")):
        sp = piv[name]
        if arms == "forward":
            tip = sp + Vector((0.05 * side * s, -1.9 * s, -0.25 * s + rng.uniform(-0.15, 0.15) * s))
        elif arms == "up":
            tip = sp + Vector((0.4 * side * s, -0.3 * s, 1.8 * s))
        else:
            tip = sp + Vector((0.15 * side * s, 0, -1.9 * s * arm_len))
        mid = sp.lerp(tip, 0.5)
        piv[name + "_mid"], piv[name + "_tip"] = mid, tip
        P[name].append(strut(sp, mid, 0.95 * w * s, 0.95 * w * s, shirt, bevel=0.06 * s))
        P[name].append(strut(mid, tip, 0.85 * w * s, 0.85 * w * s, skin, bevel=0.06 * s))
        d = (tip - sp).normalized()
        piv[name + "_hand"] = tip                                               # sin manos: brazo liso estilo Roblox
        for k in range(2):                                                      # manga rota
            P[name].append(cone(0.14 * w * s, 0.3 * s, mid + d * 0.1 * s + Vector(((k - 0.5) * 0.4 * w * s, 0, 0)),
                                shirt, rot=d, verts=3))
    # piernas
    if not no_legs:
        for side, name in ((-1, "LeftLeg"), (1, "RightLeg")):
            hp = piv[name]
            step = {"stand": 0.0, "run": 0.6 * side}[legs]
            foot = hp + Vector((0, step * s, -1.9 * s))
            mid = hp.lerp(foot, 0.55)
            piv[name + "_mid"], piv[name + "_foot"] = mid, foot
            P[name].append(strut(hp, mid, 0.95 * w * s, 0.95 * w * s, pants, bevel=0.06 * s))
            P[name].append(strut(mid, foot, 0.9 * w * s, 0.9 * w * s, skin if torn and side > 0 else pants, bevel=0.06 * s))
            P[name].append(box((1.0 * w * s, 1.25 * s, 0.3 * s), foot + Vector((0, -0.15 * s, 0.05 * s)), K["SHOE"], bevel=0.08 * s))
    return P, piv


def finish(P, piv, name_scale=1.0):
    objs = []
    for part, parts in P.items():
        if parts:
            objs.append(join(parts, part, piv[part]))
    return objs


# ------------------------------------------------------------------ variantes
# ------------------------------------------------------------------ zombi básico (R6 clásico, sin cara, detallado)
# Proporciones R6 exactas: cabeza redonda, torso 2x1x2, brazos y piernas 1x1x2. El frente de la cabeza es liso (sin cara),
# va descalzo y sin uñas. Brazos estirados hacia adelante. Su derecha está en -X.
ZB_PIV = dict(Head=Vector((0, 0, 4.0)), Torso=Vector((0, 0, 3.0)),
           RightArm=Vector((-1.5, 0, 3.5)), LeftArm=Vector((1.5, 0, 3.5)),
           RightLeg=Vector((-0.5, 0, 2.0)), LeftLeg=Vector((0.5, 0, 2.0)))
ZB_HEAD = Vector((0, 0, 4.6))            # centro de la cabeza
ZB_E = 0.02                               # despegue de los "calcos" sobre la superficie


def _zb_mats():
    return dict(
        SKIN=mat("Piel_Zombi", (0.30, 0.52, 0.18)),
        ROT=mat("Piel_Podrida", (0.18, 0.32, 0.10)),
        SHIRT=mat("Camisa_Celeste", (0.10, 0.28, 0.50)),
        SHIRT2=mat("Camisa_Oscura", (0.05, 0.14, 0.28)),
        PANTS=mat("Pantalon_Marron", (0.24, 0.14, 0.07)),
        PATCH=mat("Parche_Jean", (0.16, 0.22, 0.38)),
        MUD=mat("Barro", (0.17, 0.11, 0.06)),
        DIRT=mat("Tierra", (0.26, 0.20, 0.10)),
        BELT=mat("Cinturon", (0.10, 0.06, 0.04)),
        BUCKLE=mat("Hebilla", (0.55, 0.55, 0.58), 0.9, 0.3),
        BLOOD=mat("Sangre", (0.30, 0.01, 0.01), rough=0.3),
        BLOOD2=mat("Sangre_Seca", (0.16, 0.02, 0.02)),
        FLESH=mat("Carne", (0.50, 0.08, 0.09), rough=0.4),
        BONE=mat("Hueso", (0.88, 0.85, 0.74)),
        BRAIN=mat("Cerebro", (0.85, 0.45, 0.50), rough=0.35),
        STITCH=mat("Costura", (0.03, 0.03, 0.03)),
        BANDAGE=mat("Venda", (0.82, 0.78, 0.66)),
        RUST=mat("Oxido", (0.35, 0.18, 0.08), 0.6, 0.6),
    )


def _zb_front(P, part, size, x, z, y, m, rot=0.0):
    """Calco plano sobre una cara que mira a -Y (y = cara frontal) o +Y si y > 0."""
    sy = 1 if y > 0 else -1
    P[part].append(box((size[0], 0.04, size[1]), Vector((x, y + sy * ZB_E, z)), m, rot=(0, rot, 0), bevel=0))


def _zb_side(P, part, size, x, y, z, m, rot=0.0):
    """Calco plano sobre una cara lateral (x = cara)."""
    sx = 1 if x > 0 else -1
    P[part].append(box((0.04, size[0], size[1]), Vector((x + sx * ZB_E, y, z)), m, rot=(rot, 0, 0), bevel=0))


def _zb_vtri(P, part, x, z, y, r, m):
    """Triángulo plano que apunta hacia abajo, pegado a la cara frontal (y < 0) o trasera (y > 0)."""
    sy = 1 if y > 0 else -1
    P[part].append(cone(r, 0.04, Vector((x, y + sy * ZB_E, z)), m, rot=(math.pi / 2, math.pi / 2, 0), verts=3))


def _zb_jagged_ring(P, part, cx, cy, z, w, d, m, rng, n=4, size=0.16, down=True):
    """Borde desgarrado: dientes triangulares alrededor de una caja (w x d) a la altura z."""
    pts = []  # (x, y)
    for k in range(n):
        t = (k + 0.5) / n
        pts += [(cx - w / 2 + t * w, cy - d / 2 - ZB_E), (cx - w / 2 + t * w, cy + d / 2 + ZB_E)]
    for k in range(max(2, n // 2)):
        t = (k + 0.5) / max(2, n // 2)
        pts += [(cx - w / 2 - ZB_E, cy - d / 2 + t * d), (cx + w / 2 + ZB_E, cy - d / 2 + t * d)]
    for x, y in pts:
        h = size * rng.uniform(0.7, 1.4)
        c = Vector((x, y, z - h / 2 if down else z + h / 2))
        P[part].append(cone(size * rng.uniform(0.6, 0.9), h, c, m, rot=(math.pi if down else 0, 0, 0), verts=3))


def _zb_stitches(P, part, a, b, normal, m, n=5, w=0.03, cross=0.18):
    """Costura: línea de a a b con puntadas cruzadas, pegada a la superficie con esa normal."""
    a, b, nrm = Vector(a), Vector(b), Vector(normal)
    P[part].append(strut(a, b, w, w, m, bevel=0))
    d = (b - a).normalized()
    perp = d.cross(nrm).normalized()
    for k in range(n):
        c = a.lerp(b, (k + 0.5) / n)
        P[part].append(strut(c - perp * cross / 2, c + perp * cross / 2, w, w, m, bevel=0))


# ------------------------------------------------------------------ partes
def _zb_torso(P, K, rng, chest=True):
    T = "Torso"
    P[T].append(box((2, 1, 2), (0, 0, 3), K["SHIRT"], bevel=0.03))
    P[T].append(box((0.7, 0.7, 0.12), (0, 0, 4.03), K["SKIN"], bevel=0.02))                     # cuello
    # cuello en V roto: triángulo de piel, borde de la remera y una cadenita oxidada
    _zb_vtri(P, T, 0, 3.8, -0.5, 0.36, K["SKIN"])
    P[T].append(box((0.8, 0.8, 0.07), (0, 0, 4.0), K["SHIRT2"], bevel=0.02))
    for sx in (-1, 1):
        P[T].append(strut(Vector((sx * 0.02, -0.53, 3.6)), Vector((sx * 0.33, -0.53, 3.98)), 0.07, 0.04, K["SHIRT2"], bevel=0))
    for k in range(6):
        t = (k + 0.5) / 6
        P[T].append(box((0.06, 0.04, 0.06), Vector((-0.3 + 0.6 * t, -0.55, 3.95 - math.sin(t * math.pi) * 0.42)), K["RUST"],
                        rot=(0, math.pi / 4, 0), bevel=0))
    # borde de abajo desgarrado (la camisa cuelga sobre el cinturón)
    _zb_jagged_ring(P, T, 0, 0, 2.32, 2.0, 1.0, K["SHIRT"], rng, n=6, size=0.17)
    # cinturón con hebilla
    P[T].append(box((2.04, 1.04, 0.22), (0, 0, 2.11), K["BELT"], bevel=0.02))
    P[T].append(box((0.34, 0.06, 0.26), (0.15, -0.53, 2.11), K["BUCKLE"], bevel=0.02))
    P[T].append(box((0.2, 0.07, 0.12), (0.15, -0.54, 2.11), K["BELT"], bevel=0))
    for x in (-0.6, 0.75):                                                       # presillas
        P[T].append(box((0.08, 0.06, 0.28), (x, -0.53, 2.11), K["BELT"], bevel=0))

    # agujero grande en el pecho: piel, carne y costillas
    hc = Vector((0.45, -0.5, 3.05))
    _zb_front(P, T, (0.85, 0.8), hc.x, hc.z, -0.5, K["SKIN"])
    _zb_front(P, T, (0.6, 0.55), hc.x, hc.z, -0.52, K["FLESH"])
    for k in range(3):
        P[T].append(box((0.55, 0.06, 0.08), (hc.x, -0.57, hc.z + 0.18 - k * 0.17), K["BONE"], rot=(0, 0.08 * (k - 1), 0), bevel=0.01))
    for k in range(10):                                                          # tela rota alrededor del agujero
        a = k / 10 * 2 * math.pi
        p = Vector((hc.x + math.cos(a) * 0.46, -0.53, hc.z + math.sin(a) * 0.43))
        _zb_front(P, T, (0.15, 0.15), p.x, p.z, -0.51, K["SHIRT"], rot=math.pi / 4)
    # sangre que chorrea del agujero
    for k, (x, ln) in enumerate(((0.3, 0.55), (0.55, 0.35), (0.7, 0.7))):
        _zb_front(P, T, (0.09, ln), x, hc.z - 0.38 - ln / 2, -0.51, K["BLOOD"])
        P[T].append(sphere(0.07, (x, -0.54, hc.z - 0.38 - ln), K["BLOOD"], subdiv=1, scale=(1, 0.5, 1.2)))

    # zarpazo en el pecho izquierdo (lado -X es su derecha). chest=False deja libre ese lado para un emblema
    for k in range(3 if chest else 0):
        _zb_front(P, T, (0.07, 0.75), -0.75 + k * 0.17, 3.45 - k * 0.03, -0.5, K["FLESH"], rot=0.55)
        _zb_front(P, T, (0.03, 0.6), -0.75 + k * 0.17, 3.45 - k * 0.03, -0.52, K["BLOOD"], rot=0.55)
    # manchas de sangre seca
    for _ in range(6):
        _zb_front(P, T, (rng.uniform(0.12, 0.3), rng.uniform(0.1, 0.25)), rng.uniform(-0.85, -0.1), rng.uniform(2.4, 3.1), -0.5,
              K["BLOOD2"], rot=rng.uniform(0, 3))
    # bolsillo roto en el pecho derecho (lado -X)
    if chest:
        _zb_front(P, T, (0.42, 0.42), -0.5, 3.55, -0.5, K["SHIRT2"])
        P[T].append(box((0.44, 0.05, 0.06), (-0.5, -0.53, 3.75), K["SHIRT"], bevel=0))
        _zb_vtri(P, T, -0.35, 3.3, -0.53, 0.1, K["SHIRT2"])                            # esquina colgando
    for _ in range(4):                                                            # barro
        _zb_front(P, T, (rng.uniform(0.15, 0.3), rng.uniform(0.08, 0.15)), rng.uniform(-0.9, 0.9), rng.uniform(2.3, 2.6), -0.5,
              K["DIRT"], rot=rng.uniform(-0.3, 0.3))
    # parche cosido a la camisa
    _zb_front(P, T, (0.38, 0.32), -0.55, 2.65, -0.5, K["SHIRT2"], rot=0.12)
    _zb_stitches(P, T, (-0.75, -0.55, 2.82), (-0.35, -0.55, 2.86), (0, -1, 0), K["STITCH"], n=4, w=0.025, cross=0.1)

    # espalda: desgarro con columna a la vista
    _zb_front(P, T, (0.7, 1.2), 0, 3.05, 0.5, K["SKIN"])
    _zb_front(P, T, (0.5, 1.0), 0, 3.05, 0.52, K["FLESH"])
    for k in range(5):
        P[T].append(box((0.22, 0.1, 0.13), (0, 0.58, 3.5 - k * 0.22), K["BONE"], bevel=0.02))
        P[T].append(box((0.4, 0.07, 0.04), (0, 0.57, 3.5 - k * 0.22), K["BONE"], bevel=0))
    for k in range(8):
        a = k / 8 * 2 * math.pi
        p = Vector((math.cos(a) * 0.4, 0.53, 3.05 + math.sin(a) * 0.65))
        _zb_front(P, T, (0.15, 0.15), p.x, p.z, 0.51, K["SHIRT"], rot=math.pi / 4)
    for _ in range(4):
        _zb_front(P, T, (rng.uniform(0.15, 0.3), rng.uniform(0.12, 0.3)), rng.uniform(-0.85, 0.85), rng.uniform(2.4, 3.8), 0.5,
              K["BLOOD2"], rot=rng.uniform(0, 3))
    # tiras de tela colgando a los costados
    for sx, z in ((-1, 2.35), (1, 2.5)):
        P[T].append(box((0.04, 0.22, 0.55), (sx * (1.0 + ZB_E), -0.15, z - 0.25), K["SHIRT"], rot=(0.15 * sx, 0, 0), bevel=0))
        _zb_side(P, T, (0.25, 0.3), sx * 1.0, 0.2, 3.3, K["BLOOD2"])


def _zb_head(P, K, rng):
    H = "Head"
    # cabeza redonda clásica de Roblox (cilindro con bordes redondeados). Sin cara.
    P[H].append(cyl(0.62, 1.2, ZB_HEAD, K["SKIN"], verts=24, bevel=0.16))
    # cerebro expuesto arriba (lado izquierdo, +X)
    bc = ZB_HEAD + Vector((0.2, 0.1, 0.6))
    P[H].append(cyl(0.3, 0.06, bc, K["FLESH"], verts=12, bevel=0))
    P[H].append(sphere(0.27, bc + Vector((0, 0, 0.02)), K["BRAIN"], subdiv=2, scale=(1, 0.95, 0.38)))
    for k in range(3):
        P[H].append(box((0.04, 0.4, 0.05), bc + Vector((-0.12 + k * 0.12, 0, 0.1)), K["FLESH"], rot=(0, 0, 0.3 * (k - 1)), bevel=0))
    for k in range(7):                                                           # cráneo roto alrededor
        a = k / 7 * 2 * math.pi
        P[H].append(box((0.12, 0.12, 0.08), bc + Vector((math.cos(a) * 0.32, math.sin(a) * 0.32, 0.02)), K["BONE"],
                        rot=(0, 0, a), bevel=0.01))
    # costura que cruza la cabeza de lado a lado por arriba (lado derecho, -X)
    _zb_stitches(P, H, ZB_HEAD + Vector((-0.63, 0.15, 0.25)), ZB_HEAD + Vector((-0.35, 0.05, 0.62)), (-1, 0, 1), K["STITCH"], n=4)
    _zb_stitches(P, H, ZB_HEAD + Vector((-0.35, 0.05, 0.62)), ZB_HEAD + Vector((-0.05, -0.25, 0.62)), (0, 0, 1), K["STITCH"], n=3)
    # manchas podridas a los costados y atrás (el frente queda liso: SIN CARA)
    for sx in (-1, 1):
        for _ in range(3):
            a = math.pi / 2 - sx * (math.pi / 2 - rng.uniform(0.15, 1.3))           # siempre hacia atrás (y > 0)
            p = ZB_HEAD + Vector((math.cos(a) * (0.62 + ZB_E), math.sin(a) * (0.62 + ZB_E), rng.uniform(-0.35, 0.3)))
            r = rng.uniform(0.14, 0.26)
            P[H].append(box((0.04, r, r * 0.8), p, K["ROT"], rot=(rng.uniform(-0.5, 0.5), 0, a), bevel=0))
    # sangre que chorrea por atrás desde el cerebro
    for x, ln in ((0.1, 0.6), (0.3, 0.4), (0.45, 0.75)):
        y = math.sqrt(max(0.0, 0.62 ** 2 - x ** 2)) + ZB_E
        P[H].append(box((0.07, 0.04, ln), ZB_HEAD + Vector((x, y, 0.5 - ln / 2)), K["BLOOD"], rot=(0, 0, -math.atan2(x, y)), bevel=0))
    # mordida en la parte de atrás con hueso
    a = math.radians(125)
    p = ZB_HEAD + Vector((math.cos(a) * (0.62 + ZB_E), math.sin(a) * (0.62 + ZB_E), -0.2))
    P[H].append(box((0.04, 0.3, 0.26), p, K["FLESH"], rot=(0, 0, a), bevel=0))
    P[H].append(box((0.06, 0.14, 0.08), p, K["BONE"], rot=(0.4, 0, a), bevel=0))
    for k in range(5):                                                           # marcas de dientes
        b = k / 5 * 2 * math.pi
        q = p + Vector((-math.sin(a), math.cos(a), 0)) * math.cos(b) * 0.2 + Vector((0, 0, math.sin(b) * 0.17))
        P[H].append(box((0.05, 0.06, 0.06), q, K["BLOOD2"], rot=(0, 0, a), bevel=0))


def _zb_arm(P, K, rng, name, sx):
    """Brazo R6 (1x1x2) colgando; después se gira hacia adelante. sx: lado (-1 derecha, +1 izquierda)."""
    A = name
    x = 1.5 * sx
    P[A].append(box((1, 1, 2), (x, 0, 3), K["SKIN"], bevel=0.03))
    # manga corta rota
    P[A].append(box((1.06, 1.06, 0.7), (x, 0, 3.66), K["SHIRT"], bevel=0.03))
    _zb_jagged_ring(P, A, x, 0, 3.32, 1.06, 1.06, K["SHIRT"], rng, n=3, size=0.15)
    # punta del brazo lisa (sin manos ni uñas, estilo R6), manchada de sangre
    for dx, dy, r in ((-0.15, -0.1, 0.42), (0.2, 0.15, 0.3), (-0.2, 0.25, 0.22)):
        P[A].append(box((r, r * 0.8, 0.04), (x + dx, dy, 2.0 - ZB_E), K["BLOOD2"], rot=(0, 0, r * 4), bevel=0))
    for k, (dx, ln) in enumerate(((-0.3, 0.35), (0.05, 0.55), (0.3, 0.25))):
        _zb_front(P, A, (0.09, ln), x + dx, 2.0 + ln / 2, -0.5, K["BLOOD"])
        _zb_front(P, A, (0.09, ln * 0.8), x - dx, 2.0 + ln * 0.4, 0.5, K["BLOOD"])
    for z in (2.35, 2.75):                                                         # venas podridas
        _zb_side(P, A, (0.06, 0.45), x + 0.5 * sx, -0.1, z, K["ROT"], rot=0.6)
    if sx < 0:
        # brazo derecho: vendas con sangre
        for k, z in enumerate((2.95, 2.68, 2.42)):
            P[A].append(box((1.05, 1.05, 0.13), (x, 0, z), K["BANDAGE"], rot=(0.04 * (k - 1), 0.05 * (1 - k), 0), bevel=0.02))
        P[A].append(box((0.06, 0.25, 0.55), (x - 0.54, -0.25, 2.25), K["BANDAGE"], rot=(0.25, 0, 0), bevel=0))  # punta suelta
        _zb_front(P, A, (0.3, 0.25), x + 0.1, 2.7, -0.54, K["BLOOD"], rot=0.3)
        _zb_side(P, A, (0.3, 0.22), x - 0.54, 0.1, 2.82, K["BLOOD2"])
    else:
        # brazo izquierdo: mordida con hueso y venas podridas
        _zb_front(P, A, (0.5, 0.42), x, 2.7, -0.5, K["FLESH"])
        P[A].append(box((0.12, 0.06, 0.45), (x + 0.05, -0.55, 2.7), K["BONE"], bevel=0.01))
        for k in range(6):                                                       # marcas de dientes
            a = k / 6 * 2 * math.pi
            _zb_front(P, A, (0.08, 0.08), x + math.cos(a) * 0.33, 2.7 + math.sin(a) * 0.28, -0.5, K["BLOOD2"])
        for _ in range(4):
            _zb_side(P, A, (rng.uniform(0.15, 0.3), rng.uniform(0.15, 0.35)), x + 0.5, rng.uniform(-0.3, 0.3), rng.uniform(2.3, 3.1), K["ROT"],
                 rot=rng.uniform(0, 1))
    for _ in range(3):                                                           # sangre seca por todos lados
        _zb_front(P, A, (rng.uniform(0.1, 0.2), rng.uniform(0.1, 0.2)), x + rng.uniform(-0.3, 0.3), rng.uniform(2.2, 3.1), 0.5,
              K["BLOOD2"], rot=rng.uniform(0, 3))


def _zb_leg(P, K, rng, name, sx):
    G = name
    x = 0.5 * sx
    hem = 0.75 if sx > 0 else 0.6                                                # altura de la botamanga rota
    P[G].append(box((1, 1, 2), (x, 0, 1), K["SKIN"], bevel=0.03))                # pierna (piel)
    P[G].append(box((1.03, 1.03, 2.0 - hem), (x, 0, 1.0 + hem / 2), K["PANTS"], bevel=0.03))
    _zb_jagged_ring(P, G, x, 0, hem, 1.03, 1.03, K["PANTS"], rng, n=3, size=0.15)
    # pie descalzo (sin zapatos ni uñas): barro en la planta y alrededor, tierra que sube por el tobillo
    P[G].append(box((1.02, 1.02, 0.14), (x, 0, 0.07), K["MUD"], bevel=0.02))
    for _ in range(5):
        _zb_front(P, G, (rng.uniform(0.12, 0.3), rng.uniform(0.1, 0.25)), x + rng.uniform(-0.35, 0.35), rng.uniform(0.18, 0.4),
              rng.choice((-0.5, 0.5)), K["DIRT"], rot=rng.uniform(0, 3))
    for _ in range(2):
        _zb_side(P, G, (rng.uniform(0.2, 0.4), rng.uniform(0.1, 0.2)), x + 0.5 * sx, rng.uniform(-0.3, 0.3), rng.uniform(0.18, 0.35),
             K["DIRT"], rot=rng.uniform(0, 3))
    if sx > 0:
        # pierna izquierda: pantalón roto en la rodilla, rodilla a la vista con la rótula
        _zb_front(P, G, (0.7, 0.45), x, 1.2, -0.515, K["SKIN"])
        P[G].append(sphere(0.16, (x, -0.54, 1.22), K["BONE"], subdiv=1, scale=(1.2, 0.5, 1)))   # rótula
        _zb_front(P, G, (0.3, 0.16), x - 0.15, 1.07, -0.545, K["FLESH"], rot=0.4)
        for k in range(5):                                                       # hilachas
            P[G].append(cone(0.08, 0.17, Vector((x - 0.3 + k * 0.15, -0.55, 1.45)), K["PANTS"], rot=(math.pi, 0, 0), verts=3))
        # tajo en la canilla
        _zb_front(P, G, (0.08, 0.4), x + 0.15, 0.5, -0.5, K["FLESH"], rot=0.3)
    else:
        # pierna derecha: parche de jean cosido y botamanga rota
        _zb_front(P, G, (0.45, 0.42), x + 0.05, 1.35, -0.5, K["PATCH"], rot=-0.1)
        for z in (1.12, 1.58):
            _zb_stitches(P, G, (x - 0.2, -0.54, z), (x + 0.28, -0.54, z - 0.05), (0, -1, 0), K["STITCH"], n=4, w=0.025, cross=0.08)
        # grillete oxidado con cadena cortada en el tobillo
        P[G].append(box((1.1, 1.1, 0.16), (x, 0, 0.42), K["RUST"], bevel=0.03))
        for k in range(3):
            P[G].append(box((0.14, 0.06, 0.22), (x - 0.25 + k * 0.12, -0.6 - k * 0.04, 0.3 - k * 0.1), K["RUST"],
                            rot=(0, 0.5 * (k % 2), 0), bevel=0.01))
    for _ in range(3):
        _zb_front(P, G, (rng.uniform(0.1, 0.25), rng.uniform(0.1, 0.25)), x + rng.uniform(-0.3, 0.3), rng.uniform(0.7, 1.8),
              rng.choice((-0.5, 0.5)), K["BLOOD2"], rot=rng.uniform(0, 3))


# pose de zombi: brazos estirados hacia adelante (uno un poco más bajo) y cabeza ladeada
ZB_POSE = {"RightArm": Matrix.Rotation(-math.radians(84), 4, "X"), "LeftArm": Matrix.Rotation(-math.radians(95), 4, "X"),
           "Head": Matrix.Rotation(math.radians(9), 4, "Y") @ Matrix.Rotation(math.radians(6), 4, "X")}


def _zb_body(K, rng, extra=None, pose=None, chest=True):
    """Cuerpo del zombi básico armado y en pose. `extra(P)` agrega accesorios en pose de reposo antes de unir.

    `pose` = {parte: matriz de rotación alrededor de su articulación} (por defecto ZB_POSE).
    """
    P = {k: [] for k in ZB_PIV}
    _zb_torso(P, K, rng, chest)
    _zb_head(P, K, rng)
    _zb_arm(P, K, rng, "RightArm", -1)
    _zb_arm(P, K, rng, "LeftArm", 1)
    _zb_leg(P, K, rng, "RightLeg", -1)
    _zb_leg(P, K, rng, "LeftLeg", 1)
    if extra:
        extra(P)
    objs = {k: join(v, k, ZB_PIV[k]) for k, v in P.items()}
    for part, m in (pose or ZB_POSE).items():
        L.transform([objs[part]], m, ZB_PIV[part])
    return list(objs.values())


def e_basico():
    """Zombi básico: R6 clásico, sin cara, descalzo y sin uñas, con mucho detalle."""
    return _zb_body(_zb_mats(), random.Random(7)), 1.0


def e_generador():
    """Zombi de apoyo con un generador de escudos en la espalda (el escudo se crea en el juego).

    El núcleo de energía es una parte aparte, `Nucleo`, con el pivote en su centro: sirve de punto de origen
    para el escudo y para animarlo. Hay que soldarlo al `Torso` (WeldConstraint o Motor6D).
    """
    K = _zb_mats()
    K.update(SHIRT=mat("Mono_Tecnico", (0.20, 0.22, 0.25)), SHIRT2=mat("Mono_Oscuro", (0.09, 0.10, 0.12)),
             PANTS=mat("Mono_Pantalon", (0.15, 0.16, 0.19)))
    metal = mat("Metal_Generador", (0.12, 0.13, 0.16), 0.8, 0.35)
    steel = mat("Acero", (0.5, 0.52, 0.56), 0.9, 0.3)
    black = mat("Negro", (0.02, 0.02, 0.02))
    yellow = mat("Peligro_Amarillo", (0.95, 0.7, 0.05), 0.2, 0.5)
    stripe = mat("Franja_Celeste", (0.2, 0.7, 1.0))
    hose = mat("Manguera", (0.05, 0.05, 0.06), 0.1, 0.6)
    leather = mat("Cuero_Bolsillo", (0.25, 0.17, 0.09))
    glow = mat("Energia_Celeste", (0.3, 0.85, 1.0), emission=(0.2, 0.75, 1.0), strength=3)
    white = mat("Dial", (0.92, 0.92, 0.88))
    leds = [mat(f"Led_{n}", c, emission=c, strength=4) for n, c in (("Verde", (0.1, 1, 0.2)), ("Amarillo", (1, 0.8, 0.1)), ("Rojo", (1, 0.1, 0.05)))]
    pc = Vector((0, 0.82, 3.1))                                                  # centro de la mochila
    cc = pc + Vector((0, 0.42, 0))                                               # centro del núcleo
    by = pc.y + 0.325                                                            # cara de atrás de la mochila

    def corrugated(T, pts, r, m, ring_m, step=0.12):
        """Manguera corrugada: tramos con anillitos cada `step`."""
        for a, b in zip(pts, pts[1:]):
            T.append(L.rod(a, b, r, m, verts=6))
            d = b - a
            for k in range(1, max(1, int(d.length / step))):
                T.append(L.torus(r * 1.15, r * 0.35, a + d * (k * step / d.length), ring_m, rot=d.normalized(), seg=8, minor=3))

    def coil(T, base, h, scale=1.0):
        """Proyector tipo bobina: base, varilla, anillos de energía y punta brillante."""
        T.append(cyl(0.12 * scale, 0.12, base + Vector((0, 0, 0.06)), steel, verts=10, bevel=0.01))
        T.append(L.rod(base, base + Vector((0, 0, h)), 0.035 * scale, steel))
        for k in range(3):
            T.append(L.torus((0.13 - k * 0.025) * scale, 0.022, base + Vector((0, 0, h * (0.35 + k * 0.2))), glow, seg=12, minor=4))
        T.append(sphere(0.08 * scale, base + Vector((0, 0, h + 0.05)), glow, subdiv=2))

    def glyphs(P, part, base, u, v, segs, m):
        """Letras con cajitas: cada seg es (u0, v0, u1, v1) en el plano (u = derecha, v = arriba)."""
        for u0, v0, u1, v1 in segs:
            c = base + u * ((u0 + u1) / 2) + v * ((v0 + v1) / 2)
            size = [0.02, 0.02, 0.02]
            for axis, ext in ((u, abs(u1 - u0) + 0.03), (v, abs(v1 - v0) + 0.03)):
                i = max(range(3), key=lambda j: abs(axis[j]))
                size[i] = ext
            P[part].append(box(tuple(size), c, m, bevel=0))

    def gear(P):
        T = P["Torso"]
        # --- mochila generadora
        T.append(box((1.5, 0.65, 1.6), pc, metal, bevel=0.08))
        for z in (0.62, -0.62):                                                  # bandas de acero
            T.append(box((1.56, 0.7, 0.12), pc + Vector((0, 0, z)), steel, bevel=0.02))
        for sx in (-1, 1):
            for sz in (-1, 1):                                                   # remaches
                T.append(sphere(0.05, Vector((sx * 0.68, by + 0.01, pc.z + sz * 0.48)), steel, subdiv=1))
            # celdas de energía a los costados
            for y in (0.66, 1.0):
                c = Vector((sx * 0.84, y, 3.0))
                T.append(cyl(0.1, 0.62, c, glow, verts=10, bevel=0))
                for z in (-0.33, 0.33):
                    T.append(cyl(0.12, 0.06, c + Vector((0, 0, z)), steel, verts=10, bevel=0))
            T.append(box((0.08, 0.6, 0.1), Vector((sx * 0.8, 0.83, 3.3)), metal, bevel=0))      # abrazadera de las celdas
            # franjas de peligro a los costados, arriba
            for k in range(6):
                T.append(box((0.03, 0.105, 0.16), Vector((sx * 0.765, 0.55 + k * 0.105, 3.62)), yellow if k % 2 == 0 else black,
                             rot=(0.5, 0, 0), bevel=0))
        # ventilación brillante abajo
        T.append(box((0.9, 0.42, 0.04), pc + Vector((0, 0, -0.81)), glow, bevel=0))
        for k in range(5):
            T.append(box((0.05, 0.46, 0.06), pc + Vector((-0.36 + k * 0.18, 0, -0.83)), black, bevel=0))
        # manómetro con aguja
        g = Vector((-0.55, by + 0.03, 3.5))
        T.append(cyl(0.16, 0.06, g, steel, rot=(math.pi / 2, 0, 0), verts=16, bevel=0.01))
        T.append(cyl(0.13, 0.03, g + Vector((0, 0.03, 0)), white, rot=(math.pi / 2, 0, 0), verts=16, bevel=0))
        T.append(box((0.02, 0.02, 0.11), g + Vector((0.03, 0.05, 0.03)), leds[2], rot=(0, -0.7, 0), bevel=0))
        for k in range(5):                                                       # marcas del dial
            a = math.pi * (0.15 + k * 0.175)
            T.append(box((0.015, 0.02, 0.035), g + Vector((-math.cos(a) * 0.1, 0.05, math.sin(a) * 0.1)), black, rot=(0, a - math.pi / 2, 0), bevel=0))
        # luces de estado
        for k, m in enumerate(leds):
            T.append(box((0.09, 0.05, 0.09), Vector((0.45 + k * 0.13, by + 0.01, 3.55)), m, bevel=0))
        T.append(box((0.42, 0.04, 0.14), Vector((0.58, by + 0.005, 3.55)), black, bevel=0))
        # placa con remaches abajo del núcleo
        T.append(box((0.5, 0.04, 0.3), Vector((0.55, by + 0.01, 2.75)), steel, bevel=0.01))
        for k in range(3):
            T.append(box((0.3, 0.05, 0.03), Vector((0.55, by + 0.02, 2.82 - k * 0.07)), black, bevel=0))
        # manija arriba y 2 proyectores tipo bobina, uno a cada lado
        for sx in (-1, 1):
            T.append(box((0.06, 0.06, 0.18), Vector((sx * 0.25, 0.62, 3.99)), steel, bevel=0))
            coil(T, Vector((sx * 0.55, 0.95, 3.9)), 0.75)
        T.append(box((0.56, 0.08, 0.06), Vector((0, 0.62, 4.08)), black, bevel=0.01))
        # --- tirantes con hebillas
        for sx in (-1, 1):
            T.append(box((0.25, 1.06, 0.06), (sx * 0.55, 0, 4.03), metal, bevel=0.01))
            T.append(box((0.25, 0.06, 0.45), (sx * 0.55, -0.53, 3.8), metal, bevel=0.01))
            T.append(box((0.3, 0.07, 0.16), (sx * 0.55, -0.56, 3.62), steel, bevel=0.01))
            T.append(box((0.18, 0.08, 0.06), (sx * 0.55, -0.57, 3.62), black, bevel=0))
        # --- emisor del pecho con barra de carga
        em = Vector((0, -0.6, 3.22))
        T.append(cyl(0.24, 0.1, em, steel, rot=(math.pi / 2, 0, 0), verts=16, bevel=0.02))
        T.append(cyl(0.16, 0.06, em + Vector((0, -0.05, 0)), glow, rot=(math.pi / 2, 0, 0), verts=16, bevel=0))
        T.append(L.torus(0.24, 0.03, em + Vector((0, -0.05, 0)), metal, rot=(math.pi / 2, 0, 0), seg=16, minor=4))
        T.append(box((0.46, 0.06, 0.13), em + Vector((0, 0, -0.36)), black, bevel=0.01))
        for k, m in enumerate((glow, glow, black)):
            T.append(box((0.12, 0.07, 0.08), em + Vector((-0.14 + k * 0.14, -0.01, -0.36)), m, bevel=0))
        # --- mangueras corrugadas de la mochila al emisor
        for sx in (-1, 1):
            pts = [Vector((sx * 0.72, 0.5, 3.75)), Vector((sx * 0.8, 0.1, 4.08)), Vector((sx * 0.8, -0.55, 3.85)),
                   Vector((sx * 0.35, -0.62, 3.45)), em + Vector((sx * 0.17, 0, 0.05))]
            corrugated(T, pts, 0.045, hose, glow if sx > 0 else steel)
        # --- cable enchufado en la nuca, con costura
        nk = Vector((0, 0.36, 4.05))
        corrugated(T, [Vector((0, 0.5, 3.92)), nk + Vector((0, 0.06, 0))], 0.04, hose, steel, step=0.08)
        T.append(box((0.14, 0.06, 0.1), nk, steel, bevel=0.01))
        _zb_stitches(P, "Torso", Vector((-0.2, 0.37, 4.06)), Vector((0.2, 0.37, 4.06)), (0, 1, 0), K["STITCH"], n=4, w=0.02, cross=0.08)
        # --- bolsillos de herramientas en el cinturón
        for sx in (-1, 1):
            c = Vector((sx * 0.82, -0.6, 2.02))
            T.append(box((0.32, 0.2, 0.34), c, leather, bevel=0.03))
            T.append(box((0.34, 0.22, 0.1), c + Vector((0, 0, 0.14)), leather, rot=(0.15, 0, 0), bevel=0.02))
            T.append(box((0.06, 0.04, 0.06), c + Vector((0, -0.12, 0.08)), steel, bevel=0))
        T.append(L.rod(Vector((-0.75, -0.6, 2.15)), Vector((-0.72, -0.62, 2.45)), 0.03, steel))   # destornillador
        T.append(box((0.07, 0.07, 0.12), Vector((-0.72, -0.62, 2.5)), yellow, bevel=0.01))
        T.append(box((0.05, 0.03, 0.3), Vector((0.85, -0.62, 2.3)), steel, bevel=0))                # llave inglesa
        T.append(box((0.14, 0.03, 0.08), Vector((0.85, -0.62, 2.47)), steel, bevel=0))
        # --- franjas celestes en el mono (piernas y mangas)
        for nm, x in (("RightLeg", -0.5), ("LeftLeg", 0.5)):
            P[nm].append(box((1.05, 1.05, 0.1), (x, 0, 1.6), stripe, bevel=0))
        for nm, x in (("RightArm", -1.5), ("LeftArm", 1.5)):
            P[nm].append(box((1.08, 1.08, 0.08), (x, 0, 3.42), stripe, bevel=0))
        # --- parche "G-7" en la manga derecha (texto acomodado para el brazo estirado hacia adelante)
        pb = Vector((-2.05, 0.0, 3.68))
        u, v = Vector((0, 0, -1)), Vector((0, -1, 0))                            # derecha / arriba con el brazo en pose
        P["RightArm"].append(box((0.04, 0.32, 0.56), pb, K["SHIRT2"], bevel=0))
        q = pb + Vector((-0.02, 0, 0))
        glyphs(P, "RightArm", q, u, v, [(-0.22, 0.09, -0.12, 0.09), (-0.22, -0.09, -0.22, 0.09), (-0.22, -0.09, -0.12, -0.09),
                                        (-0.12, -0.09, -0.12, 0.0), (-0.16, 0.0, -0.12, 0.0),            # G
                                        (-0.05, 0.0, 0.05, 0.0),                                          # -
                                        (0.12, 0.09, 0.22, 0.09), (0.22, -0.09, 0.22, 0.09)], stripe)     # 7
        # --- mando de muñeca (brazo izquierdo, sin manos ni uñas)
        A = P["LeftArm"]
        A.append(box((1.1, 1.1, 0.32), (1.5, 0, 2.3), metal, bevel=0.04))
        A.append(box((0.5, 0.05, 0.2), (1.5, -0.57, 2.3), glow, bevel=0))
        for k, m in enumerate(leds):
            A.append(box((0.07, 0.05, 0.07), (1.55 + 0.1 * k, -0.57, 2.42), m, bevel=0))
        A.append(cyl(0.12, 0.08, (1.5, 0, 2.0 - 0.06), glow, verts=12, bevel=0))              # emisor en la punta
        A.append(cyl(0.08, 0.08, (2.08, -0.2, 2.3), steel, rot=(0, math.pi / 2, 0), verts=10, bevel=0))   # perilla
        A.append(box((0.04, 0.03, 0.08), (2.13, -0.2, 2.3), black, bevel=0))
        A.append(L.rod(Vector((2.06, 0.25, 2.2)), Vector((2.06, 0.25, 2.95)), 0.025, steel))    # mini antena
        A.append(sphere(0.05, (2.06, 0.25, 2.97), leds[2], subdiv=1))
        # --- auricular en la cabeza
        h = ZB_HEAD + Vector((0.63, 0.05, 0.0))
        P["Head"].append(box((0.1, 0.35, 0.35), h, metal, bevel=0.03))
        P["Head"].append(box((0.04, 0.2, 0.2), h + Vector((0.06, 0, 0)), glow, bevel=0))
        P["Head"].append(L.rod(h + Vector((0.05, -0.1, -0.1)), h + Vector((0.0, -0.45, -0.35)), 0.025, metal, verts=6))

    objs = _zb_body(K, random.Random(11), gear)
    # núcleo de energía: parte aparte (origen del escudo en el juego)
    core = [cyl(0.3, 1.05, cc, glow, verts=16, bevel=0)]
    for z in (-0.25, 0.25):
        core.append(L.torus(0.33, 0.05, cc + Vector((0, 0, z)), steel, seg=16, minor=6))
    for z in (-0.56, 0.56):
        core.append(cyl(0.35, 0.1, cc + Vector((0, 0, z)), steel, verts=16, bevel=0.02))
    for k in range(4):                                                           # jaula
        a = k / 4 * 2 * math.pi + math.pi / 4
        core.append(box((0.05, 0.05, 1.02), cc + Vector((math.cos(a) * 0.31, math.sin(a) * 0.31, 0)), metal, bevel=0))
    objs.append(join(core, "Nucleo", cc))
    return objs, 1.0


def e_veloz():
    """Zombi veloz: ropa deportiva, turbina con propulsores en la espalda y propulsores en las piernas."""
    K = _zb_mats()
    K.update(SHIRT=mat("Musculosa_Naranja", (0.95, 0.38, 0.04)), SHIRT2=mat("Negro_Deportivo", (0.04, 0.04, 0.05)),
             PANTS=mat("Jogger_Negro", (0.06, 0.06, 0.07)))
    metal = mat("Metal_Turbo", (0.14, 0.14, 0.17), 0.8, 0.35)
    steel = mat("Acero", (0.5, 0.52, 0.56), 0.9, 0.3)
    black = mat("Negro", (0.02, 0.02, 0.02))
    orange = mat("Naranja", (1.0, 0.45, 0.05))
    yellow = mat("Rayo_Amarillo", (1.0, 0.82, 0.05), 0.1, 0.4)
    red = mat("Rojo_Turbo", (0.75, 0.05, 0.05), 0.3, 0.4)
    white = mat("Dial", (0.92, 0.92, 0.88))
    fire = mat("Fuego_Turbo", (1.0, 0.5, 0.1), emission=(1.0, 0.45, 0.05), strength=4)
    tc = Vector((0, 0.78, 3.25))                                                  # centro de la turbina (eje Y)

    def bolt(T, part, c, h, y, m, outline=None):
        """Rayo en zigzag plano sobre una cara que mira a -Y (y < 0) o +Y (y > 0)."""
        s = h / 0.6
        pts = [Vector((0.2, 0, 0.3)), Vector((-0.1, 0, 0.0)), Vector((0.12, 0, 0.0)), Vector((-0.2, 0, -0.3))]
        sy = 1 if y > 0 else -1
        for mm, w, dy in ((outline, 0.17, 0.0), (m, 0.1, 0.015)) if outline else ((m, 0.1, 0.0),):
            for a, b in zip(pts, pts[1:]):
                pa = c + Vector((a.x * s, y + sy * (ZB_E + dy), a.z * s))
                pb = c + Vector((b.x * s, y + sy * (ZB_E + dy), b.z * s))
                T[part].append(strut(pa, pb + (pb - pa).normalized() * 0.03, 0.03, w * s, mm, bevel=0))

    def gear(P):
        T = P["Torso"]
        # --- montura de la turbina en la espalda, con tirantes
        T.append(box((1.3, 0.25, 1.3), Vector((0, 0.62, 3.2)), metal, bevel=0.06))
        T.append(cyl(0.62, 0.3, tc, metal, rot=(math.pi / 2, 0, 0), verts=24, bevel=0.03))          # carcasa
        T.append(L.torus(0.6, 0.06, tc + Vector((0, 0.16, 0)), orange, rot=(math.pi / 2, 0, 0), seg=24, minor=6))
        for k in range(4):                                                       # rejilla de protección
            a = k / 4 * math.pi
            T.append(box((1.15, 0.04, 0.04), tc + Vector((0, 0.2, 0)), steel, rot=(0, a, 0), bevel=0))
        for sx in (-1, 1):
            T.append(box((0.25, 1.06, 0.06), (sx * 0.55, 0, 4.03), black, bevel=0.01))
            T.append(box((0.25, 0.06, 0.45), (sx * 0.55, -0.53, 3.8), black, bevel=0.01))
            T.append(box((0.3, 0.07, 0.14), (sx * 0.55, -0.56, 3.6), steel, bevel=0.01))
            # propulsores a los costados de la turbina, apuntando para abajo y atrás
            top = Vector((sx * 0.78, 0.75, 3.45))
            bot = top + Vector((sx * 0.12, 0.35, -1.0))
            d = (bot - top).normalized()
            T.append(L.rod(top, bot, 0.17, metal, verts=12))
            T.append(cyl(0.2, 0.08, top, steel, rot=d, verts=12, bevel=0))
            for t in (0.3, 0.6):
                T.append(L.torus(0.18, 0.03, top.lerp(bot, t), red, rot=d, seg=12, minor=4))
            T.append(cyl(0.2, 0.25, bot + d * 0.1, steel, rot=d, verts=12, bevel=0, r2=0.25))      # tobera
            T.append(cyl(0.2, 0.03, bot + d * 0.23, fire, rot=d, verts=12, bevel=0))
            T.append(L.rod(tc + Vector((sx * 0.45, 0.05, 0.35)), top + Vector((0, 0, 0.05)), 0.035, black, verts=6))  # caño
            bolt(P, "Torso", Vector((sx * 0.45, 0, 2.75)), 0.4, 0.75, yellow)    # rayitos en la montura
        # --- emblema de rayo en el pecho
        bolt(P, "Torso", Vector((-0.45, 0, 3.15)), 1.0, -0.5, yellow, outline=black)
        # franjas negras a los costados de la musculosa
        for sx in (-1, 1):
            _zb_side(P, "Torso", (0.14, 1.6), sx * 1.0, -0.3, 3.05, black)
        # --- cabeza: vincha con tiras al viento
        hb = ZB_HEAD + Vector((0, 0, 0.3))
        P["Head"].append(cyl(0.645, 0.16, hb, red, verts=24, bevel=0))
        for sx in (-1, 1):
            a = hb + Vector((sx * 0.08, 0.6, -0.02))
            P["Head"].append(strut(a, a + Vector((sx * 0.25, 0.75, -0.25)), 0.03, 0.13, red, bevel=0))
            P["Head"].append(strut(a + Vector((sx * 0.25, 0.75, -0.25)), a + Vector((sx * 0.35, 1.25, -0.2)), 0.03, 0.11, red, bevel=0))
        P["Head"].append(box((0.18, 0.06, 0.18), hb + Vector((0, 0.66, 0)), red, bevel=0.02))      # nudo
        # --- brazos: franja naranja en la manga; velocímetro en la muñeca izquierda
        for nm, sx in (("RightArm", -1), ("LeftArm", 1)):
            P[nm].append(box((1.08, 1.08, 0.08), (sx * 1.5, 0, 3.42), black, bevel=0))
            _zb_side(P, nm, (0.12, 0.6), sx * 2.03, 0, 3.66, orange)
        A = P["LeftArm"]
        A.append(box((1.08, 1.08, 0.32), (1.5, 0, 2.35), black, bevel=0.04))
        g = Vector((2.06, 0, 2.35))
        A.append(cyl(0.24, 0.06, g, steel, rot=(0, math.pi / 2, 0), verts=20, bevel=0.01))
        A.append(cyl(0.2, 0.03, g + Vector((0.03, 0, 0)), white, rot=(0, math.pi / 2, 0), verts=20, bevel=0))
        for k in range(7):                                                       # marcas, las últimas en rojo
            a = math.radians(200 - k * 37)
            A.append(box((0.02, 0.025, 0.05), g + Vector((0.05, math.cos(a) * 0.15, math.sin(a) * 0.15)), red if k >= 5 else black,
                         rot=(a - math.pi / 2, 0, 0), bevel=0))
        a = math.radians(-20)                                                    # aguja a fondo
        A.append(strut(g + Vector((0.06, 0, 0)), g + Vector((0.06, math.cos(a) * 0.16, math.sin(a) * 0.16)), 0.02, 0.025, red, bevel=0))
        A.append(cyl(0.03, 0.03, g + Vector((0.07, 0, 0)), black, rot=(0, math.pi / 2, 0), verts=8, bevel=0))
        # --- piernas: franjas laterales y propulsores en las pantorrillas (pies descalzos)
        for nm, sx in (("RightLeg", -1), ("LeftLeg", 1)):
            G = P[nm]
            x = sx * 0.5
            _zb_side(P, nm, (0.14, 1.1), sx * 1.0, 0, 1.4, orange)
            for z in (1.0, 0.62):                                                # correas
                G.append(box((1.06, 1.06, 0.08), (x, 0, z), black, bevel=0))
            G.append(box((0.6, 0.3, 0.62), (x, 0.66, 0.85), metal, bevel=0.05))  # cuerpo del propulsor
            G.append(box((0.5, 0.05, 0.12), (x, 0.82, 1.0), orange, bevel=0))
            bolt(P, nm, Vector((x, 0, 0.8)), 0.25, 0.81, yellow)
            n = Vector((x, 0.72, 0.48))
            G.append(cyl(0.16, 0.2, n, steel, verts=12, bevel=0, r2=0.21))       # tobera para abajo
            G.append(cyl(0.18, 0.03, n + Vector((0, 0, -0.11)), fire, verts=12, bevel=0))
            G.append(strut(Vector((x + sx * 0.3, 0.55, 1.1)), Vector((x + sx * 0.45, 0.95, 0.75)), 0.04, 0.2, red, bevel=0))  # aleta

        # aspas de la turbina
        T += [cyl(0.12, 0.34, tc, fire, rot=(math.pi / 2, 0, 0), verts=12, bevel=0),
              cyl(0.18, 0.3, tc, steel, rot=(math.pi / 2, 0, 0), verts=12, bevel=0.02)]
        for k in range(8):
            a = k / 8 * 2 * math.pi
            T.append(box((0.42, 0.04, 0.14), tc + Vector((math.cos(a) * 0.36, 0.02, math.sin(a) * 0.36)), steel,
                         rot=(0.35, -a, 0), bevel=0))

    return _zb_body(K, random.Random(23), gear, chest=False), 1.0


def e_divisor():
    """Zombi divisor: gordo y cosido con pedazos de varios zombis; al morir se parte en zombis chicos (en el juego)."""
    K = _zb_mats()
    K.update(SHIRT=mat("Franela_Roja", (0.55, 0.12, 0.1)), SHIRT2=mat("Franela_Oscura", (0.25, 0.05, 0.05)),
             PANTS=mat("Pantalon_Marron", (0.24, 0.14, 0.07)))
    skin_b = mat("Piel_Gris_Azulada", (0.35, 0.45, 0.5))
    skin_c = mat("Piel_Violacea", (0.45, 0.35, 0.5))
    jean = mat("Jean_Remendado", (0.12, 0.2, 0.38))
    blue = mat("Remiendo_Azul", (0.12, 0.3, 0.55))
    steel = mat("Grapa", (0.6, 0.6, 0.62), 0.9, 0.3)
    ooze = mat("Baba_Verde", (0.45, 1.0, 0.15), emission=(0.4, 1.0, 0.1), strength=3)
    st = K["STITCH"]

    def seam_ring(P, part, cx, cy, z, w, d, staples=True):
        """Costura alrededor de una caja (w x d) a la altura z, con grapas de metal."""
        for (a, b, nrm) in (((cx - w / 2 + 0.05, cy - d / 2 - 0.02, z), (cx + w / 2 - 0.05, cy - d / 2 - 0.02, z), (0, -1, 0)),
                            ((cx - w / 2 + 0.05, cy + d / 2 + 0.02, z), (cx + w / 2 - 0.05, cy + d / 2 + 0.02, z), (0, 1, 0)),
                            ((cx - w / 2 - 0.02, cy - d / 2 + 0.05, z), (cx - w / 2 - 0.02, cy + d / 2 - 0.05, z), (-1, 0, 0)),
                            ((cx + w / 2 + 0.02, cy - d / 2 + 0.05, z), (cx + w / 2 + 0.02, cy + d / 2 - 0.05, z), (1, 0, 0))):
            _zb_stitches(P, part, a, b, nrm, st, n=4, w=0.025, cross=0.1)
        if staples:
            P[part].append(box((0.06, 0.05, 0.2), (cx + w * 0.2, cy - d / 2 - 0.04, z), steel, bevel=0))

    def drip(P, part, x, z, y, ln):
        """Chorro de baba verde sobre una cara frontal (y < 0) o trasera (y > 0)."""
        _zb_front(P, part, (0.07, ln), x, z - ln / 2, y, ooze)
        sy = 1 if y > 0 else -1
        P[part].append(sphere(0.06, (x, y + sy * 0.04, z - ln), ooze, subdiv=1, scale=(1, 0.6, 1.3)))

    def gear(P):
        T = P["Torso"]
        # --- panza gorda con costura en Y
        bc = Vector((0, -0.68, 2.62))
        T.append(box((1.6, 0.4, 0.78), bc, K["SKIN"], bevel=0.15))
        fy = bc.y - 0.2
        _zb_stitches(P, "Torso", (0, fy - 0.02, 2.95), (0, fy - 0.02, 2.3), (0, -1, 0), st, n=6, w=0.03, cross=0.14)
        for sx in (-1, 1):
            _zb_stitches(P, "Torso", (0, fy - 0.02, 2.95), (sx * 0.55, fy - 0.02, 3.0), (0, -1, 0), st, n=4, w=0.03, cross=0.12)
        _zb_front(P, "Torso", (0.45, 0.32), 0.45, 2.55, fy, skin_b, rot=0.1)          # pedazo de piel de otro zombi
        for k, (a, b) in enumerate((((0.22, 2.4), (0.68, 2.42)), ((0.22, 2.72), (0.68, 2.7)))):
            _zb_stitches(P, "Torso", (a[0], fy - 0.03, a[1]), (b[0], fy - 0.03, b[1]), (0, -1, 0), st, n=4, w=0.02, cross=0.08)
        for x, ln in ((0.02, 0.35), (-0.12, 0.2), (0.3, 0.25)):
            drip(P, "Torso", x, 2.33, fy, ln)
        for x in (-0.4, 0.4):                                                       # grapas en la panza
            T.append(box((0.2, 0.05, 0.05), (x * 0.5, fy - 0.04, 2.6 + x * 0.3), steel, bevel=0))
        # rollos a los costados
        for sx in (-1, 1):
            T.append(box((0.25, 0.7, 0.5), (sx * 1.06, -0.15, 2.45), K["SKIN"], bevel=0.1))
            _zb_stitches(P, "Torso", (sx * 1.2, -0.45, 2.7), (sx * 1.2, 0.15, 2.65), (sx, 0, 0), st, n=3, w=0.02, cross=0.08)
        # remiendo de otra camisa (azul) en el pecho derecho y en la espalda, cosidos
        _zb_front(P, "Torso", (0.55, 0.55), -0.5, 3.45, -0.5, blue, rot=0.08)
        _zb_front(P, "Torso", (0.6, 0.5), 0.55, 3.55, 0.5, blue, rot=-0.1)
        for z in (3.18, 3.72):
            _zb_stitches(P, "Torso", (-0.78, -0.55, z), (-0.22, -0.55, z + 0.04), (0, -1, 0), st, n=4, w=0.02, cross=0.08)
        # costura del cuello (cabeza cosida a otro cuerpo) con baba
        seam_ring(P, "Torso", 0, 0, 4.06, 0.72, 0.72, staples=False)
        drip(P, "Torso", 0.15, 3.98, -0.5, 0.3)
        # brazo chiquito cosido en la espalda (de otro zombi)
        base = Vector((-0.55, 0.52, 3.55))
        tip = base + Vector((-0.25, 0.75, 0.45))
        T.append(strut(base, tip, 0.42, 0.42, skin_c, bevel=0.04))
        T.append(L.torus(0.27, 0.035, base + Vector((0, 0.06, 0)), st, rot=(tip - base).normalized(), seg=12, minor=4))
        for k in range(6):
            a = k / 6 * 2 * math.pi
            T.append(box((0.05, 0.12, 0.05), base + Vector((math.cos(a) * 0.27, 0.06, math.sin(a) * 0.27)), st, bevel=0))
        T.append(box((0.43, 0.43, 0.05), tip, K["BLOOD2"], rot=(0.6, 0, 0.3), bevel=0))
        drip(P, "Torso", -0.4, 3.35, 0.5, 0.45)
        # --- brazos: la mitad de abajo es de otros zombis
        for nm, sx, sk in (("RightArm", -1, skin_b), ("LeftArm", 1, skin_c)):
            x = sx * 1.5
            P[nm].append(box((1.015, 1.015, 0.84), (x, 0, 2.41), sk, bevel=0.02))      # tapa también la punta
            seam_ring(P, nm, x, 0, 2.84, 1.02, 1.02)
            drip(P, nm, x + 0.2 * sx, 2.8, -0.51, 0.25)
        # --- piernas: pantalón de dos colores y la canilla derecha de otro zombi
        for o in P["LeftLeg"]:
            for i, m in enumerate(o.data.materials):
                if m == K["PANTS"]:
                    o.data.materials[i] = jean
        P["RightLeg"].append(box((1.015, 1.015, 0.42), (-0.5, 0, 0.36), skin_b, bevel=0.02))
        seam_ring(P, "RightLeg", -0.5, 0, 0.57, 1.02, 1.02, staples=False)
        for z in (1.25, 1.75):                                                      # costura del pantalón remendado
            _zb_side(P, "LeftLeg", (0.04, 0.5), 1.0, 0, z, st)

    return _zb_body(K, random.Random(31), gear, chest=False), 1.0


def e_explosivo():
    """Zombi explosivo (kamikaze): bomba con mecha en la espalda, barriles de TNT, dinamita y detonador."""
    K = _zb_mats()
    K.update(SHIRT=mat("Camisa_Caqui", (0.55, 0.45, 0.25)), SHIRT2=mat("Caqui_Oscuro", (0.3, 0.24, 0.12)),
             PANTS=mat("Pantalon_Oliva", (0.2, 0.22, 0.12)))
    bomb = mat("Bomba_Negra", (0.04, 0.04, 0.05), 0.4, 0.35)
    steel = mat("Acero", (0.5, 0.52, 0.56), 0.9, 0.3)
    red = mat("Dinamita_Roja", (0.75, 0.06, 0.04), 0.1, 0.5)
    white = mat("Etiqueta_Blanca", (0.92, 0.9, 0.85))
    black = mat("Negro", (0.02, 0.02, 0.02))
    leather = mat("Cuero_Canana", (0.25, 0.15, 0.07))
    rope = mat("Mecha", (0.75, 0.62, 0.38))
    tape = mat("Cinta_Gris", (0.5, 0.5, 0.48))
    soot = mat("Hollin", (0.08, 0.07, 0.07))
    spark = mat("Chispa", (1.0, 0.75, 0.15), emission=(1.0, 0.6, 0.1), strength=8)
    led = mat("Led_Rojo", (1, 0.1, 0.05), emission=(1, 0.1, 0.05), strength=5)
    rng = random.Random(42)                                                     # manchas de hollín

    def fuse(T, pts, lit=True):
        """Mecha: tramos de soga y, si está encendida, una chispa en la punta."""
        for a, b in zip(pts, pts[1:]):
            T.append(L.rod(a, b, 0.03, rope, verts=6))
        if lit:
            tip = pts[-1]
            T.append(sphere(0.07, tip, spark, subdiv=1))
            for k in range(5):
                d = Vector((math.cos(k * 1.26), math.sin(k * 1.26) * 0.6, math.sin(k * 2.1) * 0.8 + 0.3)).normalized()
                T.append(cone(0.03, 0.16, tip + d * 0.1, spark, rot=d, verts=4))

    def dynamite(T, c, h=0.42, r=0.07, lit=False):
        """Cartucho de dinamita parado, con mecha corta."""
        T.append(cyl(r, h, c, red, verts=10, bevel=0))
        T.append(cyl(r * 1.02, 0.05, c + Vector((0, 0, h * 0.3)), tape, verts=10, bevel=0))
        fuse(T, [c + Vector((0, 0, h / 2)), c + Vector((0.03, 0, h / 2 + 0.12)), c + Vector((0.07, 0.02, h / 2 + 0.2))], lit)

    def tnt(T, c, y, s=1.0):
        """Letras "TNT" en el plano y = y (mirando hacia +Y), centradas en c (x, z)."""
        segs = [(-0.27, 0.1, -0.13, 0.1), (-0.2, -0.1, -0.2, 0.1),                          # T
                (-0.08, -0.1, -0.08, 0.1), (0.08, -0.1, 0.08, 0.1), (-0.08, 0.08, 0.08, -0.08),   # N
                (0.13, 0.1, 0.27, 0.1), (0.2, -0.1, 0.2, 0.1)]                              # T
        for u0, v0, u1, v1 in segs:
            a = Vector((c.x - u0 * s, y, c.z + v0 * s))                                    # mirando a +Y: la x va al revés
            b = Vector((c.x - u1 * s, y, c.z + v1 * s))
            T.append(strut(a, b + (b - a).normalized() * 0.025 * s, 0.02, 0.05 * s, black, bevel=0))

    def gear(P):
        T = P["Torso"]
        # --- bomba redonda gigante en la espalda, con mecha encendida
        bc = Vector((0, 1.15, 3.15))
        T.append(sphere(0.68, bc, bomb, subdiv=3))
        T.append(cyl(0.22, 0.2, bc + Vector((0, 0, 0.7)), steel, verts=14, bevel=0.02))
        T.append(L.torus(0.22, 0.04, bc + Vector((0, 0, 0.78)), steel, seg=14, minor=4))
        fuse(T, [bc + Vector((0, 0, 0.8)), bc + Vector((0.05, 0.05, 1.0)), bc + Vector((0.18, 0.2, 1.15)),
                 bc + Vector((0.3, 0.42, 1.18)), bc + Vector((0.36, 0.6, 1.08))])
        T.append(sphere(0.12, bc + Vector((-0.3, 0.5, 0.35)), mat("Brillo_Bomba", (0.6, 0.6, 0.65), 0.2, 0.2), subdiv=1,
                        scale=(1, 0.4, 1.4)))                                             # brillo de caricatura
        for z in (-0.25, 0.25):                                                     # correas que la sujetan
            T.append(L.torus(0.62 + 0.0, 0.05, bc + Vector((0, 0, z)), leather, seg=20, minor=4))
        for sx in (-1, 1):
            T.append(box((0.22, 1.06, 0.06), (sx * 0.55, 0, 4.03), leather, bevel=0.01))
            T.append(box((0.22, 0.06, 0.4), (sx * 0.55, -0.53, 3.82), leather, bevel=0.01))
            T.append(box((0.26, 0.07, 0.12), (sx * 0.55, -0.56, 3.62), steel, bevel=0.01))
            # barriles de TNT a los costados de la bomba
            c = Vector((sx * 0.85, 0.9, 2.85))
            T.append(cyl(0.27, 0.8, c, red, verts=14, bevel=0.02))
            for z in (-0.3, 0.3):
                T.append(L.torus(0.275, 0.03, c + Vector((0, 0, z)), black, seg=14, minor=4))
            T.append(box((0.4, 0.04, 0.3), c + Vector((0, 0.27, 0)), white, bevel=0))
            tnt(T, c, c.y + 0.3, s=0.6)
            fuse(T, [c + Vector((0, 0, 0.4)), c + Vector((sx * 0.05, 0.05, 0.6)), c + Vector((sx * 0.12, 0.15, 0.7))], lit=False)
        # --- canana cruzada con dinamita en el pecho
        a, b = Vector((0.82, -0.56, 3.95)), Vector((-0.82, -0.56, 2.32))
        T.append(strut(a, b, 0.05, 0.22, leather, bevel=0))
        for k in range(5):
            dynamite(T, a.lerp(b, 0.18 + k * 0.16) + Vector((0, -0.08, 0)), h=0.36, r=0.065)
        # --- temporizador en el pecho
        tc = Vector((0.45, -0.58, 3.62))
        T.append(box((0.42, 0.1, 0.22), tc, black, bevel=0.02))
        for k in range(4):                                                         # números en rojo
            T.append(box((0.06, 0.03, 0.12), tc + Vector((-0.13 + k * 0.085 + (0.02 if k > 1 else 0), -0.055, 0)), led, bevel=0))
        T.append(box((0.02, 0.03, 0.02), tc + Vector((0.005, -0.055, 0.03)), led, bevel=0))
        T.append(box((0.02, 0.03, 0.02), tc + Vector((0.005, -0.055, -0.03)), led, bevel=0))
        for sx, m in ((-1, led), (1, led)):
            T.append(L.rod(tc + Vector((sx * 0.2, 0, -0.08)), tc + Vector((sx * 0.35, 0.02, -0.4)), 0.02,
                           mat("Cable_Rojo", (0.8, 0.05, 0.05)) if sx < 0 else mat("Cable_Azul", (0.05, 0.2, 0.8)), verts=6))
        # --- atados de dinamita en el cinturón
        for sx in (-1, 1):
            for k in range(3):
                dynamite(T, Vector((sx * 0.82 + (k - 1) * 0.14, -0.62, 2.0)), h=0.4, r=0.07, lit=(k == 1 and sx < 0))
            T.append(box((0.48, 0.18, 0.07), Vector((sx * 0.82, -0.62, 2.05)), tape, bevel=0))
        # --- hollín y quemaduras
        for _ in range(7):
            _zb_front(P, "Torso", (rng.uniform(0.15, 0.3), rng.uniform(0.1, 0.25)), rng.uniform(-0.9, 0.9),
                      rng.uniform(2.3, 3.9), -0.5, soot, rot=rng.uniform(0, 3))
        for nm, sx in (("RightArm", -1), ("LeftArm", 1)):
            for _ in range(3):
                _zb_side(P, nm, (rng.uniform(0.15, 0.3), rng.uniform(0.15, 0.3)), sx * 2.0, rng.uniform(-0.3, 0.3),
                         rng.uniform(2.3, 3.7), soot, rot=rng.uniform(0, 1))
        # --- detonador en la muñeca izquierda (sin manos ni uñas)
        A = P["LeftArm"]
        A.append(box((1.08, 1.08, 0.32), (1.5, 0, 2.35), black, bevel=0.04))
        A.append(box((0.45, 0.2, 0.25), (1.5, -0.6, 2.35), mat("Caja_Detonador", (0.85, 0.65, 0.05)), bevel=0.03))
        A.append(cyl(0.1, 0.08, (1.5, -0.73, 2.35), led, rot=(math.pi / 2, 0, 0), verts=12, bevel=0))     # botón rojo
        A.append(L.rod(Vector((1.92, 0.25, 2.25)), Vector((1.92, 0.25, 2.9)), 0.025, steel))
        A.append(sphere(0.05, (1.92, 0.25, 2.92), led, subdiv=1))
        A.append(L.rod(Vector((1.55, 0.4, 2.5)), Vector((1.2, 0.5, 3.4)), 0.02, mat("Cable_Rojo", (0.8, 0.05, 0.05)), verts=6))

    return _zb_body(K, random.Random(41), gear, chest=False), 1.0


def e_excavador():
    """Zombi excavador: va bajo tierra. Casco con lámpara, taladros en los brazos, motor y herramientas en la espalda, tierra encima."""
    K = _zb_mats()
    K.update(SHIRT=mat("Camisa_Trabajo", (0.32, 0.26, 0.18)), SHIRT2=mat("Trabajo_Oscuro", (0.18, 0.14, 0.09)),
             PANTS=mat("Pantalon_Tierra", (0.2, 0.16, 0.12)))
    helmet = mat("Casco_Naranja", (0.95, 0.5, 0.05), 0.2, 0.4)
    metal = mat("Metal_Taladro", (0.35, 0.36, 0.4), 0.85, 0.3)
    dark = mat("Metal_Oscuro", (0.1, 0.1, 0.12), 0.7, 0.45)
    engine = mat("Motor_Amarillo", (0.85, 0.65, 0.08), 0.4, 0.4)
    wood = mat("Madera", (0.35, 0.2, 0.1))
    dirt = mat("Tierra", (0.26, 0.17, 0.08))
    clod = mat("Terron", (0.33, 0.22, 0.1))
    mud = mat("Barro", (0.17, 0.11, 0.06))
    rock = mat("Piedra", (0.42, 0.42, 0.4))
    root = mat("Raiz", (0.4, 0.28, 0.16))
    vest = mat("Chaleco_Naranja", (1.0, 0.3, 0.02), 0.1, 0.5)
    silver = mat("Banda_Plateada", (0.8, 0.82, 0.85), 0.8, 0.2)
    black = mat("Negro", (0.02, 0.02, 0.02))
    yellow = mat("Peligro_Amarillo", (0.95, 0.7, 0.05), 0.2, 0.5)
    rope = mat("Soga", (0.7, 0.58, 0.35))
    worm = mat("Gusano", (0.85, 0.45, 0.5), rough=0.4)
    lamp = mat("Lampara", (1, 0.95, 0.7), emission=(1, 0.9, 0.6), strength=8)
    hot = mat("Metal_Al_Rojo", (1.0, 0.35, 0.05), emission=(1.0, 0.3, 0.02), strength=5)
    gems = [mat("Cristal_Violeta", (0.6, 0.2, 1.0), emission=(0.55, 0.15, 1.0), strength=3),
            mat("Cristal_Celeste", (0.2, 0.8, 1.0), emission=(0.15, 0.75, 1.0), strength=3)]
    soot = mat("Hollin", (0.08, 0.07, 0.07))
    hose = mat("Manguera", (0.05, 0.05, 0.06), 0.1, 0.6)
    rng = random.Random(53)

    def clods(T, c, spread, n, up=True):
        """Terrones y piedritas amontonados alrededor de c."""
        for _ in range(n):
            p = c + Vector((rng.uniform(-spread, spread), rng.uniform(-spread, spread), rng.uniform(0, 0.08) if up else 0))
            sz = rng.uniform(0.1, 0.22)
            T.append(box((sz, sz * rng.uniform(0.7, 1.2), sz * 0.7), p, rock if rng.random() < 0.25 else clod,
                         rot=(rng.uniform(-0.4, 0.4), rng.uniform(-0.4, 0.4), rng.uniform(0, 3)), bevel=0.02))

    def crystal(T, c, d, s=1.0):
        """Cristal de mineral que brilla, clavado en la tierra apuntando hacia d."""
        m = gems[rng.randrange(2)]
        T.append(cyl(0.08 * s, 0.3 * s, c + d * 0.1 * s, m, rot=d, verts=6, bevel=0))
        T.append(cone(0.08 * s, 0.14 * s, c + d * 0.32 * s, m, rot=d, verts=6))
        d2 = (d + Vector((0.5, 0.3, 0.2))).normalized()
        T.append(cone(0.05 * s, 0.22 * s, c + d2 * 0.12 * s, m, rot=d2, verts=6))

    def drill(A, tip, sx):
        """Taladro cónico con espiral y dientes, punta al rojo; apunta hacia -Z desde `tip` (punta del brazo en reposo)."""
        A.append(cyl(0.5, 0.24, tip + Vector((0, 0, -0.08)), dark, verts=16, bevel=0.03))
        for k in range(8):                                                       # tuercas del collar
            a = k / 8 * 2 * math.pi
            A.append(cyl(0.05, 0.06, tip + Vector((math.cos(a) * 0.42, math.sin(a) * 0.42, -0.21)), metal, verts=6, bevel=0))
        A.append(cyl(0.38, 0.12, tip + Vector((0, 0, -0.26)), yellow, verts=16, bevel=0.01))
        A.append(cone(0.36, 1.1, tip + Vector((0, 0, -0.85)), metal, rot=(math.pi, 0, 0), verts=16))
        A.append(cone(0.08, 0.2, tip + Vector((0, 0, -1.32)), hot, rot=(math.pi, 0, 0), verts=12))      # punta al rojo
        for k in range(7):                                                       # espiral con dientes
            t = k / 7
            c = tip + Vector((0, 0, -0.38 - t * 0.9))
            r = 0.34 * (1 - t) + 0.04
            A.append(L.torus(r, 0.035, c, dark, rot=Vector((0.25, 0.1 * (k % 2), 1)).normalized(), seg=12, minor=4))
            a = k * 1.9
            d = Vector((math.cos(a), math.sin(a), -0.3)).normalized()
            A.append(cone(0.05, 0.14, c + Vector((math.cos(a) * r, math.sin(a) * r, 0)), metal, rot=d, verts=4))
        for sy in (-1, 1):                                                       # pistones hidráulicos
            a0 = Vector((tip.x + sx * 0.42, sy * 0.3, 3.2))
            a1 = Vector((tip.x + sx * 0.42, sy * 0.3, 2.0))
            A.append(L.rod(a0, a0.lerp(a1, 0.55), 0.06, dark, verts=8))
            A.append(L.rod(a0.lerp(a1, 0.5), a1, 0.035, metal, verts=8))
        clods(A, tip + Vector((0, 0, -0.3)), 0.3, 3, up=False)

    def gear(P):
        T = P["Torso"]
        H = P["Head"]
        # --- casco de obra abollado, con lámpara, batería y barro
        hc = ZB_HEAD + Vector((0, 0, 0.42))
        H.append(sphere(0.72, hc, helmet, subdiv=3, scale=(1, 1, 0.6)))
        H.append(cyl(0.84, 0.06, hc + Vector((0, 0, -0.08)), helmet, verts=24, bevel=0.01))
        # taladro chico arriba del casco, apuntando adelante y arriba (el que va primero al cavar)
        db, dd = hc + Vector((0, -0.15, 0.36)), Vector((0, -0.8, 0.6)).normalized()
        H.append(cyl(0.2, 0.14, db, dark, rot=dd, verts=12, bevel=0.02))
        H.append(cyl(0.15, 0.08, db + dd * 0.1, yellow, rot=dd, verts=12, bevel=0))
        H.append(cone(0.14, 0.45, db + dd * 0.36, metal, rot=dd, verts=12))
        H.append(cone(0.04, 0.08, db + dd * 0.6, hot, rot=dd, verts=8))
        for k in range(3):
            H.append(L.torus(0.12 - k * 0.035, 0.022, db + dd * (0.2 + k * 0.12), dark, rot=dd, seg=10, minor=4))
        for a, z in ((0.7, 0.2), (2.6, 0.1), (4.2, 0.25)):                       # abolladuras
            H.append(sphere(0.09, hc + Vector((math.cos(a) * 0.66, math.sin(a) * 0.66, z)), mat("Abolladura", (0.6, 0.3, 0.03), 0.2, 0.5),
                            subdiv=1, scale=(1, 1, 0.5)))
        H.append(box((0.04, 0.25, 0.18), hc + Vector((0.66, -0.1, 0.12)), yellow, rot=(0, 0.35, 0), bevel=0))   # calcomanía
        H.append(box((0.05, 0.08, 0.08), hc + Vector((0.69, -0.1, 0.12)), black, rot=(0.785, 0.35, 0), bevel=0))
        H.append(box((0.22, 0.14, 0.28), hc + Vector((0, 0.72, 0.0)), dark, bevel=0.02))                  # batería
        H.append(cyl(0.2, 0.18, hc + Vector((0, -0.7, 0.12)), dark, rot=(math.pi / 2, 0, 0), verts=14, bevel=0.01))
        H.append(cyl(0.15, 0.04, hc + Vector((0, -0.8, 0.12)), lamp, rot=(math.pi / 2, 0, 0), verts=14, bevel=0))
        H.append(L.torus(0.17, 0.025, hc + Vector((0, -0.8, 0.12)), metal, rot=(math.pi / 2, 0, 0), seg=14, minor=4))
        H.append(L.rod(hc + Vector((0.12, -0.6, 0.0)), hc + Vector((0.1, 0.65, -0.05)), 0.025, hose, verts=6))
        for k in range(6):                                                       # barro chorreando del ala
            a = rng.uniform(0, 2 * math.pi)
            ln = rng.uniform(0.08, 0.2)
            p = hc + Vector((math.cos(a) * 0.8, math.sin(a) * 0.8, -0.1 - ln / 2))
            if math.sin(a) > -0.5:                                                # no tapar el frente
                H.append(box((0.06, 0.06, ln), p, mud, bevel=0))
        clods(H, hc + Vector((0.15, 0.15, 0.4)), 0.25, 4)
        crystal(H, hc + Vector((-0.25, 0.2, 0.38)), Vector((-0.3, 0.2, 1)).normalized(), 0.8)
        # --- medidor de profundidad en el tirante izquierdo (pantalla verde)
        mc = Vector((0.5, -0.66, 3.0))
        T.append(box((0.32, 0.1, 0.4), mc, dark, bevel=0.02))
        T.append(box((0.24, 0.03, 0.14), mc + Vector((0, -0.05, 0.08)), mat("Pantalla_Verde", (0.2, 1.0, 0.3), emission=(0.15, 1.0, 0.25), strength=3), bevel=0))
        for k in range(3):
            T.append(box((0.05, 0.03, 0.06), mc + Vector((-0.08 + k * 0.08, -0.05, -0.1)), (yellow, black, mat("Led_Rojo", (1, 0.1, 0.05), emission=(1, 0.1, 0.05), strength=4))[k], bevel=0))
        # --- martillo de geólogo y cincel colgando del cinturón (lado derecho, -X)
        hb = Vector((-0.88, -0.62, 1.95))
        T.append(strut(hb + Vector((0, 0, 0.12)), hb + Vector((0.05, 0, -0.45)), 0.06, 0.06, wood, bevel=0))
        T.append(box((0.32, 0.09, 0.1), hb + Vector((0.06, 0, -0.48)), metal, bevel=0.01))
        T.append(cone(0.05, 0.14, hb + Vector((0.27, 0, -0.48)), metal, rot=Vector((1, 0, 0)), verts=4))
        T.append(L.rod(Vector((-0.62, -0.6, 2.1)), Vector((-0.6, -0.62, 1.7)), 0.03, metal, verts=6))
        T.append(cone(0.035, 0.08, Vector((-0.6, -0.62, 1.66)), metal, rot=(math.pi, 0, 0), verts=4))
        # --- chaleco naranja con bandas plateadas (dos vueltas)
        for z in (3.3, 2.65):
            T.append(box((2.05, 1.05, 0.24), (0, 0, z), vest, bevel=0))
            T.append(box((2.07, 1.07, 0.07), (0, 0, z), silver, bevel=0))
        for sx in (-1, 1):                                                       # tiradores
            T.append(box((0.2, 0.06, 1.8), (sx * 0.5, -0.555, 3.05), K["SHIRT2"], bevel=0))
            T.append(box((0.22, 0.07, 0.1), (sx * 0.5, -0.58, 3.75), metal, bevel=0))
        # --- motor detallado en la espalda
        ec = Vector((0, 0.78, 3.1))
        T.append(box((1.1, 0.5, 0.95), ec, engine, bevel=0.06))
        for k in range(5):                                                       # aletas de enfriamiento
            T.append(box((0.9, 0.06, 0.05), ec + Vector((0, 0.27, -0.3 + k * 0.15)), dark, bevel=0))
        for k in range(5):                                                       # franjas de peligro abajo
            T.append(box((0.2, 0.52, 0.12), ec + Vector((-0.45 + k * 0.22, 0, -0.42)), yellow if k % 2 == 0 else black,
                         rot=(0, 0.5, 0), bevel=0))
        tk = ec + Vector((-0.2, 0.05, 0.62))                                     # tanque de combustible
        T.append(cyl(0.2, 0.75, tk, mat("Tanque_Rojo", (0.7, 0.08, 0.05), 0.4, 0.4), rot=(0, math.pi / 2, 0), verts=12, bevel=0.02))
        T.append(cyl(0.07, 0.08, tk + Vector((0.2, 0, 0.2)), dark, verts=8, bevel=0))
        for sx in (-1, 1):                                                       # pistones a los costados
            T.append(cyl(0.1, 0.5, ec + Vector((sx * 0.62, 0.05, 0.1)), metal, verts=10, bevel=0.01))
            T.append(cyl(0.12, 0.08, ec + Vector((sx * 0.62, 0.05, 0.38)), dark, verts=10, bevel=0))
        g = ec + Vector((0.3, 0.27, 0.25))                                      # manómetro
        T.append(cyl(0.12, 0.05, g, metal, rot=(math.pi / 2, 0, 0), verts=14, bevel=0))
        T.append(cyl(0.09, 0.03, g + Vector((0, 0.03, 0)), mat("Dial", (0.92, 0.92, 0.88)), rot=(math.pi / 2, 0, 0), verts=14, bevel=0))
        T.append(box((0.015, 0.02, 0.08), g + Vector((0.02, 0.05, 0.02)), black, rot=(0, -0.6, 0), bevel=0))
        ex0 = ec + Vector((0.4, 0.12, 0.45))                                     # escape
        T.append(L.rod(ex0, ex0 + Vector((0, 0.05, 0.85)), 0.08, dark, verts=10))
        T.append(cyl(0.11, 0.1, ex0 + Vector((0, 0.05, 0.9)), metal, verts=10, bevel=0))
        T.append(cyl(0.07, 0.04, ex0 + Vector((0, 0.05, 0.96)), soot, verts=10, bevel=0))
        # --- pico y pala cruzados en X
        a, b = Vector((-0.8, 1.12, 2.3)), Vector((0.6, 1.12, 4.6))              # pala
        T.append(strut(a, b, 0.09, 0.09, wood, bevel=0))
        T.append(box((0.3, 0.08, 0.1), b + (b - a).normalized() * 0.05, dark, rot=(0, -math.atan2(b.z - a.z, b.x - a.x), 0), bevel=0))
        T.append(box((0.5, 0.06, 0.6), a + Vector((-0.12, 0, -0.25)), metal, rot=(0, 0.52, 0), bevel=0.02))
        a, b = Vector((0.8, 1.18, 2.3)), Vector((-0.55, 1.18, 4.45))            # pico
        T.append(strut(a, b, 0.09, 0.09, wood, bevel=0))
        d = (b - a).normalized()
        perp = Vector((d.z, 0, -d.x))
        T.append(strut(b - perp * 0.55, b + perp * 0.55 + d * 0.05, 0.1, 0.12, metal, bevel=0.01))
        T.append(cone(0.06, 0.2, b - perp * 0.62, metal, rot=-perp, verts=4))
        T.append(cone(0.06, 0.2, b + perp * 0.62, metal, rot=perp, verts=4))
        # rollo de soga al costado
        for k in range(3):
            T.append(L.torus(0.24, 0.045, Vector((1.08, 0.3, 2.9 + k * 0.07)), rope, rot=(0, math.pi / 2, 0), seg=14, minor=4))
        # --- mangueras y correas
        for sx in (-1, 1):
            T.append(L.rod(ec + Vector((sx * 0.5, 0, 0.3)), Vector((sx * 0.9, 0.3, 3.9)), 0.05, hose, verts=6))
            T.append(box((0.22, 1.06, 0.06), (sx * 0.55, 0, 4.03), K["SHIRT2"], bevel=0.01))
        # --- tierra, cristales y gusanos en los hombros
        for sx in (-1, 1):
            clods(T, Vector((sx * 0.6, 0, 4.03)), 0.25, 4)
            crystal(T, Vector((sx * 0.75, 0.2, 4.05)), Vector((sx * 0.5, 0.2, 1)).normalized())
        crystal(T, ec + Vector((-0.45, 0.25, -0.1)), Vector((-0.6, 0.6, 0.3)).normalized(), 0.8)
        for c in (Vector((0.4, -0.2, 4.08)), Vector((-0.35, 0.3, 4.08))):        # gusanos
            pts = [c + Vector((k * 0.08, math.sin(k * 1.4) * 0.06, abs(math.sin(k * 0.9)) * 0.06)) for k in range(5)]
            for p0, p1 in zip(pts, pts[1:]):
                T.append(L.rod(p0, p1, 0.03, worm, verts=6))
        for _ in range(8):
            _zb_front(P, "Torso", (rng.uniform(0.15, 0.35), rng.uniform(0.1, 0.25)), rng.uniform(-0.9, 0.9), rng.uniform(2.3, 3.9),
                      rng.choice((-0.5, 0.5)), dirt, rot=rng.uniform(0, 3))
        # --- farol colgado del cinturón y raíces
        fc = Vector((0.85, -0.62, 1.75))
        T.append(L.rod(Vector((0.85, -0.55, 2.1)), fc + Vector((0, 0, 0.22)), 0.02, dark, verts=6))
        T.append(cyl(0.12, 0.05, fc + Vector((0, 0, 0.18)), dark, verts=10, bevel=0))
        T.append(cyl(0.09, 0.22, fc, lamp, verts=10, bevel=0))
        for k in range(4):
            a = k / 4 * 2 * math.pi + 0.4
            T.append(box((0.025, 0.025, 0.24), fc + Vector((math.cos(a) * 0.1, math.sin(a) * 0.1, 0)), dark, bevel=0))
        T.append(cyl(0.12, 0.04, fc + Vector((0, 0, -0.13)), dark, verts=10, bevel=0))
        for k in range(3):
            p = Vector((-0.8 + k * 0.5, -0.53, 2.05))
            q = p + Vector((rng.uniform(-0.15, 0.15), -0.03, -rng.uniform(0.35, 0.6)))
            T.append(strut(p, q, 0.04, 0.04, root, bevel=0))
            T.append(strut(q, q + Vector((rng.uniform(-0.15, 0.15), 0, -0.2)), 0.03, 0.03, root, bevel=0))
        # --- taladros en las puntas de los brazos (sin manos ni uñas)
        for nm, sx in (("RightArm", -1), ("LeftArm", 1)):
            x = sx * 1.5
            drill(P[nm], Vector((x, 0, 2.0)), sx)
            P[nm].append(L.rod(Vector((x + sx * 0.52, 0.2, 3.3)), Vector((x + sx * 0.5, 0.2, 2.1)), 0.05, hose, verts=6))
            clods(P[nm], Vector((x, 0, 4.0)), 0.3, 3)
            for _ in range(3):
                _zb_side(P, nm, (rng.uniform(0.2, 0.4), rng.uniform(0.15, 0.3)), sx * 2.0, rng.uniform(-0.3, 0.3), rng.uniform(2.2, 3.2), dirt,
                         rot=rng.uniform(0, 1))
        # --- hombreras de metal remachadas (lado de afuera de cada brazo)
        for nm, sx in (("RightArm", -1), ("LeftArm", 1)):
            pc = Vector((sx * 2.06, 0, 3.6))
            P[nm].append(box((0.08, 1.12, 0.8), pc, metal, bevel=0.03))
            P[nm].append(box((0.1, 1.14, 0.08), pc + Vector((0, 0, -0.38)), dark, bevel=0))
            for y in (-0.42, 0.42):
                for z in (-0.25, 0.25):
                    P[nm].append(sphere(0.045, pc + Vector((sx * 0.05, y, z)), dark, subdiv=1))
        # --- rodilleras de metal con correas
        for nm, sx in (("RightLeg", -1), ("LeftLeg", 1)):
            kc = Vector((sx * 0.5, -0.56, 1.25))
            P[nm].append(box((0.7, 0.12, 0.45), kc, metal, bevel=0.04))
            P[nm].append(box((0.4, 0.06, 0.2), kc + Vector((0, -0.07, 0)), dark, bevel=0.01))
            for z in (1.12, 1.38):
                P[nm].append(box((1.05, 1.05, 0.06), (sx * 0.5, 0, z), black, bevel=0))
        # --- piernas cubiertas de tierra y barro
        for nm, sx in (("RightLeg", -1), ("LeftLeg", 1)):
            for _ in range(4):
                _zb_side(P, nm, (rng.uniform(0.25, 0.45), rng.uniform(0.2, 0.4)), sx * 1.0, rng.uniform(-0.3, 0.3), rng.uniform(0.3, 1.0), dirt,
                         rot=rng.uniform(0, 1))
            for y in (-0.5, 0.5):
                for _ in range(2):
                    _zb_front(P, nm, (rng.uniform(0.2, 0.4), rng.uniform(0.15, 0.3)), sx * 0.5 + rng.uniform(-0.25, 0.25), rng.uniform(0.3, 0.9), y,
                              mud, rot=rng.uniform(0, 3))
            clods(P[nm], Vector((sx * 0.5, -0.45, 0.2)), 0.35, 3, up=False)

    return _zb_body(K, random.Random(53), gear, chest=False), 1.0


def e_comandante():
    """Jefe Comandante Escudo: zombi gigante con un generador de escudos enorme (los escudos se crean en el juego)."""
    s = 2.5
    K = _zb_mats()
    K.update(SHIRT=mat("Uniforme_Rojo", (0.42, 0.03, 0.04)), SHIRT2=mat("Uniforme_Rojo_Oscuro", (0.2, 0.01, 0.02)),
             PANTS=mat("Pantalon_Azul", (0.06, 0.09, 0.35)))
    armor = mat("Blindaje_Azul_Rey", (0.05, 0.17, 0.65), 0.6, 0.3)
    dark = mat("Metal_Oscuro", (0.1, 0.1, 0.12), 0.7, 0.45)
    steel = mat("Acero", (0.5, 0.52, 0.56), 0.9, 0.3)
    gold = mat("Oro", (1.0, 0.72, 0.2), 1.0, 0.25)
    black = mat("Negro", (0.02, 0.02, 0.02))
    yellow = mat("Peligro_Amarillo", (0.95, 0.7, 0.05), 0.2, 0.5)
    banner = mat("Estandarte_Rojo", (0.6, 0.04, 0.05))
    cape = mat("Capa_Roja", (0.55, 0.03, 0.04), 0.0, 0.6)
    glow = mat("Energia_Celeste", (0.3, 0.85, 1.0), emission=(0.2, 0.75, 1.0), strength=3)
    medals = [mat("Cinta_Roja", (0.7, 0.05, 0.05)), mat("Cinta_Azul", (0.1, 0.3, 0.8)), mat("Cinta_Verde", (0.1, 0.5, 0.15))]

    def hexplate(T, c, r, axis, m, depth=0.06):
        """Placa hexagonal con el eje en `axis`."""
        T.append(cyl(r, depth, c, m, rot=axis, verts=6, bevel=0))

    def coil(T, base, h, sc=1.0):
        T.append(cyl(0.13 * sc, 0.12, base + Vector((0, 0, 0.06)), steel, verts=10, bevel=0.01))
        T.append(L.rod(base, base + Vector((0, 0, h)), 0.035 * sc, steel))
        for k in range(3):
            T.append(L.torus((0.14 - k * 0.03) * sc, 0.022, base + Vector((0, 0, h * (0.35 + k * 0.2))), glow, seg=12, minor=4))
        T.append(sphere(0.08 * sc, base + Vector((0, 0, h + 0.05)), glow, subdiv=2))

    def gear(P):
        T = P["Torso"]
        H = P["Head"]
        # --- gorra de oficial con visera e insignia hexagonal (la visera no es una cara)
        hc = ZB_HEAD + Vector((0, 0, 0.5))
        H.append(cyl(0.66, 0.28, hc, armor, verts=24, bevel=0.03))
        H.append(cyl(0.7, 0.1, hc + Vector((0, 0, 0.16)), armor, verts=24, bevel=0.03))
        for k in range(9):                                                         # penacho rojo
            a = math.radians(-60 + k * 15)
            H.append(box((0.06, 0.12, 0.5), hc + Vector((0, math.sin(a) * 0.3, 0.3 + math.cos(a) * 0.2)), banner, rot=(a, 0, 0), bevel=0))
        H.append(box((0.1, 0.5, 0.08), hc + Vector((0, 0, 0.22)), gold, bevel=0))
        H.append(box((0.08, 0.2, 0.2), hc + Vector((0.68, 0.1, 0)), armor, bevel=0.02))                # antena de comunicación
        H.append(L.rod(hc + Vector((0.7, 0.15, 0.08)), hc + Vector((0.74, 0.25, 0.8)), 0.025, steel, verts=6))
        H.append(sphere(0.05, hc + Vector((0.74, 0.25, 0.83)), mat("Led_Rojo", (1, 0.1, 0.05), emission=(1, 0.1, 0.05), strength=5), subdiv=1))
        H.append(cyl(0.665, 0.08, hc + Vector((0, 0, -0.1)), gold, verts=24, bevel=0))
        H.append(box((0.9, 0.42, 0.05), hc + Vector((0, -0.72, -0.16)), black, rot=(0.25, 0, 0), bevel=0.02))      # visera
        hexplate(H, hc + Vector((0, -0.68, 0.06)), 0.14, (math.pi / 2, 0, 0), gold, 0.05)
        hexplate(H, hc + Vector((0, -0.71, 0.06)), 0.08, (math.pi / 2, 0, 0), glow, 0.04)
        # --- peto blindado con hexágono que brilla, medallas y hebilla dorada
        T.append(box((1.7, 0.14, 1.15), (0, -0.56, 3.35), armor, bevel=0.05))
        T.append(box((1.74, 0.16, 0.08), (0, -0.57, 3.92), gold, bevel=0))
        T.append(box((1.74, 0.16, 0.08), (0, -0.57, 2.78), gold, bevel=0))
        hexplate(T, Vector((0, -0.65, 3.35)), 0.3, (math.pi / 2, 0, 0), gold, 0.06)
        hexplate(T, Vector((0, -0.69, 3.35)), 0.22, (math.pi / 2, 0, 0), glow, 0.05)
        for k, m in enumerate(medals):                                             # medallas
            x = -0.65 + k * 0.17
            T.append(box((0.12, 0.05, 0.16), (x, -0.66, 3.7), m, bevel=0))
            T.append(cyl(0.06, 0.04, (x, -0.66, 3.55), gold, rot=(math.pi / 2, 0, 0), verts=10, bevel=0))
        T.append(box((0.5, 0.1, 0.3), (0, -0.56, 2.11), gold, bevel=0.03))        # hebilla
        hexplate(T, Vector((0, -0.62, 2.11)), 0.1, (math.pi / 2, 0, 0), glow, 0.04)
        # --- hombreras enormes con borde dorado y púas
        for sx in (-1, 1):
            pc = Vector((sx * 1.45, 0, 4.15))
            T.append(box((1.35, 1.3, 0.35), pc, armor, bevel=0.08))
            T.append(box((1.39, 1.34, 0.08), pc + Vector((0, 0, -0.16)), gold, bevel=0))
            T.append(box((1.15, 1.1, 0.2), pc + Vector((0, 0, 0.22)), armor, bevel=0.06))
            for k in range(3):
                T.append(cone(0.1, 0.35, pc + Vector((sx * 0.25 + (k - 1) * sx * 0.25, 0, 0.45)), steel,
                              rot=Vector((sx * 0.3, 0, 1)).normalized(), verts=6))
            hexplate(T, pc + Vector((sx * 0.68, 0, 0)), 0.15, (0, math.pi / 2, 0), glow, 0.04)
        # --- generador gigante en la espalda: 3 núcleos, 4 bobinas, rejillas y franjas
        gc = Vector((0, 0.98, 3.05))
        T.append(box((1.8, 0.85, 1.9), gc, armor, bevel=0.1))
        for z in (0.82, -0.82):
            T.append(box((1.86, 0.9, 0.12), gc + Vector((0, 0, z)), gold if z > 0 else dark, bevel=0.02))
        for k, x in enumerate((-0.52, 0, 0.52)):                                   # núcleos
            c = gc + Vector((x, 0.48, 0.05))
            T.append(cyl(0.2, 1.1, c, glow, verts=12, bevel=0))
            for z in (-0.58, 0.58):
                T.append(cyl(0.24, 0.08, c + Vector((0, 0, z)), steel, verts=12, bevel=0.01))
            for z in (-0.25, 0.25):
                T.append(L.torus(0.22, 0.035, c + Vector((0, 0, z)), dark, seg=12, minor=4))
        for k in range(6):                                                          # franjas de peligro abajo
            T.append(box((0.26, 0.88, 0.14), gc + Vector((-0.65 + k * 0.26, 0, -0.98)), yellow if k % 2 == 0 else black,
                         rot=(0, 0.5, 0), bevel=0))
        for sx in (-1, 1):                                                          # rejillas laterales que brillan
            T.append(box((0.04, 0.6, 0.9), gc + Vector((sx * 0.92, 0, 0)), glow, bevel=0))
            for k in range(5):
                T.append(box((0.06, 0.64, 0.06), gc + Vector((sx * 0.94, 0, -0.36 + k * 0.18)), dark, bevel=0))
        for x, y in ((-0.6, 0.75), (0.6, 0.75), (-0.6, 1.25), (0.6, 1.25)):         # bobinas
            coil(T, Vector((x, y, gc.z + 0.95)), 0.9, 1.2)
        # plato proyector hexagonal arriba del generador (de donde sale el escudo)
        dc = gc + Vector((0, 0.15, 1.08))
        dd = Vector((0, 0.35, 1)).normalized()
        T.append(cyl(0.18, 0.2, dc, steel, rot=dd, verts=10, bevel=0.01))
        hexplate(T, dc + dd * 0.15, 0.62, dd, gold, 0.06)
        hexplate(T, dc + dd * 0.19, 0.55, dd, armor, 0.04)
        for k in range(7):                                                          # panal en el plato
            q = Vector((0, 0, 0)) if k == 0 else Vector((math.cos(k * math.pi / 3), math.sin(k * math.pi / 3), 0)) * 0.3
            q = dd.to_track_quat("Z", "Y").to_matrix() @ q
            hexplate(T, dc + dd * 0.22 + q, 0.14, dd, glow, 0.03)
        tip = dc + dd * 0.85
        for k in range(3):                                                          # varillas al emisor
            a = k / 3 * 2 * math.pi
            b = dc + dd * 0.2 + dd.to_track_quat("Z", "Y").to_matrix() @ Vector((math.cos(a) * 0.5, math.sin(a) * 0.5, 0))
            T.append(L.rod(b, tip, 0.025, gold, verts=6))
        T.append(sphere(0.11, tip, glow, subdiv=2))
        T.append(L.torus(0.16, 0.025, tip, gold, rot=dd, seg=12, minor=4))
        # gola de armadura alrededor del cuello
        T.append(cyl(0.68, 0.2, Vector((0, 0, 4.08)), armor, verts=24, bevel=0.03))
        T.append(L.torus(0.68, 0.035, Vector((0, 0, 4.18)), gold, seg=24, minor=4))
        for sx in (-1, 1):                                                          # estrellas de rango en la gola
            for k in range(3):
                T.append(cyl(0.065, 0.03, Vector((sx * (0.22 + k * 0.14), -0.69, 4.08)), gold, rot=(math.pi / 2, 0, 0), verts=5, bevel=0))
        # faldón de placas sobre los muslos (adelante y a los costados)
        for x, y, w, rz in ((-0.5, -0.66, 0.8, 0), (0.5, -0.66, 0.8, 0), (-1.0, -0.2, 0.6, 1), (1.0, -0.2, 0.6, 1)):
            c = Vector((x, y, 1.72))
            sz = (w, 0.1, 0.55) if not rz else (0.1, w, 0.55)
            T.append(box(sz, c, armor, rot=(0.12 if not rz else 0, 0, 0), bevel=0.03))
            T.append(box((sz[0] + 0.03, sz[1] + 0.03, 0.06), c + Vector((0, 0, -0.27)), gold, bevel=0))
            if not rz:
                hexplate(T, c + Vector((0, -0.07, 0.03)), 0.1, (math.pi / 2, 0, 0), glow, 0.03)
        # emisores chicos de escudo en las hombreras
        for sx in (-1, 1):
            ec = Vector((sx * 1.2, 0.35, 4.55))
            T.append(cyl(0.1, 0.25, ec, steel, verts=10, bevel=0))
            hexplate(T, ec + Vector((0, 0, 0.14)), 0.16, (0, 0, 0), gold, 0.04)
            hexplate(T, ec + Vector((0, 0, 0.17)), 0.11, (0, 0, 0), glow, 0.03)
        # franjas de luz en el frente de las hombreras
        for sx in (-1, 1):
            T.append(box((1.0, 0.04, 0.08), (sx * 1.45, -0.67, 4.1), glow, bevel=0))
        # bolsas azules con broche dorado en el cinturón
        for sx in (-1, 1):
            bc = Vector((sx * 1.12, -0.05, 2.05))
            T.append(box((0.24, 0.4, 0.34), bc, armor, bevel=0.03))
            T.append(box((0.26, 0.42, 0.1), bc + Vector((0, 0, 0.14)), K["SHIRT2"], rot=(0, -sx * 0.12, 0), bevel=0.02))
            T.append(box((0.05, 0.08, 0.08), bc + Vector((sx * 0.13, 0, 0.07)), gold, bevel=0))
        # alas hexagonales a los costados del generador (3 placas en abanico por lado)
        for sx in (-1, 1):
            base = gc + Vector((sx * 0.92, 0.1, 0.2))
            T.append(cyl(0.12, 0.3, base + Vector((sx * 0.1, 0, 0)), steel, rot=(0, math.pi / 2, 0), verts=10, bevel=0.01))
            for k, (dx, dz, r) in enumerate(((0.75, 0.75, 0.42), (1.0, 0.05, 0.48), (0.75, -0.65, 0.38))):
                c = base + Vector((sx * dx, 0.25, dz))
                n = Vector((sx * 0.35, 1, 0.1 * (1 - k))).normalized()             # mira hacia atrás y un poco afuera
                T.append(strut(base + Vector((sx * 0.15, 0, 0)), c, 0.07, 0.07, steel, bevel=0))
                hexplate(T, c, r, n, gold, 0.06)
                hexplate(T, c + n * 0.035, r * 0.82, n, armor, 0.03)
                hexplate(T, c + n * 0.055, r * 0.55, n, glow, 0.03)
        # marcas de batalla: rayones en las hombreras y el generador
        for sx in (-1, 1):
            for k in range(3):
                T.append(box((0.4, 0.05, 0.025), (sx * (1.3 + k * 0.08), -0.35 + k * 0.08, 4.43), K["SHIRT2"], rot=(0, 0, sx * 0.7), bevel=0))
        for k in range(3):
            T.append(box((0.03, 0.025, 0.5), gc + Vector((0.3 + k * 0.09, 0.44, -0.55)), black, rot=(0, 0.5, 0), bevel=0))
        # estandarte del comandante
        pb = gc + Vector((-0.8, 0.3, 0.95))
        T.append(L.rod(pb, pb + Vector((0, 0, 1.7)), 0.04, gold))
        T.append(sphere(0.08, pb + Vector((0, 0, 1.75)), gold, subdiv=1))
        fl = pb + Vector((-0.4, 0, 1.3))
        T.append(box((0.8, 0.04, 0.6), fl, banner, bevel=0))
        T.append(box((0.84, 0.05, 0.05), fl + Vector((0, 0, 0.3)), gold, bevel=0))
        for k in range(3):                                                          # borde rasgado
            T.append(cone(0.13, 0.2, fl + Vector((-0.27 + k * 0.27, 0, -0.38)), banner, rot=(math.pi, 0, 0), verts=3))
        for y in (-0.03, 0.03):
            hexplate(T, fl + Vector((0, y * 1.2, 0.02)), 0.18, (math.pi / 2, 0, 0), glow, 0.02)
        # caños del generador a las hombreras
        for sx in (-1, 1):
            T.append(L.rod(gc + Vector((sx * 0.75, -0.2, 0.9)), Vector((sx * 1.2, 0.3, 4.2)), 0.07, dark, verts=8))
        # --- banda cruzada roja con estrella dorada
        a0, a1 = Vector((0.85, -0.67, 3.88)), Vector((-0.85, -0.67, 2.82))
        T.append(strut(a0, a1, 0.04, 0.22, banner, bevel=0))
        T.append(strut(a0 + Vector((0, -0.01, 0.11)), a1 + Vector((0, -0.01, 0.11)), 0.04, 0.03, gold, bevel=0))
        T.append(strut(a0 + Vector((0, -0.01, -0.11)), a1 + Vector((0, -0.01, -0.11)), 0.04, 0.03, gold, bevel=0))
        st = a0.lerp(a1, 0.2) + Vector((0, -0.04, 0))
        T.append(cyl(0.13, 0.04, st, gold, rot=(math.pi / 2, 0, 0), verts=5, bevel=0))
        # --- líneas de energía en el peto
        for sx in (-1, 1):
            T.append(box((0.5, 0.03, 0.05), (sx * 0.5, -0.64, 3.1), glow, rot=(0, sx * 0.5, 0), bevel=0))
            T.append(box((0.05, 0.03, 0.4), (sx * 0.72, -0.64, 3.55), glow, bevel=0))
        # --- flecos dorados en las hombreras y colas de capa roja rasgadas
        for sx in (-1, 1):
            for k in range(7):
                T.append(box((0.05, 0.06, 0.28), (sx * 2.14, -0.5 + k * 0.165, 3.86), gold, bevel=0))
            cc = Vector((sx * 1.35, 0.7, 2.7))
            T.append(box((0.62, 0.05, 2.5), cc, cape, rot=(-0.12, 0, sx * 0.05), bevel=0))
            T.append(box((0.64, 0.06, 0.08), cc + Vector((0, -0.15, 1.2)), gold, rot=(-0.12, 0, 0), bevel=0))
            for k in range(3):                                                     # borde rasgado
                T.append(cone(0.11, 0.22, cc + Vector((-0.2 + k * 0.2, 0.15, -1.33)), cape, rot=(math.pi, 0, 0), verts=3))
            _zb_front(P, "Torso", (0.2, 0.15), cc.x, 2.0, cc.y + 0.12, K["BLOOD2"], rot=0.6)   # agujero/mancha
        # --- brazo izquierdo: escudo hexagonal de placas (sin manos ni uñas)
        A = P["LeftArm"]
        A.append(box((1.15, 1.15, 0.5), (1.5, 0, 2.4), armor, bevel=0.05))
        sc = Vector((2.12, 0, 2.7))
        hexplate(A, sc, 0.95, (0, math.pi / 2, 0), armor, 0.12)
        hexplate(A, sc + Vector((0.07, 0, 0)), 0.98, (0, math.pi / 2, 0), gold, 0.03)
        hexplate(A, sc + Vector((0.08, 0, 0)), 0.9, (0, math.pi / 2, 0), dark, 0.03)
        hp = cyl(0.95, 0.12, sc + Vector((0.01, 0, 0)), armor, rot=(0, math.pi / 2, 0), verts=6, bevel=0)
        A.append(hp)
        corners = [hp.matrix_world @ v.co for v in hp.data.vertices if (hp.matrix_world @ v.co).x > sc.x + 0.01]
        for cp in corners:                                                          # púas en las 6 puntas
            d = (cp - Vector((cp.x, sc.y, sc.z))).normalized()
            A.append(cone(0.07, 0.3, cp + d * 0.12, steel, rot=d, verts=6))
        for k in range(7):                                                          # panal de 7 hexágonos
            if k == 0:
                q = Vector((0, 0, 0))
            else:
                a = (k - 1) / 6 * 2 * math.pi + math.pi / 6
                q = Vector((0, math.cos(a) * 0.46, math.sin(a) * 0.46))
            hexplate(A, sc + Vector((0.12, 0, 0)) + q, 0.24, (0, math.pi / 2, 0), glow, 0.03)
        # anillos de energía en los antebrazos
        for nm, sx in (("RightArm", -1), ("LeftArm", 1)):
            for z in (2.95, 3.15):
                P[nm].append(box((1.1, 1.1, 0.06), (sx * 1.5, 0, z), glow, bevel=0))
        # --- brazo derecho: cañón emisor en la punta
        R = P["RightArm"]
        R.append(box((1.15, 1.15, 0.6), (-1.5, 0, 2.45), armor, bevel=0.05))
        R.append(cyl(0.45, 0.2, (-1.5, 0, 2.0), dark, verts=16, bevel=0.02))
        R.append(L.torus(0.36, 0.06, Vector((-1.5, 0, 1.88)), glow, seg=16, minor=6))
        R.append(cyl(0.22, 0.05, (-1.5, 0, 1.88), glow, verts=16, bevel=0))
        for k in range(4):
            a = k / 4 * 2 * math.pi
            R.append(box((0.08, 0.08, 0.35), (-1.5 + math.cos(a) * 0.5, math.sin(a) * 0.5, 2.0), gold, bevel=0))
        R.append(cyl(0.28, 0.45, (-1.5, 0, 1.62), dark, verts=16, bevel=0.02))      # caño
        for z in (1.72, 1.52):
            R.append(L.torus(0.29, 0.035, Vector((-1.5, 0, z)), glow, seg=16, minor=4))
        R.append(cyl(0.2, 0.04, (-1.5, 0, 1.38), glow, verts=16, bevel=0))          # boca de energía
        for k in range(6):                                                          # aletas de enfriamiento
            a = k / 6 * 2 * math.pi
            R.append(box((0.22, 0.04, 0.35), (-1.5 + math.cos(a) * 0.38, math.sin(a) * 0.38, 1.66), armor, rot=(0, 0, a), bevel=0))
        # --- grebas de metal en las piernas (siguen descalzos)
        for nm, sx in (("RightLeg", -1), ("LeftLeg", 1)):
            x = sx * 0.5
            P[nm].append(box((1.08, 1.08, 0.75), (x, 0, 1.05), armor, bevel=0.04))
            P[nm].append(box((1.1, 1.1, 0.06), (x, 0, 1.42), gold, bevel=0))
            P[nm].append(box((0.55, 0.14, 0.45), (x, -0.58, 1.35), armor, bevel=0.04))
            hexplate(P[nm], Vector((x, -0.66, 1.35)), 0.12, (math.pi / 2, 0, 0), glow, 0.04)
            for k in range(3):                                                      # púas de la rodillera
                P[nm].append(cone(0.06, 0.22, Vector((x - 0.15 + k * 0.15, -0.72, 1.48)), steel, rot=Vector((0, -0.5, 1)).normalized(), verts=6))
            for dx in (-0.4, 0.4):                                                  # líneas de energía
                P[nm].append(box((0.04, 0.03, 0.55), (x + dx, -0.555, 1.0), glow, bevel=0))

    objs = _zb_body(K, random.Random(61), gear, chest=False)
    L.transform(objs, Matrix.Scale(s, 4), (0, 0, 0))
    return objs, s


def e_corredor():
    K = base_mats()
    skin = mat("Piel_Corredor", (0.45, 0.6, 0.3))
    P, piv = humanoid(skin, mat("Musculosa", (0.85, 0.85, 0.8)), mat("Short_Rojo", (0.7, 0.1, 0.1)),
                      mat("Ojo_Amarillo", (1, 0.9, 0.1), emission=(1, 0.85, 0.1), strength=4), K, s=1.05, w=0.75,
                      arms="forward", legs="run", hunch=0.35)
    hc = piv["Head"] + Vector((0, 0, 0.62 * 1.05))
    P["Head"].append(box((1.3, 1.25, 0.2), hc + Vector((0, 0, 0.3)), mat("Vincha", (0.8, 0.05, 0.05)), bevel=0.03))
    P["Head"].append(strut(hc + Vector((0, 0.6, 0.3)), hc + Vector((0.2, 1.3, 0.1)), 0.15, 0.08, mat("Vincha", (0.8, 0.05, 0.05)), bevel=0))
    return finish(P, piv), 1.05


def e_tanque():
    K = base_mats()
    s = 1.55
    skin = mat("Piel_Tanque", (0.3, 0.45, 0.25))
    shirt = mat("Remera_Negra", (0.12, 0.12, 0.14))
    P, piv = humanoid(skin, shirt, mat("Jean_Oscuro", (0.12, 0.15, 0.3)),
                      mat("Ojo_Rojo", (1, 0.1, 0.05), emission=(1, 0.1, 0.05), strength=4), K, s=s, w=1.35, arms="down")
    P["Torso"].append(sphere(1.0 * s, piv["Torso"] + Vector((0, -0.35 * s, -0.25 * s)), skin, subdiv=2, scale=(1.05, 0.7, 0.85)))  # panza
    for k in range(6):                                                          # cadena cruzada
        t = k / 5
        p = piv["Torso"] + Vector(((-0.9 + 1.8 * t) * s, -0.55 * s, (0.8 - 1.4 * t) * s))
        P["Torso"].append(torus(0.14 * s, 0.04 * s, p, K["METAL"], rot=(math.pi / 2, 0, 0.7 * (k % 2)), seg=8, minor=4))
    for side, nm in ((-1, "LeftArm"), (1, "RightArm")):
        P[nm].append(box((1.3 * s, 1.3 * s, 0.35 * s), piv[nm] + Vector((0.15 * side * s, 0, 0.1 * s)), K["DARKM"], bevel=0.08 * s))
    return finish(P, piv), s


def e_escudo():
    K = base_mats()
    P, piv = humanoid(mat("Piel_Zombi", (0.35, 0.55, 0.25)), mat("Uniforme_Policia", (0.1, 0.12, 0.25)),
                      mat("Pantalon_Policia", (0.08, 0.08, 0.12)), mat("Ojo_Rojo", (1, 0.1, 0.05), emission=(1, 0.1, 0.05), strength=4), K)
    hc = piv["Head"] + Vector((0, 0, 0.62))
    P["Head"].append(sphere(0.78, hc + Vector((0, 0.05, 0.2)), K["DARKM"], subdiv=2, scale=(1.05, 1.05, 0.8)))   # casco
    P["Head"].append(box((1.1, 0.08, 0.35), hc + Vector((0, -0.66, 0.15)), mat("Visera", (0.4, 0.6, 0.8), 0.2, 0.1), rot=(0.3, 0, 0), bevel=0))
    tip = piv["LeftArm"] + Vector((0.05, -1.9, -0.25))
    sc = tip + Vector((0.3, -0.45, -0.3))                                       # escudo antidisturbios
    P["LeftArm"].append(box((1.9, 0.15, 3.2), sc, K["METAL"], bevel=0.1))
    P["LeftArm"].append(box((1.95, 0.18, 0.15), sc + Vector((0, 0, 1.5)), K["DARKM"], bevel=0))
    P["LeftArm"].append(box((1.95, 0.18, 0.15), sc + Vector((0, 0, -1.5)), K["DARKM"], bevel=0))
    P["LeftArm"].append(box((1.2, 0.2, 0.35), sc + Vector((0, 0, 0.9)), mat("Visera", (0.4, 0.6, 0.8), 0.2, 0.1), bevel=0))
    P["LeftArm"].append(box((1.0, 0.2, 0.25), sc + Vector((0, 0, -0.2)), mat("Franja_Amarilla", (1, 0.8, 0.1)), bevel=0))
    for k in range(3):
        P["LeftArm"].append(box((0.3, 0.2, 0.08), sc + Vector((-0.6 + k * 0.6, -0.05, 0.3)), K["BLOOD"], rot=(0, 0.3 * k, 0), bevel=0))
    return finish(P, piv), 1.0


def e_radiactivo():
    K = base_mats()
    glow = mat("Radiacion", (0.5, 1.0, 0.1), emission=(0.4, 1.0, 0.05), strength=5)
    P, piv = humanoid(mat("Piel_Radiactiva", (0.55, 0.75, 0.2)), mat("Traje_Amarillo", (0.9, 0.75, 0.1)),
                      mat("Traje_Amarillo", (0.9, 0.75, 0.1)), glow, K)
    hc = piv["Head"] + Vector((0, 0, 0.62))
    P["Head"].append(box((0.7, 0.3, 0.55), hc + Vector((0, -0.7, -0.15)), K["DARKM"], bevel=0.08))           # máscara de gas
    for sx in (-1, 1):
        P["Head"].append(cyl(0.22, 0.3, hc + Vector((sx * 0.45, -0.75, -0.3)), K["DARKM"], rot=(math.pi / 2, 0, 0), verts=10))
        P["Head"].append(cyl(0.16, 0.05, hc + Vector((sx * 0.3, -0.64, 0.12)), glow, rot=(math.pi / 2, 0, 0), verts=10, bevel=0))
    bc = piv["Torso"] + Vector((0, 0.95, 0.1))                                  # barril en la espalda
    P["Torso"].append(cyl(0.6, 1.5, bc, mat("Barril_Toxico", (0.2, 0.35, 0.1), 0.4, 0.4), verts=12))
    P["Torso"].append(cyl(0.45, 0.05, bc + Vector((0, 0, 0.76)), glow, verts=12, bevel=0))
    for z in (-0.5, 0.5):
        P["Torso"].append(torus(0.61, 0.05, bc + Vector((0, 0, z)), K["DARKM"], seg=12, minor=4))
    P["Torso"].append(box((0.6, 0.05, 0.6), piv["Torso"] + Vector((0, -0.52, 0.3)), K["BLACK"], rot=(0, math.pi / 4, 0), bevel=0))
    P["Torso"].append(box((0.4, 0.06, 0.4), piv["Torso"] + Vector((0, -0.53, 0.3)), glow, rot=(0, math.pi / 4, 0), bevel=0))
    for k in range(4):                                                          # manchas brillantes
        P["Torso"].append(sphere(0.15, piv["Torso"] + Vector((-0.8 + k * 0.5, -0.5, -0.7 + (k % 2) * 0.4)), glow, subdiv=1))
    return finish(P, piv), 1.0


def e_astral():
    K = base_mats()
    rng = random.Random(6)
    skin = mat("Piel_Astral", (0.55, 0.35, 0.95), emission=(0.45, 0.2, 0.9), strength=0.8)
    star = mat("Estrella_Astral", (1, 0.9, 1), emission=(0.9, 0.7, 1.0), strength=6)
    P, piv = humanoid(skin, mat("Tunica_Astral", (0.2, 0.08, 0.4)), mat("Tunica_Astral", (0.2, 0.08, 0.4)), star, K, torn=False)
    hc = piv["Head"] + Vector((0, 0, 0.62))
    P["Head"].append(torus(0.7, 0.06, hc + Vector((0, 0.1, 0.95)), star, rot=(0.25, 0, 0), seg=20, minor=4))    # aureola
    for k in range(8):                                                          # estrellas orbitando
        a = k * math.pi / 4
        P["Torso"].append(sphere(0.12, piv["Torso"] + Vector((math.cos(a) * 1.8, math.sin(a) * 1.2, rng.uniform(-0.8, 1.2))), star, subdiv=1))
    for k in range(6):                                                          # grietas de luz
        P["Torso"].append(box((0.06, 0.05, rng.uniform(0.4, 0.8)), piv["Torso"] + Vector((rng.uniform(-0.8, 0.8), -0.52, rng.uniform(-0.6, 0.6))),
                              star, rot=(0, rng.uniform(-0.6, 0.6), 0), bevel=0))
    return finish(P, piv), 1.0


def e_cosmico():
    K = base_mats()
    rng = random.Random(8)
    skin = mat("Piel_Cosmica", (0.04, 0.05, 0.18))
    speck = mat("Polvo_Estelar", (0.8, 0.9, 1), emission=(0.7, 0.85, 1.0), strength=5)
    nebula = mat("Nebulosa", (0.9, 0.3, 0.8), emission=(0.8, 0.2, 0.9), strength=1.5)
    P, piv = humanoid(skin, mat("Armadura_Cosmica", (0.08, 0.05, 0.25), 0.6, 0.3), skin,
                      mat("Ojo_Cian", (0.2, 1, 1), emission=(0.1, 1, 1), strength=6), K, torn=False)
    for part in ("Torso", "LeftArm", "RightArm", "LeftLeg", "RightLeg", "Head"):
        c = piv[part] + (Vector((0, 0, 0.62)) if part == "Head" else Vector((0, 0, -0.9 if "Leg" in part else 0)))
        for k in range(5):
            P[part].append(sphere(0.05, c + Vector((rng.uniform(-0.5, 0.5), -0.55, rng.uniform(-0.6, 0.6))), speck, subdiv=1))
    cape_top = piv["Torso"] + Vector((0, 0.55, 0.9))                            # capa de nebulosa
    P["Torso"].append(strut(cape_top, cape_top + Vector((0, 0.9, -3.4)), 2.4, 0.08, nebula, bevel=0))
    ring_c = piv["Torso"] + Vector((0, 0, 0.3))
    P["Torso"].append(torus(1.9, 0.07, ring_c, speck, rot=(0.35, 0.2, 0), seg=28, minor=4))                  # anillo planetario
    P["Torso"].append(sphere(0.3, ring_c + Vector((1.9, 0.2, 0.6)), mat("Planeta", (0.9, 0.5, 0.2)), subdiv=2))
    return finish(P, piv), 1.0


def e_radiante():
    K = base_mats()
    gold_glow = mat("Luz_Radiante", (1.0, 0.85, 0.3), emission=(1.0, 0.8, 0.3), strength=4)
    P, piv = humanoid(mat("Piel_Radiante", (0.95, 0.8, 0.45), emission=(1.0, 0.75, 0.3), strength=0.6),
                      mat("Tunica_Blanca", (0.95, 0.93, 0.85)), mat("Tunica_Blanca", (0.95, 0.93, 0.85)),
                      mat("Ojo_Blanco", (1, 1, 1), emission=(1, 1, 0.9), strength=8), K, torn=False, arms="up")
    hc = piv["Head"] + Vector((0, 0, 0.62))
    for k in range(9):                                                          # corona de rayos
        a = math.pi * (0.1 + 0.8 * k / 8)
        d = Vector((math.cos(a), 0.15, math.sin(a)))
        P["Head"].append(cone(0.12, 0.8, hc + Vector((0, 0.3, 0.1)) + d * 1.05, K["GOLD"], rot=d, verts=4))
    P["Head"].append(torus(0.95, 0.05, hc + Vector((0, 0.3, 0.1)), gold_glow, rot=(math.pi / 2, 0, 0), seg=20, minor=4))
    P["Torso"].append(sphere(0.3, piv["Torso"] + Vector((0, -0.55, 0.2)), gold_glow, subdiv=2))              # núcleo de luz
    for side, nm in ((-1, "LeftArm"), (1, "RightArm")):
        tip = piv[nm] + Vector((0.4 * side, -0.3, 1.8))
        P[nm].append(sphere(0.35, tip + Vector((0, 0, 0.4)), gold_glow, subdiv=2))
    return finish(P, piv), 1.0


def e_invocador():
    K = base_mats()
    robe = mat("Tunica_Invocador", (0.15, 0.05, 0.1))
    rune = mat("Runa", (0.9, 0.2, 0.3), emission=(1.0, 0.1, 0.25), strength=5)
    P, piv = humanoid(mat("Piel_Palida", (0.55, 0.62, 0.5)), robe, robe, rune, K, torn=False, arms="down")
    P["LeftLeg"], P["RightLeg"] = [], []
    P["Torso"].append(cyl(1.25, 2.1, Vector((0, 0, 1.05)), robe, verts=8, bevel=0.05, r2=0.85))                # túnica larga
    P["Torso"].append(torus(1.05, 0.06, Vector((0, 0, 1.4)), K["GOLD"], seg=16, minor=4))
    hc = piv["Head"] + Vector((0, 0, 0.62))
    P["Head"].append(box((1.5, 1.45, 1.4), hc + Vector((0, 0.12, 0.15)), robe, bevel=0.3))                     # capucha
    P["Head"].append(cone(0.6, 0.8, hc + Vector((0, 0.35, 1.0)), robe, rot=(-0.4, 0, 0), verts=8))
    tip = piv["RightArm"] + Vector((0.15, 0, -1.9))                              # bastón
    P["RightArm"].append(rod(tip + Vector((0, -0.3, -1.6)), tip + Vector((0, -0.3, 2.4)), 0.09, K["WOOD"], verts=8))
    P["RightArm"].append(sphere(0.35, tip + Vector((0, -0.3, 2.75)), rune, subdiv=2))
    for k in range(3):
        a = k * 2.1
        P["RightArm"].append(cone(0.08, 0.5, tip + Vector((math.cos(a) * 0.3, -0.3 + math.sin(a) * 0.3, 2.55)), K["GOLD"],
                                  rot=Vector((math.cos(a), math.sin(a), 1.5)), verts=4))
    for k in range(6):                                                          # runas flotando
        a = k * math.pi / 3
        P["Torso"].append(box((0.35, 0.05, 0.35), Vector((math.cos(a) * 1.9, math.sin(a) * 1.9, 0.15)), rune,
                              rot=(0, 0, a), bevel=0))
    return finish(P, piv), 1.0


def e_espectral():
    K = base_mats()
    ghost = mat("Fantasma", (0.6, 0.85, 1.0), emission=(0.4, 0.75, 1.0), strength=1.2)
    P, piv = humanoid(ghost, ghost, ghost, mat("Ojo_Vacio", (0.02, 0.05, 0.1)), K, torn=False, no_legs=True)
    for k in range(4):                                                          # cola que se desvanece
        z = 1.8 - k * 0.45
        P["Torso"].append(cyl(0.95 - k * 0.2, 0.5, Vector((0, 0.1 * k, z)), ghost, verts=8, bevel=0.05, r2=0.85 - k * 0.2))
    P["Torso"].append(cone(0.2, 0.6, Vector((0, 0.5, 0.2)), ghost, rot=(math.pi, 0, 0), verts=6))
    for side, nm in ((-1, "LeftArm"), (1, "RightArm")):                          # cadenas
        tip = piv[nm] + Vector((0.05 * side, -1.9, -0.25))
        for k in range(4):
            P[nm].append(torus(0.12, 0.035, tip + Vector((0, 0.1 * k, -0.25 * k - 0.2)), K["DARKM"],
                               rot=(math.pi / 2 * (k % 2), 0, 0), seg=8, minor=4))
    # sube todo 1 unidad: flota
    return finish(P, piv), 1.0


def e_minijefe():
    K = base_mats()
    s = 2.0
    armor = mat("Armadura_Oxidada", (0.35, 0.22, 0.15), 0.7, 0.5)
    P, piv = humanoid(mat("Piel_Bruto", (0.3, 0.42, 0.22)), mat("Cuero", (0.3, 0.18, 0.1)), mat("Cuero", (0.3, 0.18, 0.1)),
                      mat("Ojo_Naranja", (1, 0.5, 0.05), emission=(1, 0.45, 0.05), strength=5), K, s=s, w=1.2, arms="down")
    hc = piv["Head"] + Vector((0, 0, 0.62 * s))
    P["Head"].append(box((1.4 * s, 1.35 * s, 0.6 * s), hc + Vector((0, 0, 0.4 * s)), armor, bevel=0.1 * s))   # casco
    for sx in (-1, 1):
        P["Head"].append(cone(0.2 * s, 0.9 * s, hc + Vector((sx * 0.75 * s, 0, 0.75 * s)), K["WHITE"],
                              rot=Vector((sx * 0.8, 0, 1)), verts=6))
    P["Torso"].append(box((2.2 * s, 1.15 * s, 1.1 * s), piv["Torso"] + Vector((0, 0, 0.45 * s)), armor, bevel=0.1 * s))  # peto
    for side, nm in ((-1, "LeftArm"), (1, "RightArm")):                          # hombreras con pinchos
        c = piv[nm] + Vector((0.15 * side * s, 0, 0.15 * s))
        P[nm].append(sphere(0.75 * s, c, armor, subdiv=1, scale=(1.1, 1, 0.7)))
        for k in range(3):
            P[nm].append(cone(0.12 * s, 0.6 * s, c + Vector(((-0.3 + k * 0.3) * s, 0, 0.5 * s)), K["METAL"], verts=5))
    tip = piv["RightArm"] + Vector((0.15 * s, 0, -1.9 * s))                     # garrote con clavos
    club = tip + Vector((0, -0.5 * s, 0.4 * s))
    P["RightArm"].append(strut(tip, club + Vector((0, -0.4 * s, 1.6 * s)), 0.35 * s, 0.35 * s, K["WOOD"], bevel=0.05))
    P["RightArm"].append(sphere(0.55 * s, club + Vector((0, -0.45 * s, 1.8 * s)), K["WOOD"], subdiv=1, scale=(1, 1, 1.3)))
    for k in range(6):
        a = k * math.pi / 3
        P["RightArm"].append(cone(0.08 * s, 0.4 * s, club + Vector((math.cos(a) * 0.55 * s, -0.45 * s + math.sin(a) * 0.55 * s, 1.8 * s)),
                                  K["METAL"], rot=Vector((math.cos(a), math.sin(a), 0)), verts=4))
    return finish(P, piv), s


def e_jefe():
    K = base_mats()
    s = 3.0
    royal = mat("Terciopelo_Rojo", (0.55, 0.03, 0.08))
    P, piv = humanoid(mat("Piel_Rey", (0.4, 0.5, 0.35)), mat("Armadura_Real", (0.2, 0.18, 0.25), 0.7, 0.35), royal,
                      mat("Ojo_Violeta", (0.8, 0.2, 1), emission=(0.8, 0.1, 1), strength=6), K, s=s, w=1.1, arms="down", torn=False)
    hc = piv["Head"] + Vector((0, 0, 0.62 * s))
    P["Head"].append(cyl(0.72 * s, 0.35 * s, hc + Vector((0, 0, 0.72 * s)), K["GOLD"], verts=10))            # corona
    for k in range(5):
        a = k * 2 * math.pi / 5
        p = hc + Vector((math.cos(a) * 0.62 * s, math.sin(a) * 0.62 * s, 1.05 * s))
        P["Head"].append(cone(0.14 * s, 0.5 * s, p, K["GOLD"], verts=4))
        P["Head"].append(sphere(0.07 * s, p + Vector((0, 0, -0.18 * s)), mat("Rubi", (0.9, 0.05, 0.1), 0.2, 0.1), subdiv=1))
    P["Head"].append(box((0.9 * s, 0.1 * s, 0.35 * s), hc + Vector((0, -0.6 * s, -0.55 * s)), mat("Barba", (0.8, 0.8, 0.75)), bevel=0.05))
    cape_top = piv["Torso"] + Vector((0, 0.55 * s, 0.9 * s))                    # capa real
    P["Torso"].append(strut(cape_top, cape_top + Vector((0, 0.8 * s, -3.6 * s)), 2.6 * s, 0.1 * s, royal, bevel=0))
    P["Torso"].append(box((2.7 * s, 0.4 * s, 0.4 * s), cape_top + Vector((0, 0, 0.1 * s)), mat("Piel_Armiño", (0.95, 0.95, 0.95)), bevel=0.1 * s))
    P["Torso"].append(box((0.6 * s, 0.06 * s, 0.6 * s), piv["Torso"] + Vector((0, -0.52 * s, 0.2 * s)), K["GOLD"],
                          rot=(0, math.pi / 4, 0), bevel=0.02))
    tip = piv["RightArm"] + Vector((0.15 * s, 0, -1.9 * s))                     # cetro
    P["RightArm"].append(rod(tip + Vector((0, -0.3 * s, -1.2 * s)), tip + Vector((0, -0.3 * s, 1.6 * s)), 0.1 * s, K["GOLD"], verts=8))
    P["RightArm"].append(sphere(0.35 * s, tip + Vector((0, -0.3 * s, 1.9 * s)), mat("Ojo_Violeta", (0.8, 0.2, 1)), subdiv=2))
    P["RightArm"].append(torus(0.4 * s, 0.05 * s, tip + Vector((0, -0.3 * s, 1.9 * s)), K["GOLD"], seg=16, minor=4))
    for side, nm in ((-1, "LeftArm"), (1, "RightArm")):
        P[nm].append(sphere(0.7 * s, piv[nm] + Vector((0.1 * side * s, 0, 0.1 * s)), K["GOLD"], subdiv=1, scale=(1.1, 1, 0.6)))
    return finish(P, piv), s


# ------------------------------------------------------------------ helpers de detalle
def chain(P, part, a, b, s, m, n=None):
    """Cadena de eslabones de a hasta b."""
    a, b = Vector(a), Vector(b)
    n = n or max(3, int((b - a).length / (0.28 * s)))
    d = (b - a).normalized()
    for k in range(n):
        p = a.lerp(b, (k + 0.5) / n)
        P[part].append(torus(0.13 * s, 0.045 * s, p, m, rot=d.to_track_quat("X", "Z").to_euler() if k % 2 else
                             (d.to_track_quat("X", "Z") @ Matrix.Rotation(math.pi / 2, 3, "X").to_quaternion()).to_euler(),
                             seg=8, minor=4))


def binary(P, part, c, s, m, rng, n=6, spread=0.5, face_y=-0.52):
    """Código binario brillando (unos y ceros) sobre una superficie."""
    for k in range(n):
        p = c + Vector((rng.uniform(-spread, spread) * s, face_y * s, rng.uniform(-spread, spread) * s))
        if rng.random() < 0.5:
            P[part].append(box((0.05 * s, 0.04 * s, 0.2 * s), p, m, bevel=0))
        else:
            P[part].append(torus(0.07 * s, 0.025 * s, p, m, rot=(math.pi / 2, 0, 0), seg=8, minor=4))


def robot_arm(P, name, piv, s, K, glow):
    """Reemplaza el brazo por uno robótico (segmentos, articulaciones, pinza)."""
    sp, tip = piv[name], piv[name + "_tip"]
    P[name] = []
    mid = sp.lerp(tip, 0.5)
    d = (tip - sp).normalized()
    P[name] += [sphere(0.45 * s, sp, K["DARKM"], subdiv=2),
                strut(sp, mid, 0.55 * s, 0.55 * s, K["METAL"], bevel=0.05 * s),
                sphere(0.32 * s, mid, K["DARKM"], subdiv=2),
                torus(0.3 * s, 0.05 * s, mid, glow, rot=d, seg=12, minor=4),
                rod(mid, tip, 0.2 * s, K["METAL"], verts=10),
                rod(sp.lerp(mid, 0.2) + Vector((0, 0, -0.25 * s)), mid.lerp(tip, 0.6) + Vector((0, 0, -0.2 * s)), 0.06 * s, K["DARKM"], verts=6)]
    base = tip
    P[name].append(box((0.55 * s, 0.55 * s, 0.35 * s), base, K["DARKM"], rot=d.to_track_quat("Z", "Y").to_euler(), bevel=0.05 * s))
    for sd in (-1, 1):                                                          # pinza
        side = Vector((0.2 * sd * s, 0, 0))
        P[name].append(strut(base + side, base + side + d * 0.55 * s + Vector((0, 0, 0.1 * sd * s)), 0.12 * s, 0.25 * s, K["METAL"], bevel=0))


def robot_leg(P, name, piv, s, K, glow):
    hp, foot = piv[name], piv[name + "_foot"]
    P[name] = []
    knee = hp.lerp(foot, 0.5) + Vector((0, -0.25 * s, 0))
    P[name] += [sphere(0.42 * s, hp, K["DARKM"], subdiv=2),
                strut(hp, knee, 0.5 * s, 0.5 * s, K["METAL"], bevel=0.05 * s),
                sphere(0.3 * s, knee, glow, subdiv=2),
                rod(knee, foot + Vector((0, 0, 0.25 * s)), 0.18 * s, K["METAL"], verts=10),
                rod(hp + Vector((0, 0.3 * s, -0.2 * s)), foot + Vector((0, 0.3 * s, 0.5 * s)), 0.07 * s, K["DARKM"], verts=6),
                box((1.0 * s, 1.35 * s, 0.3 * s), foot + Vector((0, -0.15 * s, 0.05 * s)), K["DARKM"], bevel=0.05 * s)]


# ------------------------------------------------------------------ enemigos nuevos
def e_cyborg():
    K = base_mats()
    glow = mat("Luz_Cyborg", (1, 0.15, 0.1), emission=(1, 0.1, 0.05), strength=6)
    P, piv = humanoid(mat("Piel_Zombi", (0.35, 0.55, 0.25)), mat("Remera_Gris", (0.35, 0.35, 0.38)),
                      mat("Pantalon_Marron", (0.3, 0.2, 0.12)), mat("Ojo_Rojo", (1, 0.1, 0.05), emission=(1, 0.1, 0.05), strength=4), K,
                      hair=mat("Pelo_Oscuro", (0.12, 0.08, 0.05)))
    robot_arm(P, "LeftArm", piv, 1.0, K, glow)
    robot_leg(P, "RightLeg", piv, 1.0, K, glow)
    hc = piv["Head"] + Vector((0, 0, 0.62))
    P["Head"] += [box((0.66, 1.25, 1.25), hc + Vector((-0.33, 0, 0.02)), K["METAL"], bevel=0.1),            # media cara de metal
                  cyl(0.18, 0.12, hc + Vector((-0.3, -0.64, 0.12)), glow, rot=(math.pi / 2, 0, 0), verts=12, bevel=0),
                  torus(0.2, 0.04, hc + Vector((-0.3, -0.66, 0.12)), K["DARKM"], rot=(math.pi / 2, 0, 0), seg=12, minor=4),
                  rod(hc + Vector((-0.45, 0.2, 0.6)), hc + Vector((-0.6, 0.3, 1.3)), 0.03, K["DARKM"], verts=6),
                  sphere(0.07, hc + Vector((-0.6, 0.3, 1.33)), glow, subdiv=1)]
    tc = piv["Torso"]
    P["Torso"] += [box((0.9, 0.08, 0.9), tc + Vector((-0.4, -0.52, 0.25)), K["METAL"], bevel=0.05),         # placa del pecho
                   cyl(0.22, 0.1, tc + Vector((-0.4, -0.58, 0.25)), glow, rot=(math.pi / 2, 0, 0), verts=12, bevel=0)]
    for k in range(3):                                                          # cables sueltos
        P["Torso"].append(rod(tc + Vector((-0.8, -0.4, 0.6 - k * 0.2)), tc + Vector((-1.3, -0.5, 0.3 - k * 0.3)), 0.03,
                              [K["BLACK"], glow, mat("Cable_Azul", (0.1, 0.3, 0.9))][k], verts=5))
    return finish(P, piv), 1.0


def e_mecanico():
    K = base_mats()
    glow = mat("Luz_Mecanica", (0.2, 0.9, 1), emission=(0.1, 0.8, 1), strength=6)
    P, piv = humanoid(mat("Piel_Mecanico", (0.4, 0.5, 0.3)), mat("Mono_Naranja", (0.85, 0.4, 0.1)),
                      mat("Mono_Naranja", (0.85, 0.4, 0.1)), glow, K, legs="stand", arms="forward")
    robot_leg(P, "LeftLeg", piv, 1.0, K, glow)
    robot_leg(P, "RightLeg", piv, 1.0, K, glow)
    tip = piv["RightArm_tip"]                                                   # taladro en la mano
    d = (tip - piv["RightArm"]).normalized()
    P["RightArm"] = [x for x in P["RightArm"]]
    P["RightArm"] += [cyl(0.4, 0.4, tip + d * 0.3, K["DARKM"], rot=d, verts=12),
                      cone(0.35, 1.2, tip + d * 1.1, K["METAL"], rot=d, verts=8)]
    for k in range(3):
        P["RightArm"].append(torus(0.28 - k * 0.07, 0.04, tip + d * (0.75 + k * 0.3), K["GOLD"], rot=d, seg=10, minor=4))
    hc = piv["Head"] + Vector((0, 0, 0.62))
    P["Head"] += [box((1.35, 1.3, 0.55), hc + Vector((0, 0, 0.45)), K["METAL"], bevel=0.1),                # tapa de cráneo robótica
                  box((1.37, 0.1, 0.12), hc + Vector((0, -0.65, 0.3)), glow, bevel=0)]
    for sx in (-1, 1):
        P["Head"].append(box((0.15, 0.4, 0.4), hc + Vector((sx * 0.7, 0, 0.1)), K["DARKM"], bevel=0.03))
    return finish(P, piv), 1.0


def e_boxeador():
    K = base_mats()
    green = mat("Piel_Verde_Oscura", (0.15, 0.5, 0.2))
    black = mat("Ropa_Negra", (0.05, 0.05, 0.06))
    P, piv = humanoid(green, black, black, mat("Ojo_Blanco_Zombi", (0.95, 0.95, 0.8), emission=(1, 1, 0.8), strength=2), K,
                      arms="down", torn=False, hand=green, hand_size=1.35)
    for nm in ("LeftArm", "RightArm"):                                          # brazaletes con placas y cadenas
        m, t = piv[nm + "_mid"], piv[nm + "_tip"]
        P[nm].append(strut(m.lerp(t, 0.1), t, 1.08, 1.08, black, bevel=0.06))
        for k in range(3):
            P[nm].append(box((1.1, 1.1, 0.08), m.lerp(t, 0.25 + k * 0.3), K["DARKM"], bevel=0))
        chain(P, nm, t + Vector((0, -0.56, 0.3)), t + Vector((0, -0.56, -0.4)), 1.0, K["METAL"])
    return finish(P, piv), 1.0


def e_blindado():
    K = base_mats()
    rng = random.Random(4)
    tan = mat("Piel_Arena", (0.78, 0.7, 0.5))
    olive = mat("Torso_Oliva", (0.35, 0.33, 0.15))
    plate = mat("Chapa_Diamante", (0.62, 0.62, 0.65), 0.9, 0.3)
    redb = mat("Banda_Roja", (0.8, 0.1, 0.08))
    P, piv = humanoid(tan, olive, olive, mat("Ojo_Rojo", (1, 0.1, 0.05), emission=(1, 0.1, 0.05), strength=4), K,
                      arms="forward", torn=False, hand=tan)
    tc = piv["Torso"]
    for k in range(3):                                                          # zarpazos rojos
        P["Torso"].append(box((0.08, 0.05, 1.2), tc + Vector((0.1 + k * 0.22, -0.52, 0.1)), redb, rot=(0, 0.6, 0), bevel=0))
    for nm in ("LeftArm", "RightArm", "LeftLeg", "RightLeg"):                    # bandas de chapa antideslizante
        a = piv[nm + "_mid"]
        b = piv.get(nm + "_tip") or piv.get(nm + "_foot")
        for t, m in ((0.15, plate), (0.45, redb), (0.7, plate)):
            P[nm].append(strut(a.lerp(b, t), a.lerp(b, t + 0.14), 1.05, 1.05, m, bevel=0.03))
        for k in range(6):
            p = a.lerp(b, 0.22) + Vector((rng.uniform(-0.35, 0.35), -0.53, rng.uniform(-0.1, 0.1)))
            P[nm].append(box((0.12, 0.03, 0.05), p, K["DARKM"], rot=(0, rng.choice([0.8, -0.8]), 0), bevel=0))
    return finish(P, piv), 1.0


def e_sigiloso():
    K = base_mats()
    cloak = mat("Capa_Sigilo", (0.08, 0.1, 0.12))
    P, piv = humanoid(mat("Piel_Gris", (0.35, 0.4, 0.35)), cloak, mat("Ropa_Negra", (0.05, 0.05, 0.06)),
                      mat("Ojo_Verde", (0.3, 1, 0.3), emission=(0.2, 1, 0.3), strength=6), K, torn=False, hunch=0.3)
    hc = piv["Head"] + Vector((0, 0, 0.62))
    P["Head"] += [box((1.5, 1.45, 1.4), hc + Vector((0, 0.12, 0.1)), cloak, bevel=0.3),                     # capucha
                  box((1.2, 0.1, 0.55), hc + Vector((0, -0.64, -0.25)), K["BLACK"], bevel=0.03)]            # máscara
    P["Torso"].append(strut(piv["Torso"] + Vector((0, 0.55, 0.9)), Vector((0, 1.3, 0.3)), 2.3, 0.08, cloak, bevel=0))
    for sx in (-1, 1):                                                          # dagas
        P["Torso"].append(box((0.12, 0.08, 0.7), piv["Torso"] + Vector((sx * 0.7, 0.55, -0.6)), K["METAL"], rot=(0, sx * 0.5, 0), bevel=0))
    return finish(P, piv), 1.0


def e_alado():
    K = base_mats()
    wing = mat("Ala_Murcielago", (0.18, 0.08, 0.1))
    P, piv = humanoid(mat("Piel_Alado", (0.45, 0.4, 0.5)), mat("Chaleco_Rasgado", (0.25, 0.1, 0.12)),
                      mat("Pantalon_Oscuro", (0.15, 0.12, 0.12)), mat("Ojo_Amarillo", (1, 0.9, 0.1), emission=(1, 0.85, 0.1), strength=5), K,
                      arms="up", legs="stand")
    base = piv["Torso"] + Vector((0, 0.55, 0.6))
    for sx in (-1, 1):                                                          # alas de murciélago
        tip = base + Vector((sx * 3.2, 0.8, 1.2))
        P["Torso"].append(strut(base, tip, 0.12, 0.12, K["BLACK"], bevel=0))
        for k in range(4):
            f = base + Vector((sx * (1.0 + k * 0.7), 0.6, 1.0 - k * 0.3))
            end = f + Vector((sx * 0.3, 0.1, -1.8 + k * 0.2))
            P["Torso"].append(strut(tip.lerp(base, k / 4), end, 0.06, 0.06, K["BLACK"], bevel=0))
            P["Torso"].append(strut(base.lerp(tip, 0.25 + k * 0.2) + Vector((0, 0.05, -0.4)), end + Vector((0, 0, 0.4)),
                                    0.05, 0.9, wing, bevel=0))
    return finish(P, piv), 1.0


def e_lich():
    K = base_mats()
    s = 1.35
    robe = mat("Tunica_Lich", (0.16, 0.16, 0.18))
    bone = mat("Calavera", (0.88, 0.86, 0.8))
    socket = mat("Cuenca", (0.02, 0.02, 0.03))
    P, piv = humanoid(mat("Piel_Lich", (0.55, 0.6, 0.55)), robe, robe, socket, K, s=s, torn=False, arms="down", hunch=0.45,
                      hand=mat("Piel_Lich", (0.55, 0.6, 0.55)))
    hc = piv["Head"] + Vector((0, 0, 0.62 * s))
    P["Head"] = [box((1.2 * s, 1.15 * s, 1.1 * s), hc + Vector((0, 0, 0.1 * s)), bone, bevel=0.2 * s),     # calavera
                 box((0.9 * s, 0.9 * s, 0.45 * s), hc + Vector((0, -0.1 * s, -0.5 * s)), bone, bevel=0.1 * s)]
    for sx in (-1, 1):
        P["Head"].append(box((0.34 * s, 0.1 * s, 0.34 * s), hc + Vector((sx * 0.28 * s, -0.56 * s, 0.1 * s)), socket, bevel=0.05 * s))
        P["Head"].append(sphere(0.07 * s, hc + Vector((sx * 0.28 * s, -0.6 * s, 0.1 * s)),
                                mat("Brillo_Lich", (0.3, 1, 0.8), emission=(0.2, 1, 0.8), strength=6), subdiv=1))
        P["Head"].append(cone(0.14 * s, 0.6 * s, hc + Vector((sx * 0.5 * s, 0.1 * s, 0.75 * s)), bone, rot=Vector((sx * 0.5, 0.2, 1)), verts=6))
    P["Head"].append(box((0.14 * s, 0.1 * s, 0.2 * s), hc + Vector((0, -0.56 * s, -0.15 * s)), socket, bevel=0))
    for k in range(5):
        P["Head"].append(box((0.1 * s, 0.1 * s, 0.14 * s), hc + Vector(((-0.3 + k * 0.15) * s, -0.56 * s, -0.5 * s)), K["TEETH"], bevel=0))
    tc = piv["Torso"]
    P["Torso"].append(cyl(1.3 * s, 2.2 * s, Vector((0, 0.1 * s, 1.1 * s)), robe, verts=9, bevel=0.05, r2=1.0 * s))   # túnica
    for k in range(9):                                                          # borde deshilachado
        a = k * 2 * math.pi / 9
        P["Torso"].append(cone(0.25 * s, 0.4 * s, Vector((math.cos(a) * 1.2 * s, math.sin(a) * 1.2 * s + 0.1 * s, 0.1 * s)), robe,
                               rot=(math.pi, 0, 0), verts=3))
    P["Torso"].append(strut(tc + Vector((-1.0 * s, -0.55 * s, 0.9 * s)), tc + Vector((1.0 * s, -0.55 * s, -0.7 * s)), 0.25 * s, 0.08 * s,
                            mat("Correa", (0.12, 0.08, 0.05)), bevel=0))
    hand = piv["RightArm_hand"]                                                 # bastón con cráneo
    P["RightArm"] += [rod(hand + Vector((0, -0.2 * s, -1.8 * s)), hand + Vector((0, -0.2 * s, 2.6 * s)), 0.08 * s, K["BLACK"], verts=8),
                      box((0.55 * s, 0.5 * s, 0.5 * s), hand + Vector((0, -0.2 * s, 2.95 * s)), bone, bevel=0.1 * s)]
    for sx in (-1, 1):
        P["RightArm"].append(cone(0.08 * s, 0.4 * s, hand + Vector((sx * 0.25 * s, -0.2 * s, 3.3 * s)), K["BLACK"], rot=Vector((sx, 0, 1)), verts=5))
        P["RightArm"].append(box((0.12 * s, 0.06 * s, 0.12 * s), hand + Vector((sx * 0.12 * s, -0.46 * s, 3.0 * s)), socket, bevel=0))
    return finish(P, piv), s


def e_1x1x1x1():
    K = base_mats()
    s = 3.0
    rng = random.Random(11)
    glowg = mat("Verde_1x1", (0.15, 0.95, 0.35), emission=(0.1, 0.9, 0.3), strength=1.8)
    darkg = mat("Verde_Oscuro_1x1", (0.05, 0.35, 0.12))
    fire = mat("Fuego_Verde", (0.2, 1.0, 0.3), emission=(0.1, 1.0, 0.25), strength=6)
    red = mat("Ojo_Rojo_1x1", (1, 0.05, 0.05), emission=(1, 0.05, 0.05), strength=8)
    cape = mat("Capa_Roja", (0.7, 0.03, 0.05))
    P, piv = humanoid(glowg, glowg, darkg, K["BLACK"], K, s=s, torn=False, arms="down")
    hc = piv["Head"] + Vector((0, 0, 0.62 * s))
    P["Head"].append(box((0.3 * s, 0.08 * s, 0.26 * s), hc + Vector((0.3 * s, -0.62 * s, 0.12 * s)), red, bevel=0))      # ojo rojo
    P["Head"].append(cyl(0.72 * s, 0.4 * s, hc + Vector((0, 0, 0.78 * s)), darkg, verts=4, bevel=0.05 * s))           # corona de dominó
    for k in range(4):
        a = k * math.pi / 2 + math.pi / 4
        P["Head"].append(cone(0.18 * s, 0.45 * s, hc + Vector((math.cos(a) * 0.5 * s, math.sin(a) * 0.5 * s, 1.18 * s)), glowg, verts=4))
    for rz in (0.7, -0.7):                                                      # X en el frente
        P["Head"].append(box((0.08 * s, 0.05 * s, 0.35 * s), hc + Vector((0, -0.52 * s, 0.8 * s)), fire, rot=(0, rz, 0), bevel=0))
    tc = piv["Torso"]
    for k in range(4):                                                          # costillas negras
        P["Torso"].append(box((1.3 * s, 0.05 * s, 0.1 * s), tc + Vector((0, -0.52 * s, (0.5 - k * 0.3) * s)), K["BLACK"], bevel=0))
    P["Torso"].append(box((0.14 * s, 0.05 * s, 1.3 * s), tc + Vector((0, -0.53 * s, 0.05 * s)), K["BLACK"], bevel=0))
    for k in range(6):                                                          # marca de corona en el cuello
        a = k * math.pi / 3
        P["Torso"].append(cone(0.08 * s, 0.3 * s, tc + Vector((math.cos(a) * 0.45 * s, math.sin(a) * 0.35 * s, 1.1 * s)), fire, verts=4))
    cape_top = tc + Vector((0, 0.55 * s, 0.9 * s))
    P["Torso"].append(strut(cape_top, cape_top + Vector((0, 1.1 * s, -3.7 * s)), 3.0 * s, 0.1 * s, cape, bevel=0))
    sp = piv["LeftArm"] + Vector((-0.2 * s, 0, 0.3 * s))                       # hombrera dominó
    P["LeftArm"].append(box((1.2 * s, 1.1 * s, 0.4 * s), sp, K["BLACK"], rot=(0, -0.3, 0), bevel=0.05 * s))
    for dx, dy in ((-0.3, -0.25), (0, 0), (0.3, 0.25), (-0.3, 0.25), (0.3, -0.25)):
        P["LeftArm"].append(sphere(0.07 * s, sp + Vector((dx * s, dy * s, 0.22 * s)), K["WHITE"], subdiv=1))
    for nm in ("LeftArm", "RightArm"):                                           # muñequeras de cadena + espadas de fuego
        chain(P, nm, piv[nm + "_tip"] + Vector((-0.55 * s, -0.55 * s, 0.2 * s)), piv[nm + "_tip"] + Vector((0.55 * s, -0.55 * s, 0.2 * s)), s, glowg, n=5)
        h = piv[nm + "_hand"]
        P[nm] += [box((0.2 * s, 0.2 * s, 0.6 * s), h, K["BLACK"], bevel=0.02 * s),
                  box((0.7 * s, 0.25 * s, 0.12 * s), h + Vector((0, -0.2 * s, 0.1 * s)), darkg, bevel=0),
                  box((0.25 * s, 0.1 * s, 3.2 * s), h + Vector((0, -0.6 * s, 1.1 * s)), fire, rot=(-1.2, 0, 0), bevel=0.02 * s)]
        for k in range(4):
            P[nm].append(cone(0.2 * s, 0.6 * s, h + Vector((rng.uniform(-0.15, 0.15) * s, (-1.0 - k * 0.55) * s, (0.5 + k * 0.2) * s)),
                              fire, rot=(-0.3, 0, 0), verts=5))
    for k in range(8):                                                          # llamas oscuras en los pies
        a = k * math.pi / 4
        P["Torso"].append(cone(0.25 * s, rng.uniform(0.5, 1.0) * s, Vector((math.cos(a) * 1.1 * s, math.sin(a) * 0.7 * s, 0.3 * s)), darkg, verts=5))
    return finish(P, piv), s


def e_john_doe():
    K = base_mats()
    s = 3.0
    rng = random.Random(21)
    pale = mat("Piel_Palida_JD", (0.95, 0.85, 0.75))
    yellow = mat("Torso_Amarillo", (0.98, 0.8, 0.1))
    blue = mat("Pantalon_Celeste", (0.35, 0.6, 0.9))
    corrupt = mat("Corrupcion", (0.02, 0.02, 0.03), 0.3, 0.3)
    code = mat("Codigo_Rojo", (1, 0.05, 0.05), emission=(1, 0.05, 0.05), strength=7)
    P, piv = humanoid(pale, yellow, blue, K["BLACK"], K, s=s, torn=False, arms="down")
    hc = piv["Head"] + Vector((0, 0, 0.62 * s))
    P["Head"].append(box((0.18 * s, 0.08 * s, 0.16 * s), hc + Vector((0.3 * s, -0.63 * s, 0.12 * s)), code, bevel=0))       # ojo derecho rojo
    P["Head"].append(box((0.55 * s, 0.07 * s, 0.6 * s), hc + Vector((0.35 * s, -0.61 * s, 0.1 * s)), corrupt, bevel=0))
    tc = piv["Torso"]
    R = tc + Vector((-0.55 * s, -0.53 * s, 0.45 * s))                           # la "R"
    P["Torso"] += [box((0.08 * s, 0.05 * s, 0.6 * s), R, K["BLACK"], bevel=0),
                   box((0.28 * s, 0.05 * s, 0.07 * s), R + Vector((0.14 * s, 0, 0.27 * s)), K["BLACK"], bevel=0),
                   box((0.28 * s, 0.05 * s, 0.07 * s), R + Vector((0.14 * s, 0, 0.02 * s)), K["BLACK"], bevel=0),
                   box((0.07 * s, 0.05 * s, 0.25 * s), R + Vector((0.28 * s, 0, 0.15 * s)), K["BLACK"], bevel=0),
                   box((0.07 * s, 0.05 * s, 0.33 * s), R + Vector((0.2 * s, 0, -0.14 * s)), K["BLACK"], rot=(0, 0.6, 0), bevel=0)]
    binary(P, "Torso", tc + Vector((0.4 * s, 0, -0.2 * s)), s, code, rng, n=8, spread=0.45)
    # brazo derecho: todo corrupción con forma de púa enorme
    sp = piv["RightArm"]
    P["RightArm"] = [sphere(0.6 * s, sp, corrupt, subdiv=1),
                     cone(0.65 * s, 4.2 * s, sp + Vector((0.2 * s, -0.4 * s, -1.9 * s)), corrupt, rot=Vector((0.1, -0.2, -1)), verts=6)]
    for k in range(5):
        P["RightArm"].append(cone(0.2 * s, 1.0 * s, sp + Vector((rng.uniform(0, 0.5) * s, -0.4 * s, -k * 0.7 * s)), corrupt,
                                  rot=Vector((1, -0.3, 0.2)), verts=5))
    binary(P, "RightArm", sp + Vector((0.1 * s, 0, -1.2 * s)), s, code, rng, n=8, spread=0.4, face_y=-0.75)
    # punta del brazo izquierdo corrupta (sin uñas ni garras)
    h = piv["LeftArm_hand"]
    P["LeftArm"].append(box((0.95 * s, 0.95 * s, 0.9 * s), h, corrupt, bevel=0.05 * s))
    binary(P, "LeftArm", h, s, code, rng, n=4, spread=0.3, face_y=-0.5)
    for nm in ("LeftLeg", "RightLeg"):                                           # pies negros
        P[nm].append(box((1.1 * s, 1.35 * s, 0.7 * s), piv[nm + "_foot"] + Vector((0, -0.1 * s, 0.25 * s)), corrupt, bevel=0.08 * s))
        binary(P, nm, piv[nm + "_foot"] + Vector((0, 0, 0.3 * s)), s, code, rng, n=3, spread=0.3, face_y=-0.8)
    return finish(P, piv), s


def e_brute():
    K = base_mats()
    s = 2.4
    rng = random.Random(31)
    green = mat("Piel_Brute", (0.2, 0.55, 0.2))
    vest = mat("Chaleco_Negro", (0.04, 0.04, 0.05))
    pants = mat("Pantalon_Violeta", (0.1, 0.08, 0.28))
    red = mat("Ojo_Rojo_Brute", (1, 0.05, 0.05), emission=(1, 0.05, 0.05), strength=8)
    steel = mat("Acero_Cadena", (0.7, 0.72, 0.75), 0.9, 0.3)
    P, piv = humanoid(green, green, pants, red, K, s=s, w=1.9, arms="down", arm_len=1.25, torn=False, hand=green, hand_size=1.05)
    hc = piv["Head"] + Vector((0, 0, 0.62 * s))
    for rz in (0.7, -0.7):                                                      # cicatriz en X roja
        P["Head"].append(box((0.07 * s, 0.07 * s, 0.5 * s), hc + Vector((-0.3 * s, -0.62 * s, 0.25 * s)), red, rot=(0, rz, 0), bevel=0))
    P["Head"].append(box((1.28 * s, 0.1 * s, 0.1 * s), hc + Vector((0, -0.6 * s, 0.28 * s)), mat("Ceja", (0.05, 0.2, 0.05)),
                         rot=(0, 0.12, 0), bevel=0))
    tc = piv["Torso"]
    P["Torso"].append(box((2.1 * s, 1.1 * s, 1.9 * s), tc, vest, bevel=0.08 * s))                               # chaleco
    P["Torso"].append(box((0.7 * s, 0.05 * s, 1.3 * s), tc + Vector((0, -0.56 * s, 0.1 * s)), green, bevel=0))  # pecho a la vista
    for k in range(9):                                                          # cuello de pelo roto
        a = k * math.pi / 8
        P["Torso"].append(cone(0.15 * s, 0.5 * s, tc + Vector((math.cos(a) * 1.0 * s, -0.2 * s + math.sin(a) * 0.1, 1.0 * s)), vest,
                               rot=Vector((math.cos(a) * 0.4, 0, 1)), verts=3))
    for k in range(6):                                                          # borde desgarrado
        P["Torso"].append(cone(0.2 * s, 0.4 * s, tc + Vector(((-0.85 + k * 0.34) * s, -0.3 * s, -1.0 * s)), vest, rot=(math.pi, 0, 0), verts=3))
    chain(P, "Torso", tc + Vector((-1.0 * s, -0.6 * s, 0.9 * s)), tc + Vector((0.9 * s, -0.6 * s, -0.8 * s)), s, steel)
    chain(P, "Torso", tc + Vector((1.0 * s, -0.6 * s, 0.9 * s)), tc + Vector((-0.9 * s, -0.6 * s, -0.8 * s)), s, steel)
    lock = tc + Vector((0, -0.72 * s, -0.25 * s))                               # candado
    P["Torso"] += [box((0.65 * s, 0.25 * s, 0.55 * s), lock, steel, bevel=0.05 * s),
                   torus(0.2 * s, 0.06 * s, lock + Vector((0, 0, 0.35 * s)), steel, rot=(math.pi / 2, 0, 0), seg=10, minor=4),
                   box((0.1 * s, 0.05 * s, 0.22 * s), lock + Vector((0, -0.13 * s, -0.05 * s)), K["BLACK"], bevel=0)]
    for nm in ("LeftArm", "RightArm"):                                           # esposas con pinchos
        t = piv[nm + "_tip"]
        P[nm].append(box((2.05 * s, 2.05 * s, 0.45 * s), t + Vector((0, 0, 0.2 * s)), vest, bevel=0.05 * s))
        for k in range(8):
            a = k * math.pi / 4
            P[nm].append(cone(0.12 * s, 0.4 * s, t + Vector((math.cos(a) * 1.05 * s, math.sin(a) * 1.05 * s, 0.2 * s)), steel,
                              rot=Vector((math.cos(a), math.sin(a), 0)), verts=4))
        for k in range(4):                                                      # grietas en la piel
            P[nm].append(box((0.05 * s, 0.03 * s, 0.4 * s), piv[nm].lerp(t, 0.3 + k * 0.12) + Vector((rng.uniform(-0.5, 0.5) * s, -0.96 * s, 0)),
                             mat("Grieta", (0.08, 0.3, 0.08)), rot=(0, rng.uniform(-0.8, 0.8), 0), bevel=0))
    for nm in ("LeftLeg", "RightLeg"):                                           # grilletes en los tobillos
        f = piv[nm + "_foot"]
        P[nm].append(box((1.05 * s, 1.05 * s, 0.3 * s), f + Vector((0, 0, 0.5 * s)), vest, bevel=0.03 * s))
    chain(P, "LeftLeg", piv["LeftLeg_foot"] + Vector((0, -0.55 * s, 0.5 * s)), piv["RightLeg_foot"] + Vector((0, -0.55 * s, 0.5 * s)), s, steel, n=5)
    return finish(P, piv), s


def e_esqueleto():
    K = base_mats()
    bone = mat("Hueso_Esqueleto", (0.9, 0.88, 0.8))
    dark = mat("Hueco", (0.05, 0.05, 0.06))
    P, piv = humanoid(bone, bone, bone, mat("Ojo_Azul", (0.3, 0.6, 1), emission=(0.2, 0.5, 1), strength=6), K, torn=False, w=0.55)
    tc = piv["Torso"]
    P["Torso"] = [box((0.3, 0.3, 2.0), tc, bone, bevel=0.05)]                   # columna
    for k in range(4):                                                          # costillas
        P["Torso"].append(box((1.7 - k * 0.15, 0.7, 0.14), tc + Vector((0, -0.1, 0.7 - k * 0.35)), bone, bevel=0.05))
    P["Torso"].append(box((1.6, 0.8, 0.35), tc + Vector((0, 0, -0.9)), bone, bevel=0.08))                      # pelvis
    return finish(P, piv), 1.0


def e_golem_lava():
    K = base_mats()
    s = 1.8
    rng = random.Random(41)
    rock = mat("Roca_Golem", (0.15, 0.12, 0.11))
    lava = mat("Lava_Golem", (1, 0.4, 0.05), emission=(1, 0.35, 0.02), strength=6)
    P, piv = humanoid(rock, rock, rock, lava, K, s=s, w=1.4, arms="down", torn=False)
    for part in ("Torso", "LeftArm", "RightArm", "LeftLeg", "RightLeg", "Head"):   # grietas de lava
        c = piv[part] + (Vector((0, 0, 0.62 * s)) if part == "Head" else Vector((0, 0, -0.8 * s if part != "Torso" else 0)))
        for k in range(4):
            P[part].append(box((0.08 * s, 0.05 * s, rng.uniform(0.3, 0.7) * s), c + Vector((rng.uniform(-0.4, 0.4) * s, -0.62 * s, rng.uniform(-0.5, 0.5) * s)),
                               lava, rot=(0, rng.uniform(-0.9, 0.9), 0), bevel=0))
    for k in range(5):                                                          # rocas en los hombros
        P["Torso"].append(sphere(rng.uniform(0.3, 0.5) * s, piv["Torso"] + Vector((rng.uniform(-1, 1) * s, 0.2 * s, 1.0 * s)), rock, subdiv=1))
    return finish(P, piv), s


def e_abominacion():
    K = base_mats()
    s = 1.7
    flesh = mat("Carne_Cosida", (0.55, 0.45, 0.4))
    P, piv = humanoid(flesh, mat("Delantal", (0.4, 0.38, 0.3)), mat("Pantalon_Marron", (0.3, 0.2, 0.12)),
                      mat("Ojo_Amarillo", (1, 0.9, 0.1), emission=(1, 0.85, 0.1), strength=4), K, s=s, w=1.2, hunch=0.4)
    tc = piv["Torso"]
    P["Torso"].append(sphere(1.1 * s, tc + Vector((0, -0.3 * s, -0.2 * s)), flesh, subdiv=2, scale=(1.1, 0.8, 0.9)))
    for k in range(6):                                                          # costuras
        p = tc + Vector(((-0.8 + k * 0.3) * s, -1.15 * s, (0.2 - (k % 2) * 0.3) * s))
        P["Torso"].append(box((0.25 * s, 0.05 * s, 0.05 * s), p, K["BLACK"], rot=(0, 0.3 * (k % 2 * 2 - 1), 0), bevel=0))
    for sx in (-1, 1):                                                          # brazos extra
        a = tc + Vector((sx * 1.1 * s, -0.2 * s, -0.4 * s))
        P["Torso"].append(strut(a, a + Vector((sx * 0.6 * s, -1.5 * s, -0.5 * s)), 0.6 * s, 0.6 * s, flesh, bevel=0.05 * s))
    hc = piv["Head"] + Vector((0, 0, 0.62 * s))
    P["Head"].append(box((0.4 * s, 0.2 * s, 0.4 * s), hc + Vector((0.2 * s, -0.55 * s, 0.35 * s)), K["METAL"], bevel=0.03 * s))  # tornillo
    return finish(P, piv), s


def e_vacio():
    K = base_mats()
    rng = random.Random(61)
    void = mat("Vacio", (0.03, 0.0, 0.06))
    edge = mat("Borde_Vacio", (0.6, 0.1, 1), emission=(0.5, 0.05, 1), strength=5)
    P, piv = humanoid(void, void, void, edge, K, torn=False, w=0.9)
    for part in ("Torso", "LeftArm", "RightArm", "LeftLeg", "RightLeg"):
        c = piv[part] + Vector((0, 0, -0.8 if part != "Torso" else 0))
        for k in range(3):
            P[part].append(box((0.06, 0.06, rng.uniform(0.4, 0.9)), c + Vector((rng.uniform(-0.4, 0.4), -0.52, rng.uniform(-0.5, 0.5))), edge,
                               rot=(0, rng.uniform(-1, 1), 0), bevel=0))
    for k in range(6):                                                          # cubos de vacío flotando
        a = k * math.pi / 3
        P["Torso"].append(box((0.3, 0.3, 0.3), piv["Torso"] + Vector((math.cos(a) * 1.8, math.sin(a) * 1.8, rng.uniform(-0.5, 1.2))), void,
                              rot=(rng.uniform(0, 1), rng.uniform(0, 1), 0), bevel=0))
    return finish(P, piv), 1.0


def e_helado():
    K = base_mats()
    ice = mat("Hielo_Zombi", (0.6, 0.85, 1.0), 0.1, 0.1)
    P, piv = humanoid(mat("Piel_Helada", (0.55, 0.7, 0.8)), mat("Abrigo_Azul", (0.15, 0.3, 0.55)), mat("Pantalon_Oscuro", (0.15, 0.12, 0.12)),
                      mat("Ojo_Celeste", (0.4, 0.9, 1), emission=(0.3, 0.8, 1), strength=6), K)
    hc = piv["Head"] + Vector((0, 0, 0.62))
    for k in range(5):                                                          # carámbanos
        P["Head"].append(cone(0.1, 0.35, hc + Vector((-0.4 + k * 0.2, -0.62, -0.5)), ice, rot=(math.pi, 0, 0), verts=5))
    P["Head"].append(box((1.35, 1.3, 0.35), hc + Vector((0, 0, 0.55)), ice, bevel=0.08))
    for nm in ("LeftArm", "RightArm"):
        P[nm].append(strut(piv[nm + "_mid"], piv[nm + "_tip"], 1.0, 1.0, ice, bevel=0.1))
    for k in range(4):
        P["Torso"].append(cone(0.2, 0.7, piv["Torso"] + Vector((-0.6 + k * 0.4, 0.4, 1.0)), ice, verts=5))
    return finish(P, piv), 1.0


def e_minero():
    K = base_mats()
    P, piv = humanoid(mat("Piel_Zombi", (0.35, 0.55, 0.25)), mat("Camisa_Cuadros", (0.6, 0.15, 0.1)), mat("Jean", (0.2, 0.3, 0.55)),
                      mat("Ojo_Rojo", (1, 0.1, 0.05), emission=(1, 0.1, 0.05), strength=4), K)
    hc = piv["Head"] + Vector((0, 0, 0.62))
    P["Head"] += [sphere(0.8, hc + Vector((0, 0, 0.35)), mat("Casco_Amarillo", (1, 0.8, 0.1), 0.2, 0.4), subdiv=2, scale=(1, 1, 0.6)),
                  cyl(0.18, 0.2, hc + Vector((0, -0.7, 0.5)), mat("Linterna", (1, 1, 0.8), emission=(1, 1, 0.7), strength=8),
                      rot=(math.pi / 2, 0, 0), verts=10)]
    tip = piv["RightArm_tip"]                                                   # pico
    P["RightArm"] += [strut(tip + Vector((0, 0, -0.3)), tip + Vector((0, -0.2, 1.6)), 0.15, 0.15, K["WOOD"], bevel=0),
                      strut(tip + Vector((-0.8, -0.2, 1.5)), tip + Vector((0.8, -0.2, 1.5)), 0.18, 0.18, K["METAL"], bevel=0)]
    for sx in (-1, 1):                                                          # tirantes
        P["Torso"].append(box((0.18, 0.05, 2.0), piv["Torso"] + Vector((sx * 0.5, -0.52, 0)), mat("Tirante", (0.3, 0.2, 0.1)), bevel=0))
    return finish(P, piv), 1.0


# ------------------------------------------------------------------ armaduras
ARMORS = {
    "bronce": ((0.72, 0.42, 0.18), (0.45, 0.25, 0.1), None),
    "hierro": ((0.62, 0.64, 0.68), (0.3, 0.32, 0.36), None),
    "oro": ((1.0, 0.75, 0.2), (0.75, 0.1, 0.1), None),
    "diamante": ((0.45, 0.9, 1.0), (0.2, 0.5, 0.9), (0.3, 0.85, 1.0)),
    "obsidiana": ((0.1, 0.06, 0.16), (0.55, 0.15, 0.9), (0.6, 0.15, 1.0)),
}


def armor(P, piv, s, tier, K):
    """Armadura completa: casco con visera, peto, hombreras, guanteletes y grebas."""
    col, trim_c, glow_c = ARMORS[tier]
    A = mat(f"Armadura_{tier}", col, 0.9, 0.25)
    T = mat(f"Borde_{tier}", trim_c, 0.8, 0.3)
    G = mat(f"Brillo_{tier}", glow_c, emission=glow_c, strength=4) if glow_c else T
    hc = piv["Head"] + Vector((0, 0, 0.62 * s))
    H = P["Head"]
    H.append(box((1.45 * s, 1.4 * s, 1.0 * s), hc + Vector((0, 0.02 * s, 0.25 * s)), A, bevel=0.15 * s))      # casco
    H.append(box((1.48 * s, 0.1 * s, 0.14 * s), hc + Vector((0, -0.7 * s, 0.1 * s)), K["BLACK"], bevel=0))     # visera
    H.append(box((0.16 * s, 0.12 * s, 0.5 * s), hc + Vector((0, -0.71 * s, -0.12 * s)), A, bevel=0.03 * s))      # nasal
    H.append(box((0.2 * s, 1.45 * s, 0.25 * s), hc + Vector((0, 0.02 * s, 0.82 * s)), T, bevel=0.05 * s))      # cresta
    H.append(cone(0.12 * s, 0.5 * s, hc + Vector((0, 0.35 * s, 1.15 * s)), G, verts=5))
    tc = piv["Torso"]
    P["Torso"].append(box((2.2 * s, 1.2 * s, 1.5 * s), tc + Vector((0, 0, 0.3 * s)), A, bevel=0.12 * s))      # peto
    P["Torso"].append(box((2.25 * s, 1.25 * s, 0.15 * s), tc + Vector((0, 0, -0.45 * s)), T, bevel=0.03 * s))
    P["Torso"].append(box((0.12 * s, 0.1 * s, 1.1 * s), tc + Vector((0, -0.62 * s, 0.35 * s)), T, bevel=0))
    P["Torso"].append(box((0.55 * s, 0.1 * s, 0.55 * s), tc + Vector((0, -0.63 * s, 0.45 * s)), G, rot=(0, math.pi / 4, 0), bevel=0))  # emblema
    for k in range(3):                                                          # faldón de placas
        P["Torso"].append(box((0.62 * s, 1.15 * s, 0.5 * s), Vector(((-0.66 + k * 0.66) * s, 0, 1.8 * s)), A, rot=(0, 0, 0), bevel=0.06 * s))
    for side, nm in ((-1, "LeftArm"), (1, "RightArm")):
        c = piv[nm] + Vector((0.12 * side * s, 0, 0.18 * s))                     # hombrera
        P[nm].append(sphere(0.72 * s, c, A, subdiv=2, scale=(1.05, 1.0, 0.65)))
        P[nm].append(torus(0.66 * s, 0.06 * s, c + Vector((0, 0, -0.12 * s)), T, seg=16, minor=4))
        P[nm].append(strut(piv[nm + "_mid"], piv[nm + "_tip"], 1.05 * s, 1.05 * s, A, bevel=0.08 * s))  # guantelete
        P[nm].append(strut(piv[nm + "_mid"], piv[nm + "_mid"].lerp(piv[nm + "_tip"], 0.2), 1.12 * s, 1.12 * s, T, bevel=0.03 * s))
    for nm in ("LeftLeg", "RightLeg"):
        if nm + "_mid" in piv:
            P[nm].append(strut(piv[nm + "_mid"], piv[nm + "_foot"] + Vector((0, 0, 0.3 * s)), 1.08 * s, 1.08 * s, A, bevel=0.08 * s))
            P[nm].append(sphere(0.35 * s, piv[nm + "_mid"] + Vector((0, -0.5 * s, 0)), T, subdiv=1))            # rodillera


def armored(tier, s=1.1, weapon="espada"):
    def build():
        K = base_mats()
        P, piv = humanoid(mat("Piel_Zombi", (0.35, 0.55, 0.25)), mat("Cota_Malla", (0.3, 0.3, 0.33), 0.6, 0.5),
                          mat("Pantalon_Oscuro", (0.15, 0.12, 0.12)),
                          mat("Ojo_Rojo", (1, 0.1, 0.05), emission=(1, 0.1, 0.05), strength=4), K, s=s, torn=False)
        armor(P, piv, s, tier, K)
        col = ARMORS[tier][0]
        blade = mat(f"Hoja_{tier}", col, 0.9, 0.2)
        tip = piv["RightArm_tip"]
        if weapon == "espada":
            P["RightArm"].append(box((0.25 * s, 0.25 * s, 0.25 * s), tip, K["WOOD"], bevel=0.03))
            P["RightArm"].append(box((0.9 * s, 0.2 * s, 0.15 * s), tip + Vector((0, -0.25 * s, 0)), mat(f"Borde_{tier}", ARMORS[tier][1]), bevel=0))
            P["RightArm"].append(strut(tip + Vector((0, -0.3 * s, 0)), tip + Vector((0, -2.4 * s, 0.3 * s)), 0.3 * s, 0.1 * s, blade, bevel=0.02))
        else:                                                                   # hacha
            P["RightArm"].append(strut(tip + Vector((0, 0, -0.6 * s)), tip + Vector((0, 0, 1.6 * s)), 0.15 * s, 0.15 * s, K["WOOD"], bevel=0))
            head = tip + Vector((0, 0, 1.35 * s))
            P["RightArm"].append(box((0.12 * s, 0.7 * s, 0.9 * s), head + Vector((0, -0.4 * s, 0)), blade, bevel=0.03 * s))
            P["RightArm"].append(box((0.1 * s, 0.25 * s, 1.15 * s), head + Vector((0, -0.8 * s, 0)), blade, bevel=0.02 * s))
            P["RightArm"].append(cone(0.12 * s, 0.4 * s, head + Vector((0, 0.3 * s, 0)), blade, rot=(-math.pi / 2, 0, 0), verts=4))
        return finish(P, piv), s
    return build


BUILDERS = {
    "zombi_basico": e_basico,
    "zombi_generador": e_generador,
    "zombi_veloz": e_veloz,
    "zombi_divisor": e_divisor,
    "zombi_explosivo": e_explosivo,
    "zombi_excavador": e_excavador,
    "jefe_comandante_escudo": e_comandante,
    "zombi_corredor": e_corredor,
    "zombi_tanque": e_tanque,
    "zombi_escudo": e_escudo,
    "zombi_radiactivo": e_radiactivo,
    "zombi_astral": e_astral,
    "zombi_cosmico": e_cosmico,
    "zombi_radiante": e_radiante,
    "zombi_invocador": e_invocador,
    "zombi_espectral": e_espectral,
    "minijefe_bruto": e_minijefe,
    "jefe_rey_zombi": e_jefe,
    "zombi_armadura_bronce": armored("bronce", 1.05, "hacha"),
    "zombi_armadura_hierro": armored("hierro", 1.1, "espada"),
    "zombi_armadura_oro": armored("oro", 1.15, "espada"),
    "zombi_armadura_diamante": armored("diamante", 1.2, "espada"),
    "zombi_armadura_obsidiana": armored("obsidiana", 1.3, "hacha"),
    "zombi_cyborg": e_cyborg,
    "zombi_mecanico": e_mecanico,
    "zombi_boxeador": e_boxeador,
    "zombi_blindado": e_blindado,
    "zombi_sigiloso": e_sigiloso,
    "zombi_alado": e_alado,
    "jefe_brute": e_brute,
    "zombi_esqueleto": e_esqueleto,
    "golem_lava": e_golem_lava,
    "zombi_abominacion": e_abominacion,
    "zombi_vacio": e_vacio,
    "zombi_helado": e_helado,
    "zombi_minero": e_minero,
}


# enemigos que además salen como modelo de Roblox ya pintado (.rbxmx, hecho de Parts)
CON_RBXMX = {"zombi_basico", "zombi_generador", "zombi_veloz", "zombi_divisor", "zombi_explosivo", "zombi_excavador",
             "jefe_comandante_escudo"}


def build(nm):
    L.reset()
    objs, s = BUILDERS[nm]()
    if nm in ("zombi_espectral", "zombi_alado"):                               # vuelan
        for o in objs:
            o.location.z += 1.0
    out = os.path.join(HERE, nm)
    if nm in CON_RBXMX:
        pivots = {o.name: o.matrix_world.translation.copy() for o in objs}
        os.makedirs(out, exist_ok=True)
        n = rbxmx.write(os.path.join(out, nm + ".rbxmx"), nm, L.SPECS, pivots)
        shutil.copy(os.path.join(out, nm + ".rbxmx"), os.path.join(HERE, "..", "roblox", nm + ".rbxmx"))
        print(f"RBXMX {nm}: {n} Parts")
    L.export(out, nm, objs)
    if not os.environ.get("NO_RENDER"):
        L.render(out, target=(0, -0.5 * s, 2.6 * s), dist=0.85 * s)
    print("LISTO", nm)


if __name__ == "__main__":
    for nm in [a for a in sys.argv[1:] if a in BUILDERS] or list(BUILDERS):
        build(nm)
