"""Enemigos HD del Tower Defense: 5 zombis orgánicos de alto detalle (< 20.000 triángulos cada uno).

    zombi_rapido_hd      encorvado para correr, ropa que flamea hacia atrás, mandíbula larga
    zombi_blindado_hd    chatarra antidisturbios soldada, casco táctico abollado, escudo roto
    zombi_berserk_hd     músculos hipertrofiados, tendones, venas, cicatrices con grapas
    zombi_radiactivo_hd  traje hazmat derretido, pústulas y cristales que brotan del cuerpo
    zombi_gigante_hd     tanque colosal con una viga de acero y concreto incrustada en la mano

La geometría sale de `malla.py` (todas las piezas son cáscaras cerradas con normales hacia
afuera) y se valida con `malla.revisar` antes de exportar: si hay mallas abiertas, normales
invertidas, caras coplanares superpuestas o más de 20.000 triángulos/vértices, no se exporta.

Cada enemigo se separa en partes con el pivote en su articulación (igual que `enemigos/`):
Head, Torso, LeftArm, RightArm, LeftLeg, RightLeg (+ Weapon en el gigante). Mira hacia -Y.

Uso:  python enemigos_hd.py [nombre ...]      (sin nombres arma los 5)
      NO_RENDER=1 solo exporta;  SOLO_REVISAR=1 solo valida y muestra los números.
"""
import json
import math
import os
import struct
import sys

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
sys.path.insert(0, os.path.join(HERE, ".."))
from malla import (P, Noise, align, along, bump, crystal, ellipsoid, rbox, revisar, ring_loop,  # noqa: E402
                   rot, seg_dist, solidify, spike, total, tube, unit)

# ------------------------------------------------------------------ materiales
# nombre: (color, metálico, rugosidad, emisión)
MATS = {
    "Piel_Rapido": ((0.17, 0.23, 0.15), 0.0, 0.6, None),
    "Camisa_Rota": ((0.035, 0.04, 0.085), 0.0, 0.9, None),
    "Pantalon": ((0.10, 0.065, 0.045), 0.0, 0.9, None),
    "Hueso": ((0.80, 0.76, 0.62), 0.0, 0.5, None),
    "Dientes": ((0.85, 0.80, 0.58), 0.0, 0.4, None),
    "Boca": ((0.20, 0.02, 0.03), 0.0, 0.5, None),
    "Garra": ((0.06, 0.05, 0.04), 0.1, 0.4, None),
    "Pelo": ((0.04, 0.04, 0.04), 0.0, 0.8, None),
    "Ojo_Amarillo": ((1.0, 0.75, 0.1), 0.0, 0.3, (1.0, 0.7, 0.05)),
    "Sangre": ((0.30, 0.02, 0.02), 0.0, 0.35, None),
    # blindado
    "Piel_Blindado": ((0.16, 0.20, 0.14), 0.0, 0.6, None),
    "Tela_Tactica": ((0.035, 0.04, 0.045), 0.0, 0.9, None),
    "Blindaje": ((0.11, 0.12, 0.14), 0.6, 0.45, None),
    "Oxido": ((0.28, 0.12, 0.05), 0.3, 0.8, None),
    "Soldadura": ((0.32, 0.28, 0.22), 0.7, 0.5, None),
    "Tornillo": ((0.40, 0.40, 0.42), 0.9, 0.3, None),
    "Vidrio": ((0.06, 0.10, 0.12), 0.2, 0.1, None),
    "Advertencia": ((0.75, 0.55, 0.04), 0.1, 0.5, None),
    "Correa": ((0.02, 0.02, 0.02), 0.0, 0.7, None),
    "Bota": ((0.03, 0.028, 0.025), 0.0, 0.6, None),
    "Ojo_Rojo": ((1.0, 0.1, 0.05), 0.0, 0.3, (1.0, 0.08, 0.03)),
    # berserk
    "Piel_Berserk": ((0.13, 0.15, 0.11), 0.0, 0.55, None),
    "Vena": ((0.32, 0.03, 0.16), 0.0, 0.4, None),
    "Musculo": ((0.40, 0.04, 0.04), 0.0, 0.35, None),
    "Cicatriz": ((0.50, 0.24, 0.22), 0.0, 0.5, None),
    "Pantalon_Berserk": ((0.06, 0.06, 0.08), 0.0, 0.9, None),
    "Cadena": ((0.25, 0.25, 0.27), 0.9, 0.35, None),
    "Madera_Soga": ((0.30, 0.22, 0.12), 0.0, 0.9, None),
    # radiactivo
    "Hazmat": ((0.45, 0.32, 0.025), 0.0, 0.55, None),
    "Hazmat_Quemado": ((0.18, 0.13, 0.03), 0.0, 0.7, None),
    "Goma": ((0.03, 0.03, 0.03), 0.0, 0.6, None),
    "Piel_Toxica": ((0.12, 0.16, 0.08), 0.0, 0.5, None),
    "Tumor": ((0.22, 0.2, 0.08), 0.0, 0.45, None),
    "Pustula": ((0.45, 1.0, 0.15), 0.0, 0.3, (0.4, 1.0, 0.1)),
    "Cristal": ((0.2, 1.0, 0.45), 0.1, 0.1, (0.15, 1.0, 0.35)),
    "Lente": ((0.05, 0.12, 0.08), 0.3, 0.1, None),
    "Tanque": ((0.2, 0.22, 0.2), 0.7, 0.4, None),
    # gigante
    "Piel_Gigante": ((0.14, 0.15, 0.13), 0.0, 0.55, None),
    "Pantalon_Gigante": ((0.07, 0.05, 0.035), 0.0, 0.9, None),
    "Acero": ((0.24, 0.2, 0.18), 0.75, 0.5, None),
    "Concreto": ((0.33, 0.32, 0.3), 0.0, 0.95, None),
    "Varilla": ((0.22, 0.09, 0.04), 0.6, 0.6, None),
}


class Enemigo:
    def __init__(self, nombre, pivotes):
        self.nombre = nombre
        self.piv = {k: np.asarray(v, float) for k, v in pivotes.items()}
        self.partes = {k: [] for k in self.piv}

    def add(self, parte, *shells):
        for s in shells:
            if isinstance(s, (list, tuple)):
                self.add(parte, *s)
            else:
                self.partes[parte].append(s)

    def mover(self, partes, d):
        for p in partes:
            self.piv[p] = self.piv[p] + d
            for sh in self.partes[p]:
                sh.V = sh.V + d

    def todas(self):
        return [s for v in self.partes.values() for s in v]


# ------------------------------------------------------------------ ayudas de anatomía
def dedos(base, d, w, n, largo, r, piel, garra, curva=(0, 0, -0.04), abiertos=0.35):
    """Dedos con garra desde `base`, en dirección d, repartidos sobre el vector w."""
    out = []
    for i in range(n):
        o = (i - (n - 1) / 2) / max(n - 1, 1)
        dd = unit(d + w * o * abiertos)
        b = base + w * o * r * 2.6 * (n - 1) / 2
        p1, p2 = b + dd * largo * 0.45, b + dd * largo * 0.85 + np.asarray(curva)
        out.append(tube([b, p1, p2], [r, r * 0.9, r * 0.8], piel, sides=6, capseg=1))
        out.append(spike(p2, p2 + unit(p2 - p1) * largo * 0.45 + np.asarray(curva) * 1.5, r * 0.75, garra, sides=5))
    return out


def dientes(puntos, direcciones, largos, r, mat):
    return [spike(p, p + unit(d) * L, r, mat, sides=5) for p, d, L in zip(puntos, direcciones, largos)]


def cinta(pts, anchos, mat, grosor=0.2, up=(0, 0, 1), onda=0.05, fase=0.0):
    """Jirón de tela plano que sigue una curva y ondula (flamea al correr)."""
    pts = np.asarray(pts, float)
    t = np.linspace(0, 1, 9)
    idx = t * (len(pts) - 1)
    lo = np.minimum(idx.astype(int), len(pts) - 2)
    f = (idx - lo)[:, None]
    fino = pts[lo] * (1 - f) + pts[lo + 1] * f
    fino[:, 2] += onda * np.sin(t * 2 * math.pi * 1.3 + fase) * t
    an = np.interp(idx, np.arange(len(anchos)), anchos) * 1.5
    return tube(fino, an, mat, sides=6, caps=("flat", "point"), aspect=(grosor * 0.6, 1), up=up, point=1.2)


def domo(radii, mat, c, R, keep, grosor, n=8, disp=None):
    """Placa curva con espesor recortada de un elipsoide (hombreras, casco, rodilleras, visor)."""
    e = ellipsoid(radii, mat, (0, 0, 0), None, n=n, disp=disp)
    s = solidify(e, lambda Cc, sh: keep(sh.U[sh.F].mean(1)), grosor)
    return s.xf(R, c)


def placa(size, mat, c, R, curva=0.0, k=(4, 1, 4), r=0.04, abolladuras=()):
    """Placa gruesa curvada hacia atrás en los bordes, con abolladuras (local: -Y es el frente)."""
    s = rbox(size, mat, r=r, k=k)
    hx = size[0] / 2
    s.deform(lambda V: V + np.outer((V[:, 0] / hx) ** 2 * curva, [0, 1, 0]))
    if abolladuras:
        s.displace(total(*[bump(p, rr, -h) for p, rr, h in abolladuras]))
    return s.xf(R, c)


def perno(p, normal, mat="Tornillo", r=0.035, h=0.04):
    return tube([np.asarray(p) - unit(normal) * h, np.asarray(p) + unit(normal) * h], r, mat, sides=6,
                caps=("flat", "flat"), smooth=False)


def cordon(pts, mat="Soldadura", r=0.03, n=24):
    """Cordón de soldadura: tubo con radio que late a lo largo de la costura."""
    pts = np.asarray(pts, float)
    t = np.linspace(0, len(pts) - 1, n)
    lo = np.minimum(t.astype(int), len(pts) - 2)
    f = (t - lo)[:, None]
    q = pts[lo] * (1 - f) + pts[lo + 1] * f
    rr = r * (1 + 0.35 * np.cos(np.arange(n) * math.pi))
    return tube(q, rr, mat, sides=6)


def marco(d):
    """Rotación que pone el -Y local (el frente) mirando hacia d, con Z lo más arriba posible."""
    d = unit(d)
    right = unit(np.cross([0, 0, 1], d))
    back = -d
    return np.column_stack([right, back, np.cross(right, back)])


def perp(d):
    d = unit(d)
    u1 = unit(np.cross(d, [0, 0, 1] if abs(d[2]) < 0.9 else [1, 0, 0]))
    return u1, np.cross(d, u1)


def por_superficie(a, b, radio, ang, mat, r=0.028, onda=0.35, n=10, fase=0.0, fuera=0.35, t0=0.08, t1=0.92):
    """Vena/tendón que recorre la superficie de un músculo estirado entre a y b (elipsoide `along`)."""
    a, b = np.asarray(a, float), np.asarray(b, float)
    d = b - a
    u1, u2 = perp(d)
    rx, ry = (radio, radio) if np.isscalar(radio) else radio
    pts = []
    for t in np.linspace(t0, t1, n):
        th = ang + onda * math.sin(t * 9 + fase)
        k = math.sqrt(max(0.0, 1 - (2 * t - 1) ** 2))
        pts.append(a + d * t + (u1 * math.cos(th) * rx + u2 * math.sin(th) * ry) * k + unit(
            u1 * math.cos(th) + u2 * math.sin(th)) * r * fuera)
    return tube(pts, [r * 0.6] + [r] * (n - 2) + [r * 0.6], mat, sides=5, capseg=1)


def puno(d, c, piel, hueso="Hueso", s=1.0):
    """Puño cerrado mirando hacia d, centrado en c."""
    R = marco(d)
    L = lambda p: c + R @ (np.asarray(p, float) * s)  # noqa: E731
    out = [rbox(np.array([0.34, 0.32, 0.34]) * s, piel, c, R, r=0.08 * s)]
    for i, x in enumerate((-0.125, -0.042, 0.042, 0.125)):
        out.append(rbox(np.array([0.078, 0.15, 0.13]) * s, piel, L((x, -0.2, 0.07 - 0.012 * i)), R @ rot(-8), r=0.035 * s))
        out.append(ellipsoid(np.array([0.032, 0.03, 0.022]) * s, hueso, L((x, -0.27, 0.1 - 0.012 * i)), R, n=2))
    out.append(rbox(np.array([0.32, 0.12, 0.13]) * s, piel, L((0, -0.19, -0.085)), R @ rot(25), r=0.04 * s))
    out.append(rbox(np.array([0.1, 0.24, 0.1]) * s, piel, L((0.2, -0.1, -0.1)), R @ rot(0, 0, -25), r=0.04 * s))
    return out


def a_mano(R, c):
    return lambda p: np.asarray(c) + R @ np.asarray(p, float)


# ------------------------------------------------------------------ 1. Zombi Rápido
def zombi_rapido():
    SK, CL, PA = "Piel_Rapido", "Camisa_Rota", "Pantalon"
    nz = Noise(11, 3.2)
    # torso encorvado: pelvis -> abdomen -> caja torácica inclinada 55°
    Rc, C = rot(55), P(0, 3.0, 0.5)
    chest = a_mano(Rc, C)
    hips = P(0, 2.08, 0)
    neck = chest((0, 0.02, 0.5))
    H = neck + P(0, 0.22, 0.32)
    Rh = rot(-12)
    head = a_mano(Rh, H)
    shL, shR = chest((0.5, 0.06, 0.26)), chest((-0.5, 0.06, 0.26))
    E = Enemigo("zombi_rapido_hd", dict(Head=neck, Torso=hips + P(0, 0.5, 0.2), LeftArm=shL, RightArm=shR,
                                        LeftLeg=P(0.26, 1.82, 0), RightLeg=P(-0.26, 1.82, 0)))

    def costillas(U):
        g = np.cos(U[:, 2] * math.pi * 4.5) ** 6
        m = np.clip(-U[:, 1] * 2.2 + 0.4, 0, 1) * (U[:, 2] > -0.75) * (U[:, 2] < 0.45)
        m *= np.clip((np.abs(U[:, 0]) - 0.1) * 8, 0, 1)
        return -0.1 * g * m + 0.03 * nz(U * 2)

    E.add("Torso",
          ellipsoid((0.6, 0.42, 0.52), SK, C, Rc, n=14, disp=costillas),
          ellipsoid((0.38, 0.28, 0.45), SK, P(0, 2.5, 0.17), rot(30), n=8,
                    disp=lambda U: -0.12 * np.clip(-U[:, 1], 0, 1) ** 2),
          ellipsoid((0.46, 0.3, 0.3), SK, hips, rot(-5), n=6),
          tube([chest((0, -0.02, 0.42)), neck + P(0, 0.12, 0.2)], [0.14, 0.11], SK, sides=10))
    # columna marcada: vértebras sobre la espalda
    for t in np.linspace(-0.8, 0.95, 8):
        p = chest((0, 0.4 * math.sqrt(max(0.05, 1 - t * t * 0.85)), t * 0.52))
        E.add("Torso", ellipsoid((0.075, 0.06, 0.05), SK, p, Rc, n=2))
    for t in (0.2, 0.55):
        E.add("Torso", ellipsoid((0.07, 0.06, 0.05), SK, P(0, 2.5, 0.17) + (rot(30) @ P(0, 0.9 * t - 0.35, -0.3)), n=2))

    # --- camisa rota (con espesor real) y jirones que flamean hacia atrás
    def keep_camisa(Cc, s):
        U = s.U[s.F].mean(1)
        tajo = (U[:, 1] < -0.2) & (U[:, 0] < 0.45 + 0.15 * nz(Cc * 6)) & (U[:, 2] > -0.55 + 0.1 * nz(Cc * 7)) & (U[:, 2] < 0.35)
        return (nz(Cc * 1.4) > -0.2) & (U[:, 2] < 0.8) & ~tajo
    E.add("Torso", solidify(ellipsoid((0.64, 0.45, 0.56), CL, C, Rc, n=11), keep_camisa, 0.035))

    def keep_faldon(Cc, s):
        U = s.U[s.F].mean(1)
        return (U[:, 2] > -0.25 + 0.35 * nz(Cc * 2.5)) & (nz(Cc * 3 + 5) > -0.55)
    E.add("Torso", solidify(ellipsoid((0.45, 0.35, 0.5), CL, P(0, 2.55, 0.15), rot(30), n=8), keep_faldon, 0.03))
    for i, x in enumerate((-0.32, -0.12, 0.08, 0.3)):
        b = P(x, 2.42 + 0.05 * (i % 2), -0.12)
        E.add("Torso", cinta([b, b + P(0.05 * x, 0.1, -0.35), b + P(0.12 * x, 0.02, -0.75 - 0.1 * (i % 2)),
                              b + P(0.2 * x, 0.14, -1.05)], [0.09, 0.08, 0.06, 0.03], CL))
    for i, x in enumerate((-0.35, 0.0, 0.33)):          # desde los hombros
        b = chest((x, 0.42, 0.1))
        E.add("Torso", cinta([b, b + P(0, 0.12, -0.3), b + P(0.05 * x, 0.25, -0.75), b + P(0.1 * x, 0.2, -1.0)],
                             [0.08, 0.07, 0.05, 0.02], CL))

    # --- short rasgado
    E.add("Torso", solidify(ellipsoid((0.5, 0.34, 0.34), PA, hips, rot(-5), n=9),
                            lambda Cc, s: (nz(Cc * 2 + 3) > -0.5) & (s.U[s.F].mean(1)[:, 2] < 0.75), 0.03))

    # --- cabeza: cráneo alargado, cuencas, mandíbula larga caída
    socket = [unit(np.array([sx * 0.42, -0.82, 0.22])) for sx in (-1, 1)]

    def craneo(U):
        d = sum(-0.13 * np.exp(-np.sum((U - s) ** 2, 1) / 0.03) for s in socket)
        d += -0.07 * np.exp(-np.sum((U - [0.75, -0.45, -0.35]) ** 2, 1) / 0.05)    # pómulos hundidos
        d += -0.07 * np.exp(-np.sum((U - [-0.75, -0.45, -0.35]) ** 2, 1) / 0.05)
        return d + 0.025 * nz(U * 3)
    hr = np.array([0.3, 0.38, 0.3])
    E.add("Head", ellipsoid(hr, SK, H, Rh, n=12, disp=craneo))
    for s in socket:
        E.add("Head", ellipsoid((0.062, 0.05, 0.05), "Ojo_Amarillo", head(s * hr * 0.9), Rh, n=3))
    E.add("Head", tube([head((0.19, -0.33, 0.13)), head((0, -0.37, 0.16)), head((-0.19, -0.33, 0.13))],
                       [0.04, 0.05, 0.04], SK, sides=6, aspect=(1, 0.6)))
    E.add("Head", ellipsoid((0.21, 0.3, 0.1), SK, head((0, -0.3, -0.16)), Rh, n=7))            # hocico
    E.add("Head", ellipsoid((0.17, 0.3, 0.1), "Boca", head((0, -0.3, -0.27)), Rh @ rot(12), n=4))
    hinge, Rj = head((0, -0.05, -0.2)), Rh @ rot(30)
    jaw = a_mano(Rj, hinge)
    E.add("Head", ellipsoid((0.19, 0.46, 0.07), SK, jaw((0, -0.38, 0)), Rj, n=7,
                            disp=lambda U: 0.04 * nz(U * 3 + 1)))
    ang = np.radians(np.linspace(-70, 70, 9))
    up_t = [head((0.19 * math.sin(a), -0.3 - 0.27 * math.cos(a), -0.23)) for a in ang]
    E.add("Head", dientes(up_t, [Rh @ np.array([0, -0.15, -1.0])] * 9,
                          [0.08 + 0.08 * (abs(abs(a) - 0.75) < 0.2) for a in ang], 0.024, "Dientes"))
    lo_t = [jaw((0.16 * math.sin(a), -0.4 - 0.38 * math.cos(a), 0.05)) for a in ang[1:-1]]
    E.add("Head", dientes(lo_t, [Rj @ np.array([0, -0.2, 1.0])] * 7, [0.07 + 0.04 * (i % 2) for i in range(7)],
                          0.022, "Dientes"))
    for i, x in enumerate((-0.16, -0.05, 0.06, 0.17)):          # mechones hacia atrás
        b = head((x, 0.2, 0.2))
        E.add("Head", cinta([b, b + P(0.03 * x, 0.02, -0.25), b + P(0.1 * x, -0.1, -0.55 - 0.05 * i)],
                            [0.05, 0.04, 0.02], "Pelo", grosor=0.35))

    # --- brazos barridos hacia atrás (pose de sprint), finos y tensos
    for lado, sh, el, wr in ((1, shL, P(0.76, 2.8, -0.02), P(0.68, 2.45, -0.72)),
                            (-1, shR, P(-0.8, 2.95, 0.06), P(-0.76, 2.66, -0.64))):
        parte = "LeftArm" if lado > 0 else "RightArm"
        E.add(parte,
              tube([sh, (sh + el) / 2, el, el + (wr - el) * 0.35, wr], [0.13, 0.095, 0.075, 0.09, 0.058], SK, sides=10),
              along(sh + (el - sh) * 0.05, sh + (el - sh) * 0.45, 0.13, SK, n=5),
              ellipsoid((0.075, 0.075, 0.075), SK, el, n=3))
        d = unit(wr - el)
        w = unit(np.cross(d, [0, 0, 1])) * lado
        for o in (-0.05, 0.05):                                         # tendones del antebrazo
            E.add(parte, tube([el + d * 0.08 + w * o + P(0, 0.06, 0), wr - d * 0.05 + w * o * 0.6 + P(0, 0.04, 0)],
                              0.017, SK, sides=5))
        E.add(parte, along(wr - d * 0.02, wr + d * 0.16, (0.075, 0.035), SK, n=4))
        E.add(parte, dedos(wr + d * 0.14, d, w, 4, 0.2, 0.021, SK, "Garra", curva=P(0, -0.05, 0)))
        # manga rota: tela con espesor alrededor del brazo, termina en jirones
        manga = tube([sh - (el - sh) * 0.08, sh + (el - sh) * 0.3, sh + (el - sh) * 0.62], [0.2, 0.16, 0.135],
                     CL, sides=12, caps=("none", "none"))
        E.add(parte, solidify(manga, lambda Cc, s, sh=sh, el=el: (seg_dist(Cc, sh, el)[1] < 0.5 + 0.12 * nz(Cc * 4))
                              & (nz(Cc * 5 + 9) > -0.6), 0.025))
        b = sh + (el - sh) * 0.5 + P(0, 0, -0.1)
        E.add(parte, cinta([b, b + P(0.05 * lado, 0.05, -0.3), b + P(0.1 * lado, 0.15, -0.65)], [0.07, 0.05, 0.02], CL))

    # --- piernas en zancada
    for lado, hip, kn, an, pies in ((-1, P(-0.26, 1.82, 0), P(-0.28, 1.2, 0.58), P(-0.28, 0.3, 0.22),
                                     [P(-0.28, 0.12, 0.4), P(-0.28, 0.08, 0.6)]),
                                    (1, P(0.26, 1.82, -0.05), P(0.31, 1.05, -0.3), P(0.33, 0.45, -0.88),
                                     [P(0.33, 0.22, -0.78), P(0.33, 0.09, -0.62)])):
        parte = "LeftLeg" if lado > 0 else "RightLeg"
        E.add(parte,
              tube([hip, (hip + kn) / 2, kn, kn + (an - kn) * 0.3, an], [0.18, 0.14, 0.095, 0.11, 0.068], SK, sides=11),
              ellipsoid((0.085, 0.07, 0.09), SK, kn + unit(np.cross(an - hip, [1, 0, 0])) * 0.03, n=3),
              along(kn + (an - kn) * 0.12 + P(0, 0, -0.07), kn + (an - kn) * 0.6 + P(0, 0, -0.05), 0.09, SK, n=4),
              tube([an] + pies, [0.075, 0.085, 0.07], SK, sides=8, aspect=(0.8, 1.3)))
        d = unit(pies[-1] - pies[-2])
        E.add(parte, dedos(pies[-1], d, P(1, 0, 0), 3, 0.13, 0.03, SK, "Garra", curva=P(0, -0.02, 0), abiertos=0.5))
        thigh = tube([hip + (hip - kn) * 0.08, hip + (kn - hip) * 0.3, hip + (kn - hip) * 0.6],
                     [0.23, 0.2, 0.175], PA, sides=12, caps=("none", "none"))
        E.add(parte, solidify(thigh, lambda Cc, s, hip=hip, kn=kn: (seg_dist(Cc, hip, kn)[1] < 0.48 + 0.12 * nz(Cc * 4 + 2))
                              & (nz(Cc * 5) > -0.55), 0.028))
        b = hip + (kn - hip) * 0.5 + P(0, 0, -0.18)
        E.add(parte, cinta([b, b + P(0.04 * lado, 0.02, -0.3), b + P(0.08 * lado, 0.12, -0.6)], [0.07, 0.05, 0.02], PA))
    E.mover(("Torso", "Head", "LeftArm", "RightArm"), P(0, -0.2, 0))
    return E, dict(target=(0, 0, 2.1), dist=0.7)


# ------------------------------------------------------------------ 2. Zombi Blindado
def zombi_blindado():
    SK, TE, AR, RU = "Piel_Blindado", "Tela_Tactica", "Blindaje", "Oxido"
    nz = Noise(21, 3.0)
    hips, C, Hc = P(0, 2.35, 0), P(0, 3.4, 0.05), P(0, 4.62, 0.18)
    shL, shR = P(1.12, 3.95, 0.05), P(-1.12, 3.95, 0.05)
    E = Enemigo("zombi_blindado_hd", dict(Head=P(0, 4.2, 0.1), Torso=C, LeftArm=shL, RightArm=shR,
                                          LeftLeg=P(0.42, 2.3, 0), RightLeg=P(-0.42, 2.3, 0)))
    # --- cuerpo base (tela táctica) y cinturón con bolsillos
    E.add("Torso",
          ellipsoid((1.0, 0.6, 0.85), TE, C, rot(8), n=9, disp=lambda U: 0.03 * nz(U * 3)),
          ellipsoid((0.62, 0.42, 0.4), TE, hips, n=6),
          domo((0.7, 0.47, 0.52), "Correa", hips + P(0, 0.2, 0), None, lambda U: np.abs(U[:, 2]) < 0.14, 0.05, n=9))
    for x, f in ((-0.45, 0.33), (0.0, 0.46), (0.42, 0.34), (0.66, -0.05)):
        R = rot(0, 0, -math.degrees(math.atan2(x, f + 0.2)) * 0.9)
        E.add("Torso", rbox((0.24, 0.13, 0.24), TE, hips + P(x, 0.12, f), R, r=0.04))
    # --- peto abollado + placa del abdomen soldada + espaldar
    E.add("Torso",
          placa((1.85, 0.22, 1.1), AR, P(0, 3.55, 0.57), rot(8, 0, -4), curva=0.12, k=(6, 1, 5),
                abolladuras=[(P(0.35, 0.25, -0.1), 0.14, 0.07), (P(-0.4, -0.2, -0.1), 0.1, 0.05),
                             (P(0.05, -0.3, -0.1), 0.06, 0.04), (P(-0.15, 0.3, -0.1), 0.05, 0.035)]),
          placa((1.22, 0.16, 0.42), RU, P(0.06, 2.85, 0.56), rot(4, 0, 6), curva=0.15, k=(5, 1, 2)),
          placa((1.7, 0.18, 1.0), AR, P(0, 3.5, -0.56), rot(-6, 0, 3), curva=-0.14, k=(5, 1, 4)))
    for lado in (-1, 1):
        E.add("Torso", rbox((0.1, 1.05, 0.16), "Correa", P(lado * 0.98, 3.35, 0.02), rot(0, 0, 0), r=0.03),
              rbox((0.1, 1.0, 0.13), "Correa", P(lado * 0.93, 2.95, 0.02), rot(0, 0, 0), r=0.03))
        E.add("Torso", placa((0.5, 0.08, 0.5), AR if lado > 0 else RU, hips + P(lado * 0.42, -0.3, 0.42), rot(-10, 0, lado * 8),
                             curva=0.06, k=(2, 1, 2), r=0.025))
    E.add("Torso", cordon([P(-0.55, 3.07, 0.64), P(0, 3.03, 0.7), P(0.6, 3.06, 0.62)], r=0.032),
          cordon([P(-0.62, 2.9, 0.54), P(-0.62, 3.1, 0.58)], r=0.028, n=8))
    for x, z in ((-0.6, 3.95), (0.55, 3.98), (-0.62, 3.2), (0.6, 3.15)):
        E.add("Torso", perno(P(x, z, 0.66 - 0.18 * (abs(x) > 0.5) + 0.02), P(0, 0, 1)))
    E.add("Torso", ring_loop(P(0, 4.15, 0.08), (0.36, 0.32), 0.075, AR, seg=18, sides=8))
    # --- hombrera izquierda: 3 láminas superpuestas con remaches
    for i in range(3):
        R = rot(0, 22 + 12 * i, 0)
        c = shL + P(0.1 * i, 0.08 - 0.2 * i, 0)
        E.add("LeftArm", domo((0.52 - 0.05 * i, 0.5 - 0.04 * i, 0.4), AR if i != 1 else RU, c, R,
                              lambda U: U[:, 2] > -0.05, 0.055, n=7))
        for a in (-0.6, 0, 0.6):
            p = c + R @ (np.array([0.52 - 0.05 * i, 0.5 - 0.04 * i, 0.4]) * [math.cos(1.25) * math.cos(a), math.cos(1.25) * math.sin(a),
                                                                  math.sin(1.25)] * 1.02)
            E.add("LeftArm", ellipsoid((0.035, 0.035, 0.03), "Tornillo", p, R, n=2))
    E.add("LeftArm", tube([shL + rot(0, 22, 0) @ np.array([0, -0.45, 0.25]), shL + rot(0, 22, 0) @ np.array([0, 0, 0.42]),
                           shL + rot(0, 22, 0) @ np.array([0, 0.45, 0.25])], 0.045, AR, sides=6))
    # --- hombro derecho: chapa de auto oxidada soldada y atornillada
    Rp = rot(10, -32, 0)
    E.add("RightArm", placa((0.95, 0.8, 0.09), RU, shR + P(-0.08, 0.28, 0), Rp, curva=0.0, k=(3, 3, 1), r=0.03,
                            abolladuras=[(np.array([0.15, 0.1, 0.04]), 0.12, 0.04)]),
          cordon([shR + Rp @ np.array([0.36, -0.3, -0.02]), shR + Rp @ np.array([0.38, 0.3, -0.02])], r=0.028, n=12))
    Rp2 = rot(-8, -50, 6)
    E.add("RightArm", placa((0.6, 0.55, 0.07), AR, shR + P(-0.34, -0.05, 0.02), Rp2, k=(2, 2, 1), r=0.025))
    E.add("Torso", placa((1.3, 0.03, 0.14), "Advertencia", P(0, 3.72, -0.66), rot(-6, 0, 3), curva=-0.08, k=(4, 1, 1), r=0.01))
    for u, v in ((-0.28, -0.25), (-0.28, 0.25), (0.25, 0.0)):
        E.add("RightArm", perno(shR + P(-0.08, 0.28, 0) + Rp @ np.array([u, v, 0.04]), Rp @ np.array([0, 0, 1])))
    # --- brazos
    arms = {1: (shL, P(1.36, 3.0, 0.2), P(1.2, 2.3, 0.55)), -1: (shR, P(-1.4, 2.95, 0.05), P(-1.34, 2.15, 0.28))}
    for lado, (sh, el, wr) in arms.items():
        parte = "LeftArm" if lado > 0 else "RightArm"
        E.add(parte, tube([sh, (sh + el) / 2, el], [0.32, 0.29, 0.25], TE, sides=12),
              tube([el, el + (wr - el) * 0.4, wr], [0.25, 0.27, 0.2], TE if lado > 0 else SK, sides=12,
                   caps=("round", "round")))
        E.add(parte, ellipsoid((0.2, 0.2, 0.2), AR, el + P(0, 0, -0.08), n=5))
    # antebrazo izquierdo: escudo antidisturbios rajado con visor y franja
    shield_c, Rs = P(1.24, 2.7, 0.66), rot(4, 0, -6)
    bend = 0.14
    E.add("LeftArm", placa((1.0, 0.07, 1.55), "Vidrio", shield_c, Rs, curva=bend, k=(6, 1, 7), r=0.03,
                           abolladuras=[(np.array([0.2, -0.04, 0.3]), 0.08, 0.02)]))

    def sobre_escudo(size, mat, z, gap=0.006):
        s = rbox(size, mat, r=0.01, k=(4, 1, 1))
        s.deform(lambda V: V + np.outer((V[:, 0] / 0.5) ** 2 * bend, [0, 1, 0]) + [0, -0.035 - size[1] / 2 - gap, z])
        return s.xf(Rs, shield_c)
    E.add("LeftArm", sobre_escudo((0.56, 0.035, 0.24), "Tela_Tactica", 0.48),
          sobre_escudo((0.9, 0.02, 0.12), "Advertencia", -0.3))
    E.add("LeftArm", rbox((0.62, 0.05, 0.3), "Correa", shield_c + Rs @ np.array([0, -0.08, 0.48]), Rs, r=0.02, k=(2, 1, 1)))
    E.add("LeftArm", rbox((0.5, 0.04, 0.2), "Vidrio", shield_c + Rs @ np.array([0, -0.12, 0.48]), Rs, r=0.015))
    crack = [np.array([0.46, -0.052, 0.72]), np.array([0.25, -0.05, 0.55]), np.array([0.3, -0.05, 0.3]),
             np.array([0.05, -0.05, 0.12]), np.array([0.12, -0.05, -0.1])]
    crack = [p + [0, (p[0] / 0.5) ** 2 * bend - 0.004, 0] for p in crack]
    E.add("LeftArm", tube([shield_c + Rs @ p for p in crack], 0.014, "Tornillo", sides=4))
    E.add("LeftArm", rbox((0.32, 0.32, 0.3), "Correa", P(1.2, 2.25, 0.5), rot(-20), r=0.08))      # guante
    # antebrazo derecho: piel expuesta con chapa atornillada a la carne, garras
    d = unit(arms[-1][2] - arms[-1][1])
    E.add("RightArm", placa((0.3, 0.07, 0.5), RU, (arms[-1][1] + arms[-1][2]) / 2 + P(-0.22, 0, 0.05),
                            rot(0, 80, 0) @ rot(-8), curva=0.06, k=(2, 1, 2), r=0.025))
    for t in (0.25, 0.75):
        p = arms[-1][1] + (arms[-1][2] - arms[-1][1]) * t + P(-0.29, 0, 0.05)
        E.add("RightArm", perno(p, P(-1, 0, 0)), ellipsoid((0.04, 0.04, 0.02), "Sangre", p + P(0.02, -0.06, 0), n=2))
    wr = arms[-1][2]
    E.add("RightArm", along(wr, wr + d * 0.22, (0.12, 0.07), SK, n=4))
    E.add("RightArm", dedos(wr + d * 0.2, d, P(0, 0, 1), 4, 0.24, 0.035, SK, "Garra", curva=P(0, 0, 0.05)))
    # --- piernas, rodilleras, canilleras y botas
    for lado, hip, kn, an in ((1, P(0.42, 2.3, 0), P(0.5, 1.28, 0.14), P(0.52, 0.45, 0.02)),
                             (-1, P(-0.42, 2.3, 0), P(-0.52, 1.3, 0.04), P(-0.56, 0.45, -0.04))):
        parte = "LeftLeg" if lado > 0 else "RightLeg"
        E.add(parte, tube([hip, (hip + kn) / 2, kn, kn + (an - kn) * 0.4, an], [0.31, 0.27, 0.22, 0.23, 0.18], TE, sides=12),
              domo((0.2, 0.16, 0.22), AR, kn + P(0, 0.02, 0.16), None, lambda U: U[:, 1] < -0.05, 0.05, n=6,
                   disp=lambda U: -0.05 * np.exp(-np.sum((U - [0.3, -0.8, 0.3]) ** 2, 1) / 0.05)),
              placa((0.34, 0.07, 0.55), AR if lado > 0 else RU, kn + (an - kn) * 0.5 + P(0, 0, 0.19), rot(-4),
                    curva=0.1, k=(3, 1, 3), r=0.025),
              rbox((0.44, 0.72, 0.46), "Bota", P(lado * 0.54, 0.26, 0.1), rot(0, 0, 0), r=0.1, k=(2, 2, 1)),
              rbox((0.48, 0.78, 0.08), "Correa", P(lado * 0.54, 0.045, 0.1), None, r=0.035, k=(2, 2, 1)))
        for z in (0.34, 0.2):
            E.add(parte, rbox((0.46, 0.08, 0.05), "Correa", P(lado * 0.54, z, 0.42 + 0.01 * z), rot(0, 0, 0), r=0.02))
    E.add("LeftLeg", placa((0.4, 0.07, 0.5), RU, P(0.5, 1.9, 0.26), rot(-8, 0, 8), curva=0.1, k=(3, 1, 3), r=0.025),
          cordon([P(0.34, 2.1, 0.3), P(0.66, 2.08, 0.25)], r=0.025, n=10))
    # --- cabeza: cara podrida bajo el casco
    E.add("Head", ellipsoid((0.35, 0.38, 0.38), SK, Hc + P(0, -0.08, 0), n=6,
                            disp=lambda U: 0.04 * nz(U * 3)),
          ellipsoid((0.26, 0.24, 0.1), SK, Hc + P(0, -0.38, 0.22), rot(-10), n=5),
          ellipsoid((0.2, 0.2, 0.07), "Boca", Hc + P(0, -0.3, 0.3), rot(-10), n=4))
    for sx in (-1, 1):
        E.add("Head", ellipsoid((0.065, 0.04, 0.045), "Ojo_Rojo", Hc + P(sx * 0.13, -0.02, 0.36), n=3))
    ang = np.radians(np.linspace(-60, 60, 7))
    E.add("Head", dientes([Hc + P(0.18 * math.sin(a), -0.3, 0.3 + 0.18 * math.cos(a)) for a in ang],
                          [P(0, 1, 0.1)] * 7, [0.07] * 7, 0.022, "Dientes"))
    # casco táctico abollado con visor levantado y rajado
    dents = [unit(np.array([0.55, -0.35, 0.75])), unit(np.array([-0.65, 0.3, 0.6])), unit(np.array([0.1, 0.6, 0.8]))]
    hdisp = lambda U: sum(-0.12 * np.exp(-np.sum((U - dd) ** 2, 1) / 0.025) for dd in dents)  # noqa: E731
    hcen = Hc + P(0, 0.08, -0.02)
    E.add("Head", domo((0.47, 0.52, 0.45), AR, hcen, None,
                       lambda U: (U[:, 2] > -0.3) & ~((U[:, 1] < -0.45) & (U[:, 2] < 0.3)), 0.06, n=10, disp=hdisp))
    for sx in (-1, 1):
        E.add("Head", tube([hcen + P(sx * 0.46, -0.02, 0), hcen + P(sx * 0.56, -0.02, 0)], 0.14, "Correa", sides=12,
                           caps=("flat", "flat")),
              rbox((0.05, 0.36, 0.07), AR, hcen + P(sx * 0.46, 0.2, 0.02), rot(0, sx * 12, 0), r=0.02),
              tube([hcen + P(sx * 0.48, -0.15, -0.02), hcen + P(sx * 0.3, -0.35, 0.18), hcen + P(0, -0.42, 0.24)],
                   0.022, "Correa", sides=5))
    E.add("Head", rbox((0.16, 0.14, 0.07), AR, hcen + P(0, 0.4, 0.33), rot(-60), r=0.02),
          rbox((0.06, 0.12, 0.05), "Tornillo", hcen + P(0, 0.44, 0.44), rot(-60), r=0.015))
    Rv = rot(-32)
    E.add("Head", domo((0.53, 0.58, 0.51), "Vidrio", hcen, Rv,
                       lambda U: (U[:, 1] < -0.35) & (U[:, 2] > -0.42) & (U[:, 2] < 0.22), 0.03, n=11))
    vc = [unit(np.array(v)) * [0.535, 0.585, 0.515] for v in
          ([0.25, -0.9, 0.2], [0.12, -0.95, 0.05], [0.2, -0.9, -0.12], [0.05, -0.92, -0.3])]
    E.add("Head", tube([hcen + Rv @ p for p in vc], 0.01, "Tornillo", sides=4))
    return E, dict(target=(0, 0, 2.6), dist=0.8)


# ------------------------------------------------------------------ 3. Zombi Berserk
def zombi_berserk():
    SK, VE, PA = "Piel_Berserk", "Vena", "Pantalon_Berserk"
    nz = Noise(31, 3.0)
    hips = P(0, 2.1, 0)
    Cc, Rc, rc = P(0, 3.5, 0.4), rot(22), np.array([1.05, 0.62, 0.72])
    H = P(0, 4.2, 0.98)
    shL, shR = P(1.15, 3.78, 0.2), P(-1.15, 3.78, 0.2)
    E = Enemigo("zombi_berserk_hd", dict(Head=P(0, 4.0, 0.7), Torso=P(0, 3.0, 0.2), LeftArm=shL, RightArm=shR,
                                         LeftLeg=P(0.45, 2.05, 0), RightLeg=P(-0.45, 2.05, 0)))

    def surf(u, k=1.0):
        return Cc + Rc @ (unit(np.array(u, float)) * rc * k)

    # cicatrices profundas: polilíneas sobre el pecho (garras) -> surco + tejido rosado + grapas
    scars = [[(-0.75, -0.55, 0.45), (-0.3, -0.9, 0.15), (0.15, -0.9, -0.2), (0.5, -0.65, -0.5)],
             [(-0.55, -0.7, 0.55), (-0.1, -0.95, 0.3), (0.3, -0.85, 0.05), (0.65, -0.55, -0.25)],
             [(0.35, -0.75, 0.55), (0.65, -0.6, 0.3)]]
    scar_pts = []
    for sc in scars:
        u = [np.array(p) for p in sc]
        fine = [unit(u[i] * (1 - t) + u[i + 1] * t) for i in range(len(u) - 1) for t in np.linspace(0, 1, 6)[:-1]] + [unit(u[-1])]
        scar_pts.append(np.array([surf(p) for p in fine]))

    def pecho(X, N):
        L = (X - Cc) @ Rc                                      # coordenadas locales
        U = unit(L / rc)
        front = np.clip(-U[:, 1] * 2 - 0.2, 0, 1)
        d = -0.07 * np.exp(-(U[:, 0] / 0.06) ** 2) * front                       # separación de pectorales
        d += -0.06 * np.exp(-((U[:, 2] + 0.35 + 0.25 * U[:, 0] ** 2) / 0.07) ** 2) * front   # borde inferior
        d += 0.05 * np.exp(-((np.abs(U[:, 0]) - 0.45) / 0.3) ** 2 - ((U[:, 2] + 0.05) / 0.3) ** 2) * front  # volumen
        for sp in scar_pts:
            dist = np.min(np.stack([seg_dist(X, sp[i], sp[i + 1])[0] for i in range(len(sp) - 1)]), 0)
            d += -0.06 * np.exp(-(dist / 0.035) ** 2) + 0.018 * np.exp(-((dist - 0.07) / 0.03) ** 2)
        return d + 0.015 * nz(X * 2)
    chest = ellipsoid(rc, SK, Cc, Rc, n=14).displace(pecho)
    E.add("Torso", chest)
    for sp in scar_pts:
        E.add("Torso", tube([Cc + (p - Cc) * 0.955 for p in sp], 0.022, "Cicatriz", sides=4, capseg=1))
        for i in range(1, len(sp) - 1, 2):
            tdir = unit(sp[i + 1] - sp[i - 1])
            nrm = unit(sp[i] - Cc)
            w = unit(np.cross(tdir, nrm))
            E.add("Torso", tube([sp[i] - w * 0.07 + nrm * 0.005, sp[i] + nrm * 0.02, sp[i] + w * 0.07 + nrm * 0.005],
                                0.012, "Cadena", sides=4, caps=("flat", "flat")))

    def abdominales(U):
        front = np.clip(-U[:, 1] * 2 - 0.3, 0, 1)
        d = -0.07 * np.exp(-(U[:, 0] / 0.07) ** 2) * front
        for zz in (-0.35, 0.02, 0.38):
            d += -0.05 * np.exp(-((U[:, 2] - zz) / 0.07) ** 2) * front * (np.abs(U[:, 0]) < 0.55)
        return d
    E.add("Torso",
          ellipsoid((0.62, 0.46, 0.58), SK, P(0, 2.75, 0.24), rot(15), n=9, disp=abdominales),
          ellipsoid((0.95, 0.52, 0.72), SK, P(0, 3.45, -0.08), rot(22), n=7, disp=lambda U: 0.03 * nz(U * 3)
                    - 0.09 * np.exp(-(U[:, 0] / 0.08) ** 2) * np.clip(U[:, 1] * 2, 0, 1)
                    + 0.08 * np.exp(-((np.abs(U[:, 0]) - 0.45) / 0.18) ** 2 - ((U[:, 2] - 0.25) / 0.3) ** 2) * np.clip(U[:, 1] * 2, 0, 1)),
          ellipsoid((0.62, 0.42, 0.38), SK, hips, n=4))
    for lado in (-1, 1):
        E.add("Torso", along(P(lado * 0.12, 4.18, 0.25), P(lado * 0.78, 3.98, 0.05), (0.3, 0.25), SK, n=5),
              tube([P(lado * 0.22, 4.12, 0.72), P(lado * 0.15, 4.02, 0.86), P(lado * 0.06, 3.9, 0.98)],
                   [0.055, 0.06, 0.045], SK, sides=7))
    # púas de hueso que salen de la espalda, con carne abierta en la base
    for i, (x, z, f) in enumerate(((0.05, 3.95, -0.45), (-0.1, 3.55, -0.62), (0.08, 3.12, -0.6))):
        b = P(x, z, f)
        E.add("Torso", ellipsoid((0.13, 0.08, 0.13), "Musculo", b, rot(-60), n=3),
              spike(b + P(0, -0.05, 0.05), b + P(0.1 * (i - 1), 0.35 - 0.05 * i, -0.4), 0.075 - 0.01 * i, "Hueso", sides=6))
    # --- cabeza hundida entre los hombros, gruñendo
    Rh = rot(8)
    hr = np.array([0.27, 0.31, 0.29])
    socket = [unit(np.array([sx * 0.42, -0.85, 0.12])) for sx in (-1, 1)]
    E.add("Head", ellipsoid(hr, SK, H, Rh, n=8, disp=lambda U: sum(-0.12 * np.exp(-np.sum((U - q) ** 2, 1) / 0.03)
                                                                  for q in socket) + 0.02 * nz(U * 3)),
          tube([H + Rh @ np.array([0.24, -0.25, 0.1]), H + Rh @ np.array([0, -0.32, 0.12]), H + Rh @ np.array([-0.24, -0.25, 0.1])],
               [0.05, 0.065, 0.05], SK, sides=7, aspect=(1, 0.7)),
          ellipsoid((0.22, 0.2, 0.09), SK, H + Rh @ np.array([0, -0.12, -0.26]), Rh, n=5),
          ellipsoid((0.17, 0.15, 0.08), "Boca", H + Rh @ np.array([0, -0.2, -0.17]), Rh, n=4))
    for q in socket:
        E.add("Head", ellipsoid((0.06, 0.045, 0.045), "Ojo_Rojo", H + Rh @ (q * hr * 0.88), Rh, n=3))
    ang = np.radians(np.linspace(-65, 65, 8))
    E.add("Head", dientes([H + Rh @ np.array([0.14 * math.sin(a), -0.2 - 0.14 * math.cos(a), -0.1]) for a in ang],
                          [Rh @ np.array([0, -0.2, -1])] * 8, [0.07 + 0.03 * (abs(a) > 0.8) for a in ang], 0.02, "Dientes"),
          dientes([H + Rh @ np.array([0.13 * math.sin(a), -0.19 - 0.13 * math.cos(a), -0.22]) for a in ang[1:-1]],
                  [Rh @ np.array([0, -0.2, 1])] * 6, [0.06] * 6, 0.02, "Dientes"))
    # --- brazos enormes, puños cerrados listos para embestir
    arms = {1: (shL, P(1.52, 2.95, -0.05), P(1.18, 2.58, 0.78)), -1: (shR, P(-1.52, 2.98, -0.02), P(-1.2, 2.62, 0.8))}
    for lado, (sh, el, wr) in arms.items():
        parte = "LeftArm" if lado > 0 else "RightArm"
        E.add(parte, ellipsoid((0.42, 0.37, 0.31), SK, sh + P(lado * 0.02, 0.08, 0), rot(0, lado * 35, 0), n=6,
                               disp=lambda U: 0.03 * nz(U * 3)))
        E.add(parte, along(sh + (el - sh) * 0.08, el + (el - sh) * 0.05, (0.34, 0.31), SK, n=7,
                           disp=lambda U: 0.1 * np.exp(-((U[:, 2] + 0.1) / 0.5) ** 2) * np.clip(U[:, 1] * -1, 0, 1)))
        E.add(parte, ellipsoid((0.21, 0.21, 0.21), SK, el, n=4))
        E.add(parte, along(el - (wr - el) * 0.05, wr, (0.31, 0.27), SK, n=7,
                           disp=lambda U: -0.28 * np.clip(U[:, 2], 0, 1) ** 1.5 + 0.03 * nz(U * 4)))
        # tendones tensos en el antebrazo y venas saltadas
        for k, a0 in enumerate((0.45, 1.5)):
            E.add(parte, por_superficie(el, wr, (0.24, 0.2), a0 * lado, SK, r=0.035, onda=0.05, n=7, fuera=0.2,
                                        t0=0.3, t1=0.95))
        E.add(parte, por_superficie(sh + (el - sh) * 0.08, el, (0.32, 0.3), 2.6 * lado, VE, r=0.028, onda=0.4, n=10, fase=lado),
              por_superficie(sh + (el - sh) * 0.08, el, (0.32, 0.3), 1.2 * lado, VE, r=0.022, onda=0.5, n=8, fase=2,
                             t0=0.3, t1=0.85),
              por_superficie(el, wr, (0.28, 0.23), -0.5 * lado, VE, r=0.025, onda=0.6, n=10, fase=1, t0=0.1, t1=0.85))
        E.add(parte, puno(wr - el, wr + unit(wr - el) * 0.2, SK, s=1.15))
    # carne desgarrada en el hombro izquierdo: fibras musculares expuestas
    for i in range(4):
        a = shL + P(0.02 + 0.06 * i, 0.3 - 0.06 * i, 0.28)
        E.add("LeftArm", along(a, a + P(0.18, -0.28, 0.06), 0.045, "Musculo", n=3))
    # --- pantalón rasgado, cinturón y cadena colgando
    E.add("Torso", solidify(ellipsoid((0.68, 0.48, 0.46), PA, hips + P(0, 0.05, 0), None, n=7),
                            lambda C2, sh: (nz(C2 * 2.5) > -0.5) & (sh.U[sh.F].mean(1)[:, 2] < 0.7), 0.035),
          domo((0.7, 0.5, 0.5), "Correa", hips + P(0, 0.22, 0), None, lambda U: np.abs(U[:, 2]) < 0.12, 0.045, n=9))
    for i in range(7):
        c = P(0.45 - 0.035 * i, 2.18 - 0.09 * i + 0.004 * i * i, 0.38 - 0.02 * i)
        E.add("Torso", ring_loop(c, (0.06, 0.035), 0.015, "Cadena", R=rot(0, 90 * (i % 2), 70), seg=10, sides=5))
    # --- piernas en postura amplia y agresiva
    for lado, hip, kn, an in ((1, P(0.45, 2.05, 0), P(0.62, 1.2, 0.38), P(0.6, 0.3, 0.05)),
                             (-1, P(-0.45, 2.05, 0), P(-0.6, 1.18, 0.18), P(-0.62, 0.3, -0.15))):
        parte = "LeftLeg" if lado > 0 else "RightLeg"
        E.add(parte, tube([hip, (hip + kn) / 2, kn, kn + (an - kn) * 0.35, an], [0.42, 0.34, 0.22, 0.25, 0.17], SK, sides=11),
              along(kn + (an - kn) * 0.1 + P(0, 0, -0.1), kn + (an - kn) * 0.62 + P(0, 0, -0.07), 0.23, SK, n=4),
              ellipsoid((0.14, 0.12, 0.14), SK, kn + P(0, 0.02, 0.1), n=4),
              tube([an, an + P(0, -0.18, 0.18), an + P(0, -0.24, 0.4)], [0.15, 0.15, 0.12], SK, sides=8, aspect=(0.75, 1.3)))
        E.add(parte, dedos(an + P(0, -0.24, 0.42), P(0, -0.2, 1), P(1, 0, 0), 3, 0.13, 0.045, SK, "Garra",
                           curva=P(0, -0.02, 0), abiertos=0.5))
        E.add(parte, solidify(tube([hip + (hip - kn) * 0.05, hip + (kn - hip) * 0.35, hip + (kn - hip) * 0.7],
                                   [0.46, 0.4, 0.33], PA, sides=11, caps=("none", "none")),
                              lambda C2, sh, hip=hip, kn=kn: (seg_dist(C2, hip, kn)[1] < 0.6 + 0.15 * nz(C2 * 4))
                              & (nz(C2 * 5 + 3) > -0.5), 0.03))
        E.add(parte, por_superficie(hip, kn, (0.33, 0.3), 0.9 * lado, VE, r=0.02, onda=0.5, n=8, t0=0.55, t1=0.95))
    return E, dict(target=(0, 0, 2.7), dist=0.8)


# ------------------------------------------------------------------ 4. Zombi Radiactivo
def pustulas(centro, radio, n, rng, mat="Pustula", tam=(0.035, 0.1), normal=None):
    """Racimo asimétrico de pústulas brillantes; algunas reventadas (con cráter oscuro)."""
    out = []
    for i in range(n):
        v = unit(rng.normal(size=3))
        if normal is not None:
            v = unit(v + np.asarray(normal) * 1.2)
        r = rng.uniform(*tam)
        c = np.asarray(centro) + v * radio * rng.uniform(0.2, 1.0)
        out.append(ellipsoid((r, r, r * 0.8), mat, c, rot(*rng.uniform(0, 180, 3)), n=3 if r > 0.06 else 2))
        if r > 0.07 and i % 2 == 0:
            out.append(ellipsoid((r * 0.4, r * 0.4, r * 0.25), "Hazmat_Quemado", c + v * r * 0.75,
                                 rot(*rng.uniform(0, 180, 3)), n=2))
    return out


def racimo(base, normal, n, rng, largo=(0.3, 0.7), grosor=(0.05, 0.1), abre=0.55):
    """Grupo de cristales que brotan de la piel en abanico."""
    out = []
    normal = unit(normal)
    u1, u2 = perp(normal)
    for i in range(n):
        a = rng.uniform(0, 2 * math.pi)
        d = unit(normal + (u1 * math.cos(a) + u2 * math.sin(a)) * rng.uniform(0.1, abre))
        b = np.asarray(base) + (u1 * math.cos(a) + u2 * math.sin(a)) * rng.uniform(0, 0.08)
        L, r = rng.uniform(*largo) * (1.0 if i else 1.3), rng.uniform(*grosor) * (1.0 if i else 1.3)
        out.append(crystal(b - d * 0.06, b + d * L, r, "Cristal", twist=rng.uniform(0, 1)))
    return out


def gota(p, largo, r, mat="Hazmat"):
    """Chorro derretido que cuelga con una gota en la punta."""
    p = np.asarray(p, float)
    return tube([p + P(0, 0.04, 0), p + P(0, -largo * 0.5, 0.01), p + P(0, -largo, 0)], [r, r * 0.6, r * 0.95],
                mat, sides=6, capseg=2)


def zombi_radiactivo():
    HZ, BU, GO, SK = "Hazmat", "Hazmat_Quemado", "Goma", "Piel_Toxica"
    nz = Noise(41, 2.6)
    rng = np.random.default_rng(4)
    hips, C, Rc = P(0, 2.2, 0), P(0, 3.25, 0.18), rot(14)
    H = P(0, 4.45, 0.42)
    shL, shR = P(0.85, 3.85, 0.2), P(-0.85, 3.85, 0.2)
    E = Enemigo("zombi_radiactivo_hd", dict(Head=P(0, 4.1, 0.32), Torso=C, LeftArm=shL, RightArm=shR,
                                            LeftLeg=P(0.36, 2.15, 0), RightLeg=P(-0.36, 2.15, 0)))
    # --- cuerpo mutado debajo y traje derretido encima (con agujeros reales)
    E.add("Torso", ellipsoid((0.74, 0.5, 0.8), SK, C, Rc, n=9,
                             disp=lambda U: 0.12 * np.exp(-np.sum((U - [-0.55, -0.6, 0.35]) ** 2, 1) / 0.08)
                             + 0.1 * np.exp(-np.sum((U - [0.3, 0.8, 0.2]) ** 2, 1) / 0.1) + 0.04 * nz(U * 3)),
          ellipsoid((0.56, 0.4, 0.36), SK, hips, n=5))
    agujeros = [np.array(v) for v in ([-0.55, -0.6, 0.35], [0.3, 0.8, 0.25], [0.6, -0.4, -0.5])]

    def keep_traje(C2, sh):
        U = sh.U[sh.F].mean(1)
        hole = np.zeros(len(U), bool)
        for h in agujeros:
            hole |= np.sum((U - unit(h)) ** 2, 1) < 0.16 + 0.1 * nz(C2 * 6)
        return ~hole & (U[:, 2] < 0.9)

    def arrugas(U):
        return 0.035 * np.sin(U[:, 2] * 18 + 3 * nz(U * 2)) * (U[:, 2] < 0.2) + 0.03 * nz(U * 4) - 0.06 * np.clip(-U[:, 2] - 0.7, 0, 1)
    def quemado(C2, sh):
        U = sh.U[sh.F].mean(1)
        cerca = np.zeros(len(U), bool)
        for h in agujeros:
            cerca |= np.sum((U - unit(h)) ** 2, 1) < 0.36 + 0.2 * nz(C2 * 5 + 2)
        return cerca | (nz(C2 * 3 + 11) > 0.45) | (U[:, 2] < -0.75 + 0.15 * nz(C2 * 6))
    E.add("Torso", solidify(ellipsoid((0.8, 0.56, 0.86), HZ, C, Rc, n=11, disp=arrugas), keep_traje, 0.045).pintar(quemado, BU))
    E.add("Torso", solidify(ellipsoid((0.62, 0.46, 0.44), HZ, hips, None, n=7, disp=lambda U: 0.03 * nz(U * 4)),
                            lambda C2, sh: (sh.U[sh.F].mean(1)[:, 2] < 0.75) & (nz(C2 * 5 + 1) > -0.6), 0.04)
           .pintar(lambda C2, sh: nz(C2 * 4 + 3) > 0.35, BU))
    # parche de peligro radiactivo quemado en el pecho
    Rb = Rc @ rot(-20)
    E.add("Torso", tube([C + Rb @ np.array([0.3, -0.6, 0.35]), C + Rb @ np.array([0.3, -0.66, 0.35])], 0.16, "Goma",
                        sides=16, caps=("flat", "flat"), smooth=False))
    for k in range(3):
        a = k * 2 * math.pi / 3 + 0.5
        d = np.array([math.cos(a), 0, math.sin(a)]) * 0.075
        E.add("Torso", ellipsoid((0.05, 0.02, 0.05), "Advertencia", C + Rb @ (np.array([0.3, -0.67, 0.35]) + d), Rb, n=2))
    # gotas del traje derretido (dobladillo, pecho)
    for x, f, L in ((-0.5, 0.35, 0.35), (-0.15, 0.55, 0.22), (0.28, 0.5, 0.45), (0.6, 0.2, 0.3), (0.45, -0.3, 0.28), (-0.4, -0.4, 0.4)):
        E.add("Torso", gota(P(x, 2.45, f), L, 0.035))
    # --- carne, pústulas y cristales que atraviesan el traje
    E.add("Torso", pustulas(C + Rc @ np.array([-0.45, -0.42, 0.3]), 0.22, 9, rng, normal=Rc @ np.array([-0.6, -0.7, 0.3])),
          pustulas(C + Rc @ np.array([0.45, -0.3, -0.5]), 0.18, 6, rng, normal=Rc @ np.array([0.6, -0.5, -0.5])),
          racimo(C + Rc @ np.array([0.2, 0.42, 0.25]), Rc @ np.array([0.3, 1, 0.5]), 6, rng, largo=(0.5, 1.0), grosor=(0.08, 0.14)),
          racimo(C + Rc @ np.array([-0.35, 0.3, -0.35]), Rc @ np.array([-0.5, 1, 0]), 3, rng, largo=(0.3, 0.5)))
    # tanque de oxígeno reventado en la espalda con manguera corrugada a la máscara
    tk = C + Rc @ np.array([-0.3, 0.6, 0.05])
    E.add("Torso", tube([tk + Rc @ np.array([0, 0, -0.45]), tk + Rc @ np.array([0, 0, 0.45])], 0.2, "Tanque", sides=14),
          tube([tk + Rc @ np.array([0, 0, 0.62]), tk + Rc @ np.array([0, 0, 0.75])], 0.06, "Tanque", sides=8,
               caps=("flat", "flat")),
          rbox((1.0, 0.06, 0.12), "Correa", C + Rc @ np.array([0, 0.5, 0.35]), Rc, r=0.02, k=(4, 1, 1)),
          racimo(tk + Rc @ np.array([0.12, 0.15, 0.1]), Rc @ np.array([0.4, 1, 0.3]), 4, rng, largo=(0.35, 0.6)))
    hose = [tk + Rc @ np.array([0, 0, 0.75]), P(-0.35, 4.3, -0.3), P(-0.42, 4.2, 0.2), P(-0.2, 4.2, 0.6)]
    hp = np.array([hose[i] * (1 - t) + hose[i + 1] * t for i in range(3) for t in np.linspace(0, 1, 7)[:-1]] + [hose[-1]])
    E.add("Torso", tube(hp, 0.05 + 0.012 * np.cos(np.arange(len(hp)) * math.pi), GO, sides=8, capseg=1))
    # --- capucha, máscara de gas con un ojo roto, filtros (uno reventado de cristales)
    Rh = rot(-5)
    E.add("Head", ellipsoid((0.36, 0.38, 0.4), SK, H, Rh, n=6),
          solidify(ellipsoid((0.44, 0.46, 0.48), HZ, H + P(0, 0.05, -0.05), Rh, n=9, disp=lambda U: 0.03 * nz(U * 4)),
                   lambda C2, sh: ~((sh.U[sh.F].mean(1)[:, 1] < -0.55) & (sh.U[sh.F].mean(1)[:, 2] < 0.45))
                   & (sh.U[sh.F].mean(1)[:, 2] > -0.75), 0.04).pintar(lambda C2, sh: nz(C2 * 4 + 5) > 0.3, BU),
          ellipsoid((0.3, 0.2, 0.3), GO, H + P(0, -0.08, 0.28), Rh, n=6))
    for sx in (-1, 1):
        lc = H + P(sx * 0.14, 0.02, 0.44)
        E.add("Head", tube([lc - P(0, 0, 0.06), lc + P(0, 0, 0.02)], 0.1, GO, sides=16, caps=("flat", "flat")))
        if sx > 0:
            E.add("Head", tube([lc, lc + P(0, 0, 0.025)], 0.075, "Lente", sides=16, caps=("flat", "flat"), smooth=False))
        else:
            E.add("Head", ellipsoid((0.06, 0.05, 0.05), "Pustula", lc + P(0, 0, -0.01), n=3),
                  tube([lc + P(0.02, 0.06, 0.01), lc + P(-0.03, 0.0, 0.03), lc + P(0.04, -0.06, 0.02)], 0.012, "Lente", sides=4))
        E.add("Head", ellipsoid((0.04, 0.03, 0.04), "Pustula" if sx < 0 else "Lente", lc + P(0, 0, 0.0), n=2))
    for sx in (-1, 1):
        a, b = H + P(sx * 0.16, -0.2, 0.42), H + P(sx * 0.36, -0.42, 0.5)
        E.add("Head", tube([a, b], 0.1, "Tanque", sides=12, caps=("flat", "flat")))
        for t in (0.35, 0.65, 0.95):
            E.add("Head", ring_loop(a + (b - a) * t, 0.1, 0.018, "Tanque", R=align(b - a), seg=12, sides=4))
        if sx < 0:
            E.add("Head", racimo(b + unit(b - a) * 0.02, b - a, 3, rng, largo=(0.2, 0.35), grosor=(0.03, 0.05), abre=0.4))
    E.add("Head", racimo(H + P(0.15, 0.35, 0.05), P(0.3, 1, -0.2), 3, rng, largo=(0.3, 0.55), grosor=(0.05, 0.08)),
          pustulas(H + P(-0.3, 0.1, 0.1), 0.15, 5, rng, normal=P(-1, 0.3, 0)),
          gota(H + P(0.2, -0.2, 0.3), 0.3, 0.03), gota(H + P(-0.08, -0.25, 0.25), 0.22, 0.028))
    # --- brazo izquierdo: manga del traje con guante; derecho: mutado, tumores y garras
    el, wr = P(1.1, 3.05, 0.35), P(1.05, 2.35, 0.7)
    E.add("LeftArm", tube([shL, (shL + el) / 2, el, (el + wr) / 2, wr], [0.22, 0.2, 0.18, 0.17, 0.15], HZ, sides=12,
                          capseg=2),
          tube([wr - unit(wr - el) * 0.05, wr + unit(wr - el) * 0.1], [0.16, 0.16], GO, sides=12, caps=("flat", "round")),
          rbox((0.22, 0.2, 0.26), GO, wr + unit(wr - el) * 0.24, rot(-30), r=0.07),
          gota(el + P(0, -0.1, -0.02), 0.35, 0.03), gota((el + wr) / 2 + P(0.08, -0.12, 0), 0.25, 0.025),
          pustulas((shL + el) / 2 + P(0.12, 0.1, 0.05), 0.14, 5, rng, normal=P(1, 0, 0.5)))
    for t in (0.2, 0.45, 0.7):
        E.add("LeftArm", ring_loop(shL + (el - shL) * t, 0.215 - 0.02 * t, 0.02, HZ,
                                   R=align(el - shL), seg=14, sides=4))
    elR, wrR = P(-1.25, 3.0, 0.2), P(-1.3, 2.1, 0.55)
    E.add("RightArm", tube([shR, (shR + elR) / 2, elR], [0.24, 0.22, 0.25], SK, sides=12),
          solidify(tube([shR - (elR - shR) * 0.05, shR + (elR - shR) * 0.45], [0.28, 0.26], HZ, sides=12, caps=("none", "none")),
                   lambda C2, sh: (seg_dist(C2, shR, elR)[1] < 0.35 + 0.1 * nz(C2 * 5)) & (nz(C2 * 6) > -0.5), 0.03)
          .pintar(lambda C2, sh: seg_dist(C2, shR, elR)[1] > 0.2, BU),
          along(elR - (wrR - elR) * 0.1, wrR, (0.42, 0.36), "Tumor", n=8,
                disp=lambda U: 0.14 * np.maximum(0, nz(U * 2.2 + 4)) + 0.05 * nz(U * 5) - 0.25 * np.clip(U[:, 2], 0, 1) ** 2),
          racimo(elR + P(-0.2, 0.1, -0.1), P(-1, 0.4, -0.4), 4, rng, largo=(0.35, 0.65)),
          pustulas((elR + wrR) / 2 + P(-0.25, 0, 0.15), 0.25, 10, rng, normal=P(-1, 0, 1), tam=(0.04, 0.12)),
          pustulas(shR + P(-0.2, 0.15, 0.1), 0.15, 5, rng, normal=P(-1, 0.5, 0.3)))
    d = unit(wrR - elR)
    E.add("RightArm", along(wrR - d * 0.1, wrR + d * 0.2, (0.16, 0.09), "Tumor", n=4),
          dedos(wrR + d * 0.18, d, P(0, 0, 1), 4, 0.36, 0.04, "Tumor", "Garra", curva=P(0, 0, 0.1), abiertos=0.5))
    # --- piernas: una con el traje, la otra con la rodilla deshecha
    for lado, hip, kn, an in ((1, P(0.36, 2.15, 0), P(0.42, 1.25, 0.2), P(0.44, 0.45, 0.05)),
                             (-1, P(-0.36, 2.15, 0), P(-0.44, 1.22, 0.05), P(-0.46, 0.45, -0.1))):
        parte = "LeftLeg" if lado > 0 else "RightLeg"
        E.add(parte, tube([hip, (hip + kn) / 2, kn, kn + (an - kn) * 0.4, an], [0.27, 0.24, 0.2, 0.2, 0.17],
                          SK if lado < 0 else HZ, sides=12, capseg=2),
              rbox((0.4, 0.66, 0.44), GO, P(lado * 0.46, 0.24, 0.12), None, r=0.1, k=(1, 2, 1)),
              rbox((0.44, 0.7, 0.07), "Correa", P(lado * 0.46, 0.035, 0.12), None, r=0.03, k=(1, 2, 1)))
        for t in (0.25, 0.55):
            E.add(parte, ring_loop(hip + (kn - hip) * t, 0.25 - 0.02 * t, 0.02, HZ if lado > 0 else BU,
                                   R=align(kn - hip), seg=14, sides=4))
    E.add("RightLeg", solidify(tube([P(-0.36, 2.2, 0), P(-0.4, 1.7, 0.03), P(-0.44, 1.15, 0.05), P(-0.45, 0.8, -0.02)],
                                    [0.31, 0.28, 0.24, 0.22], HZ, sides=12, caps=("none", "none")),
                               lambda C2, sh: (nz(C2 * 4 + 7) > -0.25) & (C2[:, 2] > 0.8 + 0.15 * nz(C2 * 6)), 0.035)
          .pintar(lambda C2, sh: (nz(C2 * 4 + 7) < 0.05) | (C2[:, 2] < 1.05), BU),
          pustulas(P(-0.46, 1.2, 0.2), 0.14, 6, rng, normal=P(0, 0, 1)),
          racimo(P(-0.55, 1.6, 0.1), P(-1, 0.3, 0.2), 3, rng, largo=(0.3, 0.5)))
    E.add("LeftLeg", gota(P(0.52, 1.6, 0.2), 0.3, 0.03), gota(P(0.3, 1.3, 0.22), 0.2, 0.025))
    return E, dict(target=(0, 0, 2.6), dist=0.8)


# ------------------------------------------------------------------ 5. Zombi Gigante
def sobre(p, centro, cuerpos, paso=0.03, extra=0.0):
    """Empuja p hacia afuera desde `centro` hasta salir de todos los elipsoides (cadenas apoyadas en la piel)."""
    p, d = np.asarray(p, float), unit(np.asarray(p, float) - np.asarray(centro, float))
    for _ in range(200):
        dentro = False
        for c, R, r in cuerpos:
            q = (p - c) @ R / r
            if q @ q < 1:
                dentro = True
                break
        if not dentro:
            break
        p = p + d * paso
    return p + d * extra, d


def cadena_por(pts, normales, mat="Cadena", largo=0.3, ancho=0.18, r=0.04):
    """Eslabones alternados (acostados / parados) a lo largo de una curva sobre la piel."""
    pts = np.asarray(pts, float)
    L = np.concatenate([[0], np.cumsum(np.linalg.norm(np.diff(pts, axis=0), axis=1))])
    out = []
    for i, s_ in enumerate(np.arange(0, L[-1], largo * 0.62)):
        k = min(np.searchsorted(L, s_, side="right") - 1, len(pts) - 2)
        f = (s_ - L[k]) / max(L[k + 1] - L[k], 1e-9)
        c = pts[k] * (1 - f) + pts[k + 1] * f
        t = unit(pts[k + 1] - pts[k])
        n = unit(normales[k] * (1 - f) + normales[k + 1] * f)
        n = unit(n - t * (n @ t))
        R = np.column_stack([t, np.cross(n, t), n]) if i % 2 == 0 else np.column_stack([t, n, np.cross(t, n)])
        out.append(ring_loop(c + n * r * (1.2 if i % 2 == 0 else 2.2), (largo / 2, ancho / 2), r, mat, R=R, seg=8, sides=4))
    return out


def zombi_gigante():
    SK, PA, ST = "Piel_Gigante", "Pantalon_Gigante", "Acero"
    nz = Noise(51, 1.4)
    hips = P(0, 4.7, 0)
    Cc, Rcc, rcc = P(0, 7.6, 0.35), rot(18), np.array([2.3, 1.5, 1.5])
    Cb, Rbb, rbb = P(0, 5.7, 0.6), rot(5), np.array([1.85, 1.5, 1.45])
    H = P(0, 9.3, 1.45)
    shL, shR = P(2.45, 7.95, 0.1), P(-2.45, 7.95, 0.1)
    E = Enemigo("zombi_gigante_hd", dict(Head=P(0, 8.9, 1.0), Torso=P(0, 6.5, 0.3), LeftArm=shL, RightArm=shR,
                                         LeftLeg=P(0.95, 4.6, 0), RightLeg=P(-0.95, 4.6, 0), Weapon=P(-2.85, 4.2, 1.2)))
    # --- torso colosal: pecho, panza cosida y joroba con varillas clavadas
    belly_scar = [P(-1.2, 6.3, 1.7), P(-0.4, 5.9, 2.0), P(0.5, 5.4, 1.95), P(1.1, 4.9, 1.6)]
    bs = np.array([sobre(p, P(0, p[2], 0.4), [(Cb, Rbb, rbb)])[0] for p in belly_scar])

    def panza(X, N):
        d = 0.03 * nz(X * 1.5) * 2
        for i in range(len(bs) - 1):
            dist = seg_dist(X, bs[i], bs[i + 1])[0]
            d = d - 0.1 * np.exp(-(dist / 0.07) ** 2) + 0.035 * np.exp(-((dist - 0.14) / 0.06) ** 2)
        return d

    def pecho(X, N):
        U = unit(((X - Cc) @ Rcc) / rcc)
        front = np.clip(-U[:, 1] * 2 - 0.2, 0, 1)
        return (-0.14 * np.exp(-(U[:, 0] / 0.06) ** 2) * front - 0.1 * np.exp(-((U[:, 2] + 0.35 + 0.2 * U[:, 0] ** 2) / 0.08) ** 2) * front
                + 0.04 * nz(X * 1.8))
    E.add("Torso", ellipsoid(rcc, SK, Cc, Rcc, n=12).displace(pecho),
          ellipsoid(rbb, SK, Cb, Rbb, n=10).displace(panza),
          ellipsoid((2.0, 1.3, 1.45), SK, P(0, 7.9, -0.5), rot(25), n=7,
                    disp=lambda U: 0.05 * nz(U * 2) - 0.1 * np.exp(-(U[:, 0] / 0.08) ** 2) * np.clip(U[:, 1] * 2, 0, 1)),
          ellipsoid((1.5, 1.1, 0.9), SK, hips, n=5))
    for i in range(len(bs) - 1):
        for t in (0.3, 0.75):
            p = bs[i] + (bs[i + 1] - bs[i]) * t
            nrm = unit(p - P(0, p[2], 0.3))
            w = unit(np.cross(bs[i + 1] - bs[i], nrm))
            E.add("Torso", tube([p - w * 0.2 + nrm * 0.02, p + nrm * 0.06, p + w * 0.2 + nrm * 0.02], 0.028, "Cadena",
                                sides=4, caps=("flat", "flat")))
    E.add("Torso", tube([Cb + (p - Cb) * 0.97 for p in bs], 0.05, "Cicatriz", sides=5, capseg=1))
    for i, (x, z, f) in enumerate(((0.6, 8.6, -1.55), (-0.5, 7.7, -1.75), (0.2, 6.9, -1.5))):
        b = P(x, z, f)
        d = unit(P(0.3 * (i - 1), 0.5, -1))
        E.add("Torso", tube([b - d * 0.4, b + d * 0.9, b + d * 1.2 + P(0.25, 0.2, 0)], 0.05, "Varilla", sides=6, capseg=1),
              ellipsoid((0.16, 0.16, 0.08), "Sangre", b + d * 0.02, align(d), n=2))
    for lado in (-1, 1):
        E.add("Torso", along(P(lado * 0.3, 9.0, 0.5), P(lado * 2.0, 8.5, 0.1), (0.8, 0.65), SK, n=4))
    # cadena cruzada en el pecho (del hombro izquierdo a la cadera derecha)
    cuerpos = [(Cc, Rcc, rcc), (Cb, Rbb, rbb)]
    path, nrms = [], []
    for t in np.linspace(0, 1, 16):
        p0 = P(1.9, 8.8, 0.8) * (1 - t) + P(-1.6, 4.9, 1.2) * t
        p, n = sobre(p0, P(0, p0[2], 0.3), cuerpos, extra=0.02)
        path.append(p), nrms.append(n)
    E.add("Torso", cadena_por(path, nrms, largo=0.5, ancho=0.3, r=0.06))
    # --- pantalón rasgado y cinturón de soga
    E.add("Torso", solidify(ellipsoid((1.65, 1.2, 1.1), PA, hips + P(0, 0.1, 0.05), None, n=8),
                            lambda C2, sh: (sh.U[sh.F].mean(1)[:, 2] < 0.62 + 0.1 * nz(C2 * 3)) & (nz(C2 * 2.5 + 1) > -0.45), 0.06),
          domo((1.72, 1.28, 1.3), "Madera_Soga", hips + P(0, 0.55, 0.05), None, lambda U: np.abs(U[:, 2]) < 0.08, 0.07, n=10))
    # --- cabeza chica hundida, prognatismo con colmillos
    Rh = rot(5)
    hr = np.array([0.55, 0.6, 0.55])
    so = [unit(np.array([0.42, -0.85, 0.15])), unit(np.array([-0.42, -0.85, 0.2]))]
    E.add("Head", ellipsoid(hr, SK, H, Rh, n=8, disp=lambda U: -0.14 * np.exp(-np.sum((U - so[0]) ** 2, 1) / 0.04)
                            - 0.1 * np.exp(-np.sum((U - so[1]) ** 2, 1) / 0.02) + 0.03 * nz(U * 2)),
          tube([H + Rh @ np.array([0.48, -0.42, 0.2]), H + Rh @ np.array([0, -0.55, 0.3]), H + Rh @ np.array([-0.48, -0.42, 0.24])],
               [0.1, 0.14, 0.1], SK, sides=8, aspect=(1, 0.7)),
          ellipsoid((0.62, 0.55, 0.3), SK, H + Rh @ np.array([0, -0.35, -0.48]), Rh @ rot(-8), n=6),
          ellipsoid((0.46, 0.4, 0.14), "Boca", H + Rh @ np.array([0, -0.38, -0.3]), Rh, n=4))
    E.add("Head", ellipsoid((0.13, 0.1, 0.11), "Ojo_Amarillo", H + Rh @ (so[0] * hr * 0.9), Rh, n=3),
          ellipsoid((0.07, 0.05, 0.06), "Ojo_Amarillo", H + Rh @ (so[1] * hr * 0.9), Rh, n=3))
    for sx in (-1, 1):
        b = H + Rh @ np.array([sx * 0.36, -0.72, -0.4])
        E.add("Head", spike(b, b + P(sx * 0.08, 0.38, 0.12), 0.08, "Dientes", sides=6, bend=P(sx * 0.05, 0, -0.06)))
    ang = np.radians(np.linspace(-50, 50, 6))
    E.add("Head", dientes([H + Rh @ np.array([0.3 * math.sin(a), -0.35 - 0.48 * math.cos(a), -0.36]) for a in ang],
                          [P(0, 1, 0.1)] * 6, [0.1] * 6, 0.04, "Dientes"))
    # --- brazos: el izquierdo cuelga hasta la rodilla con garras, el derecho empuña la viga
    arms = {1: (shL, P(2.95, 5.9, 0.15), P(2.85, 3.7, 0.5)), -1: (shR, P(-2.95, 5.9, 0.3), P(-2.85, 4.45, 1.05))}
    for lado, (sh, el, wr) in arms.items():
        parte = "LeftArm" if lado > 0 else "RightArm"
        E.add(parte, ellipsoid((1.0, 0.95, 0.85), SK, sh + P(lado * 0.05, 0.2, 0), rot(0, lado * 30, 0), n=6,
                               disp=lambda U: 0.04 * nz(U * 2)),
              along(sh + (el - sh) * 0.1, el, (0.8, 0.72), SK, n=6, disp=lambda U: 0.04 * nz(U * 2)),
              ellipsoid((0.6, 0.6, 0.6), SK, el, n=3),
              along(el - (wr - el) * 0.05, wr, (0.9, 0.8), SK, n=6, disp=lambda U: -0.35 * np.clip(U[:, 2], 0, 1) ** 1.5
                    + 0.05 * nz(U * 3)),
              por_superficie(sh + (el - sh) * 0.1, el, (0.8, 0.72), 2.4 * lado, "Vena", r=0.05, onda=0.35, n=9),
              por_superficie(el, wr, (0.75, 0.6), -0.6 * lado, "Vena", r=0.05, onda=0.5, n=9, t0=0.1, t1=0.8))
        E.add(parte, ring_loop(wr - unit(wr - el) * 0.15, 0.62, 0.09, ST, R=align(wr - el), seg=16, sides=6))
    d = unit(arms[1][2] - arms[1][1])
    wr = arms[1][2]
    E.add("LeftArm", along(wr - d * 0.2, wr + d * 0.55, (0.5, 0.28), SK, n=5),
          dedos(wr + d * 0.5, d, P(0, 0, 1), 4, 0.75, 0.1, SK, "Garra", curva=P(0, 0, 0.18), abiertos=0.45))
    for i in range(3):                                            # grillete con cadena rota colgando
        c = wr - d * 0.15 + P(0.1, -0.7 - 0.28 * i, 0.3 + 0.05 * i)
        E.add("LeftArm", ring_loop(c, (0.16, 0.1), 0.04, "Cadena", R=rot(90 * (i % 2), 0, 90), seg=8, sides=4))
    # puño derecho atravesado por la viga + carne crecida alrededor
    dR = unit(arms[-1][2] - arms[-1][1])
    fist = arms[-1][2] + dR * 0.45
    E.add("RightArm", puno(dR, fist, SK, s=2.7))
    top, bot = fist + P(0.15, 1.5, -0.9), P(-3.25, 0.75, 3.7)
    ax = unit(bot - top)
    for t, r in ((0.05, 0.45), (-0.05, 0.4)):
        c = fist + ax * (np.linalg.norm(fist - top) * 0 + (0.55 if t > 0 else -0.55))
        E.add("RightArm", ellipsoid((r, r, r * 0.8), SK, c, align(ax), n=4, disp=lambda U: 0.1 * nz(U * 3)),
              ellipsoid((r * 0.7, r * 0.7, r * 0.3), "Sangre", c + ax * 0.2 * np.sign(t), align(ax), n=3))
    # --- arma: viga doble T doblada con un bloque de concreto y varillas en la punta
    Lb = np.linalg.norm(bot - top)
    Rw = align(ax) @ rot(0, 0, 25)
    bendf = lambda V: V + np.outer(0.35 * (V[:, 2] / (Lb / 2)) ** 2, [1, 0, 0])  # noqa: E731
    E.add("Weapon", rbox((0.82, 0.11, Lb), ST, r=0.02, k=(1, 1, 10)).deform(lambda V: bendf(V + [0, 0.37, 0])).xf(Rw, (top + bot) / 2),
          rbox((0.82, 0.11, Lb), ST, r=0.02, k=(1, 1, 10)).deform(lambda V: bendf(V + [0, -0.37, 0])).xf(Rw, (top + bot) / 2),
          rbox((0.1, 0.68, Lb - 0.06), ST, r=0.015, k=(1, 1, 10)).deform(bendf).xf(Rw, (top + bot) / 2))
    for zz in (-Lb / 2 + 0.25, Lb / 2 - 0.25):
        for yy in (0.44, -0.44):
            for xx in (-0.26, 0.26):
                q = Rw @ (np.array([xx + 0.35 * (zz / (Lb / 2)) ** 2, yy, zz])) + (top + bot) / 2
                E.add("Weapon", perno(q, Rw @ np.array([0, np.sign(yy), 0]), r=0.05, h=0.05))
    tip = Rw @ np.array([0.35, 0, Lb / 2]) + (top + bot) / 2
    E.add("Weapon", ellipsoid((0.95, 0.85, 0.8), "Concreto", tip + P(0, 0.05, 0.1), rot(15, 30, 10), n=6, smooth=False,
                              disp=lambda U: 0.22 * nz(U * 2.5 + 7) + 0.1 * nz(U * 6)))
    for i in range(5):
        a = i * 2 * math.pi / 5 + 0.3
        dd = unit(np.array([math.cos(a), math.sin(a), 0.4 * math.cos(a * 2)]))
        b = tip + dd * 0.5
        E.add("Weapon", tube([b, b + dd * 0.7, b + dd * 0.9 + P(0.2 * math.sin(a), 0.3, 0)], 0.04, "Varilla", sides=5, capseg=1))
    # --- piernas como pilares, pies enormes, grilletes con cadena rota
    for lado, hip, kn, an in ((1, P(0.95, 4.6, 0), P(1.1, 2.6, 0.25), P(1.15, 0.85, 0.1)),
                             (-1, P(-0.95, 4.6, 0), P(-1.15, 2.55, 0.05), P(-1.2, 0.85, -0.12))):
        parte = "LeftLeg" if lado > 0 else "RightLeg"
        E.add(parte, tube([hip, (hip + kn) / 2, kn, kn + (an - kn) * 0.4, an], [0.95, 0.88, 0.78, 0.85, 0.72], SK, sides=13,
                          capseg=2),
              ellipsoid((0.45, 0.35, 0.45), SK, kn + P(0, 0.05, 0.62), n=3),
              rbox((1.4, 2.0, 0.85), SK, an + P(0, -0.42, 0.35), rot(-3), r=0.34, k=(1, 2, 1)),
              ring_loop(an + P(0, 0.05, 0), 0.8, 0.1, ST, seg=18, sides=6))
        fd = P(0, -0.1, 1)
        E.add(parte, dedos(an + P(0, -0.55, 1.2), fd, P(1, 0, 0), 3, 0.4, 0.14, SK, "Garra", curva=P(0, -0.1, 0), abiertos=0.4))
        E.add(parte, solidify(tube([hip + (hip - kn) * 0.1, hip + (kn - hip) * 0.35, hip + (kn - hip) * 0.72],
                                   [1.03, 0.97, 0.9], PA, sides=13, caps=("none", "none")),
                              lambda C2, sh, hip=hip, kn=kn: (seg_dist(C2, hip, kn)[1] < 0.62 + 0.15 * nz(C2 * 3))
                              & (nz(C2 * 3 + 5) > -0.5), 0.05))
    for i in range(4):
        c = P(1.55 + 0.26 * i, 0.12 + 0.05 * (i % 2), 0.3 - 0.12 * i)
        E.add("LeftLeg", ring_loop(c, (0.17, 0.11), 0.04, "Cadena", R=rot(90 * (i % 2), 0, 20), seg=8, sides=4))
    return E, dict(target=(0, 0, 5.4), dist=1.6)


BUILDERS = {
    "zombi_rapido_hd": zombi_rapido,
    "zombi_blindado_hd": zombi_blindado,
    "zombi_berserk_hd": zombi_berserk,
    "zombi_radiactivo_hd": zombi_radiactivo,
    "zombi_gigante_hd": zombi_gigante,
}


# ------------------------------------------------------------------ exportación
def glb_stats(path):
    with open(path, "rb") as f:
        data = f.read()
    ln = struct.unpack_from("<I", data, 12)[0]
    js = json.loads(data[20:20 + ln])
    v = t = 0
    for m in js["meshes"]:
        for p in m["primitives"]:
            v += js["accessors"][p["attributes"]["POSITION"]]["count"]
            t += js["accessors"][p["indices"]]["count"] // 3
    return v, t


def to_blender(E):
    import bpy
    import lib_torretas as L
    mats = {}
    objs = []
    for parte, shells in E.partes.items():
        if not shells:
            continue
        names, V, F, mi, sm, off = [], [], [], [], [], 0
        for s in shells:
            fm = getattr(s, "fmat", None)
            fm = [s.mat] * len(s.F) if fm is None else list(fm)
            for n in dict.fromkeys(fm):
                if n not in names:
                    names.append(n)
            V.append(s.V)
            F.append(s.F + off)
            off += len(s.V)
            mi += [names.index(n) for n in fm]
            sm += [s.smooth] * len(s.F)
        V = np.concatenate(V) - E.piv[parte]
        F = np.concatenate(F)
        me = bpy.data.meshes.new(parte)
        me.from_pydata(V.tolist(), [], F.tolist())
        me.update()
        for n in names:
            if n not in mats:
                col, met, rough, emi = MATS[n]
                mats[n] = bpy.data.materials.get(n) or L.material(n, col, met, rough, emi, 5.0)
            me.materials.append(mats[n])
        me.polygons.foreach_set("material_index", mi)
        me.polygons.foreach_set("use_smooth", sm)
        ob = bpy.data.objects.new(parte, me)
        bpy.context.scene.collection.objects.link(ob)
        ob.location = E.piv[parte].tolist()
        objs.append(ob)
    return objs


def build(nm):
    E, cam = BUILDERS[nm]()
    ok, info = revisar(E.todas())
    print(f"{nm}: {info['triangulos']} triángulos, {info['vertices']} vértices, {info['piezas']} piezas")
    for p in info["problemas"]:
        print("   PROBLEMA:", p)
    if os.environ.get("SOLO_REVISAR"):
        por = {}
        for parte, shells in E.partes.items():
            for s in shells:
                fm = getattr(s, "fmat", None)
                for n in ([s.mat] * s.tris() if fm is None else fm):
                    por[(parte, n)] = por.get((parte, n), 0) + 1
        for k, v in sorted(por.items(), key=lambda kv: -kv[1]):
            print(f"   {k[0]:9s} {k[1]:16s} {v}")
        return info
    if not ok:
        raise SystemExit(f"{nm}: no pasa la revisión, no se exporta")
    import lib_torretas as L
    L.reset()
    objs = to_blender(E)
    out = os.path.join(HERE, nm)
    L.export(out, nm, objs)
    v, t = glb_stats(os.path.join(out, nm + ".glb"))
    info["glb_vertices"], info["glb_triangulos"] = v, t
    print(f"   .glb: {t} triángulos, {v} vértices")
    with open(os.path.join(out, "revision.json"), "w") as f:
        json.dump(info, f, indent=2, ensure_ascii=False)
    if not os.environ.get("NO_RENDER"):
        L.render(out, **cam)
    return info


def foto_grupal(path=os.path.join(HERE, "enemigos_hd.png")):
    """Importa los 5 .glb ya exportados y los renderiza juntos, en fila."""
    import bpy
    import lib_torretas as L
    L.reset()
    xs = {"zombi_rapido_hd": -7.2, "zombi_blindado_hd": -3.9, "zombi_berserk_hd": 0.0,
          "zombi_radiactivo_hd": 3.9, "zombi_gigante_hd": 9.0}
    for nm, x in xs.items():
        antes = set(bpy.data.objects)
        bpy.ops.import_scene.gltf(filepath=os.path.join(HERE, nm, nm + ".glb"))
        for o in set(bpy.data.objects) - antes:
            if o.parent is None:
                o.location.x += x
    L.render(os.path.dirname(path), target=(2.0, 0, 4.6), dist=3.45, res=1400,
             views={os.path.splitext(os.path.basename(path))[0]: (0.6, -9.5, 0.9)})


if __name__ == "__main__":
    if "--foto" in sys.argv:
        foto_grupal()
        raise SystemExit
    for nm in [a for a in sys.argv[1:] if a in BUILDERS] or list(BUILDERS):
        build(nm)
