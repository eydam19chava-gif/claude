"""Mini-librería de mallas cerradas (numpy) para los enemigos HD.

Todo lo que sale de acá es una "cáscara" (Shell) cerrada y con normales hacia afuera:
cajas redondeadas, elipsoides deformables, tubos que siguen una curva, cristales y
ropa rasgada con espesor. `revisar()` valida la topología antes de exportar.

Ejes como en Blender: Z arriba, el personaje mira hacia -Y. Para pensar las poses se
usa P(x, z, f): x = lado, z = altura, f = hacia adelante (se guarda como y = -f).
"""
import math

import numpy as np


def P(x, z, f=0.0):
    return np.array([x, -f, z], float)


def unit(v):
    v = np.asarray(v, float)
    n = np.linalg.norm(v, axis=-1, keepdims=True)
    return v / np.where(n < 1e-12, 1, n)


def rot(x=0.0, y=0.0, z=0.0):
    """Rotación en grados (primero X, después Y, después Z)."""
    x, y, z = map(math.radians, (x, y, z))
    cx, sx, cy, sy, cz, sz = math.cos(x), math.sin(x), math.cos(y), math.sin(y), math.cos(z), math.sin(z)
    Rx = np.array([[1, 0, 0], [0, cx, -sx], [0, sx, cx]])
    Ry = np.array([[cy, 0, sy], [0, 1, 0], [-sy, 0, cy]])
    Rz = np.array([[cz, -sz, 0], [sz, cz, 0], [0, 0, 1]])
    return Rz @ Ry @ Rx


def align(v, up=(0, 0, 1)):
    """Rotación que lleva el eje Z local a la dirección v (Rodrigues)."""
    a, b = unit(up), unit(v)
    c = float(np.dot(a, b))
    if c > 1 - 1e-9:
        return np.eye(3)
    if c < -1 + 1e-9:
        return rot(180, 0, 0)
    k = np.cross(a, b)
    K = np.array([[0, -k[2], k[1]], [k[2], 0, -k[0]], [-k[1], k[0], 0]])
    return np.eye(3) + K + K @ K * (1 / (1 + c))


def weld(V, F, eps=1e-7):
    key = np.round(V / eps).astype(np.int64)
    _, idx, inv = np.unique(key, axis=0, return_index=True, return_inverse=True)
    inv = inv.reshape(-1)
    F2 = inv[F]
    ok = (F2[:, 0] != F2[:, 1]) & (F2[:, 1] != F2[:, 2]) & (F2[:, 0] != F2[:, 2])
    return V[idx], F2[ok]


def compact(V, F):
    used = np.unique(F)
    remap = -np.ones(len(V), int)
    remap[used] = np.arange(len(used))
    return V[used], remap[F]


class Shell:
    def __init__(self, V, F, mat, smooth=True, closed=True):
        self.V = np.asarray(V, float)
        self.F = np.asarray(F, np.int64)
        self.mat, self.smooth, self.closed = mat, smooth, closed

    # --- transformaciones
    def xf(self, R=None, t=(0, 0, 0), s=None):
        V = self.V
        if s is not None:
            V = V * np.asarray(s, float)
            if np.prod(np.sign(s)) < 0:          # espejo: invertir el orden para no dar vuelta las normales
                self.F = self.F[:, ::-1].copy()
        if R is not None:
            V = V @ np.asarray(R).T
        self.V = V + np.asarray(t, float)
        return self

    def mirror_x(self):
        return Shell(self.V * [-1, 1, 1], self.F[:, ::-1].copy(), self.mat, self.smooth, self.closed)

    def deform(self, fn):
        self.V = fn(self.V.copy())
        return self

    def normals(self):
        a, b, c = (self.V[self.F[:, i]] for i in range(3))
        fn = np.cross(b - a, c - a)
        N = np.zeros_like(self.V)
        for i in range(3):
            np.add.at(N, self.F[:, i], fn)
        return unit(N)

    def displace(self, fn):
        """Mueve cada vértice sobre su normal: fn(V, N) -> distancia."""
        N = self.normals()
        self.V = self.V + N * np.asarray(fn(self.V, N))[:, None]
        return self

    def volume(self):
        a, b, c = (self.V[self.F[:, i]] for i in range(3))
        return float(np.einsum("ij,ij->i", a, np.cross(b, c)).sum() / 6)

    def fix(self):
        if self.closed and self.volume() < 0:
            self.F = self.F[:, ::-1].copy()
        return self

    def tris(self):
        return len(self.F)

    def pintar(self, fn, mat):
        """Cambia el material de las caras donde fn(centroides, shell) es True (manchas, quemaduras)."""
        if getattr(self, "fmat", None) is None:
            self.fmat = np.array([self.mat] * len(self.F), dtype=object)
        C = self.V[self.F].mean(1)
        self.fmat[fn(C, self)] = mat
        return self


# ------------------------------------------------------------------ ruido
class Noise:
    """Ruido suave determinístico (suma de ondas en direcciones al azar), valores ~[-1, 1]."""

    def __init__(self, seed, freq=1.0, waves=10):
        rng = np.random.default_rng(seed)
        self.d = unit(rng.normal(size=(waves, 3))) * freq * rng.uniform(0.6, 1.8, (waves, 1))
        self.ph = rng.uniform(0, 2 * math.pi, waves)
        self.a = 1 / np.arange(1, waves + 1) ** 0.5
        self.a /= self.a.sum() * 0.55

    def __call__(self, X):
        return np.clip((np.sin(np.asarray(X) @ self.d.T + self.ph) * self.a).sum(-1), -1, 1)


def seg_dist(X, a, b):
    a, b = np.asarray(a, float), np.asarray(b, float)
    ab = b - a
    t = np.clip(((X - a) @ ab) / max(ab @ ab, 1e-12), 0, 1)
    return np.linalg.norm(X - (a + t[:, None] * ab), axis=1), t


def groove(a, b, width, depth, rim=0.35):
    """Cicatriz: surco con bordes levantados a lo largo del segmento a-b."""
    def fn(X, N):
        d, _ = seg_dist(X, a, b)
        return -depth * np.exp(-(d / width) ** 2) + depth * rim * np.exp(-((d - 1.7 * width) / width) ** 2)
    return fn


def bump(c, r, h):
    def fn(X, N):
        return h * np.exp(-(np.linalg.norm(X - np.asarray(c), axis=1) / r) ** 2)
    return fn


def total(*fns):
    return lambda X, N: sum(f(X, N) for f in fns)


# ------------------------------------------------------------------ primitivas
def _grid_box(cx, cy, cz):
    C = [np.asarray(cx), np.asarray(cy), np.asarray(cz)]
    V, F = [], []
    for a in range(3):
        b, c = [(1, 2), (2, 0), (0, 1)][a]
        for s in (-1, 1):
            base, nb, nc = len(V), len(C[b]), len(C[c])
            val = C[a][0] if s < 0 else C[a][-1]
            for i in range(nb):
                for j in range(nc):
                    p = [0.0, 0.0, 0.0]
                    p[a], p[b], p[c] = val, C[b][i], C[c][j]
                    V.append(p)
            for i in range(nb - 1):
                for j in range(nc - 1):
                    q = [base + i * nc + j, base + (i + 1) * nc + j, base + (i + 1) * nc + j + 1, base + i * nc + j + 1]
                    if s > 0:
                        F += [[q[0], q[1], q[2]], [q[0], q[2], q[3]]]
                    else:
                        F += [[q[0], q[2], q[1]], [q[0], q[3], q[2]]]
    return weld(np.array(V), np.array(F))


def _coords(h, r, m, k):
    if r <= 1e-9:
        return np.linspace(-h, h, k + 1)
    hr = h - r
    end = [-hr - r * math.tan((m - i) / m * math.pi / 4) for i in range(m)]
    mid = list(np.linspace(-hr, hr, k + 1))
    return np.array(end + mid + [-e for e in reversed(end)])


def rbox(size, mat, c=(0, 0, 0), R=None, r=0.04, m=1, k=(1, 1, 1), smooth=True):
    """Caja con bordes redondeados (k = divisiones de la parte plana por eje)."""
    h = np.asarray(size, float) / 2
    rr = min(r, *(h * 0.98))
    kk = k if isinstance(k, (tuple, list)) else (k, k, k)
    V, F = _grid_box(*[_coords(h[i], rr, m, kk[i]) for i in range(3)])
    if rr > 0:
        inner = np.clip(V, -(h - rr), h - rr)
        d = V - inner
        V = inner + rr * unit(d)
    return Shell(V, F, mat, smooth).xf(R, c).fix()


def ellipsoid(radii, mat, c=(0, 0, 0), R=None, n=8, disp=None, smooth=True):
    """Elipsoide desde un cubo-esfera. disp(U) -> factor extra de radio (U = dirección unitaria local)."""
    t = np.tan(np.linspace(-math.pi / 4, math.pi / 4, n + 1))
    V, F = _grid_box(t, t, t)
    U = unit(V)
    f = 1 + (disp(U) if disp else 0)
    s = Shell(U * np.asarray(f).reshape(-1, 1) * np.asarray(radii, float), F, mat, smooth)
    s.U = U                                          # dirección local, útil para recortes
    return s.xf(R, c).fix()


def along(a, b, r, mat, n=8, bulge=1.0, disp=None, roll=0.0):
    """Elipsoide estirado entre dos puntos (músculos, huesos)."""
    a, b = np.asarray(a, float), np.asarray(b, float)
    L = np.linalg.norm(b - a) / 2
    rx, ry = (r, r) if np.isscalar(r) else r
    return ellipsoid((rx, ry, L * bulge), mat, (a + b) / 2, align(b - a) @ rot(0, 0, roll), n, disp)


def tube(pts, radii, mat, sides=8, caps=("round", "round"), aspect=(1, 1), up=None, closed=False,
         capseg=3, point=2.5, smooth=True, twist=0.0):
    """Tubo por una polilínea. caps: 'round', 'point', 'flat' o 'none' (abierto)."""
    Pt = np.asarray(pts, float)
    n = len(Pt)
    rad = np.full(n, radii, float) if np.isscalar(radii) else np.asarray(radii, float)
    if closed:
        T = unit(np.roll(Pt, -1, 0) - np.roll(Pt, 1, 0))
    else:
        T = unit(np.gradient(Pt, axis=0))
    if up is not None:
        Bv = unit(np.cross(T, np.asarray(up, float)))
        N = np.cross(Bv, T)
    else:
        N = np.zeros_like(T)
        ref = np.array([0, 0, 1.0]) if abs(T[0][2]) < 0.9 else np.array([1.0, 0, 0])
        N[0] = unit(np.cross(np.cross(T[0], ref), T[0]))
        for i in range(1, n):
            v = N[i - 1] - T[i] * np.dot(N[i - 1], T[i])
            N[i] = unit(v) if np.linalg.norm(v) > 1e-9 else N[i - 1]
        Bv = np.cross(T, N)
    Bv = np.cross(T, N)
    th = np.linspace(0, 2 * math.pi, sides, endpoint=False) + twist
    ax, ay = aspect
    rings = []

    def ring(c, r, i):
        return c + np.outer(np.cos(th) * r * ax, N[i]) + np.outer(np.sin(th) * r * ay, Bv[i])

    pole0 = pole1 = None
    if not closed and caps[0] == "round":
        for j in range(capseg, 0, -1):
            ph = j / (capseg + 1) * math.pi / 2
            rings.append(ring(Pt[0] - T[0] * rad[0] * math.sin(ph), rad[0] * math.cos(ph), 0))
        pole0 = Pt[0] - T[0] * rad[0]
    elif not closed and caps[0] == "point":
        pole0 = Pt[0] - T[0] * rad[0] * point
    elif not closed and caps[0] == "flat":
        pole0 = Pt[0]
    for i in range(n):
        rings.append(ring(Pt[i], rad[i], i))
    if not closed and caps[1] == "round":
        for j in range(1, capseg + 1):
            ph = j / (capseg + 1) * math.pi / 2
            rings.append(ring(Pt[-1] + T[-1] * rad[-1] * math.sin(ph), rad[-1] * math.cos(ph), n - 1))
        pole1 = Pt[-1] + T[-1] * rad[-1]
    elif not closed and caps[1] == "point":
        pole1 = Pt[-1] + T[-1] * rad[-1] * point
    elif not closed and caps[1] == "flat":
        pole1 = Pt[-1]

    V = np.concatenate(rings)
    m, s = len(rings), sides
    F = []
    for k in range(m if closed else m - 1):
        k2 = (k + 1) % m
        for j in range(s):
            a, b = k * s + j, k * s + (j + 1) % s
            c, d = k2 * s + (j + 1) % s, k2 * s + j
            F += [[a, b, c], [a, c, d]]
    extra = []
    if pole0 is not None:
        p = len(V) + len(extra)
        extra.append(pole0)
        F += [[p, (j + 1) % s, j] for j in range(s)]
    if pole1 is not None:
        p = len(V) + len(extra)
        extra.append(pole1)
        last = (m - 1) * s
        F += [[p, last + j, last + (j + 1) % s] for j in range(s)]
    if extra:
        V = np.concatenate([V, np.array(extra)])
    is_closed = closed or (caps[0] != "none" and caps[1] != "none")
    return Shell(V, F, mat, smooth, closed=is_closed).fix()


def ring_loop(center, radius, r, mat, R=None, seg=16, sides=6, aspect=(1, 1), wobble=None):
    """Anillo cerrado (toroide) en el plano XY local."""
    th = np.linspace(0, 2 * math.pi, seg, endpoint=False)
    rx, ry = (radius, radius) if np.isscalar(radius) else radius
    pts = np.stack([np.cos(th) * rx, np.sin(th) * ry, np.zeros(seg)], 1)
    if wobble is not None:
        pts[:, 2] += wobble(th)
    R = np.eye(3) if R is None else R
    pts = pts @ R.T + np.asarray(center, float)
    return tube(pts, r, mat, sides=sides, closed=True, aspect=aspect)


def crystal(base, tip, r, mat, sides=6, twist=0.0):
    """Cristal hexagonal con punta, facetado (sombreado plano)."""
    base, tip = np.asarray(base, float), np.asarray(tip, float)
    d = tip - base
    body = base + d * 0.72
    return tube([base - unit(d) * r * 0.3, body], [r * 0.85, r], mat, sides=sides, caps=("flat", "point"),
                point=np.linalg.norm(tip - body) / r, smooth=False, twist=twist)


def spike(base, tip, r, mat, sides=6, smooth=True, bend=None):
    """Cono (dientes, garras, púas). bend = desplazamiento lateral de la punta para curvarla."""
    base, tip = np.asarray(base, float), np.asarray(tip, float)
    pts = [base + (tip - base) * t for t in (0, 0.45, 0.8)]
    if bend is not None:
        pts = [p + np.asarray(bend) * t * t for p, t in zip(pts, (0, 0.45, 0.8))]
    rr = [r, r * 0.72, r * 0.4]
    L = np.linalg.norm(tip - pts[-1]) / rr[-1]
    return tube(pts, rr, mat, sides=sides, caps=("flat", "point"), point=max(L, 0.5), smooth=smooth)


def solidify(shell, keep, thick, mat=None):
    """Borra caras (keep(centroides, shell) -> bool) y le da espesor hacia adentro: tela rota, placas."""
    V, F = shell.V, shell.F
    C = V[F].mean(1)
    F = F[keep(C, shell)]
    # sacar vértices "moño" (dos agujeros que se tocan en un punto): darían aristas no-manifold al dar espesor
    for _ in range(20):
        nv = len(V) + 1
        E = np.concatenate([F[:, [0, 1]], F[:, [1, 2]], F[:, [2, 0]]])
        bd = E[~np.isin(E[:, 0] * nv + E[:, 1], E[:, 1] * nv + E[:, 0])]
        starts, cnt = np.unique(bd[:, 0], return_counts=True)
        bad = starts[cnt > 1]
        if not len(bad):
            break
        F = F[~np.isin(F, bad).any(1)]
    U = getattr(shell, "U", None)
    used = np.unique(F)
    V, F = compact(V, F)
    s = Shell(V, F, mat or shell.mat, shell.smooth, closed=False)
    N = s.normals()
    nv = len(V)
    Vin = V - N * thick
    Fin = F[:, ::-1] + nv
    E = np.concatenate([F[:, [0, 1]], F[:, [1, 2]], F[:, [2, 0]]])
    code = E[:, 0] * (nv + 1) + E[:, 1]
    rcode = E[:, 1] * (nv + 1) + E[:, 0]
    bd = E[~np.isin(code, rcode)]
    side = []
    for a, b in bd:
        side += [[b, a, a + nv], [b, a + nv, b + nv]]
    out = Shell(np.concatenate([V, Vin]), np.concatenate([F, Fin, np.array(side, np.int64).reshape(-1, 3)]),
                mat or shell.mat, shell.smooth, closed=True)
    if U is not None:
        out.U = np.concatenate([U[used], U[used]])
    return out.fix()


def ragged(noise, amount):
    """Filtro para solidify: deja las caras donde el ruido supera `amount` (agujeros irregulares)."""
    return lambda C, s: noise(C) > amount


# ------------------------------------------------------------------ validación
def _tri2d_overlap(A, B, eps=1e-6):
    for T1, T2 in ((A, B), (B, A)):
        for i in range(3):
            e = T1[(i + 1) % 3] - T1[i]
            n = np.array([-e[1], e[0]])
            p1, p2 = T1 @ n, T2 @ n
            if p1.max() <= p2.min() + eps or p2.max() <= p1.min() + eps:
                return False
    return True


def revisar(shells, limite=20000):
    """Valida la malla completa del personaje. Devuelve (ok, informe)."""
    problemas, tris, verts = [], 0, 0
    allN, allD, allS, allT = [], [], [], []
    for si, s in enumerate(shells):
        V, F = s.V, s.F
        tris += len(F)
        verts += len(np.unique(F))
        a, b, c = V[F[:, 0]], V[F[:, 1]], V[F[:, 2]]
        cr = np.cross(b - a, c - a)
        area = np.linalg.norm(cr, axis=1) / 2
        if (area < 1e-9).any():
            problemas.append(f"pieza {si} ({s.mat}): {(area < 1e-9).sum()} triángulos degenerados")
        nv = len(V) + 1
        E = np.concatenate([F[:, [0, 1]], F[:, [1, 2]], F[:, [2, 0]]])
        code = E[:, 0] * nv + E[:, 1]
        u, cnt = np.unique(code, return_counts=True)
        if (cnt > 1).any():
            problemas.append(f"pieza {si} ({s.mat}): {(cnt > 1).sum()} aristas no-manifold")
        if not np.isin(E[:, 1] * nv + E[:, 0], u).all():
            problemas.append(f"pieza {si} ({s.mat}): malla abierta")
        if s.volume() <= 0:
            problemas.append(f"pieza {si} ({s.mat}): normales invertidas (volumen {s.volume():.4f})")
        n = cr / np.maximum(np.linalg.norm(cr, axis=1, keepdims=True), 1e-12)
        ok = area > 1e-5
        allN.append(n[ok]), allD.append(np.einsum("ij,ij->i", n[ok], a[ok])), allS.append(np.full(ok.sum(), si))
        allT.append(np.stack([a, b, c], 1)[ok])
    # z-fighting: triángulos coplanares de piezas distintas que se superponen
    N, D, S, T = map(np.concatenate, (allN, allD, allS, allT))
    sgn = np.where(np.abs(N[:, 0]) > 1e-6, np.sign(N[:, 0]), np.where(np.abs(N[:, 1]) > 1e-6, np.sign(N[:, 1]), np.sign(N[:, 2])))
    N, D = N * sgn[:, None], D * sgn
    key = np.round(N * 500).astype(np.int64)
    groups = {}
    for i, k in enumerate(map(tuple, key)):
        groups.setdefault(k, []).append(i)
    z, pares = 0, set()
    for idx in groups.values():
        if len(idx) < 2 or len(set(S[idx])) < 2:
            continue
        idx = np.array(idx)[np.argsort(D[idx])]
        for ii in range(len(idx)):
            for jj in range(ii + 1, len(idx)):
                i, j = idx[ii], idx[jj]
                if D[j] - D[i] > 2e-3:
                    break
                if S[i] == S[j]:
                    continue
                ax = np.argmax(np.abs(N[i]))
                keep = [q for q in range(3) if q != ax]
                if _tri2d_overlap(T[i][:, keep], T[j][:, keep]):
                    z += 1
                    pares.add((min(S[i], S[j]), max(S[i], S[j])))
    if z:
        det = ", ".join(f"{a}({shells[a].mat})-{b}({shells[b].mat})" for a, b in sorted(pares)[:8])
        problemas.append(f"{z} pares de caras coplanares superpuestas (z-fighting): {det}")
    if tris > limite:
        problemas.append(f"{tris} triángulos (límite {limite})")
    if verts > limite:
        problemas.append(f"{verts} vértices (límite {limite})")
    return not problemas, dict(triangulos=tris, vertices=verts, piezas=len(shells), problemas=problemas)
