"""Enemigos del Tower Defense: zombis estilo bloque (tipo Roblox R6) con variantes y jefes.

Cada enemigo se exporta separado en partes con el pivote en su articulación, para animarlo
con Motor6D en Roblox:  Head (cuello), Torso (centro), LeftArm / RightArm (hombros),
LeftLeg / RightLeg (caderas). Los accesorios van pegados a la parte que corresponde.
El enemigo mira hacia -Y. Pies en z = 0.

Uso: python enemigos.py [nombre ...]   (sin nombres arma todos)
"""
import os
import random
import sys

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))
import bpy  # noqa: E402
import bmesh  # noqa: E402  (después de bpy)
import lib_torretas as L  # noqa: E402
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
def _zb_torso(P, K, rng):
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

    # zarpazo en el pecho izquierdo (lado -X es su derecha)
    for k in range(3):
        _zb_front(P, T, (0.07, 0.75), -0.75 + k * 0.17, 3.45 - k * 0.03, -0.5, K["FLESH"], rot=0.55)
        _zb_front(P, T, (0.03, 0.6), -0.75 + k * 0.17, 3.45 - k * 0.03, -0.52, K["BLOOD"], rot=0.55)
    # manchas de sangre seca
    for _ in range(6):
        _zb_front(P, T, (rng.uniform(0.12, 0.3), rng.uniform(0.1, 0.25)), rng.uniform(-0.85, -0.1), rng.uniform(2.4, 3.1), -0.5,
              K["BLOOD2"], rot=rng.uniform(0, 3))
    # bolsillo roto en el pecho derecho (lado -X)
    _zb_front(P, T, (0.42, 0.42), -0.5, 3.55, -0.5, K["SHIRT2"])
    P[T].append(box((0.44, 0.05, 0.06), (-0.5, -0.53, 3.75), K["SHIRT"], bevel=0))
    _zb_vtri(P, T, -0.35, 3.3, -0.53, 0.1, K["SHIRT2"])                                # esquina colgando
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


def _zb_body(K, rng, extra=None):
    """Cuerpo del zombi básico armado y en pose. `extra(P)` agrega accesorios en pose de reposo antes de unir."""
    P = {k: [] for k in ZB_PIV}
    _zb_torso(P, K, rng)
    _zb_head(P, K, rng)
    _zb_arm(P, K, rng, "RightArm", -1)
    _zb_arm(P, K, rng, "LeftArm", 1)
    _zb_leg(P, K, rng, "RightLeg", -1)
    _zb_leg(P, K, rng, "LeftLeg", 1)
    if extra:
        extra(P)
    objs = {k: join(v, k, ZB_PIV[k]) for k, v in P.items()}
    # pose de zombi: brazos estirados hacia adelante (uno un poco más bajo) y cabeza ladeada
    L.transform([objs["RightArm"]], Matrix.Rotation(-math.radians(84), 4, "X"), ZB_PIV["RightArm"])
    L.transform([objs["LeftArm"]], Matrix.Rotation(-math.radians(95), 4, "X"), ZB_PIV["LeftArm"])
    L.transform([objs["Head"]], Matrix.Rotation(math.radians(9), 4, "Y") @ Matrix.Rotation(math.radians(6), 4, "X"), ZB_PIV["Head"])
    return list(objs.values())


def e_basico():
    """Zombi básico: R6 clásico, sin cara, descalzo y sin uñas, con mucho detalle."""
    return _zb_body(_zb_mats(), random.Random(7)), 1.0


def e_generador():
    """Zombi de apoyo con un generador de escudos en la espalda. La cúpula de energía es una parte aparte: `Escudo`."""
    K = _zb_mats()
    K.update(SHIRT=mat("Mono_Tecnico", (0.20, 0.22, 0.25)), SHIRT2=mat("Mono_Oscuro", (0.09, 0.10, 0.12)),
             PANTS=mat("Mono_Pantalon", (0.15, 0.16, 0.19)))
    metal = mat("Metal_Generador", (0.12, 0.13, 0.16), 0.8, 0.35)
    steel = mat("Acero", (0.5, 0.52, 0.56), 0.9, 0.3)
    stripe = mat("Franja_Celeste", (0.2, 0.7, 1.0))
    glow = mat("Energia_Celeste", (0.3, 0.85, 1.0), emission=(0.25, 0.8, 1.0), strength=6)
    leds = [mat(f"Led_{n}", c, emission=c, strength=5) for n, c in (("Verde", (0.1, 1, 0.2)), ("Amarillo", (1, 0.8, 0.1)), ("Rojo", (1, 0.1, 0.05)))]

    def gear(P):
        T = P["Torso"]
        pc = Vector((0, 0.82, 3.1))                                              # mochila generadora
        T.append(box((1.5, 0.65, 1.6), pc, metal, bevel=0.08))
        T.append(box((1.56, 0.7, 0.12), pc + Vector((0, 0, 0.62)), steel, bevel=0.02))
        T.append(box((1.56, 0.7, 0.12), pc + Vector((0, 0, -0.62)), steel, bevel=0.02))
        for sx in (-1, 1):
            for sz in (-1, 1):                                                   # remaches
                T.append(sphere(0.05, pc + Vector((sx * 0.68, 0.34, sz * 0.48)), steel, subdiv=1))
            for k in range(4):                                                   # rejillas
                T.append(box((0.04, 0.4, 0.06), pc + Vector((sx * 0.77, 0, -0.3 + k * 0.17)), mat("Negro", (0.02, 0.02, 0.02)), bevel=0))
        cc = pc + Vector((0, 0.42, 0))                                           # núcleo de energía
        T.append(cyl(0.3, 1.05, cc, glow, verts=16, bevel=0))
        for z in (-0.25, 0.25):
            T.append(L.torus(0.33, 0.05, cc + Vector((0, 0, z)), steel, seg=16, minor=6))
        for z in (-0.56, 0.56):
            T.append(cyl(0.35, 0.1, cc + Vector((0, 0, z)), steel, verts=16, bevel=0.02))
        for k, m in enumerate(leds):                                             # luces de estado
            T.append(box((0.1, 0.05, 0.1), pc + Vector((-0.55 + k * 0.15, 0.34, 0.45)), m, bevel=0))
        # antena con punta de energía
        ab = pc + Vector((0.5, 0.1, 0.8))
        T.append(L.rod(ab, ab + Vector((0, 0.05, 1.3)), 0.04, steel))
        T.append(cyl(0.08, 0.12, ab + Vector((0, 0.05, 0.05)), steel, verts=10, bevel=0))
        T.append(sphere(0.11, ab + Vector((0, 0.05, 1.38)), glow, subdiv=2))
        for z in (0.5, 0.85):
            T.append(L.torus(0.12 - z * 0.05, 0.02, ab + Vector((0, 0.05, z)), glow, seg=10, minor=4))
        # tirantes sobre los hombros
        for sx in (-1, 1):
            T.append(box((0.25, 1.06, 0.06), (sx * 0.55, 0, 4.03), metal, bevel=0.01))
            T.append(box((0.25, 0.06, 0.35), (sx * 0.55, -0.53, 3.85), metal, bevel=0.01))
            T.append(box((0.08, 0.07, 0.08), (sx * 0.55, -0.56, 3.75), steel, bevel=0))
        # cables al emisor del pecho
        em = Vector((0, -0.6, 3.25))
        for sx in (-1, 1):
            pts = [Vector((sx * 0.72, 0.5, 3.75)), Vector((sx * 0.8, 0.1, 4.08)), Vector((sx * 0.8, -0.55, 3.85)),
                   Vector((sx * 0.35, -0.6, 3.45)), em + Vector((sx * 0.15, 0, 0))]
            for a, b in zip(pts, pts[1:]):
                T.append(L.rod(a, b, 0.045, glow if sx > 0 else mat("Cable_Negro", (0.03, 0.03, 0.03)), verts=6))
        T.append(cyl(0.24, 0.1, em, steel, rot=(math.pi / 2, 0, 0), verts=16, bevel=0.02))
        T.append(cyl(0.16, 0.06, em + Vector((0, -0.05, 0)), glow, rot=(math.pi / 2, 0, 0), verts=16, bevel=0))
        T.append(L.torus(0.24, 0.03, em + Vector((0, -0.05, 0)), metal, rot=(math.pi / 2, 0, 0), seg=16, minor=4))
        # franjas celestes en el mono (piernas y mangas)
        for nm, x in (("RightLeg", -0.5), ("LeftLeg", 0.5)):
            P[nm].append(box((1.05, 1.05, 0.1), (x, 0, 1.6), stripe, bevel=0))
        for nm, x in (("RightArm", -1.5), ("LeftArm", 1.5)):
            P[nm].append(box((1.08, 1.08, 0.08), (x, 0, 3.42), stripe, bevel=0))
        # brazo izquierdo: mando de muñeca con pantalla (sin manos ni uñas)
        P["LeftArm"].append(box((1.1, 1.1, 0.32), (1.5, 0, 2.3), metal, bevel=0.04))
        P["LeftArm"].append(box((0.5, 0.05, 0.2), (1.5, -0.57, 2.3), glow, bevel=0))
        for k, m in enumerate(leds):
            P["LeftArm"].append(box((0.07, 0.05, 0.07), (1.65 + 0.1 * k - 0.1, -0.57, 2.42), m, bevel=0))
        P["LeftArm"].append(cyl(0.12, 0.08, (1.5, 0, 2.0 - 0.06), glow, verts=12, bevel=0))  # emisor en la punta
        # auricular en la cabeza
        h = ZB_HEAD + Vector((0.63, 0.05, 0.0))
        P["Head"].append(box((0.1, 0.35, 0.35), h, metal, bevel=0.03))
        P["Head"].append(box((0.04, 0.2, 0.2), h + Vector((0.06, 0, 0)), glow, bevel=0))
        P["Head"].append(L.rod(h + Vector((0.05, -0.1, -0.1)), h + Vector((0.0, -0.45, -0.35)), 0.025, metal, verts=6))

    objs = _zb_body(K, random.Random(11), gear)
    # cúpula de escudo (parte aparte para prenderla/apagarla en Roblox)
    shield = mat("Escudo_Energia", (0.35, 0.8, 1.0), rough=0.1, emission=(0.2, 0.65, 1.0), strength=1.5)
    bpy.ops.mesh.primitive_ico_sphere_add(subdivisions=3, radius=1, location=(0, -0.45, 0))
    dome = bpy.context.active_object
    dome.scale = (2.9, 3.1, 5.6)
    bpy.ops.object.transform_apply(location=False, rotation=False, scale=True)
    bm = bmesh.new()
    bm.from_mesh(dome.data)
    bmesh.ops.bisect_plane(bm, geom=bm.verts[:] + bm.edges[:] + bm.faces[:], plane_co=(0, 0, 0.05), plane_no=(0, 0, 1),
                           clear_inner=True)
    bm.to_mesh(dome.data)
    bm.free()
    dome.data.materials.append(shield)
    ring = [L.torus(2.95, 0.07, (0, -0.45, 0.07), glow, rot=(0, 0, 0), seg=40, minor=6)]
    ring[0].scale = (1, 3.15 / 2.95, 1)
    for k in range(6):                                                           # nodos emisores en el piso
        a = k / 6 * 2 * math.pi
        ring.append(box((0.25, 0.25, 0.18), (math.cos(a) * 2.9, -0.45 + math.sin(a) * 3.1, 0.09), metal, rot=(0, 0, a), bevel=0.03))
    objs.append(join([dome] + ring, "Escudo", (0, 0, 3.0)))
    return objs, 1.3


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


def build(nm):
    L.reset()
    objs, s = BUILDERS[nm]()
    if nm in ("zombi_espectral", "zombi_alado"):                               # vuelan
        for o in objs:
            o.location.z += 1.0
    out = os.path.join(HERE, nm)
    L.export(out, nm, objs)
    sh = bpy.data.materials.get("Escudo_Energia")                              # cúpula semitransparente solo en la vista
    if sh:
        sh.node_tree.nodes["Principled BSDF"].inputs["Alpha"].default_value = 0.1
    if not os.environ.get("NO_RENDER"):
        L.render(out, target=(0, -0.5 * s, 2.6 * s), dist=0.85 * s)
    print("LISTO", nm)


if __name__ == "__main__":
    for nm in [a for a in sys.argv[1:] if a in BUILDERS] or list(BUILDERS):
        build(nm)
