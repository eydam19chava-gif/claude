"""Enemigos HD del Tower Defense: 5 zombis R6 (rig de Roblox) con mucho detalle, < 20.000 triángulos.

    zombi_rapido_hd      flaco, mandíbula larga caída, camisa rasgada con costillas, jirones que vuelan
    zombi_blindado_hd    chatarra antidisturbios soldada, casco táctico abollado, escudo rajado
    zombi_berserk_hd     brazos enormes, venas, tendones, cicatrices con grapas, púas de hueso
    zombi_radiactivo_hd  traje hazmat quemado, máscara de gas, pústulas, cristales, brazo tumoral
    zombi_gigante_hd     R6 x2.3 con una viga de acero y concreto atravesándole el puño

Cuerpo R6 estándar: Head, Torso, Left Arm, Right Arm, Left Leg, Right Leg (+ Arma en el gigante),
cada parte en su lugar R6 (Torso 2x2x1 a 3 de altura, brazos y piernas 1x2x1) por la escala del
personaje. La ropa rota va "pintada" en los bloques (cara por cara) y el detalle va encima.

La geometría sale de `malla.py` (todas las piezas son cáscaras cerradas con normales hacia afuera)
y se valida con `malla.revisar` antes de exportar: si hay mallas abiertas, normales invertidas,
caras coplanares superpuestas o más de 20.000 triángulos/vértices, no se exporta.
`armar_r6.lua` (se genera solo) arma el rig R6 en Roblox con los Motor6D estándar.

Uso:  python enemigos_hd.py [nombre ...]      (sin nombres arma los 5)
      NO_RENDER=1 solo exporta;  SOLO_REVISAR=1 solo valida y muestra los números;  --foto foto grupal.
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
from malla import (P, Noise, align, bump, crystal, ellipsoid, rbox, revisar, ring_loop,  # noqa: E402
                   rot, solidify, spike, total, tube, unit)

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
    "Vena": ((0.16, 0.02, 0.09), 0.0, 0.4, None),
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

    def escalar(self, s):
        for p in self.piv:
            self.piv[p] = self.piv[p] * s
        for sh in self.todas():
            sh.V = sh.V * s

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


# ------------------------------------------------------------------ ayudas para el radiactivo y el gigante
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


# ------------------------------------------------------------------ base R6
# Medidas estándar de R6 (en studs, escala 1): Torso 2x2x1 centrado a 3 de altura, brazos y piernas
# 1x2x1, cabeza encima del torso. El personaje mira hacia -Y y su derecha es -X (así, al exportar
# queda con el frente y la derecha que espera un rig R6 de Roblox). Se arma a escala 1 y al final
# se escala todo con `s` (el gigante, el berserk...).
R6 = {
    "Head": P(0, 4.5, 0), "Torso": P(0, 3, 0), "Right Arm": P(-1.5, 3, 0), "Left Arm": P(1.5, 3, 0),
    "Right Leg": P(-0.5, 1, 0), "Left Leg": P(0.5, 1, 0),
}
PIVOTES = {
    "Head": P(0, 4, 0), "Torso": P(0, 3, 0), "Right Arm": P(-1.5, 3.5, 0), "Left Arm": P(1.5, 3.5, 0),
    "Right Leg": P(-0.5, 2, 0), "Left Leg": P(0.5, 2, 0),
}


def bloque(size, c, mat, cell=0.17, r=0.07, R=None):
    """Bloque R6 con bisel, subdividido para poder "pintarle" la ropa rota cara por cara."""
    k = tuple(max(1, round(v / cell)) for v in size)
    return rbox(size, mat, c, R, r=r, k=k)


def borde(nz, z0, amp=0.1, f=5.0, seed=0.0):
    """Caras por debajo de un borde irregular (dobladillo rasgado)."""
    return lambda C, s: C[:, 2] < z0 + amp * nz(C * f + seed)


def roturas(nz, umbral, f=2.4, seed=0.0):
    return lambda C, s: nz(C * f + seed) > umbral


def cerca(puntos, radio, nz=None, amp=0.0):
    def fn(C, s):
        m = np.zeros(len(C), bool)
        for p, r in puntos:
            d = np.linalg.norm(C - np.asarray(p), axis=1)
            m |= d < r * radio + (amp * nz(C * 6) if nz is not None else 0)
        return m
    return fn


def cuerpo_r6(E, mats, anchos=None, cell=0.17):
    """Los 6 bloques R6. mats: parte -> material base. anchos: parte -> (ancho, prof, alto) visual.

    Los bloques quedan separados 1-2 cm (brazos) o metidos dentro del torso (piernas), para que
    nunca haya dos caras en el mismo plano superpuestas (z-fighting)."""
    base = {"Torso": (1.98, 1.0, 2.0), "Head": (1.15, 1.15, 1.15), "Right Arm": (1.0, 1.0, 2.0),
            "Left Arm": (1.0, 1.0, 2.0), "Right Leg": (0.98, 0.98, 2.06), "Left Leg": (0.98, 0.98, 2.06)}
    base.update(anchos or {})
    out = {}
    for parte, size in base.items():
        c = R6[parte].copy()
        if "Arm" in parte:
            c[0] = np.sign(c[0]) * (0.99 + size[0] / 2 + 0.02)
        if "Leg" in parte:
            c[2] = size[2] / 2
        if parte == "Head":
            c[2] = 4.02 + size[2] / 2
        out[parte] = bloque(size, c, mats[parte], cell)
        out[parte].centro, out[parte].size = c, np.array(size)
    return out


def punta_garras(base, n, ancho, largo, d=(0, -0.4, -1), r=0.05, mat="Garra", eje=(1, 0, 0)):
    base, eje = np.asarray(base, float), np.asarray(eje, float)
    return [spike(base + eje * ((i - (n - 1) / 2) / max(n - 1, 1)) * ancho,
                  base + eje * ((i - (n - 1) / 2) / max(n - 1, 1)) * ancho + unit(d) * largo, r, mat, sides=5,
                  bend=P(0, 0, 0.06)) for i in range(n)]


def vena_plana(p0, p1, normal, mat="Vena", r=0.035, onda=0.08, n=9, fase=0.0):
    """Vena serpenteando sobre una cara plana (normal = hacia afuera de la cara)."""
    p0, p1, normal = np.asarray(p0, float), np.asarray(p1, float), unit(normal)
    w = unit(np.cross(p1 - p0, normal))
    pts = [p0 + (p1 - p0) * t + w * onda * math.sin(t * 7 + fase) + normal * r * 0.3 for t in np.linspace(0, 1, n)]
    return tube(pts, [r * 0.5] + [r] * (n - 2) + [r * 0.5], mat, sides=5, capseg=1)


def banda(size, c, mat, r=0.03):
    """Cinturón / grillete: caja apenas más grande que el bloque, lo rodea."""
    return rbox(size, mat, c, r=r, k=(3, 3, 1))


# ------------------------------------------------------------------ 1. Zombi Rápido (R6)
def zombi_rapido():
    SK, CL, PA = "Piel_Rapido", "Camisa_Rota", "Pantalon"
    nz = Noise(11, 2.5)
    E = Enemigo("zombi_rapido_hd", PIVOTES)
    B = cuerpo_r6(E, {"Torso": CL, "Head": SK, "Right Arm": CL, "Left Arm": CL, "Right Leg": PA, "Left Leg": PA},
                  {"Right Arm": (0.74, 0.74, 2.0), "Left Arm": (0.74, 0.74, 2.0),
                   "Right Leg": (0.8, 0.8, 2.06), "Left Leg": (0.8, 0.8, 2.06)}, cell=0.14)
    # torso: camisa con un tajo en diagonal (costillas a la vista), roturas y la columna expuesta atrás
    band = lambda C: C[:, 0] + 0.6 * (C[:, 2] - 3.0)  # noqa: E731
    tajo = lambda C, s: (C[:, 1] < -0.3) & (band(C) > -0.4 + 0.12 * nz(C * 4)) & (band(C) < 0.45 + 0.12 * nz(C * 4 + 2))  # noqa: E731
    espalda = lambda C, s: (C[:, 1] > 0.3) & (np.abs(C[:, 0]) < 0.2 + 0.07 * nz(C * 5)) & (C[:, 2] > 2.5) & (C[:, 2] < 3.85)  # noqa: E731
    B["Torso"].pintar(roturas(nz, 0.42), SK).pintar(tajo, SK).pintar(espalda, SK).pintar(borde(nz, 2.28, 0.06), PA)
    for i, z in enumerate((3.52, 3.26, 3.0, 2.74)):
        x = 0.03 - 0.6 * (z - 3.0)
        E.add("Torso", rbox((0.5 - 0.04 * i, 0.07, 0.075), "Hueso", P(x, z, 0.51), rot(0, -12, 0), r=0.03))
    for z in np.linspace(2.65, 3.7, 6):
        E.add("Torso", rbox((0.17, 0.08, 0.11), "Hueso", P(0, z, -0.51), r=0.03))
    for i, x in enumerate((-0.65, -0.2, 0.3, 0.7)):                             # jirones que cuelgan y vuelan atrás
        b = P(x, 2.08, -0.42)
        E.add("Torso", cinta([b, b + P(0, -0.35, -0.2), b + P(0.06 * x, -0.62, -0.45), b + P(0.1 * x, -0.8, -0.8 - 0.1 * (i % 2))],
                             [0.12, 0.1, 0.07, 0.03], CL, fase=i))
    for i, x in enumerate((-0.55, 0.05, 0.6)):
        b = P(x, 2.05, 0.46)
        E.add("Torso", cinta([b, b + P(0.03, -0.25, 0.02), b + P(-0.04, -0.45, -0.02)], [0.1, 0.08, 0.03], CL, grosor=0.25, fase=i))
    # cabeza: hocico largo, mandíbula caída con dientes, cuencas y ojos brillantes, mechones
    E.add("Torso", B["Torso"])
    H = B["Head"]
    hc = H.centro
    fz = hc[1] - 0.575                                  # plano de la cara (y)
    E.add("Head", H)
    for sx in (-1, 1):
        E.add("Head", rbox((0.3, 0.06, 0.2), "Boca", P(sx * 0.25, hc[2] + 0.12, -fz + 0.01), r=0.02),
              rbox((0.15, 0.05, 0.1), "Ojo_Amarillo", P(sx * 0.25, hc[2] + 0.12, -fz + 0.035), r=0.02))
    E.add("Head", rbox((1.0, 0.2, 0.14), SK, P(0, hc[2] + 0.3, -fz + 0.04), rot(-12), r=0.05),
          rbox((0.96, 0.6, 0.3), SK, P(0, hc[2] - 0.32, -fz + 0.2), r=0.08),
          rbox((0.82, 0.5, 0.2), "Boca", P(0, hc[2] - 0.5, -fz + 0.22), r=0.05))
    hinge, Rj = P(0, hc[2] - 0.55, -fz - 0.2), rot(24)
    E.add("Head", rbox((0.9, 0.95, 0.16), SK, hinge + Rj @ P(0, 0, 0.5), Rj, r=0.05))
    xs = np.linspace(-0.36, 0.36, 5)
    up = [P(x, hc[2] - 0.47, -fz + 0.47) for x in xs] + [P(sx * 0.44, hc[2] - 0.47, -fz + f) for sx in (-1, 1) for f in (0.3, 0.12)]
    E.add("Head", dientes(up, [P(0, -1, 0.1)] * len(up), [0.16 if abs(p[0]) > 0.3 else 0.11 for p in up], 0.035, "Dientes"))
    lo = [hinge + Rj @ P(x, 0.06, 0.9) for x in xs[1:-1]] + [hinge + Rj @ P(sx * 0.4, 0.06, f) for sx in (-1, 1) for f in (0.7, 0.45)]
    E.add("Head", dientes(lo, [Rj @ P(0, 1, -0.1)] * len(lo), [0.1] * len(lo), 0.03, "Dientes"))
    for i, x in enumerate((-0.4, -0.13, 0.13, 0.4)):
        b = P(x, hc[2] + 0.5, -0.5)
        E.add("Head", cinta([b, b + P(0.02, -0.15, -0.25), b + P(0.06 * x, -0.4, -0.45), b + P(0.1 * x, -0.7, -0.6)],
                            [0.09, 0.07, 0.05, 0.02], "Pelo", grosor=0.4, fase=i))
    # brazos flacos: manga rota arriba, piel abajo, tendones y garras
    for parte in ("Right Arm", "Left Arm"):
        A = B[parte]
        c = A.centro
        A.pintar(borde(nz, 3.35, 0.14, seed=c[0]), SK).pintar(roturas(nz, 0.5, seed=c[0] * 3), SK)
        E.add(parte, A)
        for dx in (-0.14, 0.14):
            E.add(parte, tube([P(c[0] + dx, 2.25, 0.37), P(c[0] + dx * 0.8, 2.75, 0.375), P(c[0] + dx * 0.6, 3.1, 0.37)],
                              0.03, SK, sides=5, capseg=1))
        E.add(parte, punta_garras(P(c[0], 2.05, 0.2), 4, 0.5, 0.32, d=P(0, -1, 0.35), r=0.045))
        b = P(c[0], 3.3, -0.35)
        E.add(parte, cinta([b, b + P(0, -0.3, -0.15), b + P(0.05 * np.sign(c[0]), -0.55, -0.4)], [0.1, 0.07, 0.03], CL))
    # piernas: pantalón hasta la rodilla, roturas, pies descalzos con garras
    for parte in ("Right Leg", "Left Leg"):
        L = B[parte]
        c = L.centro
        L.pintar(borde(nz, 0.95, 0.15, seed=c[0] * 2), SK).pintar(roturas(nz, 0.5, seed=c[0] * 5 + 1), SK)
        E.add(parte, L, punta_garras(P(c[0], 0.08, 0.4), 3, 0.5, 0.22, d=P(0, 1, 0.05), r=0.05))
        b = P(c[0], 1.05, -0.4)
        E.add(parte, cinta([b, b + P(0, -0.25, -0.2), b + P(0.05, -0.45, -0.45)], [0.1, 0.07, 0.03], PA))
    return E, 1.0


# ------------------------------------------------------------------ 2. Zombi Blindado (R6)
def zombi_blindado():
    SK, TE, AR, RU = "Piel_Blindado", "Tela_Tactica", "Blindaje", "Oxido"
    nz = Noise(21, 2.5)
    E = Enemigo("zombi_blindado_hd", PIVOTES)
    B = cuerpo_r6(E, {"Torso": TE, "Head": SK, "Right Arm": TE, "Left Arm": TE, "Right Leg": TE, "Left Leg": TE},
                  cell=0.2)
    E.add("Torso", B["Torso"])
    # peto abollado, placa del abdomen soldada, espaldar con franja, correas y cinturón
    E.add("Torso",
          placa((2.2, 0.22, 1.12), AR, P(0, 3.42, 0.6), rot(0, 0, -3), curva=0.1, k=(6, 1, 4),
                abolladuras=[(np.array([0.45, -0.1, 0.2]), 0.16, 0.07), (np.array([-0.5, -0.1, -0.25]), 0.12, 0.05),
                             (np.array([0.05, -0.1, -0.3]), 0.07, 0.04), (np.array([-0.2, -0.1, 0.35]), 0.06, 0.035)]),
          placa((1.7, 0.16, 0.42), RU, P(0.05, 2.62, 0.58), rot(0, 0, 4), curva=0.06, k=(5, 1, 2)),
          placa((2.0, 0.18, 1.3), AR, P(0, 3.3, -0.6), rot(0, 0, 2), curva=-0.08, k=(5, 1, 4)),
          placa((1.6, 0.03, 0.16), "Advertencia", P(0, 3.6, -0.705), rot(0, 0, 2), curva=-0.06, k=(4, 1, 1), r=0.01),
          cordon([P(-0.8, 2.84, 0.66), P(0, 2.82, 0.7), P(0.85, 2.86, 0.66)], r=0.035, n=26),
          banda((2.08, 1.1, 0.26), P(0, 2.2, 0), "Correa"),
          rbox((1.3, 0.85, 0.2), AR, P(0, 4.07, 0.02), r=0.05))
    for lado in (-1, 1):
        E.add("Torso", rbox((0.1, 1.25, 0.16), "Correa", P(lado * 0.955, 3.5, 0), r=0.03),
              rbox((0.1, 1.25, 0.16), "Correa", P(lado * 0.955, 3.0, 0), r=0.03))
    for x, f in ((-0.55, 0.62), (0.05, 0.62), (0.6, 0.62), (0.3, -0.62)):
        E.add("Torso", rbox((0.34, 0.16, 0.3), TE, P(x, 2.14, f), r=0.05))
    for x, z in ((-0.9, 3.9), (0.88, 3.92), (-0.9, 2.95), (0.9, 2.9)):
        E.add("Torso", perno(P(x, z, 0.72 - 0.02 * abs(x)), P(0, 0, 1)))
    # brazo izquierdo: hombrera de 3 láminas con remaches + escudo antidisturbios rajado
    A = B["Left Arm"]
    A.pintar(borde(nz, 2.4, 0.03), "Correa")
    E.add("Left Arm", A)
    sh = P(1.52, 3.95, 0)
    for i in range(3):
        R = rot(0, 18 + 14 * i, 0)
        c = sh + P(0.12 * i, 0.02 - 0.2 * i, 0)
        rad = np.array([0.72 - 0.05 * i, 0.68 - 0.04 * i, 0.46])
        E.add("Left Arm", domo(rad, AR if i != 1 else RU, c, R, lambda U: U[:, 2] > -0.05, 0.06, n=8))
        for a in (-0.7, 0, 0.7):
            p = c + R @ (rad * [math.cos(1.2) * math.cos(a), math.cos(1.2) * math.sin(a), math.sin(1.2)] * 1.02)
            E.add("Left Arm", ellipsoid((0.04, 0.04, 0.035), "Tornillo", p, R, n=2))
    shield_c, bend = P(1.55, 2.85, 0.64), 0.12
    E.add("Left Arm", placa((1.3, 0.08, 2.3), "Vidrio", shield_c, None, curva=bend, k=(6, 1, 8), r=0.035,
                            abolladuras=[(np.array([0.3, -0.04, 0.5]), 0.1, 0.03)]))

    def sobre_escudo(size, mat, z, gap=0.006):
        s = rbox(size, mat, r=0.01, k=(4, 1, 1))
        s.deform(lambda V: V + np.outer((V[:, 0] / 0.65) ** 2 * bend, [0, 1, 0]) + [0, -0.04 - size[1] / 2 - gap, z])
        return s.xf(None, shield_c)
    E.add("Left Arm", sobre_escudo((0.8, 0.035, 0.3), "Tela_Tactica", 0.72), sobre_escudo((1.2, 0.02, 0.16), "Advertencia", -0.45),
          rbox((0.68, 0.04, 0.24), "Vidrio", shield_c + P(0, 0.72, 0.11), r=0.015))
    crack = [np.array(v) for v in ([0.62, -0.058, 1.05], [0.35, -0.056, 0.82], [0.42, -0.056, 0.45], [0.1, -0.056, 0.2], [0.18, -0.056, -0.1])]
    E.add("Left Arm", tube([shield_c + p + [0, (p[0] / 0.65) ** 2 * bend, 0] for p in crack], 0.016, "Tornillo", sides=4, capseg=1))
    # brazo derecho: manga táctica arriba, carne con chapa oxidada atornillada, garras; chapa de auto en el hombro
    A = B["Right Arm"]
    A.pintar(borde(nz, 3.1, 0.15, seed=4), SK)
    E.add("Right Arm", A)
    E.add("Right Arm", placa((0.8, 0.07, 1.0), RU, P(-2.04, 2.65, 0), rot(0, 0, -90) @ rot(4), curva=0.04, k=(2, 1, 3), r=0.025),
          placa((1.2, 1.1, 0.1), RU, P(-1.6, 4.05, 0), rot(0, -22, 0), k=(3, 3, 1), r=0.03,
                abolladuras=[(np.array([0.2, 0.1, 0.05]), 0.15, 0.05)]),
          cordon([P(-1.08, 4.3, -0.45), P(-1.08, 4.3, 0.45)], r=0.03, n=12))
    for z, f in ((2.3, -0.3), (2.3, 0.3), (3.0, 0.0)):
        p = P(-2.09, z, f)
        E.add("Right Arm", perno(p, P(-1, 0, 0)), ellipsoid((0.03, 0.05, 0.06), "Sangre", p + P(0.02, -0.1, 0), n=2))
    for f in (-0.35, 0.35):
        E.add("Right Arm", perno(P(-1.55, 4.24, f), rot(0, -22, 0) @ np.array([0, 0, 1])))
    E.add("Right Arm", punta_garras(P(-1.51, 2.05, 0.2), 4, 0.6, 0.3, d=P(0, -1, 0.3), r=0.05))
    # piernas: rodilleras, canilleras, botas con suela; placa soldada en el muslo izquierdo
    for parte in ("Right Leg", "Left Leg"):
        L = B[parte]
        x = L.centro[0]
        E.add(parte, L,
              domo((0.42, 0.3, 0.36), AR, P(x, 1.15, 0.45), None, lambda U: U[:, 1] < -0.1, 0.06, n=6,
                   disp=lambda U: -0.08 * np.exp(-np.sum((U - [0.3, -0.8, 0.3]) ** 2, 1) / 0.05)),
              placa((0.8, 0.07, 0.55), AR if x > 0 else RU, P(x, 0.78, 0.55), None, curva=0.06, k=(3, 1, 3), r=0.025),
              rbox((1.01, 1.33, 0.62), "Bota", P(np.sign(x) * 0.545, 0.32, 0.1), r=0.1, k=(2, 2, 1)),
              rbox((1.03, 1.3, 0.1), "Correa", P(np.sign(x) * 0.555, 0.045, 0.1), r=0.035, k=(2, 2, 1)))
        for z in (0.45, 0.27):
            E.add(parte, rbox((1.02, 0.08, 0.06), "Correa", P(np.sign(x) * 0.545, z, 0.73), r=0.02))
    E.add("Left Leg", placa((0.8, 0.07, 0.55), RU, P(0.5, 1.65, 0.54), rot(0, 0, 6), curva=0.05, k=(3, 1, 3), r=0.025),
          cordon([P(0.12, 1.95, 0.6), P(0.88, 1.98, 0.6)], r=0.03, n=12))
    # cabeza: cara podrida (ojos rojos, dientes) bajo un casco táctico abollado con visor levantado y rajado
    H = B["Head"]
    hc = H.centro
    fz = -hc[1] + 0.575
    E.add("Head", H, rbox((0.7, 0.06, 0.22), "Boca", P(0, hc[2] - 0.32, fz + 0.01), r=0.03))
    for sx in (-1, 1):
        E.add("Head", rbox((0.16, 0.05, 0.1), "Ojo_Rojo", P(sx * 0.24, hc[2] - 0.02, fz + 0.02), r=0.02))
    xs = np.linspace(-0.28, 0.28, 6)
    E.add("Head", dientes([P(x, hc[2] - 0.22, fz + 0.03) for x in xs], [P(0, -1, 0)] * 6, [0.09] * 6, 0.028, "Dientes"),
          dientes([P(x, hc[2] - 0.42, fz + 0.03) for x in xs[1:-1]], [P(0, 1, 0)] * 4, [0.07] * 4, 0.026, "Dientes"))
    dents = [unit(np.array(v)) for v in ([0.55, -0.35, 0.75], [-0.65, 0.3, 0.6], [0.1, 0.6, 0.8])]
    hdisp = lambda U: sum(-0.13 * np.exp(-np.sum((U - dd) ** 2, 1) / 0.025) for dd in dents)  # noqa: E731
    hcen = P(0, hc[2] + 0.1, 0)
    E.add("Head", domo((0.87, 0.87, 0.66), AR, hcen, None, lambda U: U[:, 2] > 0.05, 0.07, n=12, disp=hdisp))
    for sx in (-1, 1):
        E.add("Head", tube([P(sx * 0.56, hc[2] - 0.05, 0), P(sx * 0.7, hc[2] - 0.05, 0)], 0.22, "Correa", sides=12,
                           caps=("flat", "flat")),
              rbox((0.06, 0.55, 0.08), AR, P(sx * 0.82, hc[2] + 0.2, 0.05), rot(0, sx * 10, 0), r=0.02),
              tube([P(sx * 0.6, hc[2] - 0.2, 0.2), P(sx * 0.45, hc[2] - 0.55, 0.45), P(0, hc[2] - 0.6, 0.6)], 0.025, "Correa", sides=5, capseg=1))
    E.add("Head", rbox((0.22, 0.14, 0.14), AR, hcen + P(0, 0.62, 0.62), rot(-50), r=0.03),
          rbox((0.08, 0.14, 0.08), "Tornillo", hcen + P(0, 0.72, 0.68), rot(-50), r=0.02))
    Rv = rot(-35)
    E.add("Head", domo((0.93, 0.93, 0.72), "Vidrio", hcen, Rv,
                       lambda U: (U[:, 1] < -0.4) & (U[:, 2] > -0.05) & (U[:, 2] < 0.5), 0.035, n=12))
    vc = [unit(np.array(v)) * [0.935, 0.935, 0.725] for v in ([0.25, -0.9, 0.42], [0.12, -0.95, 0.3], [0.2, -0.9, 0.15], [0.05, -0.92, 0.02])]
    E.add("Head", tube([hcen + Rv @ p for p in vc], 0.012, "Tornillo", sides=4, capseg=1))
    return E, 1.1


# ------------------------------------------------------------------ 3. Zombi Berserk (R6)
def zombi_berserk():
    SK, PA = "Piel_Berserk", "Pantalon_Berserk"
    nz = Noise(31, 2.5)
    E = Enemigo("zombi_berserk_hd", PIVOTES)
    B = cuerpo_r6(E, {"Torso": SK, "Head": SK, "Right Arm": SK, "Left Arm": SK, "Right Leg": PA, "Left Leg": PA},
                  {"Torso": (1.98, 1.1, 2.0), "Head": (1.0, 1.0, 1.0), "Right Arm": (1.3, 1.2, 2.0), "Left Arm": (1.3, 1.2, 2.0),
                   "Right Leg": (0.98, 1.0, 2.06), "Left Leg": (0.98, 1.0, 2.06)}, cell=0.18)
    B["Torso"].pintar(borde(nz, 2.32, 0.07), PA)
    E.add("Torso", B["Torso"])
    fr = 0.55
    # pectorales, abdominales, trapecios
    for sx in (-1, 1):
        E.add("Torso", rbox((0.92, 0.3, 0.66), SK, P(sx * 0.47, 3.5, fr - 0.02), rot(8, 0, sx * 4), r=0.13),
              rbox((0.78, 0.8, 0.36), SK, P(sx * 0.55, 4.06, -0.05), rot(0, sx * 22, 0), r=0.14))
        for z in (3.02, 2.68):
            E.add("Torso", rbox((0.4, 0.18, 0.28), SK, P(sx * 0.22, z, fr), r=0.08))
    # cicatrices de garra (tejido rosado en relieve) con grapas
    for (x0, z0), (x1, z1) in (((-0.8, 3.75), (-0.1, 3.3)), ((-0.72, 3.55), (0.02, 3.12)), ((0.25, 3.78), (0.85, 3.3))):
        a, b = P(x0, z0, fr + 0.14), P(x1, z1, fr + 0.14)
        E.add("Torso", tube([a, (a + b) / 2 + P(0, 0, 0.02), b], 0.04, "Cicatriz", sides=5, capseg=1, aspect=(0.6, 1), up=(0, 1, 0)))
        d = unit(b - a)
        w = unit(np.cross(d, [0, 1, 0]))
        for t in (0.2, 0.5, 0.8):
            p = a + (b - a) * t + P(0, 0, 0.03)
            E.add("Torso", tube([p - w * 0.1 + P(0, 0, -0.02), p + P(0, 0, 0.01), p + w * 0.1 + P(0, 0, -0.02)], 0.014, "Cadena",
                                sides=4, caps=("flat", "flat")))
    # púas de hueso saliendo de la espalda con carne abierta
    for i, (x, z) in enumerate(((0.1, 3.7), (-0.2, 3.25), (0.15, 2.8))):
        b = P(x, z, -0.55)
        E.add("Torso", ellipsoid((0.16, 0.06, 0.16), "Musculo", b, n=3),
              spike(b + P(0, 0, 0.1), b + P(0.12 * (i - 1), 0.35, -0.55), 0.1, "Hueso", sides=6))
    # cinturón con cadena colgando
    E.add("Torso", banda((2.06, 1.18, 0.2), P(0, 2.22, 0), "Correa"))
    for i in range(6):
        E.add("Torso", ring_loop(P(0.55 - 0.05 * i, 2.08 - 0.1 * i + 0.004 * i * i, 0.62 - 0.012 * i), (0.07, 0.04), 0.017,
                                 "Cadena", R=rot(0, 90 * (i % 2), 70), seg=8, sides=4))
    # cabeza hundida entre los trapecios, gruñendo
    H = B["Head"]
    hc = H.centro
    H.xf(None, P(0, -0.12, 0.12))
    hc = hc + P(0, -0.12, 0.12)
    fz = -hc[1] + 0.5
    E.add("Head", H, rbox((0.95, 0.24, 0.18), SK, P(0, hc[2] + 0.2, fz + 0.06), rot(-15), r=0.06),
          rbox((0.62, 0.06, 0.26), "Boca", P(0, hc[2] - 0.25, fz + 0.01), r=0.03))
    for sx in (-1, 1):
        E.add("Head", rbox((0.16, 0.05, 0.08), "Ojo_Rojo", P(sx * 0.22, hc[2] + 0.04, fz + 0.02), r=0.02))
    xs = np.linspace(-0.25, 0.25, 6)
    E.add("Head", dientes([P(x, hc[2] - 0.13, fz + 0.03) for x in xs], [P(0, -1, 0)] * 6, [0.1 if abs(x) > 0.2 else 0.08 for x in xs], 0.03, "Dientes"),
          dientes([P(x, hc[2] - 0.37, fz + 0.03) for x in xs], [P(0, 1, 0)] * 6, [0.09 if abs(x) > 0.2 else 0.07 for x in xs], 0.028, "Dientes"))
    # brazos enormes: bíceps, antebrazos, venas saltadas, tendones y puños con nudillos pelados
    for parte in ("Right Arm", "Left Arm"):
        A = B[parte]
        c = A.centro
        sx = np.sign(c[0])
        out = c[0] + sx * 0.65
        if sx > 0:
            A.pintar(lambda C, s: (C[:, 2] > 3.45) & (C[:, 1] < 0.1) & (nz(C * 4 + 2) > -0.1), "Musculo")
        E.add(parte, A,
              rbox((1.0, 0.34, 0.72), SK, P(c[0], 3.35, 0.62), rot(4), r=0.14),
              rbox((1.1, 0.3, 0.6), SK, P(c[0], 2.62, 0.62), r=0.12),
              rbox((1.45, 1.35, 0.62), SK, P(c[0], 2.06, 0.03), r=0.14))
        for k in range(4):
            x = c[0] + (k - 1.5) * 0.32
            E.add(parte, rbox((0.28, 0.2, 0.28), SK, P(x, 1.93, 0.72), r=0.07),
                  ellipsoid((0.07, 0.04, 0.05), "Hueso", P(x, 1.97, 0.83), n=2))
        for f, fase in ((-0.25, 0), (0.25, 2)):
            E.add(parte, vena_plana(P(out, 3.8, f), P(out, 2.4, f + 0.1), P(sx, 0, 0), fase=fase))
        E.add(parte, vena_plana(P(c[0] - 0.3, 3.62, 0.79), P(c[0] + 0.2, 3.05, 0.79), P(0, -1, 0), r=0.03, fase=1),
              vena_plana(P(c[0] + 0.3, 2.85, 0.77), P(c[0] - 0.1, 2.35, 0.77), P(0, -1, 0), r=0.03, fase=3))
        for dx in (-0.3, 0.0, 0.3):
            E.add(parte, tube([P(c[0] + dx, 2.4, 0.77), P(c[0] + dx * 1.1, 2.85, 0.78)], 0.035, SK, sides=5, capseg=1))
    for i in range(4):
        a = P(1.4 + 0.08 * i, 3.9 - 0.08 * i, 0.61)
        E.add("Left Arm", tube([a, a + P(0.2, -0.35, 0)], 0.05, "Musculo", sides=5, capseg=1))
    # piernas con pantalón roto y pies con garras
    for parte in ("Right Leg", "Left Leg"):
        L = B[parte]
        c = L.centro
        L.pintar(roturas(nz, 0.45, seed=c[0] * 4), SK).pintar(borde(nz, 0.45, 0.12, seed=c[0]), SK)
        E.add(parte, L, punta_garras(P(c[0], 0.08, 0.48), 3, 0.55, 0.22, d=P(0, 1, 0.05), r=0.06),
              vena_plana(P(c[0] + 0.2, 1.4, 0.51), P(c[0] - 0.1, 0.6, 0.51), P(0, -1, 0), r=0.025))
    return E, 1.2


# ------------------------------------------------------------------ 4. Zombi Radiactivo (R6)
def zombi_radiactivo():
    HZ, BU, GO, SK = "Hazmat", "Hazmat_Quemado", "Goma", "Piel_Toxica"
    nz = Noise(41, 2.5)
    rng = np.random.default_rng(4)
    E = Enemigo("zombi_radiactivo_hd", PIVOTES)
    B = cuerpo_r6(E, {"Torso": HZ, "Head": HZ, "Right Arm": "Tumor", "Left Arm": HZ, "Right Leg": HZ, "Left Leg": HZ},
                  cell=0.17)
    quem = roturas(nz, 0.3, f=2.0, seed=7)
    # torso: traje con quemaduras, agujeros con carne y pústulas, parche radiactivo, cierre
    hoyos = [(P(-0.5, 3.5, 0.5), 0.3), (P(0.55, 2.55, 0.5), 0.25), (P(0.4, 3.3, -0.5), 0.35)]
    B["Torso"].pintar(quem, BU).pintar(cerca(hoyos, 1.7, nz, 0.08), BU).pintar(cerca(hoyos, 1.0, nz, 0.06), SK)
    E.add("Torso", B["Torso"])
    for p, r in hoyos:
        n = P(0, 0, 1) if p[1] < 0 else P(0, 0, -1)
        E.add("Torso", pustulas(p + n * 0.02, r * 0.8, 6, rng, normal=n, tam=(0.05, 0.12)))
    E.add("Torso", racimo(P(0.4, 3.3, -0.52), P(0.3, 0.4, -1), 5, rng, largo=(0.5, 0.9), grosor=(0.09, 0.15)))
    E.add("Torso", tube([P(0.45, 3.55, 0.49), P(0.45, 3.55, 0.56)], 0.24, "Goma", sides=16, caps=("flat", "flat"), smooth=False),
          rbox((0.06, 0.035, 1.5), "Goma", P(-0.05, 3.05, 0.51), r=0.012))
    for k in range(3):
        a = k * 2 * math.pi / 3 + 0.5
        E.add("Torso", ellipsoid((0.075, 0.02, 0.075), "Advertencia", P(0.45 + 0.11 * math.cos(a), 3.55 + 0.11 * math.sin(a), 0.565), n=2))
    for x, f, L in ((-0.7, 0.51, 0.35), (-0.2, 0.51, 0.22), (0.3, 0.51, 0.45), (0.8, 0.2, 0.3), (0.5, -0.51, 0.28), (-0.5, -0.51, 0.4)):
        E.add("Torso", gota(P(x, 2.02, f), L, 0.04))
    # tanque reventado en la espalda con cristales y manguera corrugada a la máscara
    tk = P(-0.4, 3.1, -0.82)
    E.add("Torso", tube([tk + P(0, -0.6, 0), tk + P(0, 0.6, 0)], 0.3, "Tanque", sides=14),
          tube([tk + P(0, 0.85, 0), tk + P(0, 0.98, 0)], 0.08, "Tanque", sides=8, caps=("flat", "flat")),
          banda((0.66, 0.66, 0.08), tk + P(0, 0.35, 0), "Correa"), banda((0.66, 0.66, 0.08), tk + P(0, -0.35, 0), "Correa"),
          racimo(tk + P(-0.18, 0.1, -0.2), P(-0.6, 0.3, -1), 4, rng, largo=(0.4, 0.7)))
    hose = [tk + P(0, 0.98, 0), P(-0.55, 4.3, -0.6), P(-0.75, 4.1, 0.2), P(-0.35, 4.28, 0.78)]
    hp = np.array([hose[i] * (1 - t) + hose[i + 1] * t for i in range(3) for t in np.linspace(0, 1, 7)[:-1]] + [hose[-1]])
    E.add("Torso", tube(hp, 0.065 + 0.015 * np.cos(np.arange(len(hp)) * math.pi), GO, sides=8, capseg=1))
    # cabeza: capucha, máscara de gas (un lente roto con el ojo brillando), filtros, cristales
    H = B["Head"]
    hc = H.centro
    fz = -hc[1] + 0.575
    H.pintar(roturas(nz, 0.35, seed=3), BU)
    E.add("Head", H, rbox((0.86, 0.26, 0.72), GO, P(0, hc[2] - 0.06, fz + 0.08), r=0.1))
    for sx in (-1, 1):
        lc = P(sx * 0.22, hc[2] + 0.1, fz + 0.2)
        E.add("Head", tube([lc - P(0, 0, 0.05), lc + P(0, 0, 0.05)], 0.17, GO, sides=16, caps=("flat", "flat")))
        if sx > 0:
            E.add("Head", tube([lc + P(0, 0, 0.04), lc + P(0, 0, 0.07)], 0.13, "Lente", sides=16, caps=("flat", "flat"), smooth=False))
        else:
            E.add("Head", ellipsoid((0.1, 0.06, 0.1), "Pustula", lc + P(0, 0, 0.05), n=3),
                  tube([lc + P(0.1, 0.1, 0.07), lc + P(-0.04, 0, 0.09), lc + P(0.08, -0.1, 0.08)], 0.015, "Lente", sides=4, capseg=1))
        a, b = P(sx * 0.3, hc[2] - 0.25, fz + 0.2), P(sx * 0.55, hc[2] - 0.45, fz + 0.45)
        E.add("Head", tube([a, b], 0.15, "Tanque", sides=12, caps=("flat", "flat")))
        for t in (0.35, 0.65, 0.95):
            E.add("Head", ring_loop(a + (b - a) * t, 0.15, 0.022, "Tanque", R=align(b - a), seg=12, sides=4))
        if sx < 0:
            E.add("Head", racimo(b + unit(b - a) * 0.02, b - a, 3, rng, largo=(0.25, 0.4), grosor=(0.04, 0.06), abre=0.4))
    E.add("Head", racimo(P(0.2, hc[2] + 0.57, -0.1), P(0.3, 0.2, 1), 3, rng, largo=(0.4, 0.7), grosor=(0.07, 0.11)),
          pustulas(P(-0.58, hc[2] + 0.1, -0.1), 0.2, 5, rng, normal=P(-1, 0, 0)),
          gota(P(0.3, hc[2] - 0.42, fz + 0.1), 0.3, 0.035), gota(P(-0.12, hc[2] - 0.42, fz + 0.15), 0.22, 0.03))
    # brazo izquierdo: manga con arrugas y guante; derecho: mutado con tumores, pústulas, cristales y garras
    A = B["Left Arm"]
    A.pintar(quem, BU).pintar(borde(nz, 2.4, 0.03), GO)
    E.add("Left Arm", A, gota(P(1.7, 2.02, 0.3), 0.35, 0.035), gota(P(1.3, 2.02, -0.2), 0.25, 0.03),
          pustulas(P(2.0, 3.4, 0.1), 0.2, 5, rng, normal=P(1, 0, 0.3)))
    for z in (3.3, 2.95):
        E.add("Left Arm", banda((1.06, 1.06, 0.07), P(1.51, z, 0), HZ))
    A = B["Right Arm"]
    A.pintar(lambda C, s: C[:, 2] > 3.45 + 0.15 * nz(C * 5), HZ).pintar(lambda C, s: (C[:, 2] > 3.3) & (nz(C * 3) > 0.2), BU)
    E.add("Right Arm", A)
    tum = [(P(-1.9, 2.9, 0.3), 0.45), (P(-1.55, 2.5, 0.45), 0.4), (P(-2.0, 2.35, -0.25), 0.38), (P(-1.3, 2.8, -0.35), 0.3),
           (P(-1.6, 3.2, 0.5), 0.28)]
    for i, (c, r) in enumerate(tum):
        E.add("Right Arm", ellipsoid((r, r * 0.9, r * 1.1), "Tumor", c, rot(10 * i, 20 * i, 0), n=6,
                                     disp=lambda U, i=i: 0.15 * np.maximum(0, nz(U * 2 + i)) + 0.05 * nz(U * 5)))
    E.add("Right Arm", pustulas(P(-1.8, 2.7, 0.55), 0.3, 9, rng, normal=P(-0.3, 0, 1), tam=(0.05, 0.13)),
          racimo(P(-2.05, 3.0, -0.1), P(-1, 0.3, -0.3), 4, rng, largo=(0.4, 0.75)),
          punta_garras(P(-1.51, 2.02, 0.25), 4, 0.7, 0.5, d=P(0, -1, 0.45), r=0.06))
    # piernas: botas de goma; la derecha con la rodilla deshecha
    for parte in ("Right Leg", "Left Leg"):
        L = B[parte]
        x = L.centro[0]
        L.pintar(quem, BU)
        if x < 0:
            L.pintar(cerca([(P(x, 1.15, 0.5), 0.3)], 1.0, nz, 0.08), SK)
        E.add(parte, L, rbox((1.02, 1.25, 0.7), GO, P(np.sign(x) * 0.54, 0.36, 0.06), r=0.09, k=(2, 2, 1)),
              rbox((1.03, 1.2, 0.09), "Correa", P(np.sign(x) * 0.555, 0.04, 0.06), r=0.03, k=(2, 2, 1)))
    E.add("Right Leg", pustulas(P(-0.5, 1.15, 0.52), 0.2, 6, rng, normal=P(0, 0, 1)),
          racimo(P(-0.99, 1.5, 0.1), P(-1, 0.3, 0.2), 3, rng, largo=(0.3, 0.55)))
    E.add("Left Leg", gota(P(0.8, 1.6, 0.5), 0.3, 0.035), gota(P(0.3, 1.25, 0.5), 0.22, 0.03))
    return E, 1.0


# ------------------------------------------------------------------ 5. Zombi Gigante (R6)
def zombi_gigante():
    SK, PA, ST = "Piel_Gigante", "Pantalon_Gigante", "Acero"
    nz = Noise(51, 2.2)
    E = Enemigo("zombi_gigante_hd", {**PIVOTES, "Arma": P(-1.62, 1.95, 0.1)})
    B = cuerpo_r6(E, {"Torso": SK, "Head": SK, "Right Arm": SK, "Left Arm": SK, "Right Leg": PA, "Left Leg": PA},
                  {"Torso": (1.98, 1.2, 2.0), "Head": (1.1, 1.1, 1.1), "Right Arm": (1.2, 1.15, 2.0), "Left Arm": (1.2, 1.15, 2.0),
                   "Right Leg": (0.98, 1.1, 2.06), "Left Leg": (0.98, 1.1, 2.06)}, cell=0.16)
    fr = 0.6
    B["Torso"].pintar(borde(nz, 2.35, 0.08), PA)
    E.add("Torso", B["Torso"])
    # panza cosida, pectorales, cadena cruzada apoyada sobre el cuerpo, varillas clavadas en la espalda
    bc, br = P(0, 2.75, 0.45), np.array([0.9, 0.42, 0.62])
    E.add("Torso", ellipsoid(br, SK, bc, n=8, disp=lambda U: 0.03 * nz(U * 3)))
    for sx in (-1, 1):
        E.add("Torso", rbox((0.9, 0.3, 0.6), SK, P(sx * 0.47, 3.55, fr - 0.04), rot(8, 0, sx * 4), r=0.13),
              rbox((0.8, 0.9, 0.34), SK, P(sx * 0.55, 4.05, -0.05), rot(0, sx * 22, 0), r=0.14))
    sc = [bc + unit(np.array(v)) * br * 1.0 for v in ([-0.7, -0.6, 0.3], [-0.2, -0.95, 0.1], [0.3, -0.9, -0.15], [0.7, -0.6, -0.35])]
    E.add("Torso", tube(sc, 0.035, "Cicatriz", sides=5, capseg=1))
    for i in range(len(sc) - 1):
        p = (sc[i] + sc[i + 1]) / 2
        n = unit(p - bc)
        w = unit(np.cross(sc[i + 1] - sc[i], n))
        E.add("Torso", tube([p - w * 0.1 + n * 0.005, p + n * 0.035, p + w * 0.1 + n * 0.005], 0.015, "Cadena", sides=4, caps=("flat", "flat")))
    path, nrms = [], []
    for t in np.linspace(0, 1, 18):
        p0 = P(0.92, 4.0, fr + 0.03) * (1 - t) + P(-0.95, 2.3, fr + 0.03) * t
        p, n = sobre(p0, bc + P(0, 0, -0.3), [(bc, np.eye(3), br)], paso=0.01, extra=0.01)
        pecho = abs(p0[0] - 0.47 * np.sign(p0[0])) < 0.45 and 3.25 < p0[2] < 3.85
        if pecho:
            p = p + P(0, 0, 0.14)
        path.append(p), nrms.append(n if np.linalg.norm(p - p0) > 1e-6 else P(0, 0, 1))
    E.add("Torso", cadena_por(path, nrms, largo=0.22, ancho=0.14, r=0.03))
    for i, (x, z) in enumerate(((0.35, 3.6), (-0.4, 3.2), (0.1, 2.7))):
        b = P(x, z, -0.6)
        d = unit(P(0.3 * (i - 1), 0.4, -1))
        E.add("Torso", tube([b - d * 0.2, b + d * 0.45, b + d * 0.6 + P(0.12, 0.1, 0)], 0.028, "Varilla", sides=6, capseg=1),
              ellipsoid((0.08, 0.04, 0.08), "Sangre", b + P(0, 0.02, 0), n=2))
    E.add("Torso", banda((2.06, 1.28, 0.16), P(0, 2.32, 0), "Madera_Soga"))
    # cabeza: prognatismo con colmillos, ojos chicos desparejos
    H = B["Head"]
    hc = H.centro
    fz = -hc[1] + 0.55
    E.add("Head", H, rbox((1.0, 0.24, 0.16), SK, P(0, hc[2] + 0.22, fz + 0.05), rot(-12), r=0.06),
          rbox((1.05, 0.55, 0.36), SK, P(0, hc[2] - 0.38, fz + 0.12), r=0.1),
          rbox((0.75, 0.06, 0.12), "Boca", P(0, hc[2] - 0.2, fz + 0.09), r=0.03))
    E.add("Head", rbox((0.2, 0.05, 0.14), "Ojo_Amarillo", P(0.24, hc[2] + 0.05, fz + 0.02), r=0.03),
          rbox((0.12, 0.05, 0.08), "Ojo_Amarillo", P(-0.24, hc[2] + 0.06, fz + 0.02), r=0.02))
    for sx in (-1, 1):
        b = P(sx * 0.36, hc[2] - 0.25, fz + 0.35)
        E.add("Head", spike(b, b + P(sx * 0.05, 0.38, 0.05), 0.07, "Dientes", sides=6, bend=P(sx * 0.03, 0, -0.04)))
    E.add("Head", dientes([P(x, hc[2] - 0.22, fz + 0.32) for x in np.linspace(-0.2, 0.2, 4)], [P(0, 1, 0)] * 4, [0.08] * 4, 0.03, "Dientes"))
    # brazos: grillete con cadena rota a la izquierda + garras; puño derecho atravesado por la viga
    for parte in ("Right Arm", "Left Arm"):
        A = B[parte]
        c = A.centro
        E.add(parte, A, vena_plana(P(c[0] + np.sign(c[0]) * 0.61, 3.7, -0.2), P(c[0] + np.sign(c[0]) * 0.61, 2.5, 0.1),
                                   P(np.sign(c[0]), 0, 0), r=0.035),
              rbox((0.95, 0.3, 0.7), SK, P(c[0], 3.35, 0.6), r=0.13))
    E.add("Left Arm", banda((1.28, 1.23, 0.28), P(1.61, 2.35, 0), ST), punta_garras(P(1.61, 2.05, 0.2), 4, 0.8, 0.45, d=P(0, -1, 0.3), r=0.07))
    for i in range(3):
        E.add("Left Arm", ring_loop(P(2.26, 2.2 - 0.17 * i, 0.1), (0.09, 0.055), 0.024, "Cadena", R=rot(90 * (i % 2), 0, 90), seg=8, sides=4))
    F = P(-1.62, 1.95, 0.1)
    E.add("Right Arm", rbox((1.32, 1.3, 0.6), SK, F + P(0, 0.1, 0), r=0.14))
    for k in range(4):
        E.add("Right Arm", rbox((0.28, 0.2, 0.28), SK, F + P((k - 1.5) * 0.3, -0.05, 0.66), r=0.07))
    d = unit(P(-0.1, -0.55, 1.0))
    top, bot = F - d * 1.0, F + d * 3.1
    Lb = np.linalg.norm(bot - top)
    Rw = align(bot - top) @ rot(0, 0, 25)
    bendf = lambda V: V + np.outer(0.12 * (V[:, 2] / (Lb / 2)) ** 2, [1, 0, 0])  # noqa: E731
    mid = (top + bot) / 2
    E.add("Arma", rbox((0.36, 0.05, Lb), ST, r=0.012, k=(1, 1, 10)).deform(lambda V: bendf(V + [0, 0.155, 0])).xf(Rw, mid),
          rbox((0.36, 0.05, Lb), ST, r=0.012, k=(1, 1, 10)).deform(lambda V: bendf(V + [0, -0.155, 0])).xf(Rw, mid),
          rbox((0.045, 0.3, Lb - 0.04), ST, r=0.008, k=(1, 1, 10)).deform(bendf).xf(Rw, mid))
    for zz in (-Lb / 2 + 0.12, Lb / 2 - 0.12):
        for yy in (0.19, -0.19):
            for xx in (-0.1, 0.1):
                q = Rw @ np.array([xx + 0.12 * (zz / (Lb / 2)) ** 2, yy, zz]) + mid
                E.add("Arma", perno(q, Rw @ np.array([0, np.sign(yy), 0]), r=0.025, h=0.025))
    for t, r in ((0.55, 0.2), (-0.55, 0.18)):
        c = F + d * t
        E.add("Right Arm", ellipsoid((r, r, r * 0.8), SK, c, align(d), n=4, disp=lambda U: 0.1 * nz(U * 3)),
              ellipsoid((r * 0.7, r * 0.7, r * 0.3), "Sangre", c + d * 0.08 * np.sign(t), align(d), n=2))
    tip = Rw @ np.array([0.12, 0, Lb / 2]) + mid
    E.add("Arma", ellipsoid((0.45, 0.4, 0.38), "Concreto", tip + P(0, 0.02, 0.05), rot(15, 30, 10), n=6, smooth=False,
                            disp=lambda U: 0.22 * nz(U * 2.5 + 7) + 0.1 * nz(U * 6)))
    for i in range(5):
        a = i * 2 * math.pi / 5 + 0.3
        dd = unit(np.array([math.cos(a), math.sin(a), 0.4 * math.cos(a * 2)]))
        b = tip + dd * 0.25
        E.add("Arma", tube([b, b + dd * 0.32, b + dd * 0.42 + P(0.1 * math.sin(a), 0.14, 0)], 0.02, "Varilla", sides=5, capseg=1))
    # piernas: pantalón roto, pies con garras, grilletes con cadena rota arrastrando
    for parte in ("Right Leg", "Left Leg"):
        L = B[parte]
        x = L.centro[0]
        L.pintar(roturas(nz, 0.45, seed=x * 4), SK).pintar(borde(nz, 0.55, 0.12, seed=x), SK)
        E.add(parte, L, banda((1.02, 1.2, 0.24), P(np.sign(x) * 0.54, 0.32, 0), ST),
              punta_garras(P(x, 0.08, 0.53), 3, 0.55, 0.24, d=P(0, 1, 0.05), r=0.07))
    for i in range(4):
        E.add("Left Leg", ring_loop(P(1.12 + 0.13 * i, 0.07 + 0.02 * (i % 2), 0.2 - 0.06 * i), (0.09, 0.055), 0.022, "Cadena",
                                    R=rot(90 * (i % 2), 0, 20), seg=8, sides=4))
    return E, 2.3


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


def datos_rig(E, s):
    """Centro del bounding box de cada malla en ejes de Roblox (x, y arriba, z) + escala, para armar_r6.lua."""
    cent = {}
    for parte, shells in E.partes.items():
        if shells:
            V = np.concatenate([sh.V for sh in shells])
            c = (V.min(0) + V.max(0)) / 2
            cent[parte] = [round(float(c[0]), 4), round(float(c[2]), 4), round(float(-c[1]), 4)]
    return {"s": s, "centros": cent}


def escribir_lua():
    datos = {}
    for d in sorted(os.listdir(HERE)):
        f = os.path.join(HERE, d, "rig.json")
        if os.path.exists(f):
            datos[d] = json.load(open(f))
    filas = []
    for nm, d in datos.items():
        c = ", ".join(f'["{k}"] = Vector3.new({v[0]}, {v[1]}, {v[2]})' for k, v in d["centros"].items())
        filas.append(f'\t{nm} = {{ s = {d["s"]}, centros = {{ {c} }} }},')
    plantilla = open(os.path.join(HERE, "armar_r6_plantilla.lua")).read()
    open(os.path.join(HERE, "armar_r6.lua"), "w").write(plantilla.replace("--DATOS--", "\n".join(filas)))


def build(nm):
    E, s = BUILDERS[nm]()
    E.escalar(s)
    cam = dict(target=(0, -0.3 * s, 2.7 * s), dist=0.85 * s)
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
    with open(os.path.join(out, "rig.json"), "w") as f:
        json.dump(datos_rig(E, s), f, indent=2)
    escribir_lua()
    if not os.environ.get("NO_RENDER"):
        L.render(out, **cam)
    return info


def foto_grupal(path=os.path.join(HERE, "enemigos_hd.png")):
    """Importa los 5 .glb ya exportados y los renderiza juntos, en fila."""
    import bpy
    import lib_torretas as L
    L.reset()
    xs = {"zombi_rapido_hd": -12.5, "zombi_blindado_hd": -7.0, "zombi_berserk_hd": -1.0,
          "zombi_radiactivo_hd": 4.8, "zombi_gigante_hd": 13.2}
    for nm, x in xs.items():
        antes = set(bpy.data.objects)
        bpy.ops.import_scene.gltf(filepath=os.path.join(HERE, nm, nm + ".glb"))
        for o in set(bpy.data.objects) - antes:
            if o.parent is None:
                o.location.x += x
    L.render(os.path.dirname(path), target=(1.8, 0, 5.2), dist=4.75, res=1400,
             views={os.path.splitext(os.path.basename(path))[0]: (0.6, -9.5, 0.9)})


if __name__ == "__main__":
    if "--foto" in sys.argv:
        foto_grupal()
        raise SystemExit
    for nm in [a for a in sys.argv[1:] if a in BUILDERS] or list(BUILDERS):
        build(nm)
