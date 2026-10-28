"""Neil Armstrong Hall of Engineering second-pass exterior rebuild (rank 2, Rossen second pass).

Run headless on the saved library, which it edits in place and saves:
    blender -b modular/buildings/neil_armstrong_hall.blend --python modular/buildings/build_neil_armstrong_hall_second_pass.py

Idempotent: deletes the first-pass exterior shell (DELETE_PREFIX) and every ARMS_SP_* object, then rebuilds
the main bar, NW glass atrium, curved SW wing, SE wing and the warped red high roof with its NW prow from the
relief-corrected 2023 orthophoto trace and the photographs indexed in audit/neil_armstrong_hall/second_pass/.
Interior program objects are kept and moved inside the corrected envelope; the Armstrong statue moves to the
NW atrium entrance. Collection, root and local frame are unchanged. Dimensions are estimates, not survey values.
"""
import bpy, bmesh, math
from mathutils import Vector

COLL = "Asset_neil_armstrong_hall"
ROOT = "AssetRoot_neil_armstrong_hall"


# ---------------------------------------------------------------- materials
def principled(name, color, rough=0.6, metal=0.0, emit=None, spec=0.5):
    m = bpy.data.materials.get(name) or bpy.data.materials.new(name)
    m.use_nodes = True
    nt = m.node_tree
    nt.nodes.clear()
    out = nt.nodes.new("ShaderNodeOutputMaterial")
    b = nt.nodes.new("ShaderNodeBsdfPrincipled")
    b.inputs["Base Color"].default_value = (*color, 1)
    b.inputs["Roughness"].default_value = rough
    b.inputs["Metallic"].default_value = metal
    b.inputs["Specular IOR Level"].default_value = spec
    if emit:
        b.inputs["Emission Color"].default_value = (*emit, 1)
        b.inputs["Emission Strength"].default_value = 1.0
    nt.links.new(b.outputs[0], out.inputs[0])
    m.diffuse_color = (*color, 1)
    return m, nt, b


# ---------------------------------------------------------------- mesh accumulation
class MB:
    """Accumulates quads per material; vertical faces get metre-scaled planar UVs."""

    def __init__(self):
        self.parts = {}

    def quad(self, mat, pts):
        self.parts.setdefault(mat, []).append([Vector(p) for p in pts])

    def box(self, mat, origin, ax, ay, sx, sy, z0, z1, skip=()):
        """Box with base corner origin (2D), local axes ax/ay (unit 2D), extents sx, sy, z0..z1."""
        o = Vector((origin[0], origin[1]))
        a = Vector(ax) * sx
        b = Vector(ay) * sy
        c = [o, o + a, o + a + b, o + b]
        lo = [Vector((p.x, p.y, z0)) for p in c]
        hi = [Vector((p.x, p.y, z1)) for p in c]
        faces = {"bottom": [lo[0], lo[3], lo[2], lo[1]], "top": [hi[0], hi[1], hi[2], hi[3]],
                 "f0": [lo[0], lo[1], hi[1], hi[0]], "f1": [lo[1], lo[2], hi[2], hi[1]],
                 "f2": [lo[2], lo[3], hi[3], hi[2]], "f3": [lo[3], lo[0], hi[0], hi[3]]}
        for k, f in faces.items():
            if k not in skip:
                self.quad(mat, f)

    def build(self, name, M, parent):
        objs = []
        for mat, quads in self.parts.items():
            bm = bmesh.new()
            uvl = bm.loops.layers.uv.new("UVMap")
            for q in quads:
                vs = [bm.verts.new(p) for p in q]
                try:
                    f = bm.faces.new(vs)
                except ValueError:
                    continue
                n = (q[1] - q[0]).cross(q[2] - q[0])
                if n.length < 1e-9:
                    continue
                n.normalize()
                if abs(n.z) > 0.7:
                    for l in f.loops:
                        l[uvl].uv = (l.vert.co.x, l.vert.co.y)
                else:
                    t = Vector((-n.y, n.x, 0)).normalized()
                    for l in f.loops:
                        l[uvl].uv = (l.vert.co.dot(t), l.vert.co.z)
            bmesh.ops.remove_doubles(bm, verts=bm.verts, dist=0.0005)
            me = bpy.data.meshes.new(f"{name}_{mat}")
            bm.to_mesh(me)
            bm.free()
            me.materials.append(M[mat])
            ob = bpy.data.objects.new(f"{name}_{mat}", me)
            bpy.data.collections[COLL].objects.link(ob)
            ob.parent = parent
            objs.append(ob)
        self.parts = {}
        return objs


# ---------------------------------------------------------------- wall helpers
def rect_fill(u0, u1, z0, z1, holes):
    """Decompose rectangle minus axis-aligned holes into rectangles (u0,u1,z0,z1)."""
    zs = sorted({z0, z1, *[h[2] for h in holes if z0 < h[2] < z1], *[h[3] for h in holes if z0 < h[3] < z1]})
    out = []
    for za, zb in zip(zs, zs[1:]):
        zm = (za + zb) / 2
        hs = sorted([(h[0], h[1]) for h in holes if h[2] <= zm <= h[3]])
        u = u0
        for a, b in hs:
            if a > u:
                out.append((u, a, za, zb))
            u = max(u, b)
        if u < u1:
            out.append((u, u1, za, zb))
    return out


def seg_frame(A, B):
    A, B = Vector(A), Vector(B)
    d = B - A
    L = d.length
    t = d / L
    n = Vector((t.y, -t.x))  # outward when polygon is counter-clockwise
    return A, t, n, L


def wall(mb, A, B, z0, z1, thick, openings=(), mat="brick", glass="glass", inset=0.22, frame="bronze",
         mullions=None, outward=True):
    """Straight wall A->B (outer face on the A-B line, thickness inward).
    openings: list of (u0, u1, zb, zt[, kind]) in metres along the segment."""
    A, t, n, L = seg_frame(A, B)
    inw = -n if outward else n
    for (u0, u1, za, zb) in rect_fill(0, L, z0, z1, [o[:4] for o in openings]):
        mb.box(mat, A + t * u0, t, inw, u1 - u0, thick, za, zb)
    for o in openings:
        u0, u1, za, zb = o[:4]
        kind = o[4] if len(o) > 4 else "win"
        if kind == "void":
            continue
        g = glass if kind != "door" else "glass"
        mb.box(g, A + t * u0 + inw * inset, t, inw, u1 - u0, 0.04, za, zb)
        fw = 0.06
        # perimeter frame + mullions sitting just proud of the glass
        p = A + inw * (inset - 0.05)
        mb.box(frame, p + t * u0, t, inw, fw, 0.05, za, zb)
        mb.box(frame, p + t * (u1 - fw), t, inw, fw, 0.05, za, zb)
        mb.box(frame, p + t * u0, t, inw, u1 - u0, 0.05, za, za + fw)
        mb.box(frame, p + t * u0, t, inw, u1 - u0, 0.05, zb - fw, zb)
        w = u1 - u0
        nm = mullions if mullions is not None else max(0, int(round(w / 1.3)) - 1)
        for k in range(1, nm + 1):
            uu = u0 + w * k / (nm + 1) - 0.03
            mb.box(frame, p + t * uu, t, inw, 0.06, 0.05, za, zb)
        if kind == "door":
            mb.box(frame, p + t * u0, t, inw, w, 0.05, za + 2.6, za + 2.68)
        elif zb - za > 3.0:
            zt = za + (zb - za) * 0.78
            mb.box(frame, p + t * u0, t, inw, w, 0.05, zt, zt + 0.06)


def band(mb, A, B, z0, z1, proj=0.07, mat="lime", ext=0.0):
    A, t, n, L = seg_frame(A, B)
    mb.box(mat, A - t * ext + n * proj, t, -n, L + 2 * ext, proj + 0.05, z0, z1)


def arc_pts_c(Cc, r, a0, a1, step_deg=2.0):
    n = max(2, int(abs(a1 - a0) / step_deg) + 1)
    return [Cc + Vector((math.cos(math.radians(a0 + (a1 - a0) * i / (n - 1))),
                        math.sin(math.radians(a0 + (a1 - a0) * i / (n - 1))))) * r for i in range(n)]


def flat_poly(mb, mat, pts, z, flip=False):
    """Triangle-fan-free flat face via bmesh face (works for simple polygons)."""
    P = [Vector((p[0], p[1], z)) for p in pts]
    if flip:
        P = P[::-1]
    mb.parts.setdefault(mat, []).append(P)




def brick_material():
    m, nt, b = principled("ARMS_SP_Brick_Red", (0.36, 0.13, 0.06), rough=0.92, spec=0.15)
    uv = nt.nodes.new("ShaderNodeTexCoord")
    br = nt.nodes.new("ShaderNodeTexBrick")
    br.offset = 0.5
    br.inputs["Scale"].default_value = 1.0
    br.inputs["Brick Width"].default_value = 0.2032
    br.inputs["Row Height"].default_value = 0.0677
    br.inputs["Mortar Size"].default_value = 0.0045
    br.inputs["Color1"].default_value = (0.415, 0.147, 0.062, 1)
    br.inputs["Color2"].default_value = (0.34, 0.115, 0.05, 1)
    br.inputs["Mortar"].default_value = (0.40, 0.36, 0.30, 1)
    br.inputs["Bias"].default_value = 0.0
    nt.links.new(uv.outputs["UV"], br.inputs["Vector"])
    nt.links.new(br.outputs["Color"], b.inputs["Base Color"])
    bump = nt.nodes.new("ShaderNodeBump")
    bump.inputs["Strength"].default_value = 0.25
    nt.links.new(br.outputs["Fac"], bump.inputs["Height"])
    nt.links.new(bump.outputs["Normal"], b.inputs["Normal"])
    return m


def mats():
    """Base colours from audit/neil_armstrong_hall/second_pass/sources/color_samples.json and the
    Reynobond 'Mayflower Red' / 'Sea Wolf' specification (design_facts.json)."""
    M = {}
    M["brick"] = brick_material()
    M["lime"] = principled("ARMS_SP_Limestone", (0.62, 0.58, 0.48), rough=0.85, spec=0.2)[0]
    M["red"] = principled("ARMS_SP_Mayflower_Red_ACM", (0.24, 0.036, 0.016), rough=0.38, metal=0.3)[0]
    M["seawolf"] = principled("ARMS_SP_Sea_Wolf_ACM", (0.36, 0.37, 0.37), rough=0.35, metal=0.5)[0]
    M["white"] = principled("ARMS_SP_White_Overhang", (0.66, 0.66, 0.63), rough=0.45, metal=0.2)[0]
    M["glass"] = principled("ARMS_SP_Glass", (0.07, 0.15, 0.15), rough=0.05, metal=0.3)[0]
    M["frame"] = principled("ARMS_SP_Mullion_Silver", (0.58, 0.60, 0.61), rough=0.3, metal=0.75)[0]
    M["bronze"] = M["frame"]
    M["roof"] = principled("ARMS_SP_Roof_Membrane", (0.55, 0.56, 0.56), rough=0.85)[0]
    M["unit"] = principled("ARMS_SP_Rooftop_Unit", (0.55, 0.56, 0.57), rough=0.5, metal=0.4)[0]
    M["floor"] = principled("ARMS_SP_Floor", (0.55, 0.52, 0.46), rough=0.6)[0]
    M["letter"] = principled("ARMS_SP_Letter_Silver", (0.62, 0.63, 0.64), rough=0.3, metal=0.9)[0]
    M["steel"] = principled("ARMS_SP_Steel_Grey", (0.30, 0.31, 0.32), rough=0.4, metal=0.7)[0]
    return M


# ---------------------------------------------------------------- footprint (LiDAR NDHM + 2018/2023 orthophotos)
# Positions/heights from the lean-free 2017-2019 QL2 LiDAR height model (sources/na_ndhm_2018.*); walls set back
# from the measured roof/eyebrow edges. See second_pass/ortho_trace_notes.md.
BAR_S_Y = -13.0
EAST_NOTCH = (72.0, -5.0)   # inner corner of the inward east entrance notch (Street View, user)
REAR_GLASS_X = (2.0, 16.0)  # full-height rear (courtyard) main entrance mid-facade (user photo)
NORTH_GLASS = 34.0   # north curtain-wall length east of the entrance corner (photo estimate)
BAR_NW_Y = 17.0
NOTCH_CORNER = (-60.0, 3.0)    # re-entrant entrance corner under the NW roof point (user review + photos)
ENTRY_GLASS_X0 = -66.0         # west end of the glazed entrance bay in the west wing's north face
BAR = [(-44.0, BAR_S_Y), (EAST_NOTCH[0], BAR_S_Y), EAST_NOTCH, (76.5, EAST_NOTCH[1]), (53.0, BAR_NW_Y), (-60.0, BAR_NW_Y), (-60.0, 3.0), (-44.0, 3.0)]  # east end follows the diagonal outline under the east point (user review; LiDAR)
SW_RECT = (-80.0, -31.0, -44.0, 3.0)   # west face length per entrance photos (user review)   # west wing: plain rectangle (x0, y0, x1, y1)
SW_TOP_CTRL = (-82.5, -34.0)   # Bezier control of the separate curved top floor (rounded W/SW corner)
SW_TOP_S_INSET = 18.0          # where the curve meets the straight south side of the top floor
SE_WING = [(37.0, -13.0), (51.0, -37.5), (53.0, -37.5), (69.0, -13.0)]
BAR_H = 17.0      # main-bar walls up to the sloped eyebrow (LiDAR: eyebrow 16.3-20 m, flat top 21.6 m)
EAVE = 21.5       # red high roof: a flat plane (the soaring look of the NW point is perspective)
TIP = (-81.0, 23.0, EAVE)
WING_BRICK = 11.8
WING_TOP = 14.8   # wing roofs ~15.5 m in the LiDAR
FLOORS = [(1.2, 3.2), (5.2, 7.2), (9.2, 11.2), (13.0, 15.2)]
CURTAIN_X = (-44.0, -22.0)  # south curtain wall with horizontal sun-shade blades (2016_02 photo)


def ccw(poly):
    a = sum(poly[i][0] * poly[(i + 1) % len(poly)][1] - poly[(i + 1) % len(poly)][0] * poly[i][1] for i in range(len(poly)))
    return poly if a > 0 else poly[::-1]


def punched(L, rows, pitch=3.6, pair=True, w=0.95, gap=0.35):
    ops = []
    nb = max(1, int(L / pitch))
    bw = L / nb
    for b in range(nb):
        c = b * bw + bw / 2
        for z0, z1 in rows:
            if pair and bw > 2 * w + gap + 0.6:
                ops.append((c - gap / 2 - w, c - gap / 2, z0, z1))
                ops.append((c + gap / 2, c + gap / 2 + w, z0, z1))
            elif bw > w + 0.6:
                ops.append((c - w / 2, c + w / 2, z0, z1))
    return ops


def bar_bands(mb, A, B):
    band(mb, A, B, 0.0, 1.0, proj=0.10, ext=0.02)
    for z in (4.2, 8.2, 12.2):
        band(mb, A, B, z - 0.12, z + 0.12, proj=0.05, ext=0.02)
    band(mb, A, B, 15.8, 16.2, proj=0.08, ext=0.02)


def build_bar(mb):
    P = [Vector(p) for p in ccw(BAR)]
    n = len(P)
    for i in range(n):
        A, B = P[i], P[(i + 1) % n]
        _, t, nn, L = seg_frame(A, B)
        if L < 1.0:
            continue
        if nn.x > 0.5 and nn.y > 0.3:
            # diagonal east face: mostly blank brick with limestone bands and a glazed slot by the notch
            ops = [(0.6, 2.4, 0.4, BAR_H - 0.6, "win")]
            ops += [(o[0] + 5.0, o[1] + 5.0, o[2], o[3]) for o in punched(L - 6.0, FLOORS[1:3], pitch=6.0, pair=False, w=1.0)]
            wall(mb, A, B, 0.0, BAR_H, 0.4, ops, mullions=0)
            band(mb, A, B, 0.0, 1.0, proj=0.10, ext=0.02)
            band(mb, A, B, 8.1, 8.35, proj=0.06, ext=0.02)
            band(mb, A, B, 12.1, 12.35, proj=0.06, ext=0.02)
            band(mb, A, B, 15.8, 16.2, proj=0.08, ext=0.02)
            continue
        if (nn.x > 0.9 or nn.y > 0.9) and abs(A.x - EAST_NOTCH[0]) < 0.1 or (nn.y > 0.9 and abs(A.y - EAST_NOTCH[1]) < 0.1):
            # inward notch faces: full-height glass, doors in the east-facing face
            ops = [(0.1, L - 0.1, 4.0, BAR_H - 0.3, "win")]
            if nn.x > 0.9:
                ops += [(0.4, L - 0.4, 0.0, 3.3, "door")]
                mb.box("seawolf", A + t * 0.2 + nn * 0.05, t, -nn, L - 0.4, 0.35, 3.3, 4.0)
            else:
                ops += [(0.1, L - 0.1, 0.4, 3.8, "win")]
            wall(mb, A, B, 0.0, BAR_H, 0.25, ops, mullions=max(1, int(L / 1.5)) - 1, inset=0.12)
            for z in [4.0, 8.2, 12.2]:
                mb.box("frame", A + nn * 0.02, t, -nn, L, 0.1, z, z + 0.08)
            continue
        if False and nn.x > 0.5:
            # (superseded) diagonal east end under the east roof point: glazed entrance bay with doors and a Sea Wolf canopy
            # (location from the orthophoto paths converging under the point; facade unseen in photos)
            # east end: full-height glazed entrance wall along the diagonal (ECN Physics webcam, 2009)
            c = L * 0.4
            ops = [(0.1, L - 0.1, 4.0, BAR_H - 0.3, "win"), (0.1, c - 3.5, 0.4, 3.8, "win"),
                   (c + 3.5, L - 0.1, 0.4, 3.8, "win"), (c - 3.0, c + 3.0, 0.0, 3.3, "door")]
            wall(mb, A, B, 0.0, BAR_H, 0.3, ops, mullions=int(L / 1.6), inset=0.12)
            for z in [4.0, 8.2, 12.2]:
                mb.box("frame", A + nn * 0.02, t, -nn, L, 0.12, z, z + 0.1)
            mb.box("seawolf", A + t * (c - 4.0), t, nn, 8.0, 2.4, 3.6, 4.0)
            continue
        if nn.y > 0.9:
            gw = NORTH_GLASS  # full-height curtain wall from the entrance corner eastward (Kawneer/AGM photos)
            ops = [o for o in punched(L, FLOORS) if o[1] < L - gw - 0.6]
            ops.append((L - gw, L - 0.05, 0.4, BAR_H - 0.4, "win"))
            wall(mb, A, B, 0.0, BAR_H, 0.4, ops, mullions=int(gw / 1.6))
            bar_bands(mb, A, A + t * (L - gw))
            for z in [4.2, 8.2, 12.2]:
                mb.box("frame", A + t * (L - gw) + nn * 0.02, t, -nn, gw, 0.12, z, z + 0.1)
            for k in range(4):  # pale vertical fins at the east end of the curtain wall
                u = L - gw + 0.8 + k * 2.2
                mb.box("lime", A + t * u + nn * 0.05, t, nn, 0.6, 1.4, 0.0, 12.5)
        elif nn.y < -0.9 and abs(A.y - BAR_S_Y) < 0.1:
            # south face west->east pieces: curtain wall (separate), blank brick return, punched brick,
            # then the SE wing abuts (hidden)
            y = A.y
            for x0, x1, kind in ((CURTAIN_X[1], -15.0, "blank"), (-15.0, REAR_GLASS_X[0], "punched"),
                                 (REAR_GLASS_X[0], REAR_GLASS_X[1], "glass"), (REAR_GLASS_X[1], 37.0, "punched"),
                                 (69.0, EAST_NOTCH[0], "blank")):
                S0, S1 = Vector((x1, y)), Vector((x0, y))  # CCW order runs east->west on the south face
                if (B - A).x > 0:
                    S0, S1 = S1, S0
                LL = (S1 - S0).length
                if kind == "glass":
                    wall(mb, S0, S1, 0.0, BAR_H, 0.3, [(0.1, LL - 0.1, 4.2, BAR_H - 0.4, "win"), (0.1, LL - 0.1, 0.4, 3.9, "win"),
                                                      (LL / 2 - 2.5, LL / 2 + 2.5, 0.0, 3.3, "door")], mullions=int(LL / 1.6), inset=0.12)
                    for z in [4.2, 8.2, 12.2]:
                        mb.box("frame", S0 - Vector((0, 0.02)), (S1 - S0).normalized(), Vector((0, 1)), LL, 0.1, z, z + 0.08)
                    for xx in (min(S0.x, S1.x) - 0.6, max(S0.x, S1.x)):   # pale pilaster frame (photo)
                        mb.box("lime", (xx, BAR_S_Y - 0.5), (1, 0), (0, 1), 0.6, 0.5, 0.0, BAR_H)
                    continue
                wall(mb, S0, S1, 0.0, BAR_H, 0.4, [] if kind == "blank" else punched(LL, FLOORS, pitch=3.0, pair=False, w=1.0))
                bar_bands(mb, S0, S1)
        # remaining west-side edges are enclosed by the atrium / SW wing

    # south curtain wall with Versoleil-type horizontal blades
    A, B = Vector((CURTAIN_X[1], BAR[0][1])), Vector((CURTAIN_X[0], BAR[0][1]))
    wall(mb, A, B, 0.0, BAR_H - 0.6, 0.3, [(0.05, (A - B).length - 0.05, 0.6, BAR_H - 0.9, "win")], mullions=11)
    for z in [5.0 + 1.1 * k for k in range(10)]:
        mb.box("frame", (CURTAIN_X[0], BAR[0][1] - 0.95), (1, 0), (0, 1), CURTAIN_X[1] - CURTAIN_X[0], 0.9, z, z + 0.06)
    for x in [CURTAIN_X[0] + k * 3.0 for k in range(7)]:
        mb.box("frame", (x - 0.04, BAR[0][1] - 1.0), (1, 0), (0, 1), 0.08, 1.0, 4.8, BAR_H - 1.0)
    for z in (4.2, 8.2, 12.2):  # floor-edge transoms
        mb.box("frame", (CURTAIN_X[0], BAR[0][1] - 0.1), (1, 0), (0, 1), CURTAIN_X[1] - CURTAIN_X[0], 0.12, z, z + 0.12)
    # entrance doors at the base of the curtain wall (east end, by the brick return)
    mb.box("seawolf", (CURTAIN_X[1] - 9.0, BAR[0][1] - 1.6), (1, 0), (0, 1), 8.6, 1.6, 3.5, 3.9)
    # roof membrane + mechanical penthouse
    flat_poly(mb, "roof", BAR, BAR_H - 0.3)
    # infill between the wall tops and the flat top / clerestory (hidden under the eyebrows)
    for (y, h) in ((11.0, 20.0), (-5.5, 20.0)):
        mb.box("roof", (-44.0, y - 0.2), (1, 0), (0, 1), 99.0, 0.4, BAR_H - 0.3, h)


def build_atrium(mb):
    """Square, INWARD entrance corner under the NW roof point: the glazed west end of the main bar and a glazed
    entrance bay in the west wing's north face meet at a re-entrant corner; doors sit in the north-facing glass
    under a Sea Wolf ACM head, the Armstrong statue in front (photos 2016_01/04/05, DD_22, user review)."""
    H = 17.5
    cx, cy = NOTCH_CORNER
    # west-facing glass: main bar west end (CCW: north -> south)
    A, B = Vector((cx, BAR_NW_Y)), Vector((cx, cy))
    _, t, nn, L = seg_frame(A, B)
    wall(mb, A, B, 0.0, H, 0.25, [(0.1, L - 0.1, 0.4, H - 0.4, "win")], mullions=max(1, int(L / 1.6)) - 1, inset=0.12)
    for z in [4.4 + 2.2 * q for q in range(8)]:
        mb.box("frame", A + nn * 0.02, t, -nn, L, 0.1, z, z + 0.07)
    # north-facing glass entrance bay in the west wing (CCW: east -> west)
    A, B = Vector((cx, cy)), Vector((ENTRY_GLASS_X0, cy))
    _, t, nn, L = seg_frame(A, B)
    ops = [(0.1, L - 0.1, 4.6, H - 0.4, "win"), (0.4, L - 0.4, 0.0, 3.3, "door")]
    wall(mb, A, B, 0.0, H, 0.25, ops, mullions=max(1, int(L / 1.5)) - 1, inset=0.12)
    for z in [4.4 + 2.2 * q for q in range(8)]:
        mb.box("frame", A + nn * 0.02, t, -nn, L, 0.1, z, z + 0.07)
    mb.box("seawolf", A + t * 0.2 + nn * 0.05, t, -nn, L - 0.4, 0.35, 3.3, 4.5)    # door head panel
    mb.box("frame", (cx - 0.2, cy - 0.2), (1, 0), (0, 1), 0.4, 0.4, 0.0, H)      # re-entrant corner mullion
    mb.box("lime", (ENTRY_GLASS_X0 - 2.0, cy), (1, 0), (0, 1), (cx - ENTRY_GLASS_X0) + 6.0, 8.0, -0.05, 0.12)  # entry plaza


def bezier(p0, c, p1, n=12):
    p0, c, p1 = Vector(p0), Vector(c), Vector(p1)
    return [(1 - u) ** 2 * p0 + 2 * (1 - u) * u * c + u ** 2 * p1 for u in [k / n for k in range(n + 1)]]


def wing_bands(mb, A, B):
    band(mb, A, B, 0.0, 0.9, proj=0.10, ext=0.02)
    band(mb, A, B, 4.3, 4.5, proj=0.05, ext=0.02)
    band(mb, A, B, WING_BRICK - 0.35, WING_BRICK + 0.15, proj=0.12, ext=0.02)


def sw_units(mb, A, t, nn, L):
    """Two-storey limestone-framed window units with small paired windows above (DD_24)."""
    ops = []
    nb = max(1, int(L / 6.5))
    bw = L / nb
    for b in range(nb):
        c = b * bw + bw / 2
        ops += [(c - 1.2, c + 1.2, 1.0, 8.4), (c - 1.0, c - 0.15, 9.6, 11.8), (c + 0.15, c + 1.0, 9.6, 11.8)]
    return ops


def limestone_surrounds(mb, A, t, nn, ops):
    for o in ops:
        if len(o) == 4 and o[3] - o[2] > 6:
            for (u0, u1) in ((o[0] - 0.25, o[0]), (o[1], o[1] + 0.25)):
                mb.box("lime", A + t * u0 + nn * 0.12, t, -nn, u1 - u0, 0.2, 0.9, 8.6)
            mb.box("lime", A + t * (o[0] - 0.25) + nn * 0.12, t, -nn, o[1] - o[0] + 0.5, 0.2, 8.4, 8.75)


def build_sw_wing(mb):
    """West wing: a plain rectangular brick block; a separate curved glass top floor with white roof sits on it."""
    x0, y0, x1, y1 = SW_RECT
    cx, cy = NOTCH_CORNER
    # north face: brick west of the glazed entrance bay (name letters), the rest is under the main bar
    A, B = Vector((ENTRY_GLASS_X0, y1)), Vector((x0, y1))
    _, t, nn, L = seg_frame(A, B)
    wall(mb, A, B, 0.0, WING_BRICK, 0.4, [(L - 3.0, L - 1.8, 1.2, 8.4)])
    wing_bands(mb, A, B)
    # brick above the glazed entrance bay is replaced by glass (atrium) - bands continue across
    # west face
    A, B = Vector((x0, y1)), Vector((x0, y0))
    _, t, nn, L = seg_frame(A, B)
    ops = sw_units(mb, A, t, nn, L)
    limestone_surrounds(mb, A, t, nn, ops)
    wall(mb, A, B, 0.0, WING_BRICK, 0.4, ops)
    wing_bands(mb, A, B)
    # south face with the south-west entrance, steps and portal
    A, B = Vector((x0, y0)), Vector((x1, y0))
    _, t, nn, L = seg_frame(A, B)
    ops = sw_units(mb, A, t, nn, L)
    c = L * 0.35
    ops = [o for o in ops if o[1] < c - 2.8 or o[0] > c + 2.8] + [(c - 2.4, c + 2.4, 0.0, 3.4, "door")]
    limestone_surrounds(mb, A, t, nn, ops)
    mb.box("lime", A + t * (c - 3.0) + nn * 0.15, t, -nn, 6.0, 0.3, 3.4, 4.3)
    for k in range(3):
        mb.box("lime", A + t * (c - 4.0) + nn * (2.4 - 0.6 * k), t, -nn, 8.0, 0.6 + 0.6 * k, -0.6 + 0.2 * k, -0.2 + 0.2 * k)
    wall(mb, A, B, 0.0, WING_BRICK, 0.4, ops)
    wing_bands(mb, A, B)
    # east face: only the part south of the main bar faces the courtyard
    A, B = Vector((x1, y0)), Vector((x1, BAR_S_Y))
    _, t, nn, L = seg_frame(A, B)
    wall(mb, A, B, 0.0, WING_BRICK, 0.4, punched(L, [(5.6, 7.8), (10.0, 12.2)], pitch=4.0))
    wing_bands(mb, A, B)
    flat_poly(mb, "roof", [(x0, y0), (x1, y0), (x1, y1), (x0, y1)], WING_BRICK + 0.1)
    # separate curved top floor on the rectangle: straight N and E sides, rounded W/SW corner
    i = 0.6
    nw, se = Vector((x0 + i, y1 - i)), Vector((x1 - i, y0 + i))
    top = [Vector((x1 - i, y1 - i)), nw] + bezier(nw, SW_TOP_CTRL, Vector((x0 + SW_TOP_S_INSET, y0 + i)))[1:] + [se]
    T = [Vector(p) for p in ccw([(p.x, p.y) for p in top])]
    nT = len(T)
    for k in range(nT):
        A, B = T[k], T[(k + 1) % nT]
        _, t, nn, L = seg_frame(A, B)
        if L < 0.3:
            continue
        wall(mb, A, B, WING_BRICK + 0.15, WING_TOP, 0.25, [(0.03, L - 0.03, WING_BRICK + 0.6, WING_TOP - 0.35, "win")],
             mullions=max(0, int(L / 1.5) - 1), inset=0.1)
        mb.box("white", A - t * 0.05 + nn * 1.5, t, -nn, L + 0.1, 1.6, WING_TOP, WING_TOP + 0.75)   # overhang fascia
    flat_poly(mb, "white", [(p.x, p.y) for p in T], WING_TOP + 0.75)


def build_wing(mb, poly, style="se"):
    """SE wing: brick with punched windows, straight glass top floor and white overhang (facades unseen)."""
    P = [Vector(p) for p in ccw(poly)]
    n = len(P)
    for k in range(n):
        A, B = P[k], P[(k + 1) % n]
        _, t, nn, L = seg_frame(A, B)
        if L < 0.5 or (nn.y > 0.9 and abs(A.y - BAR_S_Y) < 0.3):
            continue
        wall(mb, A, B, 0.0, WING_BRICK, 0.4, punched(L, [(1.3, 3.1), (5.1, 6.9), (8.9, 10.7)], pitch=3.4, pair=False, w=1.1))
        wing_bands(mb, A, B)
        S0, S1 = A - nn * 0.6, B - nn * 0.6
        wall(mb, S0, S1, WING_BRICK + 0.15, WING_TOP, 0.25, [(0.05, L - 0.05, WING_BRICK + 0.6, WING_TOP - 0.35, "win")],
             mullions=max(0, int(L / 1.5) - 1), inset=0.1)
        mb.box("white", A - t * 0.05 + nn * 1.5, t, -nn, L + 0.1, 2.3, WING_TOP, WING_TOP + 0.75)
    flat_poly(mb, "white", [(p.x, p.y) for p in P], WING_TOP + 0.75)


def red_tri(mb, a, b, c, dn):
    tri = [a, b, c] if (b - a).cross(c - a).z >= 0 else [a, c, b]
    mb.parts.setdefault("red", []).append(tri)
    mb.parts.setdefault("red", []).append([p - dn for p in tri][::-1])


def red_edge(mb, a, b, dn):
    mb.quad("red", [a - dn, b - dn, b, a])


def build_high_roof(mb):
    """The red Mayflower ACM roof is ONE continuous piece (user review): a ring around the main bar's flat top with
    a flat underside everywhere, a top surface that falls toward the outer edge (LiDAR NDHM: ~20 m inside, lower
    at the edge), a sharp NW point over the entrance and the west wing with a symmetric triangular hole and a
    support beam down its middle, and a small east point just beyond the diagonal east wall."""
    from mathutils.geometry import tessellate_polygon
    z_bot, z_edge, z_in = 17.8, 18.4, 20.0
    T = Vector((-84.0, 21.0))
    outer = [T, Vector((54.5, 18.7)), Vector((87.5, -14.7)), Vector((-44.0, -15.0)), Vector((-72.0, -15.0))]
    inner = [Vector((-60.0, 11.0)), Vector((52.0, 11.0)), Vector((68.0, -5.5)), Vector((-41.0, -5.5))]
    d = ((outer[1] - T).normalized() + (outer[4] - T).normalized()).normalized()
    pdir = Vector((-d.y, d.x))
    N, C = T + d * 9.0, T + d * 24.0
    hole = [N, C + pdir * 6.0, C - pdir * 6.0]

    def dist_outer(p):
        best = 1e9
        for k in range(len(outer)):
            a, b = outer[k], outer[(k + 1) % len(outer)]
            ab = b - a
            t = max(0.0, min(1.0, (p - a).dot(ab) / ab.length_squared))
            best = min(best, (p - (a + ab * t)).length)
        return best

    def ztop(p):
        return z_edge + (z_in - z_edge) * min(1.0, dist_outer(p) / 7.0)

    def densify(loop, step=3.0):
        out = []
        for k in range(len(loop)):
            a, b = loop[k], loop[(k + 1) % len(loop)]
            n = max(1, int((b - a).length / step))
            out += [a.lerp(b, i / n) for i in range(n)]
        return out
    loops = [densify(outer), densify(inner), densify(hole, 2.0)]
    flat = [p for lp in loops for p in lp]
    tris = tessellate_polygon([[Vector((p.x, p.y, 0)) for p in lp] for lp in loops])
    for (i, j, k) in tris:
        a, b, c = (Vector((flat[q].x, flat[q].y, ztop(flat[q]))) for q in (i, j, k))
        tri = [a, b, c] if (b - a).cross(c - a).z >= 0 else [a, c, b]
        mb.parts.setdefault("red", []).append(tri)                                    # sloped top
        mb.parts.setdefault("red", []).append([Vector((p.x, p.y, z_bot)) for p in tri][::-1])  # flat soffit
    for lp in loops:   # edge faces: outer fascia, inner edge, hole edges
        for k in range(len(lp)):
            a, b = lp[k], lp[(k + 1) % len(lp)]
            mb.quad("red", [Vector((a.x, a.y, z_bot)), Vector((b.x, b.y, z_bot)), Vector((b.x, b.y, ztop(b))), Vector((a.x, a.y, ztop(a)))])
    # support beam down the middle of the hole (apex to base)
    Lb = (C - N).length
    mb.box("red", N - pdir * 0.35, d, pdir, Lb, 0.7, z_bot - 0.7, z_bot)
    # red sloped panel seen through the hole on the building side (photos)
    hl, hr = C + pdir * 6.0, C - pdir * 6.0
    mb.quad("red", [Vector((hl.x, hl.y, z_bot - 0.6)), Vector((hr.x, hr.y, z_bot - 0.6)),
                    Vector((*(hr.lerp(N, 0.4)), z_bot - 2.4)), Vector((*(hl.lerp(N, 0.4)), z_bot - 2.4))])
    # infill between the main-bar wall tops and the soffit
    flat_poly(mb, "roof", [(p.x, p.y) for p in inner], z_bot)
    # flat top with clerestory glass steps on both long sides
    top = [(p.x, p.y) for p in inner]
    flat_poly(mb, "roof", top, 21.6)
    for (a, b) in (((52.0, 11.0), (-60.0, 11.0)), ((-41.0, -5.5), (68.0, -5.5))):
        A, B = Vector(a), Vector(b)
        _, t, nn, Ls = seg_frame(A, B)
        wall(mb, A, B, z_in - 0.2, 21.6, 0.2, [(0.1, Ls - 0.1, z_in, 21.4, "win")], mullions=int(Ls / 2.0), inset=0.08)
    for (a, b) in (((-60.0, 11.0), (-41.0, -5.5)), ((68.0, -5.5), (52.0, 11.0))):
        A, B = Vector(a), Vector(b)
        wall(mb, A, B, z_bot, 21.6, 0.2)
    mb.box("unit", (40.0, -2.0), (1, 0), (0, 1), 9.0, 9.0, 21.6, 23.2)


def floors(mb):
    x0, y0, x1, y1 = SW_RECT
    for poly in (BAR, [(x0, y0), (x1, y0), (x1, y1), (x0, y1)], SE_WING):
        flat_poly(mb, "floor", poly, 0.04)


DELETE_PREFIX = ("ARMS_East_", "ARMS_West_", "ARMS_R5_", "ARMS_R6_", "ARMS_R12_9_", "ARMS_Cantilever_Canopy_Deck",
                 "ARMS_Curtain_Glass_Bay", "ARMS_Curved_Mullion", "ARMS_Curved_Transom", "ARMS_Atrium_South_Wall",
                 "ARMS_Atrium_Skylight_Glazing", "ARMS_Roof_Steel_Truss", "ARMS_Canopy_", "ARMS_Light_Canopy",
                 "ARMS_Entrance_Portal_Frame", "ARMS_Revolving_Door", "ARMS_Door_Hardware", "ARMS_Building_Sign_Header",
                 "ARMS_Gold_Lettering_Band", "ARMS_Atrium_Terrazzo_Floor", "ARMS_Moon_Plaza", "Apollo11_Bootprint",
                 "ARMS_Plaza_", "ARMS_Bike_Rack", "ARMS_LED_Bollard", "ARMS_SP_")
STATUE = ("ARMS_Statue_",)
STATUE_OFFSET = Vector((-65.75, -6.6, 0.0))     # in front of the entrance corner under the roof point (photos)
INTERIOR_OFFSET = Vector((-4.0, 18.0, 0.0))    # interior program moved inside the corrected main bar


def relocate():
    for ob in bpy.data.objects:
        if ob.name in (ROOT,) or not ob.name.startswith(("ARMS_", "Apollo")):
            continue
        if ob.parent is None or ob.parent.name != ROOT:
            continue
        off = STATUE_OFFSET if ob.name.startswith(STATUE) else INTERIOR_OFFSET
        if "sp_orig" not in ob:
            ob["sp_orig"] = list(ob.location)
        ob.location = Vector(ob["sp_orig"]) + off


def main():
    root = bpy.data.objects[ROOT]
    for ob in list(bpy.data.objects):
        if ob.name.startswith(DELETE_PREFIX):
            bpy.data.objects.remove(ob, do_unlink=True)
    for coll in (bpy.data.curves, bpy.data.meshes):
        for d in list(coll):
            if d.users == 0:
                coll.remove(d)
    relocate()
    M = mats()
    mb = MB()
    build_bar(mb)
    mb.build("ARMS_SP_MainBar", M, root)
    build_atrium(mb)
    mb.build("ARMS_SP_Atrium", M, root)
    build_sw_wing(mb)
    mb.build("ARMS_SP_SW_Wing", M, root)
    build_wing(mb, SE_WING)
    mb.build("ARMS_SP_SE_Wing", M, root)
    build_high_roof(mb)
    mb.build("ARMS_SP_HighRoof", M, root)
    floors(mb)
    mb.build("ARMS_SP_Floors", M, root)
    # building name letters on the SW wing north face beside the atrium (photo 2016_01)
    cu = bpy.data.curves.new("ARMS_SP_Name", "FONT")
    cu.body = "NEIL ARMSTRONG HALL OF ENGINEERING"
    cu.size = 0.5
    cu.extrude = 0.03
    cu.align_x = "CENTER"
    ob = bpy.data.objects.new("ARMS_SP_Name_Letters", cu)
    ob.location = (-69.5, 3.1, 2.2)
    ob.rotation_euler = (math.radians(90), 0, math.radians(180))
    cu.materials.append(M["letter"])
    bpy.data.collections[COLL].objects.link(ob)
    ob.parent = root
    for m in list(bpy.data.materials):
        if m.users == 0:
            bpy.data.materials.remove(m)
    bpy.ops.wm.save_mainfile()
    print("ARMS_SP_DONE", len(bpy.data.collections[COLL].objects))


main()
