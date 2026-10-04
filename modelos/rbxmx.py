"""Arma un modelo nativo de Roblox (.rbxmx) con Parts ya pintadas, a partir de las fichas de lib_torretas.SPECS.

Así el modelo entra a Roblox Studio con color sin subir mallas ni texturas: clic derecho en Workspace →
Insertar desde archivo. Cada primitiva se traduce a Parts:
  caja/barra -> Block, cilindro -> Cylinder, hexágono -> 3 Blocks a 0/60/120°, cono -> cilindros (o Blocks) que se
  afinan, esfera -> Block con SpecialMesh Sphere, anillo -> Blocks alrededor.
Cada articulación tiene un Part invisible "ancla" en su pivote; las piezas van soldadas (Weld) a su ancla y las anclas
se unen al Torso con Motor6D. Solo el ancla del Torso queda anclada (PrimaryPart).

Ejes: Blender (Z arriba, mira a -Y) -> Roblox (Y arriba, mira a -Z) con C(x, y, z) = (-x, z, y).
"""
import math
from xml.sax.saxutils import escape

from mathutils import Matrix, Vector

C = Matrix(((-1, 0, 0), (0, 0, 1), (0, 1, 0)))
MATERIAL = {"SmoothPlastic": 272, "Neon": 288}


def _cf(pos, R):
    vals = [pos.x, pos.y, pos.z] + [R[i][j] for i in range(3) for j in range(3)]
    tags = ["X", "Y", "Z", "R00", "R01", "R02", "R10", "R11", "R12", "R20", "R21", "R22"]
    return "".join(f"<{t}>{v:.5f}</{t}>" for t, v in zip(tags, vals))


def _to_roblox(W):
    """Matriz de Blender (con escala uniforme) -> (posición, rotación de Roblox, escala)."""
    loc, rot, scl = W.decompose()
    R = rot.to_matrix()
    return C @ loc, C @ R @ C.transposed(), scl.x


def _parts_from_spec(sp):
    """Devuelve [(forma, W_bloque, tamaño_en_ejes_locales_de_Blender (x, y, z))] para una ficha."""
    W, prim, d = sp["M"], sp["prim"], Vector(sp["dims"])
    if prim in ("box", "sphere"):
        return [("ball" if prim == "sphere" else "block", W, d)]
    if prim == "torus":
        R, r = sp["R"], sp["r"]
        n = 16 if R > 0.5 else 12
        out = []
        for k in range(n):
            th = 2 * math.pi * k / n
            Wk = W @ Matrix.Translation((R * math.cos(th), R * math.sin(th), 0)) @ Matrix.Rotation(th + math.pi / 2, 4, "Z")
            out.append(("block", Wk, Vector((2 * math.pi * R / n * 1.15, 2 * r, 2 * r))))
        return out
    r1, r2, h, verts = sp["r1"], sp["r2"], sp["depth"], sp.get("verts", 16)
    if prim == "rod" or (abs(r1 - r2) < 1e-6 and verts != 6):
        return [("cyl", W, Vector((2 * r1, 2 * r1, h)))]
    if abs(r1 - r2) < 1e-6:                                                     # prisma hexagonal = 3 rectángulos
        a0 = sp.get("a0", 0.0)
        return [("block", W @ Matrix.Rotation(a0 + k * math.pi / 3, 4, "Z"), Vector((r1, r1 * math.sqrt(3), h)))
                for k in range(3)]
    n = 3 if h > 0.6 else 2                                                     # cono: tramos que se afinan
    out = []
    for k in range(n):
        t = (k + 0.5) / n
        rr = max(r1 + (r2 - r1) * t, 0.02)
        Wk = W @ Matrix.Translation((0, 0, -h / 2 + t * h))
        if verts >= 5:
            out.append(("cyl", Wk, Vector((2 * rr, 2 * rr, h / n * 1.02))))
        else:
            out.append(("block", Wk, Vector((1.5 * rr, 1.5 * rr, h / n * 1.02))))
    return out


class _Writer:
    def __init__(self):
        self.ref = 0
        self.out = []

    def new_ref(self):
        self.ref += 1
        return f"RBX{self.ref:06d}"

    def part(self, name, pos, R, size, rgb, material="SmoothPlastic", shape=1, anchored=False, transparency=0.0,
             reflect=0.0, sphere=False, children=""):
        ref = self.new_ref()
        r, g, b = (max(0, min(255, round(c * 255))) for c in rgb)
        color = (0xFF << 24) | (r << 16) | (g << 8) | b
        mesh = ('<Item class="SpecialMesh" referent="%s"><Properties><token name="MeshType">3</token>'
                '<Vector3 name="Scale"><X>1</X><Y>1</Y><Z>1</Z></Vector3><string name="Name">Mesh</string>'
                '</Properties></Item>' % self.new_ref()) if sphere else ""
        xml = (f'<Item class="Part" referent="{ref}"><Properties>'
               f'<string name="Name">{escape(name)}</string>'
               f'<bool name="Anchored">{"true" if anchored else "false"}</bool>'
               f'<bool name="CanCollide">false</bool><bool name="CanTouch">false</bool><bool name="CanQuery">false</bool>'
               f'<CoordinateFrame name="CFrame">{_cf(pos, R)}</CoordinateFrame>'
               f'<Color3uint8 name="Color3uint8">{color}</Color3uint8>'
               f'<token name="Material">{MATERIAL[material]}</token>'
               f'<float name="Reflectance">{reflect:.2f}</float>'
               f'<float name="Transparency">{transparency:.2f}</float>'
               f'<token name="shape">{shape}</token>'
               f'<token name="TopSurface">0</token><token name="BottomSurface">0</token>'
               f'<Vector3 name="size"><X>{size[0]:.4f}</X><Y>{size[1]:.4f}</Y><Z>{size[2]:.4f}</Z></Vector3>'
               f'</Properties>{mesh}{children}</Item>')
        return ref, xml

    def joint(self, cls, name, p0, p1, c0, c1):
        I = Matrix.Identity(3)
        return (f'<Item class="{cls}" referent="{self.new_ref()}"><Properties>'
                f'<string name="Name">{name}</string>'
                f'<Ref name="Part0">{p0}</Ref><Ref name="Part1">{p1}</Ref>'
                f'<CoordinateFrame name="C0">{_cf(c0[0], c0[1])}</CoordinateFrame>'
                f'<CoordinateFrame name="C1">{_cf(c1[0] if c1 else Vector((0, 0, 0)), c1[1] if c1 else I)}</CoordinateFrame>'
                f'</Properties></Item>')


def _rel(a_pos, a_R, b_pos, b_R):
    """CFrame de b relativo a a (a⁻¹ · b)."""
    Rt = a_R.transposed()
    return Rt @ (b_pos - a_pos), Rt @ b_R


def write(path, name, specs, pivots, root="Torso"):
    """specs: {parte: [fichas]}; pivots: {parte: Vector de Blender del pivote}. Devuelve la cantidad de Parts."""
    w = _Writer()
    I = Matrix.Identity(3)
    anchors = {}
    for joint, piv in pivots.items():
        anchors[joint] = (C @ Vector(piv), w.new_ref())
    groups = []
    total = 0
    rot_cyl = Matrix.Rotation(math.pi / 2, 3, "Z")
    for joint, sps in specs.items():
        if joint not in anchors:
            continue
        a_pos, a_ref = anchors[joint]
        items = []
        for sp in sps:
            for shape, Wb, d in _parts_from_spec(sp):
                pos, R, s = _to_roblox(Wb)
                dx, dy, dz = d.x * s, d.y * s, d.z * s
                if shape == "cyl":
                    R, size, shp, sph = R @ rot_cyl, (dz, dx, dy), 2, False
                else:
                    size, shp, sph = (dx, dz, dy), 1, shape == "ball"
                size = tuple(max(v, 0.02) for v in size)
                rp, rR = _rel(a_pos, I, pos, R)
                weld = w.joint("Weld", "Weld", a_ref, "{SELF}", (rp, rR), None)
                ref, xml = w.part("Pieza", pos, R, size, sp["rgb"], "Neon" if sp["glow"] else "SmoothPlastic", shp,
                                  reflect=0.15 if (sp.get("metal", 0) > 0.7 and not sp["glow"]) else 0.0,
                                  sphere=sph, children=weld)
                items.append(xml.replace("{SELF}", ref))
                total += 1
        groups.append((joint, items))
    # anclas (invisibles) y Motor6D al Torso
    t_pos, t_ref = anchors[root]
    body = []
    for joint, items in groups:
        a_pos, a_ref = anchors[joint]
        motor = ""
        if joint != root:
            rp, rR = _rel(t_pos, I, a_pos, I)
            motor = w.joint("Motor6D", joint, t_ref, a_ref, (rp, rR), None)
        anchor = (f'<Item class="Part" referent="{a_ref}"><Properties><string name="Name">{joint}</string>'
                  f'<bool name="Anchored">{"true" if joint == root else "false"}</bool>'
                  f'<bool name="CanCollide">false</bool><bool name="CanTouch">false</bool><bool name="CanQuery">false</bool>'
                  f'<CoordinateFrame name="CFrame">{_cf(a_pos, I)}</CoordinateFrame>'
                  f'<float name="Transparency">1</float><token name="shape">1</token>'
                  f'<Vector3 name="size"><X>0.4</X><Y>0.4</Y><Z>0.4</Z></Vector3>'
                  f'</Properties>{motor}</Item>')
        body.append(f'<Item class="Model" referent="{w.new_ref()}"><Properties><string name="Name">{joint}</string></Properties>'
                    + anchor + "".join(items) + "</Item>")
    xml = ('<roblox xmlns:xmime="http://www.w3.org/2005/05/xmlmime" xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" '
           'xsi:noNamespaceSchemaLocation="http://www.roblox.com/roblox.xsd" version="4">'
           f'<Item class="Model" referent="{w.new_ref()}"><Properties><string name="Name">{escape(name)}</string>'
           f'<Ref name="PrimaryPart">{t_ref}</Ref></Properties>' + "".join(body) + "</Item></roblox>")
    with open(path, "w", encoding="utf-8") as f:
        f.write(xml)
    return total
