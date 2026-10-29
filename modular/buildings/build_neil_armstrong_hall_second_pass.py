"""Neil Armstrong Hall of Engineering second-pass exterior rebuild (rank 2, Rossen second pass).

Run headless on the saved library, which it edits in place and saves:
    blender -b modular/buildings/neil_armstrong_hall.blend --python modular/buildings/build_neil_armstrong_hall_second_pass.py

Idempotent: deletes the first-pass exterior shell (DELETE_PREFIX) and every ARMS_SP_* object, then rebuilds
the main bar, NW glass entrance corner, west wing (curved glass top floor on the block), SE wing (flush with the
pointed east end) and the uniform-width red roof band with its upturned NW point, from the satellite/LiDAR trace,
the published floor plan (Sensors 2020 fig. 4) and the photographs indexed in audit/neil_armstrong_hall/second_pass/.
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
    # darker red-brown with purple-toned headers: overcast DD_24 brick sRGB ~(96,71,59), sunlit rear photo ~(212,159,139)
    m, nt, b = principled("ARMS_SP_Brick_Red", (0.28, 0.11, 0.08), rough=0.92, spec=0.15)
    uv = nt.nodes.new("ShaderNodeTexCoord")
    br = nt.nodes.new("ShaderNodeTexBrick")
    br.offset = 0.5
    br.inputs["Scale"].default_value = 1.0
    br.inputs["Brick Width"].default_value = 0.2032
    br.inputs["Row Height"].default_value = 0.0677
    br.inputs["Mortar Size"].default_value = 0.0045
    br.inputs["Color1"].default_value = (0.31, 0.125, 0.09, 1)
    br.inputs["Color2"].default_value = (0.22, 0.085, 0.075, 1)
    br.inputs["Mortar"].default_value = (0.32, 0.30, 0.27, 1)
    br.inputs["Bias"].default_value = 0.0
    nt.links.new(uv.outputs["UV"], br.inputs["Vector"])
    nt.links.new(br.outputs["Color"], b.inputs["Base Color"])
    bump = nt.nodes.new("ShaderNodeBump")
    bump.inputs["Strength"].default_value = 0.25
    nt.links.new(br.outputs["Fac"], bump.inputs["Height"])
    nt.links.new(bump.outputs["Normal"], b.inputs["Normal"])
    return m


def panel_material():
    """Mayflower Red ACM with the cladding's panel joints (about 3.0 x 1.5 m panels, 2016_01 / 2016_03)."""
    m, nt, b = principled("ARMS_SP_Mayflower_Red_ACM", (0.24, 0.036, 0.016), rough=0.38, metal=0.3)
    uv = nt.nodes.new("ShaderNodeTexCoord")
    br = nt.nodes.new("ShaderNodeTexBrick")
    br.offset = 0.5
    br.inputs["Scale"].default_value = 1.0
    br.inputs["Brick Width"].default_value = 3.0
    br.inputs["Row Height"].default_value = 1.5
    br.inputs["Mortar Size"].default_value = 0.025
    br.inputs["Color1"].default_value = (0.24, 0.036, 0.016, 1)
    br.inputs["Color2"].default_value = (0.225, 0.033, 0.015, 1)
    br.inputs["Mortar"].default_value = (0.09, 0.015, 0.008, 1)
    br.inputs["Bias"].default_value = 0.0
    nt.links.new(uv.outputs["UV"], br.inputs["Vector"])
    nt.links.new(br.outputs["Color"], b.inputs["Base Color"])
    return m


def mats():
    """Base colours from audit/neil_armstrong_hall/second_pass/sources/color_samples.json and the
    Reynobond 'Mayflower Red' / 'Sea Wolf' specification (design_facts.json)."""
    M = {}
    M["brick"] = brick_material()
    M["lime"] = principled("ARMS_SP_Limestone", (0.62, 0.58, 0.48), rough=0.85, spec=0.2)[0]
    M["red"] = panel_material()
    M["seawolf"] = principled("ARMS_SP_Sea_Wolf_ACM", (0.36, 0.37, 0.37), rough=0.35, metal=0.5)[0]
    M["white"] = principled("ARMS_SP_White_Overhang", (0.66, 0.66, 0.63), rough=0.45, metal=0.2)[0]
    # lighter, reflective blue-green-grey glazing (DD_24 window sRGB ~(98,106,109), rear curtain wall ~(41,84,86))
    M["glass"] = principled("ARMS_SP_Glass", (0.17, 0.23, 0.24), rough=0.04, metal=0.55, spec=0.8)[0]
    M["frame"] = principled("ARMS_SP_Mullion_Silver", (0.58, 0.60, 0.61), rough=0.3, metal=0.75)[0]
    M["bronze"] = M["frame"]
    M["roof"] = principled("ARMS_SP_Roof_Membrane", (0.55, 0.56, 0.56), rough=0.85)[0]
    M["unit"] = principled("ARMS_SP_Rooftop_Unit", (0.55, 0.56, 0.57), rough=0.5, metal=0.4)[0]
    M["floor"] = principled("ARMS_SP_Floor", (0.55, 0.52, 0.46), rough=0.6)[0]
    M["letter"] = principled("ARMS_SP_Letter_Silver", (0.62, 0.63, 0.64), rough=0.3, metal=0.9)[0]
    M["steel"] = principled("ARMS_SP_Steel_Grey", (0.30, 0.31, 0.32), rough=0.4, metal=0.7)[0]
    return M


# ---------------------------------------------------------------- footprint
# Plan traced from a user-supplied north-up satellite screenshot registered to the LiDAR height model by the two red
# roof tips (scale ~0.111 m/px), cross-checked with the 2018/2023 IndianaMap aerials and the floor-plan figure.
# Heights from the lean-free 2017-2019 QL2 LiDAR NDHM (sources/na_ndhm_2018.*). See change_log.md.
BAR_S_Y = -12.5
BAR_NW_Y = 17.0
NORTH_GLASS = 22.0   # glass section on the north facade east of the entrance (drone photo; user: shorter than 34 m)
LOADING_DOCK_X = (16.0, 21.0)   # small loading-dock door on the courtyard side, no windows around it (user review)
U_DIAG = Vector((0.758, 0.652))   # direction of the west wing's NW/SE sides (satellite)
W_W0, W_S, W_E = Vector((-81.4, -2.9)), Vector((-60.1, -39.6)), Vector((-40.1, -22.4))   # satellite trace corners
W_N = W_E + (W_W0 - W_S)                                                                  # north corner (under the bar)
ENTRY_CORNER = W_W0 + U_DIAG * 20.0    # square inward entrance corner (west wing NW face meets the bar's west end)
ENTRY_BAY = 9.6                        # glazed doors bay in the west wing's NW face: six 1.6 m panes (user: wider)
# West wing widened toward the west (user review): the W corner moves out along the NW face line until the west wall's
# chord runs at 45 deg in plan, in line with the red roof's west arm, and the whole west wall - brick block and glass
# top floor alike - bows out in one convex curve
W_W = W_W0 - U_DIAG * 10.9
SW_SAG = 4.0                           # how far the top floor's west curve bows out past its chord (user: half of 8 m)


def _sw_curve(n=40):
    t = (W_S - W_W).normalized()
    c = (W_W + W_S) / 2 + Vector((t.y, -t.x)) * (2.0 * SW_SAG)   # quadratic Bezier peaks at half its control offset
    return [(1 - u) ** 2 * W_W + 2 * (1 - u) * u * c + u ** 2 * W_S for u in [k / n for k in range(n + 1)]]


SW_CURVE = _sw_curve()                 # glass top floor's west side: W corner -> S corner
ARM_DIR = Vector((0.62, -0.78))        # red roof west arm / main-bar west end direction (NW -> SE)
BAR_NW = ENTRY_CORNER - ARM_DIR * ((BAR_NW_Y - ENTRY_CORNER.y) / 0.78)
BAR_NE = Vector((53.0, BAR_NW_Y))      # north end of the diagonal east face


def isect(p, d, q, e):
    """Intersection of lines p + d*s and q + e*r (2D)."""
    p, d, q, e = Vector(p), Vector(d), Vector(q), Vector(e)
    den = d.x * e.y - d.y * e.x
    s = ((q.x - p.x) * e.y - (q.y - p.y) * e.x) / den
    return p + d * s


# the brick block below is plain and rectangular (user): its straight west wall runs along the curve's chord, moved out
# to touch the curve's peak, so the curved top floor sits ON the block without overhanging it
_t = (W_S - W_W).normalized()
_west = W_W + Vector((_t.y, -_t.x)) * SW_SAG
W_WB, W_SB = isect(_west, _t, W_W, U_DIAG), isect(_west, _t, W_S, U_DIAG)   # brick block's W and S corners


# SE wing: right-angled wedge whose east side runs straight into the bar's diagonal east face, so the east end is one
# flush point with no notch (ResearchGate Sensors 2020 fig. 4b floor plan; LiDAR wing roof edges; user review)
SE_W = Vector((40.5, BAR_S_Y))
SE_TIP = Vector((54.0, -34.5))
E_TIP = isect(SE_TIP, Vector((25.5, 20.5)).normalized(), BAR_NE, Vector((0.731, -0.682)))
SE_WING = [tuple(SE_W), tuple(SE_TIP), tuple(E_TIP)]
E_SOUTH = isect(SE_TIP, E_TIP - SE_TIP, (0.0, BAR_S_Y), (1.0, 0.0))   # where the SE wing's east side crosses the bar's south line
BAR = [(-45.85, BAR_S_Y), tuple(E_SOUTH), tuple(E_TIP), tuple(BAR_NE), tuple(BAR_NW), tuple(ENTRY_CORNER), (-55.0, -4.0)]
SW_WING = [tuple(W_WB), tuple(W_SB), tuple(W_E), tuple(W_N)]
SW_VISIBLE = [tuple(p) for p in SW_CURVE] + [tuple(W_E), BAR[0], BAR[6], tuple(ENTRY_CORNER)]   # wing outside the bar
BAR_H = 17.0      # main-bar walls up to the red roof soffit (LiDAR: roof top 18.4-20 m, flat top 21.6 m)
WING_BRICK = 11.8
WING_TOP = 14.8   # wing roofs ~15.5 m in the LiDAR
FLOORS = [(1.2, 3.2), (5.2, 7.2), (9.2, 11.2), (13.0, 15.2)]
RED_Z_BOT = 17.8  # flat underside of the red roof band (it tilts up only at the NW point)
TOP_IN = 1.0      # wing glass top floors sit this far back; their white cap projects back out flush with the brick
CURTAIN_X = (-45.8, -22.0)  # south curtain wall with horizontal sun-shade blades (2016_02, user photo 2)


def ccw(poly):
    a = sum(poly[i][0] * poly[(i + 1) % len(poly)][1] - poly[(i + 1) % len(poly)][0] * poly[i][1] for i in range(len(poly)))
    return poly if a > 0 else poly[::-1]


def inset(poly, d):
    """Offset every edge of a simple polygon inward by d and re-intersect neighbouring edges."""
    P = [Vector(p) for p in ccw([tuple(p) for p in poly])]
    n = len(P)
    lines = []
    for k in range(n):
        A, B = P[k], P[(k + 1) % n]
        t = (B - A).normalized()
        lines.append((A + Vector((-t.y, t.x)) * d, t))
    return [isect(*lines[k - 1], *lines[k]) for k in range(n)]


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


def trim(mb, A, t, nn, ops, jambs=False):
    """Limestone sills and heads (and optionally side jambs) around punched windows (rear photo 1, 2016_01)."""
    for o in ops:
        if len(o) > 4:
            continue
        u0, u1, z0, z1 = o
        mb.box("lime", A + t * (u0 - 0.12) + nn * 0.08, t, -nn, u1 - u0 + 0.24, 0.12, z0 - 0.14, z0)
        mb.box("lime", A + t * (u0 - 0.15) + nn * 0.06, t, -nn, u1 - u0 + 0.3, 0.1, z1, z1 + 0.25)
        if jambs:
            for uu in (u0 - 0.2, u1):
                mb.box("lime", A + t * uu + nn * 0.06, t, -nn, 0.2, 0.1, z0, z1)


BAR_PITCH = 2.2   # punched-window spacing on the main bar's brick facades (rear photo 1)
NORTH_ROWS = [(0.8, 3.7)] + FLOORS[1:]   # taller ground-floor windows on the Stadium Ave facade (2016_01, drone photo)


def build_bar(mb):
    P = [Vector(p) for p in ccw(BAR)]
    n = len(P)
    for i in range(n):
        A, B = P[i], P[(i + 1) % n]
        _, t, nn, L = seg_frame(A, B)
        if L < 1.0:
            continue
        if nn.x > 0.5 and nn.y > 0.3:
            # diagonal east face from the flush east point (A) to the north facade: a glazed east entrance bay at the
            # point (doors, Sea Wolf canopy), then brick with limestone bands and a few punched windows
            g0, g1 = 0.8, 8.8
            ops = [(g0, g1, 4.0, BAR_H - 0.5, "win"), (g0, g0 + 0.9, 0.4, 3.8, "win"), (g0 + 0.9, g1 - 0.9, 0.0, 3.3, "door"),
                   (g1 - 0.9, g1, 0.4, 3.8, "win")]
            ops += [(o[0] + 11.0, o[1] + 11.0, o[2], o[3]) for o in punched(L - 12.0, FLOORS[1:3], pitch=6.0, pair=False, w=1.0)]
            wall(mb, A, B, 0.0, BAR_H, 0.4, ops, mullions=None)
            for z in [4.0, 8.2, 12.2]:
                mb.box("frame", A + t * g0 + nn * 0.02, t, -nn, g1 - g0, 0.1, z, z + 0.08)
            mb.box("seawolf", A + t * (g0 + 0.6), t, nn, g1 - g0 - 1.2, 2.0, 3.5, 3.9)
            band(mb, A + t * (g1 + 0.3), B, 0.0, 1.0, proj=0.10, ext=0.02)
            band(mb, A + t * (g1 + 0.3), B, 8.1, 8.35, proj=0.06, ext=0.02)
            band(mb, A + t * (g1 + 0.3), B, 12.1, 12.35, proj=0.06, ext=0.02)
            band(mb, A + t * (g1 + 0.3), B, 15.8, 16.2, proj=0.08, ext=0.02)
            continue
        if nn.y > 0.9:
            gw = NORTH_GLASS  # full-height curtain wall from the entrance corner eastward (Kawneer/AGM photos)
            ops = [o for o in punched(L, NORTH_ROWS) if o[1] < L - gw - 0.6]
            trim(mb, A, t, nn, [o for o in ops if o[2] > 1.0])
            trim(mb, A, t, nn, [o for o in ops if o[2] < 1.0], jambs=True)
            ops.append((L - gw, L - 0.05, 0.4, BAR_H - 0.4, "win"))
            wall(mb, A, B, 0.0, BAR_H, 0.4, ops, mullions=int(gw / 1.6))
            bar_bands(mb, A, A + t * (L - gw))
            for z in [4.2, 8.2, 12.2]:
                mb.box("frame", A + t * (L - gw) + nn * 0.02, t, -nn, gw, 0.12, z, z + 0.1)
            mb.box("lime", A + t * (L - gw - 0.8) + nn * 0.05, t, nn, 0.8, 1.2, 0.0, BAR_H - 0.5)  # pale pier at the glass end
        elif nn.y < -0.9 and abs(A.y - BAR_S_Y) < 0.1:
            # south face west->east pieces: curtain wall (separate, holds the rear entrance), blank brick return, punched
            # brick, the windowless loading-dock stretch, punched brick; above the SE wing only the top storey shows
            y = A.y
            for x0, x1, kind in ((CURTAIN_X[1], -15.0, "blank"), (-15.0, LOADING_DOCK_X[0] - 6.0, "punched"),
                                 (LOADING_DOCK_X[0] - 6.0, LOADING_DOCK_X[1] + 6.0, "dock"),
                                 (LOADING_DOCK_X[1] + 6.0, SE_W.x, "punched"), (SE_W.x, E_SOUTH.x, "above_wing")):
                S0, S1 = Vector((x0, y)), Vector((x1, y))
                LL = (S1 - S0).length
                if kind == "above_wing":
                    wall(mb, S0, S1, WING_BRICK, BAR_H, 0.4)
                    band(mb, S0, S1, 15.8, 16.2, proj=0.08, ext=0.02)
                    continue
                if kind == "dock":
                    # small loading dock: one overhead door and a man door, no windows on the ground floor
                    d0, d1 = LOADING_DOCK_X[0] - x0, LOADING_DOCK_X[1] - x0
                    ops = [o for o in punched(LL, FLOORS[1:], pitch=BAR_PITCH, pair=False, w=1.0)]
                    trim(mb, S0, Vector((1, 0)), Vector((0, -1)), ops)
                    # doors at truck-bed height above the base band, bumpers below, man door reached by steps
                    ops += [(d0, d1, 1.0, 5.0, "void"), (d1 + 1.2, d1 + 2.2, 1.0, 3.3, "door")]
                    wall(mb, S0, S1, 0.0, BAR_H, 0.4, ops)
                    mb.box("steel", S0 + Vector((d0, 0.3)), (1, 0), (0, 1), d1 - d0, 0.08, 1.0, 5.0)
                    for k in range(1, 8):   # overhead-door panel joints
                        mb.box("frame", S0 + Vector((d0, 0.26)), (1, 0), (0, 1), d1 - d0, 0.04, 1.0 + k * 0.5, 1.03 + k * 0.5)
                    mb.box("seawolf", S0 + Vector((d0 - 0.6, -1.4)), (1, 0), (0, 1), d1 - d0 + 3.8, 1.4, 5.2, 5.45)
                    for xb in (d0 + 0.3, d1 - 0.5):   # dock bumpers
                        mb.box("steel", S0 + Vector((xb, -0.3)), (1, 0), (0, 1), 0.2, 0.3, 0.2, 1.0)
                    for k in range(3):   # steps up to the man door
                        mb.box("lime", S0 + Vector((d1 + 0.9, -1.2 + 0.4 * k)), (1, 0), (0, 1), 1.6, 1.2 - 0.4 * k, 0.0, 0.35 * (k + 1))
                    band(mb, S0, S1, 0.0, 1.0, proj=0.10, ext=0.02)
                    for (a, b) in ((S0, S0 + Vector((d0 - 0.6, 0))), (S0 + Vector((d1 + 3.2, 0)), S1)):
                        band(mb, a, b, 4.08, 4.32, proj=0.05)
                    for z in (8.2, 12.2):
                        band(mb, S0, S1, z - 0.12, z + 0.12, proj=0.05, ext=0.02)
                    band(mb, S0, S1, 15.8, 16.2, proj=0.08, ext=0.02)
                    continue
                ops = [] if kind == "blank" else punched(LL, FLOORS, pitch=BAR_PITCH, pair=False, w=1.0)
                trim(mb, S0, Vector((1, 0)), Vector((0, -1)), ops)
                wall(mb, S0, S1, 0.0, BAR_H, 0.4, ops)
                bar_bands(mb, S0, S1)
    # bar walls standing above the west wing's roof along the bar's west edges (behind the wing's glass top floor)
    for (a, b) in ((BAR[0], BAR[6]), (BAR[6], BAR[5])):
        wall(mb, Vector(a), Vector(b), WING_BRICK, BAR_H, 0.4)

    # south curtain wall with Versoleil-type horizontal blades; the courtyard (rear) entrance is at its base, east end,
    # under a Sea Wolf canopy (user photo 2, user review)
    A, B = Vector((CURTAIN_X[1], BAR[0][1])), Vector((CURTAIN_X[0], BAR[0][1]))
    L = (A - B).length
    ops = [(0.05, L - 0.05, 4.4, BAR_H - 0.9, "win"), (0.05, 1.2, 0.6, 4.2, "win"), (1.2, 9.2, 0.0, 3.2, "door"),
           (1.2, 9.2, 3.4, 4.2, "win"), (9.2, L - 0.05, 0.6, 4.2, "win")]
    wall(mb, A, B, 0.0, BAR_H - 0.6, 0.3, ops, mat="seawolf", mullions=None)
    for z in [5.0 + 1.1 * k for k in range(10)]:
        mb.box("frame", (CURTAIN_X[0], BAR[0][1] - 0.95), (1, 0), (0, 1), CURTAIN_X[1] - CURTAIN_X[0], 0.9, z, z + 0.06)
    for x in [CURTAIN_X[0] + k * 3.0 for k in range(7)]:
        mb.box("frame", (x - 0.04, BAR[0][1] - 1.0), (1, 0), (0, 1), 0.08, 1.0, 4.8, BAR_H - 1.0)
    for z in (4.2, 8.2, 12.2):  # floor-edge transoms
        mb.box("frame", (CURTAIN_X[0], BAR[0][1] - 0.1), (1, 0), (0, 1), CURTAIN_X[1] - CURTAIN_X[0], 0.12, z, z + 0.12)
    mb.box("seawolf", (CURTAIN_X[1] - 9.6, BAR[0][1] - 2.2), (1, 0), (0, 1), 9.0, 2.2, 3.5, 3.9)
    # four pairs of glass doors in dark aluminium frames: stiles, head and bottom rails, push bars
    y0, x0 = BAR[0][1] - 0.9, CURTAIN_X[1] - 9.2
    for k in range(9):
        mb.box("steel", (x0 + k * 1.0 - 0.06, y0), (1, 0), (0, 1), 0.12, 0.16, 0.0, 2.75)
    mb.box("steel", (x0, y0), (1, 0), (0, 1), 8.0, 0.16, 0.0, 0.18)
    mb.box("steel", (x0, y0), (1, 0), (0, 1), 8.0, 0.16, 2.62, 2.8)
    mb.box("steel", (x0 - 0.3, y0), (1, 0), (0, 1), 8.6, 0.9, 3.1, 3.5)
    for k in range(8):
        mb.box("frame", (x0 + k * 1.0 + 0.12, y0 - 0.08), (1, 0), (0, 1), 0.76, 0.06, 1.0, 1.06)
    # door glass set in the same plane as the frames
    mb.box("glass", (x0, y0 + 0.06), (1, 0), (0, 1), 8.0, 0.04, 0.18, 2.62)
    mb.box("glass", (x0, y0 + 0.06), (1, 0), (0, 1), 8.0, 0.04, 2.8, 3.1)
    for xs in (x0 - 0.3, x0 + 8.0):   # door jambs closing the gap back to the curtain wall
        mb.box("steel", (xs, y0), (1, 0), (0, 1), 0.3, 0.9, 0.0, 3.3)
    mb.box("lime", (CURTAIN_X[1] - 10.0, BAR[0][1] - 6.0), (1, 0), (0, 1), 10.0, 6.0, -0.05, 0.1)   # entry pad
    # roof membrane, deck under the red roof and a pale fascia band between the wall tops and the red soffit
    flat_poly(mb, "roof", BAR, BAR_H - 0.3)
    flat_poly(mb, "roof", BAR, RED_Z_BOT - 0.05)
    P = [Vector(p) for p in ccw(BAR)]
    for k in range(len(P)):
        A, B = P[k], P[(k + 1) % len(P)]
        _, t, nn, L = seg_frame(A, B)
        mb.box("seawolf", A, t, -nn, L, 0.4, BAR_H, RED_Z_BOT - 0.05)


def glass_face(mb, A, B, H, doors=False):
    _, t, nn, L = seg_frame(A, B)
    ops = [(0.1, L - 0.1, 4.6 if doors else 0.4, H - 0.4, "win")]
    if doors:
        ops += [(0.4, L - 0.4, 0.0, 3.3, "door"), (0.1, 0.4, 0.4, 4.4, "win")]
        mb.box("seawolf", A + t * 0.2 + nn * 0.05, t, -nn, L - 0.4, 0.35, 3.3, 4.5)   # flat door head / canopy
        mb.box("seawolf", A + t * 0.2, t, nn, L - 0.4, 2.2, 3.9, 4.3)
    wall(mb, A, B, 0.0, H, 0.25, ops, mullions=max(1, int(L / 1.6)) - 1, inset=0.12)
    for z in [4.4 + 2.2 * q for q in range(6)]:
        mb.box("frame", A + nn * 0.02, t, -nn, L, 0.1, z, z + 0.07)


def build_atrium(mb):
    """Square INWARD entrance corner under the NW roof point: the glazed diagonal west end of the main bar meets the
    west wing's NW face, whose glazed bay next to the corner holds the doors (photos 2016_01/04, DD_22, Alamy,
    satellite; user review). Statue in front."""
    H = BAR_H
    glass_face(mb, Vector(BAR_NW), ENTRY_CORNER, H)                                  # bar west end (faces SW-W)
    glass_face(mb, ENTRY_CORNER, ENTRY_CORNER - U_DIAG * ENTRY_BAY, H, doors=True)    # wing NW face bay (faces NW)
    mb.box("frame", (ENTRY_CORNER.x - 0.2, ENTRY_CORNER.y - 0.2), (1, 0), (0, 1), 0.4, 0.4, 0.0, H)
    mb.box("lime", ENTRY_CORNER - U_DIAG * 10.0 + Vector((-6.0, 0.0)), U_DIAG, Vector((-U_DIAG.y, U_DIAG.x)), 16.0, 10.0, -0.05, 0.12)


def bezier(p0, c, p1, n=16):
    p0, c, p1 = Vector(p0), Vector(c), Vector(p1)
    return [(1 - u) ** 2 * p0 + 2 * (1 - u) * u * c + u ** 2 * p1 for u in [k / n for k in range(n + 1)]]


def wing_bands(mb, A, B):
    band(mb, A, B, 0.0, 0.9, proj=0.10, ext=0.02)
    band(mb, A, B, 4.0, 4.2, proj=0.05, ext=0.02)
    band(mb, A, B, WING_BRICK - 0.35, WING_BRICK + 0.15, proj=0.12, ext=0.02)


def sw_units(L):
    """Two-storey limestone-framed window units with small paired windows above (DD_24)."""
    ops = []
    nb = max(1, int(L / 6.5))
    bw = L / nb
    for b in range(nb):
        c = b * bw + bw / 2
        ops += [(c - 1.2, c + 1.2, 1.0, 7.6), (c - 1.0, c - 0.15, 8.6, 10.8), (c + 0.15, c + 1.0, 8.6, 10.8)]
    return ops


def limestone_surrounds(mb, A, t, nn, ops):
    for o in ops:
        if len(o) == 4 and o[3] - o[2] > 5:
            for (u0, u1) in ((o[0] - 0.25, o[0]), (o[1], o[1] + 0.25)):
                mb.box("lime", A + t * u0 + nn * 0.12, t, -nn, u1 - u0, 0.2, 0.9, 7.8)
            mb.box("lime", A + t * (o[0] - 0.25) + nn * 0.12, t, -nn, o[1] - o[0] + 0.5, 0.2, 7.6, 7.95)


def top_floor(mb, outline, over=TOP_IN):
    """Glass top storey on a wing roof; its white cap projects `over` past the glass (flush with the brick below)."""
    T = [Vector(p) for p in ccw([(p.x, p.y) for p in outline])]
    flat_poly(mb, "white", [(p.x, p.y) for p in T], WING_BRICK + 0.15)
    n = len(T)
    for k in range(n):
        A, B = T[k], T[(k + 1) % n]
        _, t, nn, L = seg_frame(A, B)
        if L < 0.3:
            continue
        wall(mb, A, B, WING_BRICK + 0.15, WING_TOP, 0.25, [(0.03, L - 0.03, WING_BRICK + 0.6, WING_TOP - 0.35, "win")],
             mullions=max(0, int(L / 1.5) - 1), inset=0.1)
        mb.box("white", A - t * 0.05 + nn * over, t, -nn, L + 0.1, over + 0.1, WING_TOP, WING_TOP + 0.7)
    cap = [(p.x, p.y) for p in inset(T, -over)] if n < 12 else [(p.x, p.y) for p in T]
    flat_poly(mb, "white", cap, WING_TOP + 0.7)


SW_ENTRY_U = 13.0   # side entrance on the west wing's SW face, measured from the W corner (DD_24, r1, user review)
SW_NAME_U = 4.9     # name letters on the SW face, left of the limestone pier (DD_24)


def fins(mb, A, t, nn, ops):
    """Thin horizontal sunshade fin over each small window (DD_24, rear photo 1)."""
    for o in ops:
        mb.box("frame", A + t * (o[0] - 0.1), t, nn, o[1] - o[0] + 0.2, 0.55, o[3] + 0.05, o[3] + 0.11)


def door_leaves(mb, A, t, nn, u0, u1, n, z1=2.6):
    """Dark aluminium stiles, rails and push bars of n glass door leaves standing in front of a door opening."""
    w = (u1 - u0) / n
    for k in range(n + 1):
        mb.box("steel", A + t * (u0 + k * w - 0.06) + nn * 0.02, t, -nn, 0.12, 0.16, 0.0, z1)
    for (za, zb) in ((0.0, 0.18), (z1 - 0.15, z1)):
        mb.box("steel", A + t * u0 + nn * 0.02, t, -nn, u1 - u0, 0.16, za, zb)
    for k in range(n):
        mb.box("frame", A + t * (u0 + k * w + 0.15) + nn * 0.08, t, -nn, w - 0.3, 0.06, 1.0, 1.06)


def build_sw_wing(mb):
    """West wing: a brick block turned along the red roof's west diagonal (satellite + floor plan), widened west with a
    convex curved west wall at 45 deg in plan (user review); a separate glass top floor sits ON the block (no overhang)
    and follows the same curve; NW face = brick with the name, then the glazed entrance bay at the inward corner; side
    entrance with steps, canopy and a limestone pier on the west face (DD_24, user review)."""
    # NW face (exposed part): brick from the W corner to the entrance bay
    A, B = ENTRY_CORNER - U_DIAG * ENTRY_BAY, W_WB
    _, t, nn, L = seg_frame(A, B)
    ops = [(L - 3.6, L - 1.6, 1.2, 7.6)]   # two-storey window by the W corner (DD_24, drone photo)
    limestone_surrounds(mb, A, t, nn, ops)
    wall(mb, A, B, 0.0, WING_BRICK, 0.4, ops)
    wing_bands(mb, A, B)
    # SE (courtyard) face: mostly blank brick with one row of small windows under sunshade fins (rear photos)
    A, B = W_SB, W_E
    _, t, nn, L = seg_frame(A, B)
    ops = punched(L - 4.0, [(5.6, 7.2)], pitch=3.4, pair=False, w=1.2)
    ops = [(o[0] + 2.0, o[1] + 2.0, o[2], o[3]) for o in ops]
    fins(mb, A, t, nn, ops)
    wall(mb, A, B, 0.0, WING_BRICK, 0.4, ops)
    wing_bands(mb, A, B)
    # SW (west) face: the brick block's straight west wall from the W to the S corner (only the glass top floor above
    # is curved), built in pieces broken between openings so each opening group sits on one piece; left of the pier blank brick with the name and two near-square upper
    # windows with fins, then the side entrance, then the limestone-framed window units (DD_24, user review)
    L = sw_arc()[-1][0]
    c = SW_ENTRY_U
    small = [(2.6, 3.9, 6.0, 7.9), (5.9, 7.2, 6.0, 7.9)]
    ops = [o for o in sw_units(L) if o[0] > c + 4.6] + small
    ops += [(c - 2.2, c + 2.2, 0.0, 3.2, "door"), (c - 1.9, c + 1.9, 4.6, 10.6, "win")]
    keep = [(c - 4.6, c + 4.6)] + [(o[0] - 0.4, o[1] + 0.4) for o in ops if abs((o[0] + o[1]) / 2 - c) > 4.6]
    cuts = []
    u = 3.0
    while u < L - 1.0:
        for a, b in keep:
            if a < u < b:
                u = b
        if u < L - 1.0:
            cuts.append(u)
        u += 3.0
    cuts = [0.0] + cuts + [L]
    for s0, s1 in zip(cuts, cuts[1:]):
        A, B = sw_point(s0)[0], sw_point(s1)[0]
        _, t, nn, _ = seg_frame(A, B)
        sops = [(o[0] - s0, o[1] - s0) + tuple(o[2:]) for o in ops if s0 <= o[0] and o[1] <= s1]
        limestone_surrounds(mb, A, t, nn, sops)
        fins(mb, A, t, nn, [(o[0] - s0, o[1] - s0) + o[2:] for o in small if s0 <= o[0] and o[1] <= s1])
        wall(mb, A, B, 0.0, WING_BRICK, 0.4, sops)
        wing_bands(mb, A, B)
        if s0 <= c <= s1:   # side entrance on this piece; A + t * c lands on it
            A = A - t * s0
            door_leaves(mb, A, t, nn, c - 2.2, c + 2.2, 4, z1=3.2)   # two pairs of doors
            mb.box("seawolf", A + t * (c - 2.6), t, nn, 5.2, 1.8, 3.4, 3.7)                        # flat canopy
            mb.box("lime", A + t * (c - 3.4) + nn * 0.35, t, -nn, 0.8, 0.75, 0.0, WING_TOP + 0.7)   # tall limestone pier
            mb.box("lime", A + t * (c + 2.4) + nn * 0.15, t, -nn, 0.4, 0.55, 0.0, WING_BRICK)
            for k in range(3):   # steps down to the walk, with a landing
                mb.box("lime", A + t * (c - 4.5) + nn * (3.6 - 0.8 * k), t, -nn, 9.0, 0.8 + 0.8 * k + (1.2 if k == 2 else 0),
                       -0.6 + 0.2 * k, -0.4 + 0.2 * k)
            for s in (-4.4, 4.4):  # hand rails
                mb.box("frame", A + t * (c + s) + nn * 3.4, t, -nn, 0.06, 3.0, 0.0, 0.95)
    # NE face: only the part south of the main bar is exposed
    A = W_E
    d = (W_N - W_E).normalized()
    k = (BAR_S_Y - A.y) / d.y
    B = A + d * k
    _, t, nn, L = seg_frame(A, B)
    wall(mb, A, B, 0.0, WING_BRICK, 0.4, punched(L, [(5.2, 7.2), (9.2, 11.2)], pitch=3.2, pair=False, w=1.0))
    wing_bands(mb, A, B)
    flat_poly(mb, "roof", SW_WING, WING_BRICK + 0.1)
    # separate glass top floor ON the block (only the part outside the main bar), set back TOP_IN from the brick all
    # round and following the same west curve, so neither the glass nor the white cap overhangs the brick
    top_floor(mb, inset(SW_VISIBLE, TOP_IN))


def sw_arc():
    """(arc length, point) samples along the brick block's straight west wall, W corner first."""
    pts = [W_WB, W_SB]
    out = [(0.0, pts[0])]
    for a, b in zip(pts, pts[1:]):
        out.append((out[-1][0] + (b - a).length, b))
    return out


def sw_point(u):
    """Point and unit tangent on the west wall curve at arc length u from the W corner."""
    s = sw_arc()
    for (u0, a), (u1, b) in zip(s, s[1:]):
        if u <= u1 or (u1, b) == s[-1]:
            f = 0.0 if u1 == u0 else max(0.0, min(1.0, (u - u0) / (u1 - u0)))
            return a.lerp(b, f), (b - a).normalized()


def build_wing(mb, poly, style="se"):
    """SE wing: brick right-angled wedge with evenly spaced single windows, glass top floor and white cap; its east side
    runs flush into the bar's diagonal east face (floor plan, LiDAR, ECN webcam, user Street View and review)."""
    P = [Vector(p) for p in ccw(poly)]
    n = len(P)
    for k in range(n):
        A, B = P[k], P[(k + 1) % n]
        _, t, nn, L = seg_frame(A, B)
        if L < 0.5 or nn.y > 0.9:   # north side is inside the main bar
            continue
        wall(mb, A, B, 0.0, WING_BRICK, 0.4, punched(L, [(1.3, 3.1), (5.1, 6.9), (8.4, 10.2)], pitch=3.4, pair=False, w=1.1))
        wing_bands(mb, A, B)
    flat_poly(mb, "roof", [(p.x, p.y) for p in P], WING_BRICK + 0.1)
    top_floor(mb, inset(P, TOP_IN))


RED_OVER = 2.0         # band edge beyond the north, south and east walls ("it just sticks out a bit")
# uniform width of the red band on every side, the two arms of the NW point included (user review). Measured: the
# red strips are 6-7 m wide in the 2023 ortho (north side and west arm alike); the LiDAR flat-top edge is ~8 m in from
# the north and south eaves (y~11 and y~-6.5)
RED_W = 6.5            # (user: a little narrower than 7 m)
RED_RISE = 4.0         # the NW point tilts up by this much at its tip, hinged at the east end of the north glass
STRUT_U = 0.58         # strut foot along the doors-bay glass top from the entrance corner (2016_01, fig. 4a, ortho)
STRUT_HW = 0.4         # strut half-width
DECK_Z = RED_Z_BOT - 0.05   # wall-top deck; the band's flat underside sits on it (user: flat bottom)
RED_THICK = 0.7        # band 30% thinner than the LiDAR-height version (user): eave 0.6 -> 0.42 m, flat top 21.6 -> 20.4 m
Z_TOP = DECK_Z + RED_THICK * (21.6 - DECK_Z)   # flat main-bar top, flush with the band's inner edge
RED_Z_EDGE = DECK_Z + RED_THICK * 0.6          # eave: the top rises from here straight up to the flat top


def inside(p, poly):
    """Even-odd point-in-polygon test (2D)."""
    c = False
    n = len(poly)
    for k in range(n):
        a, b = poly[k], poly[(k + 1) % n]
        if (a.y > p.y) != (b.y > p.y) and p.x < a.x + (p.y - a.y) * (b.x - a.x) / (b.y - a.y):
            c = not c
    return c


def red_geometry():
    """Plan of the red band: outer and inner loops (N, E, S, W sides), hole triangle, strut foot and the height
    functions. The band is a parallelogram frame of uniform width; its NW corner is the point: the tip is the outer
    corner, the two arms are the north and west sides, and the hole is the frame's inner corner cut off by the top of
    the glazed doors bay (2016_01, fig. 4a, photos 3 and 5, 2023 ortho)."""
    n_w = Vector((-ARM_DIR.y, ARM_DIR.x))           # inward normal of the west arm / bar west end
    d_e = (BAR_NE - E_TIP).normalized()
    n_e = Vector((d_e.y, -d_e.x))                   # outward normal of the diagonal east face
    X = Vector((1.0, 0.0))
    door_end = ENTRY_CORNER - U_DIAG * ENTRY_BAY    # SW end of the glazed doors bay, where the west wing's brick starts

    def lines(off):
        # the west arm's inner edge runs through the end of the doors bay, so the hole's base is the whole bay top and
        # the arm reaches out over the west wing
        return [(Vector((0.0, BAR_NW_Y + RED_OVER - off)), X), (BAR_NE + n_e * (RED_OVER - off), d_e),
                (Vector((0.0, BAR_S_Y - RED_OVER + off)), X), (door_end - n_w * (RED_W - off), ARM_DIR)]

    def corners(L):
        N, E, S, W = L
        return [isect(*N, *W), isect(*N, *E), isect(*E, *S), isect(*S, *W)]
    outer, inner = corners(lines(0.0)), corners(lines(RED_W))
    # hole: apex = the arms' inner corner; base = top of the entrance glass between the arms' inner edges, i.e. the
    # last bit of the glazed bar west end, the entrance corner and the whole doors bay
    p_n = isect(Vector((0.0, inner[0].y)), X, ENTRY_CORNER, ARM_DIR)
    hole = [inner[0].copy(), p_n, ENTRY_CORNER.copy(), door_end.copy()]
    foot = ENTRY_CORNER.lerp(door_end, STRUT_U)
    # hinge of the NW tilt: from the east end of the north glass to the band's SW corner
    h1 = Vector((BAR_NW.x + NORTH_GLASS, outer[0].y))
    hd = (outer[3] - h1).normalized()
    hn = Vector((-hd.y, hd.x))
    if hn.dot(outer[0] - h1) < 0:
        hn = -hn
    span = hn.dot(outer[0] - h1)

    def dz(p):
        return RED_RISE * max(0.0, min(1.0, hn.dot(Vector((p.x, p.y)) - h1) / span))

    def dist_outer(p):
        best = 1e9
        for k in range(4):
            a, b = outer[k], outer[(k + 1) % 4]
            ab = b - a
            t = max(0.0, min(1.0, (p - a).dot(ab) / ab.length_squared))
            best = min(best, (p - (a + ab * t)).length)
        return best

    def ztop(p):
        """Top of the band (hipped: rises evenly from the eave to the flat top, flush with it) and of the flat top."""
        return RED_Z_EDGE + (Z_TOP - RED_Z_EDGE) * min(1.0, dist_outer(Vector((p.x, p.y))) / RED_W) + dz(p)

    def zbot(p):
        """Flat underside: the wall-top deck, lifted only where the NW point tilts up."""
        return DECK_Z + dz(p)

    return outer, inner, hole, foot, ztop, zbot


def build_high_roof(mb):
    """The red Mayflower ACM roof is ONE continuous piece (user review): a band of uniform width with a flat underside
    on the wall tops, whose top rises evenly from the eave just past the walls to the flat main-bar top, flush with it.
    Its NW corner is the point: two arms of the same width meet at the tip and tilt gently up toward it; between their
    inner edges and the top of the doors-bay glass is the triangular hole, with a strut from the hole's apex down to
    the glass top (2016_01, DD_22, fig. 4a, photos 3 and 5, 2023 ortho)."""
    from mathutils.geometry import delaunay_2d_cdt
    outer, inner, hole, foot, ztop, zbot = red_geometry()

    def seg(a, b, step=1.5):
        n = max(1, int((b - a).length / step))
        return [a.lerp(b, i / n) for i in range(n)]

    # constrained triangulation of the whole roof plan: outer, inner and hole loops plus the hip lines as constraints,
    # with a 1.5 m grid of interior points so the tilt bends smoothly
    verts, edges = [], []

    def add_loop(loop):
        pts = [p for k in range(len(loop)) for p in seg(loop[k], loop[(k + 1) % len(loop)])]
        i0 = len(verts)
        verts.extend(pts)
        edges.extend((i0 + k, i0 + (k + 1) % len(pts)) for k in range(len(pts)))
    add_loop(outer)
    # inner loop through the hole's base corners, plus the base itself; the hole's sides lie on the inner loop
    add_loop([inner[0], hole[1], inner[1], inner[2], inner[3], hole[3]])
    for a, b in zip(hole[1:], hole[2:]):
        pts = seg(a, b, 0.75) + [b]
        i0 = len(verts)
        verts.extend(pts)
        edges.extend((i0 + j, i0 + j + 1) for j in range(len(pts) - 1))
    for a, b in [(outer[k], inner[k]) for k in range(4)]:   # hips
        pts = seg(a, b) + [b]
        i0 = len(verts)
        verts.extend(pts)
        edges.extend((i0 + j, i0 + j + 1) for j in range(len(pts) - 1))
    lo = Vector((min(p.x for p in outer), min(p.y for p in outer)))
    hi = Vector((max(p.x for p in outer), max(p.y for p in outer)))
    g = 1.5
    for i in range(int((hi.x - lo.x) / g) + 1):
        for j in range(int((hi.y - lo.y) / g) + 1):
            p = Vector((lo.x + i * g + 0.37, lo.y + j * g + 0.23))
            if inside(p, outer) and not inside(p, hole):
                verts.append(p)
    out_v, _, out_f, _, _, _ = delaunay_2d_cdt(verts, edges, [], 0, 1e-4)
    for f in out_f:
        P = [Vector((out_v[q].x, out_v[q].y)) for q in f]
        c = sum(P, Vector((0, 0))) / 3
        if not inside(c, outer) or inside(c, hole):
            continue
        band = not inside(c, inner)
        top = [Vector((p.x, p.y, ztop(p))) for p in P]
        if (top[1] - top[0]).cross(top[2] - top[0]).z < 0:
            top = top[::-1]
        mb.parts.setdefault("red" if band else "roof", []).append(top)
        if band or not inside(c, [Vector(q) for q in BAR]):   # flat underside; red soffit wherever it is outdoors
            mb.parts.setdefault("red", []).append([Vector((v.x, v.y, zbot(v))) for v in top][::-1])
    # edge faces around the eave and the hole
    for loop in (outer, hole):
        pts = [p for k in range(len(loop)) for p in seg(loop[k], loop[(k + 1) % len(loop)])]
        for k in range(len(pts)):
            a, b = pts[k], pts[(k + 1) % len(pts)]
            za, zb = ztop(a), ztop(b)
            mb.quad("red", [Vector((a.x, a.y, zbot(a))), Vector((b.x, b.y, zbot(b))), Vector((b.x, b.y, zb)),
                            Vector((a.x, a.y, za))])
    # strut: a straight red member from the hole's apex to the top of the doors-bay glass a little past the middle of
    # the bay, with the band's own flat underside and top so it reads as part of it (2016_01, DD_22, fig. 4a, photo 3)
    apex = hole[0]
    d = (foot - apex).normalized()
    pdir = Vector((-d.y, d.x))
    za, zf = ztop(apex), ztop(foot)
    bc = [apex - pdir * STRUT_HW, foot - pdir * STRUT_HW, foot + pdir * STRUT_HW, apex + pdir * STRUT_HW]
    up = [Vector((p.x, p.y, z)) for p, z in zip(bc, (za, zf, zf, za))]
    dn = [Vector((v.x, v.y, zbot(v))) for v in up]
    mb.quad("red", up)
    mb.quad("red", [dn[0], dn[3], dn[2], dn[1]])
    for k in (0, 2):
        mb.quad("red", [dn[k], dn[(k + 1) % 4], up[(k + 1) % 4], up[k]])
    mb.box("unit", (40.0, -2.0), (1, 0), (0, 1), 9.0, 9.0, Z_TOP, Z_TOP + 1.6)


def build_roof_infill(mb):
    """What closes the gap under the red roof. No glazing (user review). Under the NW point the soffit stands clear of
    the wall tops (photos 2, 4); where the plate comes down onto the entrance glass at the hole's base a strip of red
    cladding closes it down to the glass top (2016_01). Along the bar's west walls above the west wing, which no photo
    shows, the red soffit is carried down to the wall tops so it reads as the dark underside seen there in photo 5."""
    hole, zbot = red_geometry()[2], red_geometry()[5]
    for a, b in zip(hole[1:], hole[2:]):
        _, t, nn, L = seg_frame(a, b)
        mb.box("red", a, t, -nn, L, 0.25, BAR_H, DECK_Z)
    for a, b in ((Vector(BAR[5]), Vector(BAR[6])), (Vector(BAR[6]), Vector(BAR[0]))):
        n = max(1, int((b - a).length / 1.0))
        for i in range(n):
            p, q = a.lerp(b, i / n), a.lerp(b, (i + 1) / n)
            zp, zq = zbot(p), zbot(q)
            if max(zp, zq) > DECK_Z + 0.02:
                mb.quad("red", [Vector((p.x, p.y, DECK_Z)), Vector((q.x, q.y, DECK_Z)), Vector((q.x, q.y, zq)),
                                Vector((p.x, p.y, zp))])


def floors(mb):
    for poly in (BAR, SW_WING, SE_WING):
        flat_poly(mb, "floor", poly, 0.04)


DELETE_PREFIX = ("ARMS_East_", "ARMS_West_", "ARMS_R5_", "ARMS_R6_", "ARMS_R12_9_", "ARMS_Cantilever_Canopy_Deck",
                 "ARMS_Curtain_Glass_Bay", "ARMS_Curved_Mullion", "ARMS_Curved_Transom", "ARMS_Atrium_South_Wall",
                 "ARMS_Atrium_Skylight_Glazing", "ARMS_Roof_Steel_Truss", "ARMS_Canopy_", "ARMS_Light_Canopy",
                 "ARMS_Entrance_Portal_Frame", "ARMS_Revolving_Door", "ARMS_Door_Hardware", "ARMS_Building_Sign_Header",
                 "ARMS_Gold_Lettering_Band", "ARMS_Atrium_Terrazzo_Floor", "ARMS_Moon_Plaza", "Apollo11_Bootprint",
                 "ARMS_Plaza_", "ARMS_Bike_Rack", "ARMS_LED_Bollard", "ARMS_SP_")
STATUE = ("ARMS_Statue_",)
STATUE_OFFSET = Vector((-75.95, -2.3, 0.0))     # in front of the entrance corner under the roof point (photos)
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
    build_roof_infill(mb)
    mb.build("ARMS_SP_RoofInfill", M, root)
    floors(mb)
    mb.build("ARMS_SP_Floors", M, root)
    # building name letters on the SW wing north face beside the atrium (photo 2016_01)
    cu = bpy.data.curves.new("ARMS_SP_Name", "FONT")
    cu.body = "NEIL ARMSTRONG HALL OF ENGINEERING"
    cu.size = 0.42
    cu.extrude = 0.03
    cu.align_x = "CENTER"
    cu.materials.append(M["letter"])
    # NW face, between the entrance bay and the corner window; and the SW face left of the side entrance (DD_24)
    p_sw, sw_t = sw_point(SW_NAME_U)
    sw_n = Vector((sw_t.y, -sw_t.x))
    for name, p, rz in (("ARMS_SP_Name_Letters", ENTRY_CORNER - U_DIAG * (ENTRY_BAY + 5.2) + Vector((-0.652, 0.758)) * 0.1, 220.7),
                        ("ARMS_SP_Name_Letters_SW", p_sw + sw_n * 0.1, math.degrees(math.atan2(sw_t.y, sw_t.x)))):
        ob = bpy.data.objects.new(name, cu)
        ob.location = (p.x, p.y, 2.0)
        ob.rotation_euler = (math.radians(90), 0, math.radians(rz))
        bpy.data.collections[COLL].objects.link(ob)
        ob.parent = root
    for m in list(bpy.data.materials):
        if m.users == 0:
            bpy.data.materials.remove(m)
    bpy.ops.wm.save_mainfile()
    print("ARMS_SP_DONE", len(bpy.data.collections[COLL].objects))


main()
