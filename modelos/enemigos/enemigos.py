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
             no_legs=False, hunch=0.0):
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
    # brazos
    for side, name in ((-1, "LeftArm"), (1, "RightArm")):
        sp = piv[name]
        if arms == "forward":
            tip = sp + Vector((0.05 * side * s, -1.9 * s, -0.25 * s + rng.uniform(-0.15, 0.15) * s))
        elif arms == "up":
            tip = sp + Vector((0.4 * side * s, -0.3 * s, 1.8 * s))
        else:
            tip = sp + Vector((0.15 * side * s, 0, -1.9 * s))
        mid = sp.lerp(tip, 0.5)
        piv[name + "_mid"], piv[name + "_tip"] = mid, tip
        P[name].append(strut(sp, mid, 0.95 * w * s, 0.95 * w * s, shirt, bevel=0.06 * s))
        P[name].append(strut(mid, tip, 0.85 * w * s, 0.85 * w * s, skin, bevel=0.06 * s))
        d = (tip - sp).normalized()
        for k in range(3):                                                      # garras
            off = Vector(((-0.25 + k * 0.25) * s, 0, 0)) if arms != "down" else Vector(((-0.25 + k * 0.25) * s, -0.3 * s, 0))
            P[name].append(cone(0.08 * s, 0.35 * s, tip + d * 0.5 * s + off, K["TEETH"], rot=d, verts=4))
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
def e_basico():
    K = base_mats()
    P, piv = humanoid(mat("Piel_Zombi", (0.35, 0.55, 0.25)), mat("Camisa_Azul", (0.2, 0.3, 0.55)),
                      mat("Pantalon_Marron", (0.3, 0.2, 0.12)), mat("Ojo_Rojo", (1, 0.1, 0.05), emission=(1, 0.1, 0.05), strength=4), K)
    return finish(P, piv), 1.0


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
}


def build(nm):
    L.reset()
    objs, s = BUILDERS[nm]()
    if nm == "zombi_espectral":                                                 # el fantasma flota
        for o in objs:
            o.location.z += 1.0
    out = os.path.join(HERE, nm)
    L.export(out, nm, objs)
    if not os.environ.get("NO_RENDER"):
        L.render(out, target=(0, -0.5 * s, 2.6 * s), dist=0.85 * s)
    print("LISTO", nm)


if __name__ == "__main__":
    for nm in [a for a in sys.argv[1:] if a in BUILDERS] or list(BUILDERS):
        build(nm)
