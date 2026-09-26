"""Puestos del juego como modelos sueltos: Palanca (con 5 pedestales), Tienda, Equipamientos, Diario y Mejoras.

Todos miran hacia -Y (el jugador se para del lado -Y). Cada uno se exporta a
modelos/puestos/<nombre>/ y una copia .glb a modelos/roblox/.

Uso: python puestos.py [nombre ...]   (sin nombres arma los 5)
"""
import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))
import lib_torretas as L  # noqa: E402
import bpy  # noqa: E402
from lib_torretas import Vector, box, cone, cyl, join, math, rod, sphere, strut, torus  # noqa: E402


def material(name, *args, **kw):
    """Reusa el material si ya existe (así el mapa no duplica materiales por isla)."""
    return bpy.data.materials.get(name) or L.material(name, *args, **kw)

HERE = os.path.dirname(os.path.abspath(__file__))


def mats():
    return {
        "STONE": material("Piedra", (0.55, 0.55, 0.57), 0.0, 0.8),
        "STONE_D": material("Piedra_Oscura", (0.28, 0.28, 0.3), 0.0, 0.8),
        "DARK": material("Metal_Oscuro", (0.07, 0.075, 0.085), 0.6, 0.5),
        "METAL": material("Metal", (0.35, 0.37, 0.4), 0.8, 0.35),
        "WOOD": material("Madera", (0.45, 0.27, 0.13), 0.0, 0.7),
        "WOOD_D": material("Madera_Oscura", (0.25, 0.14, 0.07), 0.0, 0.7),
        "BRICK": material("Ladrillo", (0.6, 0.33, 0.27), 0.0, 0.8),
        "BRICK_D": material("Ladrillo_Oscuro", (0.45, 0.24, 0.2), 0.0, 0.8),
        "GOLD": material("Oro", (1.0, 0.72, 0.2), 1.0, 0.25),
        "WHITE": material("Blanco", (0.95, 0.95, 0.97), 0.0, 0.6),
        "BLACK": material("Negro", (0.02, 0.02, 0.02), 0.0, 0.5),
        "SKIN": material("Piel_Noob", (1.0, 0.82, 0.1), 0.0, 0.6),
        "BLUE_NEON": material("Neon_Azul", (0.2, 0.7, 1.0), emission=(0.2, 0.65, 1.0), strength=5),
        "RED_NEON": material("Neon_Rojo", (1.0, 0.25, 0.3), emission=(1.0, 0.15, 0.2), strength=4),
        "GREEN_NEON": material("Neon_Verde", (0.3, 1.0, 0.4), emission=(0.2, 1.0, 0.3), strength=3),
        "LAMP": material("Farol", (1.0, 0.85, 0.5), emission=(1.0, 0.75, 0.35), strength=6),
    }


def noob(c, shirt, K):
    """Vendedor estilo Roblox detrás del mostrador."""
    P = []
    pants = material("Pantalon", (0.1, 0.25, 0.1), 0.0, 0.6)
    for s in (-1, 1):
        P.append(box((0.45, 0.45, 1.0), c + Vector((s * 0.25, 0, 0.5)), pants, bevel=0.03))
        P.append(box((0.42, 0.45, 1.0), c + Vector((s * 0.72, 0, 1.55)), K["SKIN"], bevel=0.03))
    P.append(box((1.0, 0.5, 1.0), c + Vector((0, 0, 1.55)), shirt, bevel=0.03))
    P.append(box((0.62, 0.62, 0.62), c + Vector((0, 0, 2.4)), K["SKIN"], bevel=0.12))
    for s in (-1, 1):
        P.append(box((0.08, 0.04, 0.14), c + Vector((s * 0.13, -0.32, 2.47)), K["BLACK"], bevel=0))
    P.append(box((0.26, 0.04, 0.05), c + Vector((0, -0.32, 2.28)), K["BLACK"], bevel=0))
    return P


def stall(K, awning, counter, counter_d, sign_mat, shirt):
    """Puesto con techo a rayas. Devuelve (partes, cartel, vendedor)."""
    W, Dp = 6.4, 4.4
    P = [box((W + 0.6, Dp + 0.6, 0.2), Vector((0, 0, 0.1)), K["WOOD_D"], bevel=0.04)]
    for k in range(7):                                                          # tablas del piso
        P.append(box((W + 0.5, 0.06, 0.02), Vector((0, -Dp / 2 + k * Dp / 6, 0.21)), K["WOOD"], bevel=0))
    fy = -Dp / 2 + 0.55
    P.append(box((W, 1.1, 1.3), Vector((0, fy, 0.85)), counter, bevel=0.05))      # mostrador
    for i in range(6):                                                          # ladrillos con relieve
        for j in range(2):
            P.append(box((0.8, 0.08, 0.4), Vector((-W / 2 + 0.55 + i * 1.06, fy - 0.57, 0.55 + j * 0.55)), counter_d,
                         bevel=0.03))
    P.append(box((W + 0.3, 1.35, 0.15), Vector((0, fy, 1.57)), K["WOOD"], bevel=0.03))
    P.append(box((W, 0.3, 3.3), Vector((0, Dp / 2 - 0.15, 1.85)), K["WOOD"], bevel=0.03))   # pared de atrás
    for z in (2.0, 2.9):
        P.append(box((W - 0.6, 0.6, 0.1), Vector((0, Dp / 2 - 0.5, z)), K["WOOD_D"], bevel=0.02))
    for s in (-1, 1):
        P.append(box((0.3, Dp, 1.3), Vector((s * W / 2, 0, 0.85)), counter, bevel=0.04))
        for y in (-1, 1):
            P.append(box((0.35, 0.35, 4.0), Vector((s * (W / 2 + 0.05), y * (Dp / 2 - 0.1), 2.1)), K["WOOD_D"], bevel=0.04))
        P.append(strut(Vector((s * W / 2, -Dp / 2, 3.2)), Vector((s * W / 2, -Dp / 2 + 1.0, 4.0)), 0.18, 0.18,
                       K["WOOD_D"], bevel=0))
    P.append(box((W + 0.4, 0.3, 0.3), Vector((0, -Dp / 2 + 0.1, 3.95)), K["WOOD_D"], bevel=0.03))
    n = 7
    for k in range(n):                                                          # techo a rayas
        m = awning[k % 2]
        x = -W / 2 - 0.3 + (k + 0.5) * (W + 0.6) / n
        P.append(box(((W + 0.6) / n + 0.01, Dp + 1.4, 0.16), Vector((x, -0.35, 4.25)), m, rot=(0.2, 0, 0), bevel=0.02))
        P.append(box(((W + 0.6) / n - 0.05, 0.12, 0.45), Vector((x, -(Dp + 1.4) / 2 - 0.35, 3.6)), m, bevel=0.03))
    sign = box((W - 1.2, 0.25, 1.3), Vector((0, 0.9, 5.35)), sign_mat, bevel=0.06)
    for s in (-1, 1):
        P.append(box((0.2, 0.2, 1.2), Vector((s * (W / 2 - 1.0), 1.0, 4.7)), K["WOOD_D"], bevel=0))
    P.append(box((W - 0.9, 0.3, 0.18), Vector((0, 0.9, 6.05)), K["GOLD"], bevel=0.03))
    P.append(box((W - 0.9, 0.3, 0.18), Vector((0, 0.9, 4.65)), K["GOLD"], bevel=0.03))
    vendor = noob(Vector((0, 0.5, 0.2)), shirt, K)
    return P, sign, vendor


def lamp_post(c, K, side=1):
    """Farol colgante de madera como el de la imagen."""
    return [box((0.35, 0.35, 4.2), c + Vector((0, 0, 2.1)), K["WOOD"], bevel=0.04),
            box((1.3, 0.25, 0.25), c + Vector((side * 0.55, 0, 4.1)), K["WOOD"], bevel=0.03),
            strut(c + Vector((0, 0, 3.3)), c + Vector((side * 0.7, 0, 4.0)), 0.15, 0.15, K["WOOD_D"], bevel=0),
            rod(c + Vector((side * 1.05, 0, 4.0)), c + Vector((side * 1.05, 0, 3.4)), 0.02, K["BLACK"], verts=4),
            box((0.4, 0.4, 0.55), c + Vector((side * 1.05, 0, 3.1)), K["LAMP"], bevel=0.05),
            cone(0.35, 0.25, c + Vector((side * 1.05, 0, 3.5)), K["DARK"], verts=4)]


# ------------------------------------------------------------------ 1. palanca + 5 pedestales
def build_palanca():
    K = mats()
    base = [box((25, 12, 0.3), Vector((0, 0, 0.15)), K["STONE"], bevel=0.05)]
    for i in range(12):                                                         # baldosas
        for j in range(6):
            if (i + j) % 2:
                base.append(box((2.0, 1.9, 0.02), Vector((-11 + i * 2.0, -4.75 + j * 1.9, 0.31)), K["STONE_D"], bevel=0))
    for s in (-1, 1):                                                           # vitrinas rojas
        c = Vector((s * 11.0, 3.2, 0.3))
        for sx in (-1, 1):
            for sy in (-1, 1):
                base.append(box((0.45, 0.45, 6.6), c + Vector((sx * 1.3, sy * 0.95, 3.3)), K["DARK"], bevel=0.05))
        base.append(box((2.3, 1.6, 5.6), c + Vector((0, 0, 3.3)),
                        material("Vitrina", (1.0, 0.35, 0.35), 0.0, 0.1, emission=(1.0, 0.25, 0.25), strength=1.2), bevel=0))
        for z, h in ((0.3, 0.6), (6.4, 0.7)):
            base.append(box((3.2, 2.4, h), c + Vector((0, 0, z)), K["DARK"], bevel=0.08))
            base.append(box((3.25, 0.05, 0.12), c + Vector((0, -1.23, z)), K["RED_NEON"], bevel=0))
        for sx in (-1, 1):
            base.append(box((0.08, 0.05, 5.4), c + Vector((sx * 1.3, -1.2, 3.3)), K["RED_NEON"], bevel=0))
    for s in (-1, 1):
        base += lamp_post(Vector((s * 12.0, -5.2, 0.3)), K, side=-s)
    objs = [join(base, "Zona", (0, 0, 0))]
    for k in range(5):                                                          # pedestales (acá aparecen las torretas)
        c = Vector(((k - 2) * 4.2, 2.8, 0.3))
        P = [box((3.3, 3.3, 0.95), c + Vector((0, 0, 0.47)), K["DARK"], bevel=0.12),
             box((2.8, 2.8, 0.1), c + Vector((0, 0, 1.0)), K["METAL"], bevel=0.02),
             box((1.9, 0.06, 0.26), c + Vector((0, -1.67, 0.5)), K["BLUE_NEON"], bevel=0),
             cyl(0.95, 0.04, c + Vector((0, 0, 1.07)), K["BLUE_NEON"], verts=20, bevel=0),
             torus(1.15, 0.05, c + Vector((0, 0, 1.08)), K["DARK"], seg=20, minor=4)]
        for sx in (-1, 1):
            for sy in (-1, 1):
                P.append(cyl(0.12, 0.08, c + Vector((sx * 1.25, sy * 1.25, 1.07)), K["METAL"], verts=6, bevel=0))
        objs.append(join(P, f"Pedestal_{k + 1}", c + Vector((0, 0, 1.05))))
    cc = Vector((0, -3.3, 0.3))                                                 # consola "Rodar"
    con = [box((2.6, 1.5, 1.4), cc + Vector((0, 0, 0.7)), K["DARK"], bevel=0.1),
           box((2.2, 0.12, 0.7), cc + Vector((0, -0.3, 1.55)), K["GREEN_NEON"], rot=(-0.6, 0, 0), bevel=0),
           box((2.7, 1.6, 0.12), cc + Vector((0, 0, 1.42)), K["METAL"], bevel=0.02),
           box((1.8, 0.05, 0.3), cc + Vector((0, -0.77, 0.75)), material("Cartel_Rodar", (0.9, 0.9, 0.9), 0.0, 0.5), bevel=0),
           cyl(0.3, 0.3, cc + Vector((1.45, 0, 1.0)), K["METAL"], rot=(0, math.pi / 2, 0), verts=12)]
    objs.append(join(con, "Consola", cc))
    piv = cc + Vector((1.62, 0, 1.0))                                           # brazo de la palanca (animable)
    arm = [rod(piv, piv + Vector((0, 0, 1.3)), 0.08, K["METAL"], verts=8),
           sphere(0.28, piv + Vector((0, 0, 1.4)), material("Bola_Roja", (0.9, 0.08, 0.08), 0.1, 0.3), subdiv=2)]
    objs.append(join(arm, "Palanca_Brazo", piv))
    return objs, dict(target=(0, 0.5, 1.5), dist=3.1)


# ------------------------------------------------------------------ 2. tienda
def build_tienda():
    K = mats()
    blue = material("Toldo_Azul", (0.1, 0.45, 0.95), 0.0, 0.6)
    P, sign, vendor = stall(K, (blue, K["WHITE"]), K["BRICK"], K["BRICK_D"],
                            material("Cartel_Tienda", (0.1, 0.45, 0.95), 0.0, 0.5), material("Remera_Azul", (0.1, 0.3, 0.9)))
    fy = -4.4 / 2 + 0.55
    cols = [(1, 0.2, 0.3), (0.2, 0.8, 1), (0.3, 1, 0.3), (0.8, 0.3, 1)]
    for k in range(4):                                                          # pociones en el mostrador
        m = material(f"Pocion_{k}", cols[k], 0.0, 0.1, emission=cols[k], strength=1.5)
        c = Vector((-2.2 + k * 1.45, fy, 1.65))
        P += [cyl(0.25, 0.45, c + Vector((0, 0, 0.23)), m, verts=10, bevel=0),
              cyl(0.1, 0.2, c + Vector((0, 0, 0.55)), K["WHITE"], verts=8, bevel=0),
              cyl(0.12, 0.08, c + Vector((0, 0, 0.68)), K["WOOD_D"], verts=8, bevel=0)]
    for k in range(5):                                                          # frascos en los estantes
        m = material(f"Pocion_{k % 4}", cols[k % 4], 0.0, 0.1, emission=cols[k % 4], strength=1.5)
        P.append(sphere(0.22, Vector((-2.2 + k * 1.1, 1.7, 2.3)), m, subdiv=1))
    for s in (-1, 1):                                                           # cajas al costado
        P += [box((1.0, 1.0, 1.0), Vector((s * 4.1, -1.6, 0.5)), K["WOOD"], rot=(0, 0, 0.2 * s), bevel=0.05),
              box((0.8, 0.8, 0.8), Vector((s * 4.1, -1.5, 1.4)), K["WOOD_D"], rot=(0, 0, -0.3 * s), bevel=0.05)]
    objs = [join(P, "Puesto", (0, 0, 0)), join(vendor, "Vendedor", (0, 0.5, 0)), sign]
    sign.name = sign.data.name = "Cartel"
    return objs, dict(target=(0, 0, 2.6), dist=1.3)


# ------------------------------------------------------------------ 3. equipamientos
def build_equipamientos():
    K = mats()
    orange = material("Toldo_Naranja", (1.0, 0.45, 0.05), 0.0, 0.6)
    P, sign, vendor = stall(K, (orange, material("Toldo_Negro", (0.12, 0.12, 0.13), 0.0, 0.6)), K["WOOD"], K["WOOD_D"],
                            material("Cartel_Equip", (0.3, 0.32, 0.36), 0.6, 0.4), material("Remera_Naranja", (0.95, 0.5, 0.1)))
    fy = -4.4 / 2 + 0.55
    oil = material("Lata_Aceite", (0.1, 0.1, 0.12), 0.5, 0.4)
    yel = material("Tapa_Amarilla", (1.0, 0.8, 0.05), 0.2, 0.4)
    for k in range(3):                                                          # latas de aceite
        c = Vector((-2.0 + k * 1.4, fy, 1.65))
        P += [box((0.6, 0.4, 0.75), c + Vector((0, 0, 0.38)), oil, bevel=0.05),
              box((0.62, 0.42, 0.18), c + Vector((0, 0, 0.45)), yel, bevel=0),
              cyl(0.08, 0.2, c + Vector((0.15, 0, 0.85)), yel, verts=8, bevel=0)]
    P += [box((0.9, 0.2, 0.1), Vector((2.2, fy, 1.72)), K["METAL"], rot=(0, 0, 0.4), bevel=0),     # llave inglesa
          torus(0.18, 0.06, Vector((2.62, fy + 0.17, 1.72)), K["METAL"], seg=10, minor=4)]
    gear_c = Vector((-2.2, 0.72, 5.35))                                         # engranaje en el cartel
    P += [cyl(0.45, 0.2, gear_c, K["METAL"], rot=(math.pi / 2, 0, 0), verts=12)]
    for k in range(8):
        a = k * math.pi / 4
        P.append(box((0.22, 0.2, 0.22), gear_c + Vector((math.cos(a) * 0.55, 0, math.sin(a) * 0.55)), K["METAL"],
                     rot=(0, -a, 0), bevel=0))
    for s in (-1, 1):                                                           # barriles de aceite
        for j in range(2):
            c = Vector((s * 4.2, -1.8 + j * 1.2, 0))
            P += [cyl(0.5, 1.3, c + Vector((0, 0, 0.65)), oil, verts=12, bevel=0.03),
                  torus(0.51, 0.04, c + Vector((0, 0, 0.35)), yel, seg=12, minor=4),
                  torus(0.51, 0.04, c + Vector((0, 0, 0.95)), yel, seg=12, minor=4)]
    objs = [join(P, "Puesto", (0, 0, 0)), join(vendor, "Vendedor", (0, 0.5, 0)), sign]
    sign.name = sign.data.name = "Cartel"
    return objs, dict(target=(0, 0, 2.6), dist=1.35)


# ------------------------------------------------------------------ 4. diario (recompensa)
def build_diario():
    K = mats()
    blue = material("Regalo_Azul", (0.15, 0.4, 1.0), 0.1, 0.4)
    yel = material("Moño_Amarillo", (1.0, 0.8, 0.1), 0.2, 0.35)
    base = [cyl(2.2, 0.4, Vector((0, 0, 0.2)), K["STONE_D"], verts=16, bevel=0.06),
            cyl(1.8, 0.5, Vector((0, 0, 0.65)), K["STONE"], verts=16, bevel=0.06),
            torus(1.82, 0.07, Vector((0, 0, 0.9)), K["GOLD"], seg=24, minor=4),
            cyl(1.4, 0.05, Vector((0, 0, 0.93)), K["BLUE_NEON"], verts=16, bevel=0)]
    for s in (-1, 1):                                                           # arco con cartel
        base.append(box((0.35, 0.35, 4.4), Vector((s * 2.5, 1.2, 2.2)), K["WOOD"], bevel=0.04))
    base.append(box((5.4, 0.3, 0.3), Vector((0, 1.2, 4.3)), K["WOOD_D"], bevel=0.03))
    sign = box((4.2, 0.2, 1.1), Vector((0, 1.05, 3.55)), material("Cartel_Diario", (1.0, 0.82, 0.35), 0.3, 0.4), bevel=0.05)
    sign.name = sign.data.name = "Cartel"
    heart = material("Corazon", (1.0, 0.2, 0.35), emission=(1.0, 0.15, 0.3), strength=2)
    for s, m in ((-1, heart), (1, material("Estrella", (1.0, 0.85, 0.2), emission=(1.0, 0.8, 0.1), strength=3))):
        c = Vector((s * 2.5, 1.2, 4.9))                                         # corazón (like) y estrella (grupo)
        if m is heart:
            base += [sphere(0.3, c + Vector((-0.18, 0, 0.1)), m, subdiv=1), sphere(0.3, c + Vector((0.18, 0, 0.1)), m, subdiv=1),
                     cone(0.45, 0.5, c + Vector((0, 0, -0.2)), m, rot=(math.pi, 0, 0), verts=8)]
        else:
            base += [cone(0.5, 0.25, c, m, rot=(math.pi / 2, 0, 0), verts=5)]
    gift = [box((1.7, 1.7, 1.5), Vector((0, 0, 1.75)), blue, bevel=0.06),
            box((1.8, 1.8, 0.35), Vector((0, 0, 2.55)), blue, bevel=0.06),
            box((0.3, 1.82, 1.85), Vector((0, 0, 1.95)), yel, bevel=0),
            box((1.82, 0.3, 1.85), Vector((0, 0, 1.95)), yel, bevel=0)]
    for s in (-1, 1):
        gift.append(sphere(0.38, Vector((s * 0.35, 0, 2.95)), yel, subdiv=1, scale=(1.2, 0.5, 0.8)))
    gift.append(sphere(0.18, Vector((0, 0, 2.9)), yel, subdiv=1))
    for k in range(4):                                                          # brillitos
        a = k * math.pi / 2 + 0.4
        gift.append(sphere(0.1, Vector((math.cos(a) * 1.4, math.sin(a) * 1.4, 2.6 + (k % 2) * 0.5)), K["GOLD"], subdiv=1))
    objs = [join(base, "Base", (0, 0, 0)), join(gift, "Regalo", (0, 0, 1.0)), sign]
    return objs, dict(target=(0, 0.3, 2.5), dist=1.05)


# ------------------------------------------------------------------ 5. cartel de mejoras
def build_mejoras():
    K = mats()
    frame = []
    for s in (-1, 1):
        frame.append(box((0.7, 0.7, 4.2), Vector((s * 3.6, 0, 2.1)), K["STONE_D"], bevel=0.08))
    frame.append(box((7.6, 0.7, 5.0), Vector((0, 0, 3.4)), K["STONE"], bevel=0.12))
    for i in range(10):                                                         # bloques con relieve en el borde
        for z in (1.05, 5.75):
            frame.append(box((0.6, 0.12, 0.35), Vector((-3.3 + i * 0.73, -0.38, z - 0.1 if z > 3 else z + 0.1)), K["STONE_D"],
                               bevel=0.03))
    frame.append(box((2.2, 0.35, 0.25), Vector((0, -0.2, 6.0)), K["LAMP"], bevel=0.05))
    green = box((6.2, 0.1, 1.7), Vector((0, -0.38, 4.35)), material("Panel_Suerte", (0.3, 0.75, 0.2), 0.0, 0.5), bevel=0.05)
    green.name = green.data.name = "Panel_Suerte"
    red = box((6.2, 0.1, 1.7), Vector((0, -0.38, 2.45)), material("Panel_Giros", (0.85, 0.15, 0.2), 0.0, 0.5), bevel=0.05)
    red.name = red.data.name = "Panel_Giros"
    clover = material("Trebol", (0.2, 0.85, 0.2), 0.0, 0.4)
    icons = []
    cc = Vector((-2.4, -0.55, 4.35))                                            # trébol (suerte)
    for k in range(4):
        a = k * math.pi / 2 + math.pi / 4
        icons.append(sphere(0.3, cc + Vector((math.cos(a) * 0.3, 0, math.sin(a) * 0.3)), clover, subdiv=1, scale=(1, 0.4, 1)))
    icons.append(strut(cc, cc + Vector((0.25, 0, -0.6)), 0.08, 0.08, clover, bevel=0))
    dc = Vector((-2.4, -0.7, 2.45))                                             # dado (giros)
    icons.append(box((0.9, 0.9, 0.9), dc, K["WHITE"], rot=(0.3, 0, 0.4), bevel=0.12))
    for dx, dz in ((-0.2, 0.2), (0, 0), (0.2, -0.2)):
        icons.append(sphere(0.07, dc + Vector((dx, -0.47, dz)), K["BLACK"], subdiv=1))
    for panel_z in (4.35, 2.45):                                                # botón "MÁXIMO"
        icons.append(box((1.3, 0.12, 0.45), Vector((2.2, -0.45, panel_z - 0.35)), K["STONE"], bevel=0.08))
    objs = [join(frame, "Marco", (0, 0, 0)), join(icons, "Iconos", (0, 0, 0)), green, red]
    return objs, dict(target=(0, 0, 3.0), dist=1.15)


BUILDERS = {
    "puesto_palanca": build_palanca,
    "puesto_tienda": build_tienda,
    "puesto_equipamientos": build_equipamientos,
    "puesto_diario": build_diario,
    "puesto_mejoras": build_mejoras,
}


def main():
    names = [a for a in sys.argv[1:] if a in BUILDERS] or list(BUILDERS)
    for nm in names:
        _build(nm)


def _build(nm):
    L.reset()
    objs, view = BUILDERS[nm]()
    out = os.path.join(HERE, nm)
    L.export(out, nm, objs)
    if not os.environ.get("NO_RENDER"):
        L.render(out, **view)
    print("LISTO", nm)


if __name__ == "__main__":
    main()
