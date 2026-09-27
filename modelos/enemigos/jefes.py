"""Jefes con proporciones Roblox R6 (todo en bloques): John Doe, 1x1x1x1 y el Lich.

Partes para animar con Motor6D (pivote en la articulación): Head, Torso, RightArm, LeftArm,
RightLeg, LeftLeg. Miran hacia -Y (su derecha está en -X). Pies en z = 0.

Uso: python jefes.py [jefe_john_doe | jefe_1x1x1x1 | lich]
"""
import os
import random
import sys

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))
import bpy  # noqa: E402
import lib_torretas as L  # noqa: E402
from lib_torretas import Matrix, Vector, box, cone, join, math, rod, sphere, strut, torus  # noqa: E402

HERE = os.path.dirname(os.path.abspath(__file__))

# esqueleto R6 (1 unidad = 1 stud)
PIV = dict(Head=Vector((0, 0, 4.0)), Torso=Vector((0, 0, 3.0)),
           RightArm=Vector((-1.5, 0, 3.5)), LeftArm=Vector((1.5, 0, 3.5)),
           RightLeg=Vector((-0.5, 0, 2.0)), LeftLeg=Vector((0.5, 0, 2.0)))
HEAD = Vector((0, 0, 4.6))            # centro de la cabeza (1.2 x 1.2 x 1.2)
FRONT = -0.61                         # cara de la cabeza (y)


def mat(name, color, metallic=0.0, rough=0.6, emission=None, strength=3.0):
    return bpy.data.materials.get(name) or L.material(name, color, metallic, rough, emission, strength)


def r6(head, torso, rarm, larm, rleg, lleg):
    P = {k: [] for k in PIV}
    P["Head"].append(box((1.2, 1.2, 1.2), HEAD, head, bevel=0.04))
    P["Torso"].append(box((2, 1, 2), (0, 0, 3), torso, bevel=0.03))
    P["RightArm"].append(box((1, 1, 2), (-1.5, 0, 3), rarm, bevel=0.03))
    P["LeftArm"].append(box((1, 1, 2), (1.5, 0, 3), larm, bevel=0.03))
    P["RightLeg"].append(box((1, 1, 2), (-0.5, 0, 1), rleg, bevel=0.03))
    P["LeftLeg"].append(box((1, 1, 2), (0.5, 0, 1), lleg, bevel=0.03))
    return P


def edges(P, part, size, center, m, t=0.07):
    """Marco de bordes (las 12 aristas) para el look de alto contraste."""
    c, (sx, sy, sz) = Vector(center), [v / 2 for v in size]
    for y in (-sy, sy):
        for z in (-sz, sz):
            P[part].append(box((size[0] + t, t, t), c + Vector((0, y, z)), m, bevel=0))
    for x in (-sx, sx):
        for z in (-sz, sz):
            P[part].append(box((t, size[1] + t, t), c + Vector((x, 0, z)), m, bevel=0))
    for x in (-sx, sx):
        for y in (-sy, sy):
            P[part].append(box((t, t, size[2] + t), c + Vector((x, y, 0)), m, bevel=0))


def smile(P, black, skip_right_eye=False):
    """Cara clásica de Roblox: dos ojos ovalados y sonrisa."""
    for sx in (-1, 1):
        if skip_right_eye and sx < 0:
            continue
        P["Head"].append(box((0.13, 0.04, 0.26), HEAD + Vector((sx * 0.22, FRONT, 0.14)), black, bevel=0.02))
    for k in range(9):
        a = math.radians(205 + k * 130 / 8)
        p = HEAD + Vector((math.cos(a) * 0.33, FRONT, -0.02 + math.sin(a) * 0.24))
        P["Head"].append(box((0.1, 0.04, 0.055), p, black, rot=(0, -(a + math.pi / 2), 0), bevel=0))


def digit(P, part, c, m, one=True, h=0.35):
    """Un 1 o un 0 en bloques."""
    c = Vector(c)
    if one:
        P[part] += [box((0.07, 0.05, h), c, m, bevel=0), box((0.12, 0.05, 0.05), c + Vector((-0.05, 0, h / 2 - 0.04)), m, bevel=0)]
    else:
        for sx in (-1, 1):
            P[part].append(box((0.06, 0.05, h), c + Vector((sx * 0.1, 0, 0)), m, bevel=0))
        for sz in (-1, 1):
            P[part].append(box((0.26, 0.05, 0.06), c + Vector((0, 0, sz * (h / 2 - 0.03))), m, bevel=0))


def chain(P, part, a, b, m, r=0.12, n=None):
    a, b = Vector(a), Vector(b)
    n = n or max(3, int((b - a).length / (r * 2.2)))
    d = (b - a).normalized()
    q = d.to_track_quat("X", "Z")
    for k in range(n):
        rot = q if k % 2 else q @ Matrix.Rotation(math.pi / 2, 3, "X").to_quaternion()
        P[part].append(torus(r, r * 0.35, a.lerp(b, (k + 0.5) / n), m, rot=rot.to_euler(), seg=8, minor=4))


def finish(P):
    return [join(parts, name, PIV[name]) for name, parts in P.items() if parts]


# ------------------------------------------------------------------ John Doe
def john_doe():
    rng = random.Random(3)
    head = mat("JD_Cabeza", (1.0, 0.86, 0.3))
    yellow = mat("JD_Torso", (1.0, 0.72, 0.04))
    pants = mat("JD_Pantalon", (0.62, 0.66, 0.95))
    black = mat("Negro", (0.02, 0.02, 0.02))
    white = mat("Blanco", (0.97, 0.97, 0.97))
    red = mat("JD_Rojo_R", (0.85, 0.05, 0.05))
    corrupt = mat("JD_Corrupcion", (0.09, 0.07, 0.07), 0.2, 0.5)
    code = mat("JD_Codigo", (1, 0.08, 0.05), emission=(1, 0.05, 0.02), strength=8)
    P = r6(head, yellow, corrupt, head, pants, pants)

    smile(P, black, skip_right_eye=True)
    eye = HEAD + Vector((-0.22, FRONT, 0.14))                                   # ojo derecho corrupto
    P["Head"] += [box((0.42, 0.06, 0.42), eye, corrupt, rot=(0, 0.25, 0), bevel=0),
                  box((0.26, 0.07, 0.3), eye + Vector((0.02, 0, 0.02)), corrupt, rot=(0, -0.3, 0), bevel=0),
                  box((0.14, 0.08, 0.14), eye + Vector((0, -0.01, 0.02)), code, rot=(0, 0.785, 0), bevel=0)]
    for k in range(4):                                                          # grietas rojas
        a = k * 1.6 + 0.3
        P["Head"].append(box((0.24, 0.07, 0.03), eye + Vector((math.cos(a) * 0.2, -0.005, math.sin(a) * 0.2)), code, rot=(0, -a, 0), bevel=0))

    # logo "R" blanco con borde rojo en el pecho (su izquierda: +X)
    R = Vector((0.45, -0.51, 3.5))
    strokes = [((0.1, 0.62), (0.0, 0)), ((0.32, 0.1), (0.13, 0.26)), ((0.32, 0.1), (0.13, 0.0)),
               ((0.1, 0.24), (0.29, 0.13))]
    for (w, h), (dx, dz) in strokes:
        P["Torso"].append(box((w + 0.08, 0.03, h + 0.08), R + Vector((dx, 0.005, dz)), red, bevel=0))
        P["Torso"].append(box((w, 0.05, h), R + Vector((dx, 0, dz)), white, bevel=0))
    leg0, leg1 = R + Vector((0.08, 0, -0.02)), R + Vector((0.3, 0, -0.3))
    P["Torso"].append(strut(leg0 + Vector((0, 0.005, 0)), leg1 + Vector((0, 0.005, 0)), 0.14, 0.03, red, bevel=0))
    P["Torso"].append(strut(leg0, leg1, 0.08, 0.05, white, bevel=0))
    P["Torso"][-4].location  # noqa

    # la corrupción chorrea por el torso (lado derecho) y los pies
    for k in range(6):
        x = -0.95 + k * 0.22
        h = rng.uniform(0.3, 1.2)
        P["Torso"].append(box((0.24, 1.06, h), (x, 0, 2.0 + h / 2), corrupt, bevel=0))
        P["Torso"].append(box((0.12, 1.06, 0.2), (x + 0.03, 0, 2.0 + h), corrupt, rot=(0, 0.785, 0), bevel=0))
    for nm, x in (("RightLeg", -0.5), ("LeftLeg", 0.5)):
        top = 0.55 if nm == "RightLeg" else 0.8
        P[nm].append(box((1.06, 1.06, top), (x, 0, top / 2), corrupt, bevel=0))
        for k in range(4):
            h = rng.uniform(0.2, 0.55)
            P[nm].append(box((0.2, 1.07, h), (x - 0.38 + k * 0.25, 0, top + h / 2 - 0.05), corrupt, bevel=0))

    # brazo derecho: masa de corrupción con púas enormes (forma de ala)
    sh = Vector((-1.5, 0, 3.5))
    P["RightArm"] = [box((1.15, 1.15, 2.1), (-1.5, 0, 3), corrupt, bevel=0.02)]
    shards = [((-0.3, 0.1, 1.0), 2.6, 0.55), ((-0.8, 0.2, 0.6), 2.4, 0.5), ((-1.0, 0.1, 0.0), 2.2, 0.45),
              ((-0.9, 0.0, -0.6), 3.0, 0.55), ((-0.4, -0.1, -1.0), 4.2, 0.65), ((-0.15, 0.2, -1.0), 3.6, 0.5)]
    for (dx, dy, dz), ln, r in shards:
        d = Vector((dx, dy, dz)).normalized()
        base = sh + Vector((-0.3, 0, -0.9)) + d * 0.3
        P["RightArm"].append(cone(r, ln, base + d * ln / 2, corrupt, rot=d, verts=4))
    for k in range(8):                                                          # púas chicas
        d = Vector((rng.uniform(-1, -0.3), rng.uniform(-0.3, 0.3), rng.uniform(-1, 1))).normalized()
        P["RightArm"].append(cone(0.2, 1.0, sh + Vector((-0.6, 0, -1.2 + rng.uniform(-0.5, 0.8))) + d * 0.6, corrupt, rot=d, verts=4))
    for k, (one, pos) in enumerate([(True, (-3.2, -0.3, 3.2)), (False, (-3.5, -0.3, 2.3)), (True, (-3.0, -0.3, 1.5)),
                                    (False, (-2.6, -0.4, 4.4)), (True, (-3.8, -0.2, 1.0))]):
        digit(P, "RightArm", pos, code, one)

    # mano izquierda corrupta con garras
    P["LeftArm"] += [box((1.1, 1.1, 0.9), (1.5, 0, 2.4), corrupt, bevel=0)]
    for k in range(3):
        h = rng.uniform(0.2, 0.5)
        P["LeftArm"].append(box((0.25, 1.11, h), (1.2 + k * 0.3, 0, 2.85 + h / 2), corrupt, bevel=0))
    for k in range(4):
        x = 1.15 + k * 0.23
        a = Vector((x, -0.35, 1.95))
        P["LeftArm"].append(strut(a, a + Vector((0, -0.25, -0.55)), 0.12, 0.12, corrupt, bevel=0))
        P["LeftArm"].append(cone(0.07, 0.35, a + Vector((0, -0.45, -0.75)), corrupt, rot=Vector((0, -0.8, -1)), verts=4))
    digit(P, "LeftArm", (2.3, -0.3, 2.0), code, True)
    digit(P, "LeftArm", (2.4, -0.3, 1.3), code, False)
    return finish(P), 3.0


# ------------------------------------------------------------------ 1x1x1x1
def one_x_one():
    rng = random.Random(5)
    dark = mat("1x_Oscuro", (0.02, 0.06, 0.03), 0.2, 0.5)
    green = mat("1x_Verde", (0.04, 0.55, 0.12), emission=(0.03, 0.6, 0.12), strength=1.0)
    neon = mat("1x_Neon", (0.2, 1.0, 0.3), emission=(0.1, 1.0, 0.2), strength=4)
    black = mat("Negro", (0.02, 0.02, 0.02))
    white = mat("1x_Punto", (0.95, 1.0, 0.95), emission=(0.9, 1.0, 0.9), strength=1.5)
    red = mat("1x_Ojo", (1, 0.1, 0.05), emission=(1, 0.08, 0.02), strength=12)
    cape = mat("1x_Capa", (0.55, 0.02, 0.04), 0.0, 0.7)
    P = r6(black, green, dark, dark, dark, dark)
    edges(P, "Head", (1.2, 1.2, 1.2), HEAD, neon, 0.06)
    for nm, c in (("RightArm", (-1.5, 0, 3)), ("LeftArm", (1.5, 0, 3)), ("RightLeg", (-0.5, 0, 1)), ("LeftLeg", (0.5, 0, 1))):
        edges(P, nm, (1, 1, 2), c, neon)
    edges(P, "Torso", (2, 1, 2), (0, 0, 3), neon)

    # costillar negro en el torso verde
    P["Torso"].append(box((0.22, 0.04, 1.6), (0, -0.52, 3.0), black, bevel=0))
    for k in range(4):
        z = 3.6 - k * 0.35
        for sx in (-1, 1):
            P["Torso"].append(box((0.65 - k * 0.05, 0.04, 0.13), (sx * 0.42, -0.52, z), black, rot=(0, sx * 0.35, 0), bevel=0))
    P["Torso"].append(box((1.2, 0.04, 0.12), (0, -0.52, 2.25), black, bevel=0))

    # ojo: estrella roja de 4 puntas
    e = HEAD + Vector((-0.24, FRONT - 0.02, 0.12))
    P["Head"] += [box((0.9, 0.03, 0.06), e, red, bevel=0), box((0.06, 0.03, 0.9), e, red, bevel=0),
                  box((0.4, 0.03, 0.05), e, red, rot=(0, 0.785, 0), bevel=0), box((0.4, 0.03, 0.05), e, red, rot=(0, -0.785, 0), bevel=0),
                  box((0.18, 0.05, 0.18), e, red, rot=(0, 0.785, 0), bevel=0)]
    P["Head"].append(box((0.35, 0.04, 0.06), HEAD + Vector((0.2, FRONT, -0.22)), neon, rot=(0, -0.2, 0), bevel=0))   # boca

    # corona dominó: ficha parada sobre la cabeza
    c = HEAD + Vector((0, 0.05, 0.6 + 0.7))
    P["Head"].append(box((1.1, 0.4, 1.4), c, black, bevel=0.03))
    edges(P, "Head", (1.1, 0.4, 1.4), c, neon, 0.07)
    P["Head"].append(box((0.95, 0.42, 0.06), c, neon, bevel=0))                 # línea del medio
    for i in range(2):
        for j in range(3):
            P["Head"].append(box((0.14, 0.44, 0.14), c + Vector((-0.24 + i * 0.48, 0, 0.17 + j * 0.2)), white, bevel=0))
    for rz in (0.75, -0.75):                                                    # X verde abajo
        P["Head"].append(box((0.09, 0.44, 0.5), c + Vector((0, 0, -0.35)), neon, rot=(0, rz, 0), bevel=0))
    for k in range(6):                                                          # marca de corona en el cuello
        x = -0.75 + k * 0.3
        P["Torso"].append(box((0.14, 1.04, 0.3), (x, 0, 4.05), neon, rot=(0, 0.785, 0), bevel=0))

    # capa roja
    P["Torso"] += [box((2.6, 1.3, 0.3), (0, 0.05, 4.05), cape, bevel=0.03),
                   strut(Vector((0, 0.6, 4.0)), Vector((0, 1.3, 0.4)), 2.8, 0.1, cape, bevel=0)]
    for k in range(6):
        P["Torso"].append(box((0.4, 0.1, 0.5), (-1.15 + k * 0.46, 1.33 - 0.01 * k, 0.2 - (k % 2) * 0.25), cape, rot=(0, 0.785, 0), bevel=0))
    for sx in (-1, 1):                                                          # la capa cae por los costados
        P["Torso"].append(strut(Vector((sx * 1.25, 0.3, 4.1)), Vector((sx * 1.7, 0.9, 0.5)), 0.12, 0.9, cape, bevel=0))
    # hombrera dominó (izquierda)
    s = Vector((1.55, 0, 4.2))
    P["LeftArm"].append(box((1.3, 1.25, 0.45), s, black, bevel=0.03))
    edges(P, "LeftArm", (1.3, 1.25, 0.45), s, neon, 0.06)
    for dx, dy in ((-0.35, -0.35), (0, 0), (0.35, 0.35), (-0.35, 0.35), (0.35, -0.35)):
        P["LeftArm"].append(box((0.16, 0.16, 0.05), s + Vector((dx, dy, 0.24)), white, bevel=0))
    # muñequeras de cadena
    for nm, x in (("RightArm", -1.5), ("LeftArm", 1.5)):
        for k in range(4):
            P[nm].append(box((1.08, 1.08, 0.1), (x, 0, 2.35 + k * 0.14), neon if k % 2 else dark, bevel=0))
    # espadas de fuego verde
    for nm, x in (("RightArm", -1.5), ("LeftArm", 1.5)):
        h = Vector((x, -0.2, 2.0))
        P[nm] += [box((0.25, 0.25, 0.6), h + Vector((0, 0, -0.2)), black, bevel=0),
                  box((0.9, 0.3, 0.15), h + Vector((0, 0, -0.55)), neon, bevel=0),
                  box((0.3, 0.1, 2.8), h + Vector((0, 0, -2.0)), neon, bevel=0)]
        for k in range(5):
            P[nm].append(cone(0.2, 0.55, h + Vector((rng.uniform(-0.15, 0.15), rng.uniform(-0.1, 0.1), -0.9 - k * 0.5)), green, verts=4))
    # llamas oscuras en los pies
    for k in range(8):
        a = k * math.pi / 4
        P["Torso"].append(cone(0.3, rng.uniform(0.6, 1.1), (math.cos(a) * 1.2, math.sin(a) * 0.8, 0.35), green, verts=4))
    return finish(P), 3.0


# ------------------------------------------------------------------ Lich
def lich():
    rng = random.Random(7)
    hood = mat("Lich_Capucha", (0.13, 0.13, 0.14), 0.0, 0.8)
    pants = mat("Lich_Pantalon", (0.09, 0.09, 0.1), 0.0, 0.8)
    skin = mat("Lich_Piel", (0.42, 0.5, 0.4), 0.0, 0.7)
    bone = mat("Lich_Hueso", (0.93, 0.91, 0.86), 0.0, 0.5)
    black = mat("Negro", (0.02, 0.02, 0.02))
    glow = mat("Lich_Brillo", (0.4, 1.0, 0.85), emission=(0.3, 1.0, 0.8), strength=6)
    iron = mat("Lich_Cadena", (0.35, 0.36, 0.38), 0.8, 0.4)
    P = r6(bone, hood, hood, hood, pants, pants)
    # antebrazos de piel
    for nm, x in (("RightArm", -1.5), ("LeftArm", 1.5)):
        P[nm].append(box((1.02, 1.02, 0.95), (x, 0, 2.47), skin, bevel=0.02))
        for k in range(3):                                                      # manga rasgada
            P[nm].append(box((0.3, 1.04, 0.25), (x - 0.33 + k * 0.33, 0, 2.95 - (k % 2) * 0.15), hood, rot=(0, 0.785, 0), bevel=0))

    # calavera con cuernos (cabeza)
    P["Head"] += [box((0.9, 0.2, 0.35), HEAD + Vector((0, -0.62, -0.42)), bone, bevel=0.03)]    # mandíbula
    for sx in (-1, 1):
        e = HEAD + Vector((sx * 0.25, FRONT, 0.1))
        P["Head"] += [box((0.3, 0.05, 0.3), e, black, bevel=0.02), box((0.08, 0.06, 0.08), e, glow, bevel=0)]
    P["Head"].append(box((0.12, 0.05, 0.16), HEAD + Vector((0, FRONT, -0.15)), black, rot=(0, 0.785, 0), bevel=0))
    for k in range(5):
        P["Head"].append(box((0.09, 0.05, 0.14), HEAD + Vector((-0.24 + k * 0.12, FRONT - 0.2, -0.4)), black if k % 2 else bone, bevel=0))
    for sx in (-1, 1):                                                          # cuernos
        base = HEAD + Vector((sx * 0.45, 0, 0.55))
        pts = [base, base + Vector((sx * 0.25, 0, 0.45)), base + Vector((sx * 0.3, 0.1, 0.9)), base + Vector((sx * 0.15, 0.2, 1.25))]
        for k in range(3):
            P["Head"].append(strut(pts[k], pts[k + 1], 0.24 - k * 0.06, 0.24 - k * 0.06, bone, bevel=0))
    # capucha detrás de la cabeza
    P["Torso"] += [box((1.5, 0.6, 1.5), (0, 0.45, 4.55), hood, bevel=0.03), box((1.6, 1.2, 0.3), (0, 0.1, 4.0), hood, bevel=0.03)]
    # cadena cruzada
    chain(P, "Torso", (-0.95, -0.55, 3.9), (0.95, -0.55, 2.2), iron, r=0.1)
    # capa rasgada atrás
    P["Torso"].append(strut(Vector((0, 0.55, 3.9)), Vector((0, 0.9, 0.9)), 2.2, 0.08, hood, bevel=0))
    for k in range(5):
        P["Torso"].append(box((0.4, 0.08, 0.5), (-0.8 + k * 0.4, 0.92, 0.8 - (k % 2) * 0.25), hood, rot=(0, 0.785, 0), bevel=0))

    # bastón con calavera (mano derecha, -X)
    st = Vector((-1.5, -0.7, 0))
    P["RightArm"] += [box((0.14, 0.14, 7.2), st + Vector((0, 0, 3.6)), black, bevel=0),
                      box((1.05, 0.25, 0.25), (-1.5, -0.35, 2.1), black, bevel=0)]
    sk = st + Vector((0, 0, 7.45))
    P["RightArm"] += [box((0.5, 0.45, 0.45), sk, bone, bevel=0.03), box((0.36, 0.1, 0.15), sk + Vector((0, -0.24, -0.25)), bone, bevel=0)]
    for sx in (-1, 1):
        P["RightArm"] += [box((0.12, 0.05, 0.12), sk + Vector((sx * 0.11, -0.23, 0.04)), black, bevel=0),
                          strut(sk + Vector((sx * 0.2, 0, 0.2)), sk + Vector((sx * 0.35, 0, 0.55)), 0.1, 0.1, bone, bevel=0),
                          strut(sk + Vector((sx * 0.35, 0, 0.55)), sk + Vector((sx * 0.3, 0.05, 0.8)), 0.07, 0.07, bone, bevel=0)]
    P["RightArm"].append(box((0.06, 0.06, 0.06), sk + Vector((0, -0.25, 0.04)), glow, bevel=0))
    for k in range(3):
        P["RightArm"].append(box((0.16, 0.16, 0.16), sk + Vector((math.cos(k * 2.1) * 0.5, math.sin(k * 2.1) * 0.5, 0.3 + k * 0.1)),
                                 glow, rot=(0.6, 0.6, 0), bevel=0))
    return finish(P), 1.5


BUILDERS = {"jefe_john_doe": john_doe, "jefe_1x1x1x1": one_x_one, "lich": lich}
VIEWS = {"vista_frente": (-3.0, -10.5, 1.2), "vista_costado": (9.0, -6.5, 2.0), "vista_atras": (-6.0, 8.5, 2.5)}

if __name__ == "__main__":
    for nm in [a for a in sys.argv[1:] if a in BUILDERS] or list(BUILDERS):
        L.reset()
        objs, s = BUILDERS[nm]()
        L.transform(objs, Matrix.Scale(s, 4), (0, 0, 0))
        out = os.path.join(HERE, nm)
        L.export(out, nm, objs)
        if not os.environ.get("NO_RENDER"):
            L.render(out, target=(-0.4 * s, 0, 3.4 * s), dist=1.08 * s, views=VIEWS)
        print("LISTO", nm)
