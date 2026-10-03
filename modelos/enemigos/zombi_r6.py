"""Zombi R6 sin cara, estilo Roblox clásico pero con mucho detalle.

Proporciones R6 exactas (1 unidad = 1 stud): cabeza redonda clásica, torso 2x1x2, brazos y piernas 1x1x2.
La cabeza NO tiene cara (frente liso). Los brazos van estirados hacia adelante, como el zombi de Roblox.

Partes para animar con Motor6D (pivote en la articulación): Head (cuello), Torso, RightArm / LeftArm
(hombros), RightLeg / LeftLeg (caderas). Mira hacia -Y (su derecha está en -X). Pies en z = 0.

Uso: python zombi_r6.py
"""
import os
import random
import sys

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))
import bpy  # noqa: E402
import lib_torretas as L  # noqa: E402
from lib_torretas import Matrix, Vector, box, cone, cyl, join, math, sphere, strut  # noqa: E402

HERE = os.path.dirname(os.path.abspath(__file__))
NAME = "zombi_r6_sin_cara"

PIV = dict(Head=Vector((0, 0, 4.0)), Torso=Vector((0, 0, 3.0)),
           RightArm=Vector((-1.5, 0, 3.5)), LeftArm=Vector((1.5, 0, 3.5)),
           RightLeg=Vector((-0.5, 0, 2.0)), LeftLeg=Vector((0.5, 0, 2.0)))
HEAD = Vector((0, 0, 4.6))            # centro de la cabeza
E = 0.02                               # despegue de los "calcos" sobre la superficie


def mat(name, color, metallic=0.0, rough=0.7, emission=None, strength=3.0):
    return bpy.data.materials.get(name) or L.material(name, color, metallic, rough, emission, strength)


def mats():
    return dict(
        SKIN=mat("Piel_Zombi", (0.30, 0.52, 0.18)),
        ROT=mat("Piel_Podrida", (0.18, 0.32, 0.10)),
        SHIRT=mat("Camisa_Celeste", (0.10, 0.28, 0.50)),
        SHIRT2=mat("Camisa_Oscura", (0.05, 0.14, 0.28)),
        PANTS=mat("Pantalon_Marron", (0.24, 0.14, 0.07)),
        PATCH=mat("Parche_Jean", (0.16, 0.22, 0.38)),
        SHOE=mat("Zapatilla", (0.06, 0.05, 0.05)),
        SOLE=mat("Suela", (0.80, 0.78, 0.72)),
        LACE=mat("Cordon", (0.90, 0.90, 0.88)),
        BELT=mat("Cinturon", (0.10, 0.06, 0.04)),
        BUCKLE=mat("Hebilla", (0.55, 0.55, 0.58), 0.9, 0.3),
        BLOOD=mat("Sangre", (0.30, 0.01, 0.01), rough=0.3),
        BLOOD2=mat("Sangre_Seca", (0.16, 0.02, 0.02)),
        FLESH=mat("Carne", (0.50, 0.08, 0.09), rough=0.4),
        BONE=mat("Hueso", (0.88, 0.85, 0.74)),
        BRAIN=mat("Cerebro", (0.85, 0.45, 0.50), rough=0.35),
        STITCH=mat("Costura", (0.03, 0.03, 0.03)),
        BANDAGE=mat("Venda", (0.82, 0.78, 0.66)),
    )


def front(P, part, size, x, z, y, m, rot=0.0):
    """Calco plano sobre una cara que mira a -Y (y = cara frontal) o +Y si y > 0."""
    sy = 1 if y > 0 else -1
    P[part].append(box((size[0], 0.04, size[1]), Vector((x, y + sy * E, z)), m, rot=(0, rot, 0), bevel=0))


def side(P, part, size, x, y, z, m, rot=0.0):
    """Calco plano sobre una cara lateral (x = cara)."""
    sx = 1 if x > 0 else -1
    P[part].append(box((0.04, size[0], size[1]), Vector((x + sx * E, y, z)), m, rot=(rot, 0, 0), bevel=0))


def jagged_ring(P, part, cx, cy, z, w, d, m, rng, n=4, size=0.16, down=True):
    """Borde desgarrado: dientes triangulares alrededor de una caja (w x d) a la altura z."""
    pts = []  # (x, y)
    for k in range(n):
        t = (k + 0.5) / n
        pts += [(cx - w / 2 + t * w, cy - d / 2 - E), (cx - w / 2 + t * w, cy + d / 2 + E)]
    for k in range(max(2, n // 2)):
        t = (k + 0.5) / max(2, n // 2)
        pts += [(cx - w / 2 - E, cy - d / 2 + t * d), (cx + w / 2 + E, cy - d / 2 + t * d)]
    for x, y in pts:
        h = size * rng.uniform(0.7, 1.4)
        c = Vector((x, y, z - h / 2 if down else z + h / 2))
        P[part].append(cone(size * rng.uniform(0.6, 0.9), h, c, m, rot=(math.pi if down else 0, 0, 0), verts=3))


def stitches(P, part, a, b, normal, m, n=5, w=0.03, cross=0.18):
    """Costura: línea de a a b con puntadas cruzadas, pegada a la superficie con esa normal."""
    a, b, nrm = Vector(a), Vector(b), Vector(normal)
    P[part].append(strut(a, b, w, w, m, bevel=0))
    d = (b - a).normalized()
    perp = d.cross(nrm).normalized()
    for k in range(n):
        c = a.lerp(b, (k + 0.5) / n)
        P[part].append(strut(c - perp * cross / 2, c + perp * cross / 2, w, w, m, bevel=0))


# ------------------------------------------------------------------ partes
def torso(P, K, rng):
    T = "Torso"
    P[T].append(box((2, 1, 2), (0, 0, 3), K["SHIRT"], bevel=0.03))
    P[T].append(box((0.7, 0.7, 0.12), (0, 0, 4.03), K["SKIN"], bevel=0.02))                     # cuello
    # cuello en V roto
    P[T].append(box((0.5, 0.04, 0.35), (0, -0.5 - E, 3.82), K["SKIN"], rot=(0, math.pi / 4, 0), bevel=0))
    # borde de abajo desgarrado (la camisa cuelga sobre el cinturón)
    jagged_ring(P, T, 0, 0, 2.32, 2.0, 1.0, K["SHIRT"], rng, n=6, size=0.17)
    # cinturón con hebilla
    P[T].append(box((2.04, 1.04, 0.22), (0, 0, 2.11), K["BELT"], bevel=0.02))
    P[T].append(box((0.34, 0.06, 0.26), (0.15, -0.53, 2.11), K["BUCKLE"], bevel=0.02))
    P[T].append(box((0.2, 0.07, 0.12), (0.15, -0.54, 2.11), K["BELT"], bevel=0))
    for x in (-0.6, 0.75):                                                       # presillas
        P[T].append(box((0.08, 0.06, 0.28), (x, -0.53, 2.11), K["BELT"], bevel=0))

    # agujero grande en el pecho: piel, carne y costillas
    hc = Vector((0.45, -0.5, 3.05))
    front(P, T, (0.85, 0.8), hc.x, hc.z, -0.5, K["SKIN"])
    front(P, T, (0.6, 0.55), hc.x, hc.z, -0.52, K["FLESH"])
    for k in range(3):
        P[T].append(box((0.55, 0.06, 0.08), (hc.x, -0.57, hc.z + 0.18 - k * 0.17), K["BONE"], rot=(0, 0.08 * (k - 1), 0), bevel=0.01))
    for k in range(10):                                                          # tela rota alrededor del agujero
        a = k / 10 * 2 * math.pi
        p = Vector((hc.x + math.cos(a) * 0.46, -0.53, hc.z + math.sin(a) * 0.43))
        front(P, T, (0.15, 0.15), p.x, p.z, -0.51, K["SHIRT"], rot=math.pi / 4)
    # sangre que chorrea del agujero
    for k, (x, ln) in enumerate(((0.3, 0.55), (0.55, 0.35), (0.7, 0.7))):
        front(P, T, (0.09, ln), x, hc.z - 0.38 - ln / 2, -0.51, K["BLOOD"])
        P[T].append(sphere(0.07, (x, -0.54, hc.z - 0.38 - ln), K["BLOOD"], subdiv=1, scale=(1, 0.5, 1.2)))

    # zarpazo en el pecho izquierdo (lado -X es su derecha)
    for k in range(3):
        front(P, T, (0.07, 0.75), -0.75 + k * 0.17, 3.45 - k * 0.03, -0.5, K["FLESH"], rot=0.55)
        front(P, T, (0.03, 0.6), -0.75 + k * 0.17, 3.45 - k * 0.03, -0.52, K["BLOOD"], rot=0.55)
    # manchas de sangre seca
    for _ in range(6):
        front(P, T, (rng.uniform(0.12, 0.3), rng.uniform(0.1, 0.25)), rng.uniform(-0.85, -0.1), rng.uniform(2.4, 3.1), -0.5,
              K["BLOOD2"], rot=rng.uniform(0, 3))
    # parche cosido a la camisa
    front(P, T, (0.38, 0.32), -0.55, 2.65, -0.5, K["SHIRT2"], rot=0.12)
    stitches(P, T, (-0.75, -0.55, 2.82), (-0.35, -0.55, 2.86), (0, -1, 0), K["STITCH"], n=4, w=0.025, cross=0.1)

    # espalda: desgarro con columna a la vista
    front(P, T, (0.7, 1.2), 0, 3.05, 0.5, K["SKIN"])
    front(P, T, (0.5, 1.0), 0, 3.05, 0.52, K["FLESH"])
    for k in range(5):
        P[T].append(box((0.22, 0.1, 0.13), (0, 0.58, 3.5 - k * 0.22), K["BONE"], bevel=0.02))
        P[T].append(box((0.4, 0.07, 0.04), (0, 0.57, 3.5 - k * 0.22), K["BONE"], bevel=0))
    for k in range(8):
        a = k / 8 * 2 * math.pi
        p = Vector((math.cos(a) * 0.4, 0.53, 3.05 + math.sin(a) * 0.65))
        front(P, T, (0.15, 0.15), p.x, p.z, 0.51, K["SHIRT"], rot=math.pi / 4)
    for _ in range(4):
        front(P, T, (rng.uniform(0.15, 0.3), rng.uniform(0.12, 0.3)), rng.uniform(-0.85, 0.85), rng.uniform(2.4, 3.8), 0.5,
              K["BLOOD2"], rot=rng.uniform(0, 3))
    # tiras de tela colgando a los costados
    for sx, z in ((-1, 2.35), (1, 2.5)):
        P[T].append(box((0.04, 0.22, 0.55), (sx * (1.0 + E), -0.15, z - 0.25), K["SHIRT"], rot=(0.15 * sx, 0, 0), bevel=0))
        side(P, T, (0.25, 0.3), sx * 1.0, 0.2, 3.3, K["BLOOD2"])


def head(P, K, rng):
    H = "Head"
    # cabeza redonda clásica de Roblox (cilindro con bordes redondeados). Sin cara.
    P[H].append(cyl(0.62, 1.2, HEAD, K["SKIN"], verts=24, bevel=0.16))
    # cerebro expuesto arriba (lado izquierdo, +X)
    bc = HEAD + Vector((0.2, 0.1, 0.6))
    P[H].append(cyl(0.3, 0.06, bc, K["FLESH"], verts=12, bevel=0))
    P[H].append(sphere(0.27, bc + Vector((0, 0, 0.02)), K["BRAIN"], subdiv=2, scale=(1, 0.95, 0.38)))
    for k in range(3):
        P[H].append(box((0.04, 0.4, 0.05), bc + Vector((-0.12 + k * 0.12, 0, 0.1)), K["FLESH"], rot=(0, 0, 0.3 * (k - 1)), bevel=0))
    for k in range(7):                                                           # cráneo roto alrededor
        a = k / 7 * 2 * math.pi
        P[H].append(box((0.12, 0.12, 0.08), bc + Vector((math.cos(a) * 0.32, math.sin(a) * 0.32, 0.02)), K["BONE"],
                        rot=(0, 0, a), bevel=0.01))
    # costura que cruza la cabeza de lado a lado por arriba (lado derecho, -X)
    stitches(P, H, HEAD + Vector((-0.63, 0.15, 0.25)), HEAD + Vector((-0.35, 0.05, 0.62)), (-1, 0, 1), K["STITCH"], n=4)
    stitches(P, H, HEAD + Vector((-0.35, 0.05, 0.62)), HEAD + Vector((-0.05, -0.25, 0.62)), (0, 0, 1), K["STITCH"], n=3)
    # manchas podridas a los costados y atrás (el frente queda liso: SIN CARA)
    for sx in (-1, 1):
        for _ in range(3):
            a = math.pi / 2 - sx * (math.pi / 2 - rng.uniform(0.15, 1.3))           # siempre hacia atrás (y > 0)
            p = HEAD + Vector((math.cos(a) * 0.62, math.sin(a) * 0.62, rng.uniform(-0.35, 0.3)))
            P[H].append(sphere(rng.uniform(0.08, 0.14), p, K["ROT"], subdiv=1, scale=(1, 1, 0.8)))
    # sangre que chorrea por atrás desde el cerebro
    for x, ln in ((0.1, 0.6), (0.3, 0.4), (0.45, 0.75)):
        y = math.sqrt(max(0.0, 0.62 ** 2 - x ** 2)) + E
        P[H].append(box((0.07, 0.04, ln), HEAD + Vector((x, y, 0.5 - ln / 2)), K["BLOOD"], rot=(0, 0, -math.atan2(x, y)), bevel=0))
    # mordida en la parte de atrás con hueso
    P[H].append(sphere(0.15, HEAD + Vector((-0.35, 0.5, -0.2)), K["FLESH"], subdiv=1, scale=(1, 0.5, 1)))
    P[H].append(box((0.1, 0.06, 0.1), HEAD + Vector((-0.36, 0.56, -0.2)), K["BONE"], rot=(0, 0, 0.6), bevel=0))


def arm(P, K, rng, name, sx):
    """Brazo R6 (1x1x2) colgando; después se gira hacia adelante. sx: lado (-1 derecha, +1 izquierda)."""
    A = name
    x = 1.5 * sx
    P[A].append(box((1, 1, 2), (x, 0, 3), K["SKIN"], bevel=0.03))
    # manga corta rota
    P[A].append(box((1.06, 1.06, 0.7), (x, 0, 3.66), K["SHIRT"], bevel=0.03))
    jagged_ring(P, A, x, 0, 3.32, 1.06, 1.06, K["SHIRT"], rng, n=3, size=0.15)
    # uñas/punta sucia del brazo (sin manos, estilo R6)
    P[A].append(box((1.02, 1.02, 0.12), (x, 0, 2.06), K["ROT"], bevel=0.02))
    for k in range(4):
        P[A].append(cone(0.05, 0.12, Vector((x - 0.36 + k * 0.24, -0.38, 1.97)), K["BONE"], rot=(math.pi, 0, 0), verts=4))
    if sx < 0:
        # brazo derecho: vendas con sangre
        for k, z in enumerate((2.95, 2.68, 2.42)):
            P[A].append(box((1.07, 1.07, 0.16), (x, 0, z), K["BANDAGE"], rot=(0.06 * (k - 1), 0.08 * (1 - k), 0), bevel=0.02))
        P[A].append(box((0.06, 0.25, 0.55), (x - 0.54, -0.25, 2.25), K["BANDAGE"], rot=(0.25, 0, 0), bevel=0))  # punta suelta
        front(P, A, (0.3, 0.25), x + 0.1, 2.7, -0.54, K["BLOOD"], rot=0.3)
        side(P, A, (0.3, 0.22), x - 0.54, 0.1, 2.82, K["BLOOD2"])
    else:
        # brazo izquierdo: mordida con hueso y venas podridas
        front(P, A, (0.5, 0.42), x, 2.7, -0.5, K["FLESH"])
        P[A].append(box((0.12, 0.06, 0.45), (x + 0.05, -0.55, 2.7), K["BONE"], bevel=0.01))
        for k in range(6):                                                       # marcas de dientes
            a = k / 6 * 2 * math.pi
            front(P, A, (0.08, 0.08), x + math.cos(a) * 0.33, 2.7 + math.sin(a) * 0.28, -0.5, K["BLOOD2"])
        for _ in range(4):
            side(P, A, (rng.uniform(0.15, 0.3), rng.uniform(0.15, 0.35)), x + 0.5, rng.uniform(-0.3, 0.3), rng.uniform(2.3, 3.1), K["ROT"],
                 rot=rng.uniform(0, 1))
    for _ in range(3):                                                           # sangre seca por todos lados
        front(P, A, (rng.uniform(0.1, 0.2), rng.uniform(0.1, 0.2)), x + rng.uniform(-0.3, 0.3), rng.uniform(2.2, 3.1), 0.5,
              K["BLOOD2"], rot=rng.uniform(0, 3))


def leg(P, K, rng, name, sx):
    G = name
    x = 0.5 * sx
    P[G].append(box((1, 1, 2), (x, 0, 1), K["PANTS"], bevel=0.03))
    # zapatilla: cuerpo, suela, puntera y cordones
    P[G].append(box((1.06, 1.16, 0.42), (x, -0.06, 0.25), K["SHOE"], bevel=0.05))
    P[G].append(box((1.08, 1.2, 0.1), (x, -0.07, 0.05), K["SOLE"], bevel=0.02))
    P[G].append(box((1.0, 0.25, 0.18), (x, -0.6, 0.15), K["SOLE"], bevel=0.04))
    for k in range(3):
        P[G].append(box((0.5, 0.05, 0.05), (x, -0.62 - E, 0.5 - k * 0.1), K["LACE"], rot=(0, 0.25 * (1 - 2 * (k % 2)), 0), bevel=0))
    if sx > 0:
        # pierna izquierda: pantalón roto en la rodilla, rodilla y canilla a la vista
        front(P, G, (0.7, 0.75), x, 1.0, -0.5, K["SKIN"])
        P[G].append(sphere(0.16, (x, -0.52, 1.05), K["BONE"], subdiv=1, scale=(1.2, 0.5, 1)))   # rótula
        front(P, G, (0.3, 0.2), x - 0.15, 0.8, -0.53, K["FLESH"], rot=0.4)
        for k in range(5):                                                       # hilachas
            P[G].append(cone(0.08, 0.17, Vector((x - 0.3 + k * 0.15, -0.53, 1.42)), K["PANTS"], rot=(math.pi, 0, 0), verts=3))
            P[G].append(cone(0.08, 0.15, Vector((x - 0.3 + k * 0.15, -0.53, 0.6)), K["PANTS"], verts=3))
    else:
        # pierna derecha: parche de jean cosido y botamanga rota
        front(P, G, (0.45, 0.42), x + 0.05, 1.35, -0.5, K["PATCH"], rot=-0.1)
        for z in (1.12, 1.58):
            stitches(P, G, (x - 0.2, -0.54, z), (x + 0.28, -0.54, z - 0.05), (0, -1, 0), K["STITCH"], n=4, w=0.025, cross=0.08)
        jagged_ring(P, G, x, 0, 0.55, 1.0, 1.0, K["PANTS"], rng, n=3, size=0.14)
    for _ in range(3):
        front(P, G, (rng.uniform(0.1, 0.25), rng.uniform(0.1, 0.25)), x + rng.uniform(-0.3, 0.3), rng.uniform(0.7, 1.8),
              rng.choice((-0.5, 0.5)), K["BLOOD2"], rot=rng.uniform(0, 3))


def build():
    rng = random.Random(7)
    K = mats()
    P = {k: [] for k in PIV}
    torso(P, K, rng)
    head(P, K, rng)
    arm(P, K, rng, "RightArm", -1)
    arm(P, K, rng, "LeftArm", 1)
    leg(P, K, rng, "RightLeg", -1)
    leg(P, K, rng, "LeftLeg", 1)
    objs = {k: join(v, k, PIV[k]) for k, v in P.items()}
    # pose de zombi: brazos estirados hacia adelante (uno un poco más bajo) y cabeza ladeada
    L.transform([objs["RightArm"]], Matrix.Rotation(-math.radians(84), 4, "X"), PIV["RightArm"])
    L.transform([objs["LeftArm"]], Matrix.Rotation(-math.radians(95), 4, "X"), PIV["LeftArm"])
    L.transform([objs["Head"]], Matrix.Rotation(math.radians(9), 4, "Y") @ Matrix.Rotation(math.radians(6), 4, "X"), PIV["Head"])
    return list(objs.values())


VIEWS = {"vista_frente": (-5.0, -10.0, 1.6), "vista_costado": (10.5, -3.0, 1.5), "vista_atras": (-6.0, 8.5, 2.5)}

if __name__ == "__main__":
    L.reset()
    objs = build()
    out = os.path.join(HERE, NAME)
    for o in objs:
        print(o.name, L.count_tris([o]))
    L.export(out, NAME, objs)
    if not os.environ.get("NO_RENDER"):
        L.render(out, target=(0, -0.6, 2.7), dist=0.95, views=VIEWS)
    print("LISTO", NAME)
