"""Wilmeth Active Learning Center (WALC) second-pass rebuild: exterior shell AND interior (user direction 2026-10-29).

Run headless on the saved library, which it edits in place and saves:
    blender -b modular/buildings/walc.blend --python modular/buildings/build_walc_second_pass.py

Idempotent: deletes every object in the asset except AssetRoot_walc (the first-pass model was a rotated 80 x 48 m
massing plus a misaligned shell) and every WALC_SP_* object, then rebuilds from:
- footprint: Purdue campus GIS FID906 (research/second_pass/buildings/walc/sources/purdue_footprint_fid906.json)
- heights: 2017-2019 QL2 LiDAR NDHM (audit/walc/second_pass/sources/walc_ndhm_2018.*)
- interior: official furnished plans, all four floors (audit/walc/second_pass/sources/WALC_Classroom_FloorPlans.pdf,
  rendered at 130 dpi), registered to FID906; Purdue emergency-preparedness floor maps (floors 1-2)
- exterior and interior photographs indexed in research/second_pass/buildings/walc/ and audit/walc/second_pass/.
Local frame: metres, X east, Y north, origin = manifest origin. Dimensions are estimates, not survey values.
"""
import bpy, bmesh, math
from mathutils import Vector

COLL = "Asset_walc"
ROOT = "AssetRoot_walc"


# ---------------------------------------------------------------- materials
def principled(name, color, rough=0.6, metal=0.0, emit=None, spec=0.5, alpha=1.0):
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
        b.inputs["Emission Strength"].default_value = 4.0
    if alpha < 1.0:
        b.inputs["Alpha"].default_value = alpha
        m.blend_method = "BLEND" if hasattr(m, "blend_method") else None
    nt.links.new(b.outputs[0], out.inputs[0])
    m.diffuse_color = (*color, 1)
    return m, nt, b


def textured(name, c1, c2, mortar, w, h, ms, rough=0.9, bump=0.2, metal=0.0):
    """Brick-texture driven material on metre UVs (brick, roof tile, panels, slats)."""
    m, nt, b = principled(name, c1, rough=rough, metal=metal, spec=0.2)
    uv = nt.nodes.new("ShaderNodeTexCoord")
    br = nt.nodes.new("ShaderNodeTexBrick")
    br.offset = 0.5
    br.inputs["Scale"].default_value = 1.0
    br.inputs["Brick Width"].default_value = w
    br.inputs["Row Height"].default_value = h
    br.inputs["Mortar Size"].default_value = ms
    br.inputs["Color1"].default_value = (*c1, 1)
    br.inputs["Color2"].default_value = (*c2, 1)
    br.inputs["Mortar"].default_value = (*mortar, 1)
    nt.links.new(uv.outputs["UV"], br.inputs["Vector"])
    nt.links.new(br.outputs["Color"], b.inputs["Base Color"])
    if bump:
        bp = nt.nodes.new("ShaderNodeBump")
        bp.inputs["Strength"].default_value = bump
        nt.links.new(br.outputs["Fac"], bp.inputs["Height"])
        nt.links.new(bp.outputs["Normal"], b.inputs["Normal"])
    return m


def image_brick(name, file, tile, rough=0.88):
    """Brick material from a tileable texture made by audit/walc/second_pass/make_brick_textures.py (packed into the
    .blend); metre UVs scaled by the tile size; bump from brightness so the mortar joints read."""
    import os
    m, nt, b = principled(name, (0.25, 0.11, 0.09), rough=rough, spec=0.15)
    path = os.path.normpath(os.path.join(bpy.path.abspath("//"), "..", "..", "audit", "walc", "second_pass", "textures", file))
    img = bpy.data.images.load(path, check_existing=True)
    if not img.packed_file:
        img.pack()
    uv = nt.nodes.new("ShaderNodeTexCoord")
    sc = nt.nodes.new("ShaderNodeVectorMath")
    sc.operation = "SCALE"
    sc.inputs["Scale"].default_value = 1.0 / tile
    tex = nt.nodes.new("ShaderNodeTexImage")
    tex.image = img
    tex.interpolation = "Linear"
    nt.links.new(uv.outputs["UV"], sc.inputs[0])
    nt.links.new(sc.outputs[0], tex.inputs["Vector"])
    nt.links.new(tex.outputs["Color"], b.inputs["Base Color"])
    bp = nt.nodes.new("ShaderNodeBump")
    bp.inputs["Strength"].default_value = 0.35
    bp.inputs["Distance"].default_value = 0.004
    nt.links.new(tex.outputs["Color"], bp.inputs["Height"])
    nt.links.new(bp.outputs["Normal"], b.inputs["Normal"])
    return m


def mats():
    """Exterior colours from research V01/V02/V04/V05/V09 (red-brown variegated brick, warm cream stone, olive-grey
    frames, dark eaves, red tile roof, blue-grey glass); interior from the BSA/Turner photographs."""
    M = {}
    # running bond and the 45-degree three-brick basketweave of the spandrel panels, variegated red / plum bricks with
    # buff mortar (user close-ups 2026-10-29; textures from make_brick_textures.py)
    M["brick"] = image_brick("WALC_SP_Brick_Running", "walc_brick_running.png", 2.032)
    M["brickd"] = image_brick("WALC_SP_Brick_Basketweave", "walc_brick_basketweave.png", 1.7242)
    M["stone"] = principled("WALC_SP_Limestone", (0.60, 0.54, 0.45), rough=0.8, spec=0.2)[0]
    # roof: muted brown-red (aerial sRGB ~150,120,100 in flat light); the 2017 drone photo is over-saturated (user: too orange)
    # roof: deep red-brown / maroon tile (user aerial sRGB ~110-128, 83-97, 86-98; review r03: less orange)
    M["roof"] = textured("WALC_SP_Roof_Tile", (0.19, 0.075, 0.065), (0.155, 0.06, 0.055), (0.10, 0.045, 0.04), 0.30, 0.38, 0.012, rough=0.75, bump=0.4)
    M["wframe"] = principled("WALC_SP_Window_Frame_Taupe", (0.33, 0.30, 0.26), rough=0.45)[0]
    M["gutter"] = principled("WALC_SP_Gutter_Bronze", (0.09, 0.067, 0.05), rough=0.4, metal=0.7)[0]
    M["eave"] = principled("WALC_SP_Soffit_Warm_Dark", (0.045, 0.031, 0.022), rough=0.7, metal=0.1)[0]
    M["frame"] = principled("WALC_SP_Frame_Bronze_Taupe", (0.30, 0.22, 0.14), rough=0.45, metal=0.5)[0]
    M["glass"] = principled("WALC_SP_Glass", (0.035, 0.05, 0.055), rough=0.02, metal=0.75, spec=0.9)[0]
    M["canopy"] = principled("WALC_SP_Canopy_Verdigris", (0.26, 0.30, 0.20), rough=0.15, metal=0.3)[0]
    M["flat"] = principled("WALC_SP_Flat_Roof", (0.16, 0.16, 0.17), rough=0.9)[0]
    M["letter"] = principled("WALC_SP_Letter_Bronze", (0.22, 0.155, 0.09), rough=0.4, metal=0.8)[0]
    # interior
    M["slab"] = principled("WALC_SP_Concrete_Slab", (0.62, 0.62, 0.60), rough=0.8)[0]
    M["white"] = principled("WALC_SP_Wall_White", (0.80, 0.80, 0.78), rough=0.85)[0]
    M["carpet"] = textured("WALC_SP_Carpet", (0.30, 0.31, 0.32), (0.25, 0.26, 0.27), (0.20, 0.45, 0.42), 1.8, 0.35, 0.01, rough=1.0, bump=0.0)
    M["woodfloor"] = textured("WALC_SP_Wood_Floor", (0.42, 0.30, 0.20), (0.36, 0.25, 0.17), (0.20, 0.14, 0.10), 1.2, 0.2, 0.004, rough=0.6, bump=0.05)
    M["wood"] = principled("WALC_SP_Wood_Dark", (0.30, 0.17, 0.09), rough=0.5)[0]
    M["slats"] = textured("WALC_SP_Wood_Slats", (0.34, 0.20, 0.11), (0.34, 0.20, 0.11), (0.05, 0.04, 0.03), 4.0, 0.12, 0.03, rough=0.6, bump=0.3)
    M["steel"] = principled("WALC_SP_Steel_Dark", (0.08, 0.08, 0.08), rough=0.4, metal=0.8)[0]
    M["column"] = principled("WALC_SP_Concrete_Column", (0.55, 0.55, 0.53), rough=0.9)[0]
    M["railglass"] = principled("WALC_SP_Rail_Glass", (0.55, 0.62, 0.62), rough=0.05, metal=0.2)[0]
    M["table"] = principled("WALC_SP_Table_White", (0.85, 0.85, 0.83), rough=0.5)[0]
    M["tablewood"] = principled("WALC_SP_Table_Wood", (0.36, 0.21, 0.11), rough=0.4)[0]
    M["chair"] = principled("WALC_SP_Chair_Charcoal", (0.06, 0.06, 0.065), rough=0.7)[0]
    M["seat"] = principled("WALC_SP_Theatre_Seat", (0.10, 0.10, 0.11), rough=0.8)[0]
    M["red"] = principled("WALC_SP_Accent_Red", (0.55, 0.05, 0.04), rough=0.7)[0]
    M["teal"] = principled("WALC_SP_Accent_Teal", (0.10, 0.35, 0.38), rough=0.8)[0]
    M["books"] = textured("WALC_SP_Book_Spines", (0.35, 0.18, 0.10), (0.15, 0.20, 0.30), (0.5, 0.45, 0.35), 0.05, 0.32, 0.01, rough=0.8, bump=0.0)
    M["curtain"] = principled("WALC_SP_Stage_Curtain", (0.55, 0.38, 0.12), rough=0.9)[0]
    M["mural"] = textured("WALC_SP_Mural_Sepia", (0.32, 0.29, 0.25), (0.20, 0.18, 0.15), (0.45, 0.42, 0.37), 2.7, 1.9, 0.08, rough=0.9, bump=0.0)
    M["painting"] = principled("WALC_SP_Painting", (0.30, 0.25, 0.18), rough=0.8)[0]
    M["light"] = principled("WALC_SP_Light_Panel", (1.0, 1.0, 0.97), emit=(1.0, 0.98, 0.92))[0]
    M["lampshade"] = principled("WALC_SP_Lamp_Glow", (1.0, 0.9, 0.7), emit=(1.0, 0.85, 0.6))[0]
    M["screen"] = principled("WALC_SP_Screen", (0.9, 0.9, 0.9), rough=0.6)[0]
    M["fabric"] = principled("WALC_SP_Upholstery", (0.30, 0.33, 0.34), rough=0.9)[0]
    return M


# ---------------------------------------------------------------- mesh accumulation (one object per material)
class MB:
    def __init__(self):
        self.parts = {}

    def poly(self, mat, pts):
        self.parts.setdefault(mat, []).append([Vector(p) for p in pts])

    def box(self, mat, origin, ax, ay, sx, sy, z0, z1, skip=()):
        o = Vector((origin[0], origin[1]))
        a, b = Vector(ax) * sx, Vector(ay) * sy
        c = [o, o + a, o + a + b, o + b]
        lo = [Vector((p.x, p.y, z0)) for p in c]
        hi = [Vector((p.x, p.y, z1)) for p in c]
        faces = {"bottom": [lo[0], lo[3], lo[2], lo[1]], "top": [hi[0], hi[1], hi[2], hi[3]],
                 "f0": [lo[0], lo[1], hi[1], hi[0]], "f1": [lo[1], lo[2], hi[2], hi[1]],
                 "f2": [lo[2], lo[3], hi[3], hi[2]], "f3": [lo[3], lo[0], hi[0], hi[3]]}
        for k, f in faces.items():
            if k not in skip:
                self.poly(mat, f)

    def abox(self, mat, x0, x1, y0, y1, z0, z1, skip=()):
        """Axis-aligned box."""
        self.box(mat, (min(x0, x1), min(y0, y1)), (1, 0), (0, 1), abs(x1 - x0), abs(y1 - y0), z0, z1, skip)

    def cyl(self, mat, cx, cy, r, z0, z1, n=10, cap=True):
        pts = [Vector((cx + r * math.cos(2 * math.pi * k / n), cy + r * math.sin(2 * math.pi * k / n))) for k in range(n)]
        for k in range(n):
            a, b = pts[k], pts[(k + 1) % n]
            self.poly(mat, [(a.x, a.y, z0), (b.x, b.y, z0), (b.x, b.y, z1), (a.x, a.y, z1)])
        if cap:
            self.poly(mat, [(p.x, p.y, z1) for p in pts])
            self.poly(mat, [(p.x, p.y, z0) for p in pts[::-1]])

    def build(self, name, M, parent):
        objs = []
        for mat, faces in self.parts.items():
            bm = bmesh.new()
            uvl = bm.loops.layers.uv.new("UVMap")
            for q in faces:
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


# ---------------------------------------------------------------- geometry helpers
def seg_frame(A, B):
    A, B = Vector(A), Vector(B)
    d = B - A
    L = d.length
    t = d / L
    return A, t, Vector((t.y, -t.x)), L     # outward normal for a counter-clockwise polygon


def rect_fill(u0, u1, z0, z1, holes):
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


def wall(mb, A, B, z0, z1, thick, openings=(), mat="brick", inset=0.2, mull=1.3, frame="frame", inner="white", trans=None,
         units=False):
    """Straight wall A->B (outer face on the line, thickness inward) with framed openings (u0, u1, zb, zt[, kind]).
    The inner face gets the interior finish. trans: spacing of horizontal glazing bars (small panes)."""
    A, t, n, L = seg_frame(A, B)
    inw = -n
    for (u0, u1, za, zb) in rect_fill(0, L, z0, z1, [o[:4] for o in openings]):
        mb.box(mat, A + t * u0, t, inw, u1 - u0, thick, za, zb, skip=("f2",))
        p0, p1 = A + t * u0 + inw * thick, A + t * u1 + inw * thick
        mb.poly(inner, [(p1.x, p1.y, za), (p0.x, p0.y, za), (p0.x, p0.y, zb), (p1.x, p1.y, zb)])
    for o in openings:
        u0, u1, za, zb = o[:4]
        kind = o[4] if len(o) > 4 else "win"
        if kind == "void":
            continue
        mb.box("glass", A + t * u0 + inw * inset, t, inw, u1 - u0, 0.03, za, zb)
        p = A + inw * (inset - 0.06)
        fw = 0.08
        mb.box(frame, p + t * u0, t, inw, fw, 0.06, za, zb)
        mb.box(frame, p + t * (u1 - fw), t, inw, fw, 0.06, za, zb)
        mb.box(frame, p + t * u0, t, inw, u1 - u0, 0.06, za, za + fw)
        mb.box(frame, p + t * u0, t, inw, u1 - u0, 0.06, zb - fw, zb)
        w = u1 - u0
        if units and kind == "win":
            # WALC end-block units: two panes wide, short top pane, tall middle, short bottom pane; wide openings
            # are pairs/groups of units split by a heavier frame mullion (user close-ups, purdue_2018, bsa)
            nu = max(1, int(round(w / 1.25)))
            uw = w / nu
            for k in range(nu):
                a = u0 + k * uw
                if k:
                    mb.box(frame, p + t * (a - 0.06), t, inw, 0.12, 0.08, za, zb)
                mb.box(frame, p + t * (a + uw / 2 - 0.025), t, inw, 0.05, 0.06, za, zb)
            bars = [za + 0.38, zb - 0.42]
            h = zb - za
            if h > 4.0:
                nseg = int(round((h - 0.8) / 2.0))
                bars += [za + 0.38 + (h - 0.8) * j / nseg for j in range(1, nseg)]
            for zz in bars:
                mb.box(frame, p + t * u0, t, inw, w, 0.06, zz, zz + 0.05)
            continue
        nm = max(0, int(round(w / mull)) - 1)
        for k in range(1, nm + 1):
            mb.box(frame, p + t * (u0 + w * k / (nm + 1) - 0.025), t, inw, 0.05, 0.06, za, zb)
        if kind == "door":
            mb.box(frame, p + t * u0, t, inw, w, 0.06, za + 2.5, za + 2.58)
        elif trans:
            k = 1
            while za + k * trans < zb - 0.3:
                zz = za + k * trans
                mb.box(frame, p + t * u0, t, inw, w, 0.06, zz, zz + 0.05)
                k += 1
        elif zb - za > 2.6:
            for zz in ([za + (zb - za) * 0.72] if zb - za < 6 else [za + 2.6 + k * 2.4 for k in range(int((zb - za - 2.6) / 2.4))]):
                mb.box(frame, p + t * u0, t, inw, w, 0.06, zz, zz + 0.06)


def band(mb, A, B, z0, z1, proj=0.08, mat="stone", ext=0.05):
    A, t, n, L = seg_frame(A, B)
    mb.box(mat, A - t * ext + n * proj, t, -n, L + 2 * ext, proj + 0.05, z0, z1)


def inside(p, poly):
    c = False
    n = len(poly)
    for k in range(n):
        a, b = poly[k], poly[(k + 1) % n]
        if (a[1] > p[1]) != (b[1] > p[1]) and p[0] < a[0] + (p[1] - a[1]) * (b[0] - a[0]) / (b[1] - a[1]):
            c = not c
    return c


def slab(mb, mat, poly, holes, z, z_under=None, under_mat="white"):
    """Flat slab over a polygon minus rectangular holes (x0, x1, y0, y1) via constrained triangulation."""
    from mathutils.geometry import delaunay_2d_cdt
    verts, edges = [], []

    def loop(pts):
        i0 = len(verts)
        verts.extend(Vector(p) for p in pts)
        edges.extend((i0 + k, i0 + (k + 1) % len(pts)) for k in range(len(pts)))
    loop(poly)
    hp = [[(h[0], h[2]), (h[1], h[2]), (h[1], h[3]), (h[0], h[3])] for h in holes]
    for h in hp:
        loop(h)
    ov, _, of, _, _, _ = delaunay_2d_cdt(verts, edges, [], 0, 1e-4)
    for f in of:
        P = [ov[q] for q in f]
        c = ((P[0].x + P[1].x + P[2].x) / 3, (P[0].y + P[1].y + P[2].y) / 3)
        if not inside(c, poly) or any(inside(c, h) for h in hp):
            continue
        tri = [Vector((p.x, p.y, z)) for p in P]
        if (tri[1] - tri[0]).cross(tri[2] - tri[0]).z < 0:
            tri = tri[::-1]
        mb.poly(mat, tri)
        if z_under is not None:
            mb.poly(under_mat, [Vector((v.x, v.y, z_under)) for v in tri][::-1])


def ccw(poly):
    a = sum(poly[i][0] * poly[(i + 1) % len(poly)][1] - poly[(i + 1) % len(poly)][0] * poly[i][1] for i in range(len(poly)))
    return poly if a > 0 else poly[::-1]


# ---------------------------------------------------------------- levels and plan registration
LB, L1, L2, L3, TOP = -5.0, 0.0, 5.5, 10.5, 15.6     # floor levels and wall plate (photos, LiDAR, 3 storeys + basement)
FLOOR_T = 0.35


def X(py):
    """Plan pixel row (130 dpi render of the floor-plans PDF, floors 1-3) -> local x (east). Registered to FID906."""
    return -16.9 + (860.0 - py) / 11.6


def Y(px):
    return -44.3 + (1195.0 - px) / 11.6


def R(px0, px1, py0, py1, dx=0.0):
    """Plan rectangle (pixels) -> (xmin, xmax, ymin, ymax). dx shifts basement-page pixels onto the floor-1 frame."""
    return (X(py1), X(py0), Y(px1 - dx), Y(px0 - dx))


# ---------------------------------------------------------------- footprint (FID906, lightly regularised) and upper-floor outline
GROUND = ccw([(-10.8, -44.3), (-0.9, -44.2), (3.7, -39.7), (39.1, -39.7), (39.1, -26.6), (40.0, -26.6), (40.0, -12.7),
              (42.1, -12.7), (42.1, -7.8), (36.0, -7.8), (36.0, 10.7), (39.9, 10.7), (39.9, 25.1), (38.8, 25.1),
              (38.8, 43.9), (-16.9, 43.9), (-16.8, 23.6), (-14.7, 23.6), (-14.7, 16.6), (-10.5, 16.6),
              (-10.5, -18.4), (-16.7, -18.4), (-16.6, -39.7), (-15.4, -39.7)])
EAST_RECESS_X, RECESS_Y = 30.5, (-18.0, 17.6)   # floors 2-3 step back over lecture hall 1018, up to the NE stair tower (p3/p4)
UPPER = ccw([(-10.8, -44.3), (-0.9, -44.2), (3.7, -39.7), (39.1, -39.7), (39.1, -26.6), (40.0, -26.6), (40.0, -18.0),
             (30.5, -18.0), (30.5, 17.6), (39.9, 17.6), (39.9, 25.1), (38.8, 25.1), (38.8, 43.9), (-16.9, 43.9),
             (-16.8, 23.6), (-14.7, 23.6), (-14.7, 16.6), (-10.5, 16.6), (-10.5, -18.4), (-16.7, -18.4), (-16.6, -39.7),
             (-15.4, -39.7)])
PIERS_Y = [(-14.2, -13.0), (-9.1, -7.9), (-4.0, -2.9), (1.0, 2.2), (6.1, 7.3), (11.2, 12.4)]   # west stone piers (FID906)
WEST_X = -10.5
ARCADE_D, ARCADE_H = 2.8, 4.6   # west entrance arcade: shopfront set back behind the piers, soffit height (V04, BSA N134)

# voids
ATRIUM = R(540, 830, 500, 600)               # open to above/below with the grand stair (plans p2/p3)
READING_VOID = (-10.5, -2.2, -18.0, 16.6)    # reading room double height under the west range roof (p3/p4, BSA N103)
MONITOR = (5.0, 17.0, -15.0, 13.5)           # clerestory monitor over the atrium (LiDAR 19.1 m)


# ---------------------------------------------------------------- exterior
def facade_openings(kind, L, z0, z1):
    """Opening schedules per facade type (photos V01/V02/V05/V09 and review r01)."""
    ops = []
    if kind == "long":            # north faces: tall two-storey units over paired ground-floor windows (V02)
        nb = max(1, int(L / 6.8))
        bw = L / nb
        for b in range(nb):
            c = b * bw + bw / 2
            if z0 < 1.0:
                ops += [(c - 1.45, c - 0.15, 1.1, 4.5), (c + 0.15, c + 1.45, 1.1, 4.5)]
            else:
                ops += [(c - 1.1, c + 1.1, 6.2, 14.3)]
    elif kind == "south":         # south faces: separate single and paired windows per floor, tall strips near the
        nb = max(1, int((L - 9.0) / 4.4))   # corners (gallery_southeast_dean_2021, V01)
        bw = (L - 9.0) / nb
        for b in range(nb):
            c = 4.5 + b * bw + bw / 2
            w = 2.3 if b % 2 == 0 else 1.1
            for (za, zb) in ((1.2, 4.5), (6.6, 9.3), (11.4, 14.1)):
                if z0 <= za and zb <= z1:
                    ops.append((c - w / 2, c + w / 2, za, zb))
        for c in (2.2, L - 2.2):
            ops.append((c - 0.55, c + 0.55, max(z0, 0.0) + 1.2, min(z1, 14.3)))
    elif kind == "end":           # west faces of the end blocks: single, double, double, single (V05)
        widths = [1.1, 2.4, 2.4, 1.1]
        cs = [L * f for f in (0.14, 0.38, 0.62, 0.86)]
        for c, w in zip(cs, widths):
            if z0 < 1.0:
                ops += [(c - 1.2, c + 1.2, 1.1, 4.6)]
            else:
                ops += [(c - w / 2, c + w / 2, 6.6, 9.4), (c - w / 2, c + w / 2, 11.4, 14.2)]
    elif kind == "strip":         # stair-tower bays at the corners of the glazed range: one tall window strip (V02, V01)
        ops = [(L / 2 - 0.7, L / 2 + 0.7, max(z0, 0.0) + 1.0, min(z1, 14.3))]
    elif kind == "east":          # east faces: regular punched windows per floor (plans; no photo)
        nb = max(1, int(L / 3.6))
        bw = L / nb
        for b in range(nb):
            c = b * bw + bw / 2
            for (za, zb) in ((1.2, 4.4), (6.6, 9.4), (11.4, 14.2)):
                if z0 <= za and zb <= z1:
                    ops.append((c - 0.6, c + 0.6, za, zb))
    return [o for o in ops if o[0] > 0.4 and o[1] < L - 0.4]


def facade_kind(A, B):
    _, t, n, L = seg_frame(A, B)
    if n.x < -0.9:
        return "end" if L > 15 else ("strip" if L > 5 else "plain")
    if n.y > 0.9:
        return "long" if L > 12 else ("strip" if L > 5 else "plain")
    if n.y < -0.9:
        return "south" if L > 12 else ("strip" if L > 5 else "plain")
    if n.x > 0.9:
        return "east" if L > 6 else "plain"
    return "plain"


def trims(mb, A, t, n, ops):
    """Stone sill and lintel at every window; a stone panel two-thirds up the tall ground-floor windows (V02, V09)."""
    for o in ops:
        if len(o) > 4:
            continue
        u0, u1, za, zb = o
        mb.box("stone", A + t * (u0 - 0.12) + n * 0.1, t, -n, u1 - u0 + 0.24, 0.16, za - 0.16, za)
        mb.box("stone", A + t * (u0 - 0.15) + n * 0.1, t, -n, u1 - u0 + 0.3, 0.16, zb, zb + 0.32)
        if za < 1.5 and zb - za > 3.0:
            zp = za + (zb - za) * 0.66
            mb.box("stone", A + t * u0 + n * 0.02, t, -n, u1 - u0, 0.2, zp, zp + 0.35)


def basketweave_panels(mb, A, t, n, L, ops, frieze_top=None):
    """Basketweave spandrel panels in the window columns of floors 2-3: the width of the window, filling the brick
    between the floor-2 belt course, the windows (with their stone sills/heads) and the stone course above the floor-3
    heads; on the end blocks also the brick frieze above that course. Piers and corners stay running bond
    (user close-ups 2026-10-29)."""
    cols = {}
    for o in ops:
        if len(o) > 4 or o[2] < L2:
            continue
        cols.setdefault((round(o[0], 2), round(o[1], 2)), []).append(o)
    for (u0, u1), wins in cols.items():
        a, b = max(0.05, u0 - 0.04), min(L - 0.05, u1 + 0.04)
        P0, P1 = A + t * a + n * 0.006, A + t * b + n * 0.006
        voids = [(o[0] - a - 0.2, o[1] - a + 0.2, o[2] - 0.17, o[3] + 0.33, "void") for o in wins]
        wall(mb, P0, P1, 5.56, 14.54, 0.006, voids, mat="brickd", inner="brickd")
        if frieze_top:
            wall(mb, P0, P1, 14.81, frieze_top, 0.006, (), mat="brickd", inner="brickd")


def east_wing_face(mb, A, B, L, zt):
    """One-storey east wing (lecture hall 1018) faces, from the user's photos of the back of the building: tall stone
    base, a basketweave field between plain brick corner piers, a stone band, an upper row of window triplets in
    running bond, stone coping. The entrance bay on the east projection gets two pairs of doors under a glass canopy
    on steel outriggers."""
    _, t, n, _ = seg_frame(A, B)
    entrance = n.x > 0.9 and abs(A.x - 42.1) < 0.2
    ops = []
    if entrance:
        c = L / 2
        ops = [(c - 2.0, c - 0.15, 0.0, 2.45, "door"), (c + 0.15, c + 2.0, 0.0, 2.45, "door"),
               (c - 2.0, c - 0.15, 2.6, 3.3, "win"), (c + 0.15, c + 2.0, 2.6, 3.3, "win")]
    else:
        ng = max(0, int((L - 2.0) / 5.0))
        for g in range(ng):
            cg = 1.0 + (L - 2.0) * (g + 0.5) / ng
            for k in (-1, 0, 1):
                ops.append((cg + k * 1.12 - 0.5, cg + k * 1.12 + 0.5, 4.75, 6.05))
        if L > 9:   # lower band: two window triplets side by side (user review of r4)
            for cg in (L / 2 - 1.74, L / 2 + 1.74):
                for k in (-1, 0, 1):
                    ops.append((cg + k * 1.12 - 0.5, cg + k * 1.12 + 0.5, 2.1, 3.6))
    ops = [o for o in ops if o[0] > 0.9 and o[1] < L - 0.9]
    wall(mb, A, B, LB, zt, 0.45, ops, mat="brick", frame="wframe", units=True)
    trims(mb, A, t, n, [o for o in ops if len(o) == 4])
    band(mb, A, B, -0.05, 1.6, proj=0.12)                 # tall stone base
    band(mb, A, B, 4.2, 4.45, proj=0.08)
    band(mb, A, B, zt - 0.55, zt, proj=0.14)              # coping
    if L > 2.4:                                           # basketweave field between the corner piers
        P0, P1 = A + t * 0.9 + n * 0.006, A + t * (L - 0.9) + n * 0.006
        voids = [(o[0] - 0.9 - 0.2, o[1] - 0.9 + 0.2, o[2] - 0.17, o[3] + 0.33, "void") for o in ops if o[2] < 4.2]
        wall(mb, P0, P1, 1.61, 4.19, 0.006, voids, mat="brickd", inner="brickd")
        wall(mb, P0, P1, 6.3, zt - 0.56, 0.006, (), mat="brickd", inner="brickd")
    if entrance:
        c = L / 2
        o = A + t * (c - 2.6)
        mb.box("canopy", o + n * 0.05, t, n, 5.2, 2.6, 3.55, 3.6)
        for k in range(4):
            uu = c - 2.4 + k * 1.6
            q = A + t * uu
            strut(mb, Vector((q.x, q.y, 3.5)), Vector((q.x + n.x * 2.6, q.y + n.y * 2.6, 3.5)), 0.18, 0.1, mat="gutter")
            strut(mb, Vector((q.x, q.y, 4.4)), Vector((q.x + n.x * 2.0, q.y + n.y * 2.0, 3.58)), 0.03, 0.03, mat="gutter")
        mb.box("stone", A + t * (c - 2.5) + n * 0.12, t, -n, 5.0, 0.15, 3.3, 3.5)


def exterior_walls(mb):
    for poly, z0, z1 in ((GROUND, LB, L2), (UPPER, L2, TOP)):
        P = [Vector(p) for p in poly]
        for k in range(len(P)):
            A, B = P[k], P[(k + 1) % len(P)]
            _, t, n, L = seg_frame(A, B)
            if L < 0.3:
                continue
            if n.x < -0.9 and abs(A.x - WEST_X) < 0.2:
                continue          # glazed west range: built separately
            low_hall = z0 < 0 and min(A.x, B.x) > EAST_RECESS_X - 0.1 and RECESS_Y[0] < A.y < RECESS_Y[1] \
                and RECESS_Y[0] < B.y < RECESS_Y[1] + 0.1
            if low_hall:
                east_wing_face(mb, A, B, L, 7.2)
                continue
            if z0 < 0 and min(A.x, B.x) > EAST_RECESS_X - 0.1:
                # ground wall that runs on past the recess: carry the part beside the one-storey wing up to its coping
                ya, yb = max(min(A.y, B.y), RECESS_Y[0]), min(max(A.y, B.y), RECESS_Y[1])
                if yb - ya > 0.2:
                    P0, P1 = (Vector((A.x, ya)), Vector((A.x, yb))) if B.y > A.y else (Vector((A.x, yb)), Vector((A.x, ya)))
                    wall(mb, P0, P1, L2, 7.2, 0.45, (), mat="brick")
                    band(mb, P0, P1, 6.65, 7.2, proj=0.14)
            kind = facade_kind(A, B)
            ops = facade_openings(kind, L, max(z0, 0.0), z1)
            wall(mb, A, B, z0, z1, 0.45, ops, mat="brick", frame="wframe", units=True)
            mid = (A + B) / 2
            on_block = mid.y > 21.0 or mid.y < -16.0
            if z0 >= L2:
                basketweave_panels(mb, A, t, n, L, ops, frieze_top=16.75 if on_block else None)
            trims(mb, A, t, n, ops)
            if z0 < 0:
                band(mb, A, B, -0.05, 1.0, proj=0.1)             # stone base
                band(mb, A, B, 5.0, 5.55, proj=0.12)             # belt course at floor 2
            else:
                band(mb, A, B, 14.55, 14.8, proj=0.08)           # stone course above the floor-3 window heads
            # shallow brick piers at the corners and between window groups (V02, V09)
            if kind in ("long", "south", "end"):
                us = [0.0, L - 0.9]
                if kind == "long":
                    nb = max(1, int(L / 6.8))
                    us += [L * b / nb - 0.45 for b in range(1, nb)]
                for u in us:
                    mb.box("brick", A + t * u + n * 0.16, t, -n, 0.9, 0.17, z0 if z0 >= 0 else 1.0, z1)
    # lecture hall 1018 low roof at 7 m (LiDAR 7.0-7.7 m)
    low = ccw([(EAST_RECESS_X, -18.0), (40.0, -18.0), (40.0, -12.7), (42.1, -12.7), (42.1, -7.8), (36.0, -7.8), (36.0, 10.7),
               (39.9, 10.7), (39.9, 17.6), (EAST_RECESS_X, 17.6)])
    slab(mb, "flat", low, [], 7.0, z_under=6.6)


def west_range(mb):
    """Glazed west range between the end blocks: six free-standing limestone piers and seven bays.
    Ground floor: an arcade - the shopfront glazing, double doors and brick piers stand ~2.8 m back behind the piers,
    under a stone soffit; suspended glass canopies at the pier line. Floors 2-3: a deep projecting olive-grey framed
    window per bay with small panes in its upper section; stone name band crossing the piers with the full name in
    dark bronze; dark steel 'W' struts under the deep eave, which is closed by a stone frieze above the windows
    (V01/V04/V06/V07, BSA N134, review r01)."""
    ys = [-18.4] + [v for p in PIERS_Y for v in p] + [16.6]
    bays = [(ys[i], ys[i + 1]) for i in range(0, len(ys), 2)]
    x = WEST_X
    xs = x + ARCADE_D            # shopfront line
    zr = 15.9 + (19.6 - 15.9) * (x - (-16.2)) / (-6.3 - (-16.2)) - 0.35   # roof underside at the wall line
    for (y0, y1) in bays:
        y0 = max(y0, -17.4)            # end bays stop at the end piers against the blocks (review r03)
        y1 = min(y1, 15.6)
        A, B = Vector((x, y1)), Vector((x, y0))         # outward normal -x
        L = y1 - y0
        # upper storeys at the pier line: deep framed window, small panes above the transom
        wall(mb, A, B, ARCADE_H, zr, 0.3, [(0.35, L - 0.35, 6.0, 14.9, "win")], mat="stone", mull=0.8)
        for zz in [12.4 + 0.5 * k for k in range(5)]:
            mb.box("frame", (x - 0.12, y0 + 0.35), (0, 1), (1, 0), L - 0.7, 0.04, zz, zz + 0.04)
        for k in range(1, int((L - 0.7) / 0.4)):
            yy = y0 + 0.35 + k * 0.4
            mb.abox("frame", x - 0.12, x - 0.08, yy - 0.015, yy + 0.015, 12.4, 14.9)
        mb.abox("frame", x - 0.95, x - 0.05, y1 - 0.38, y1 - 0.2, 5.7, 15.1)
        mb.abox("frame", x - 0.95, x - 0.05, y0 + 0.2, y0 + 0.38, 5.7, 15.1)
        mb.abox("frame", x - 0.95, x - 0.05, y0 + 0.2, y1 - 0.2, 15.0, 15.25)
        mb.abox("frame", x - 0.95, x - 0.05, y0 + 0.2, y1 - 0.2, 5.6, 5.85)
        mb.abox("frame", x - 0.85, x - 0.15, y0 + 0.38, y1 - 0.38, 10.15, 10.55)    # spandrel at floor 3
        # ground floor: shopfront set back in the arcade, double doors in the middle bays, brick piers between bays
        S0, S1 = Vector((xs, y1 - 0.45)), Vector((xs, y0 + 0.45))
        Ls = (S1 - S0).length
        mid = abs((y0 + y1) / 2) < 9.0
        ops = [(0.1, Ls - 0.1, 0.0, ARCADE_H - 0.3, "win")] if not mid else \
              [(0.1, Ls / 2 - 0.95, 0.0, ARCADE_H - 0.3, "win"), (Ls / 2 - 0.9, Ls / 2 + 0.9, 0.0, 2.5, "door"),
               (Ls / 2 - 0.9, Ls / 2 + 0.9, 2.65, ARCADE_H - 0.3, "win"), (Ls / 2 + 0.95, Ls - 0.1, 0.0, ARCADE_H - 0.3, "win")]
        wall(mb, S0, S1, L1, ARCADE_H, 0.25, ops, mat="brick", mull=1.0, frame="frame")
        mb.abox("brick", xs - 0.1, xs + 0.4, y1 - 0.45, y1 + 0.1, L1, ARCADE_H)
        mb.abox("brick", xs - 0.1, xs + 0.4, y0 - 0.1, y0 + 0.45, L1, ARCADE_H)
        if mid:   # door leaves
            for yy in (S0.y - (Ls / 2 - 0.9), S0.y - Ls / 2, S0.y - (Ls / 2 + 0.9)):
                mb.abox("frame", xs - 0.12, xs - 0.04, yy - 0.05, yy + 0.05, 0.0, 2.5)
        mb.abox("stone", x - 0.05, xs, y0, y1, ARCADE_H - 0.05, ARCADE_H)              # arcade soffit
        mb.abox("stone", x, x + 0.3, y0, y1, LB, L1)                                   # below grade
        # suspended glass canopy with tie rods at the pier line
        mb.abox("canopy", x - 2.2, x - 0.05, y0 + 0.2, y1 - 0.2, 4.15, 4.2)
        mb.abox("frame", x - 2.25, x - 0.05, y0 + 0.2, y1 - 0.2, 4.08, 4.15)
        for yy in (y0 + 0.5, y1 - 0.5):
            strut(mb, Vector((x - 2.1, yy, 4.2)), Vector((x - 0.1, yy, 5.3)), 0.04, 0.04, mat="frame")
    # free-standing limestone piers with base blocks, and the end piers against the blocks
    for (p0, p1) in PIERS_Y + [(16.6 - 1.0, 16.6), (-18.4, -17.4)]:
        mb.abox("stone", x - 1.3, x + 0.1, p0, p1, -0.05, TOP + 0.2)
        mb.abox("stone", x - 0.05, x + 0.3, p0 - 0.05, p1 + 0.05, TOP, zr + 0.05)   # frieze closes the eave above the pier
        mb.abox("stone", x - 1.5, x + 0.2, p0 - 0.15, p1 + 0.15, -0.05, 0.9)
        # slim dark-bronze paired struts on each pier, projecting from the pier face up and out to the eave edge,
        # splayed slightly apart (bsa_exterior, V04; review r03 - not flat 'W' letters in the facade plane)
        c = (p0 + p1) / 2
        for s_ in (-1, 1):
            strut(mb, Vector((x - 1.3, c + s_ * 0.22, TOP - 1.4)), Vector((-15.85, c + s_ * 0.55, 15.95)), 0.12, 0.1, mat="gutter")
        strut(mb, Vector((x - 1.3, c, TOP + 0.15)), Vector((-15.85, c, 16.0)), 0.1, 0.1, mat="gutter")
    # stone name band crossing the piers at floor-2 level (V04)
    mb.abox("stone", x - 1.55, x + 0.1, -16.0, 14.0, 4.6, 5.55)
    mb.abox("stone", x - 0.35, x + 0.1, -18.4, 16.6, 4.6, 5.6)


def name_letters(M, root):
    cu = bpy.data.curves.new("WALC_SP_Name", "FONT")
    cu.body = "THOMAS S. AND HARVEY D. WILMETH ACTIVE LEARNING CENTER"
    cu.size = 0.5
    cu.extrude = 0.03
    cu.align_x = "CENTER"
    cu.materials.append(M["letter"])
    ob = bpy.data.objects.new("WALC_SP_Name_Letters", cu)
    ob.location = (WEST_X - 1.6, -1.0, 4.9)
    ob.rotation_euler = (math.radians(90), 0, math.radians(270))
    bpy.data.collections[COLL].objects.link(ob)
    ob.parent = root


def hip_roof(mb, x0, x1, y0, y1, z_eave, z_ridge, mat="roof", t=0.18):
    """Hip roof over a rectangle (eave line), ridge along the longer axis, with a thin dark soffit and fascia."""
    w, h = x1 - x0, y1 - y0
    half = min(w, h) / 2
    if w >= h:
        r0, r1 = Vector((x0 + half, y0 + h / 2, z_ridge)), Vector((x1 - half, y0 + h / 2, z_ridge))
    else:
        r0, r1 = Vector((x0 + w / 2, y0 + half, z_ridge)), Vector((x0 + w / 2, y1 - half, z_ridge))
    c = [Vector((x0, y0, z_eave)), Vector((x1, y0, z_eave)), Vector((x1, y1, z_eave)), Vector((x0, y1, z_eave))]
    if w >= h:
        faces = [[c[0], c[1], r1, r0], [c[1], c[2], r1], [c[2], c[3], r0, r1], [c[3], c[0], r0]]
    else:
        faces = [[c[0], c[1], r0], [c[1], c[2], r1, r0], [c[2], c[3], r1], [c[3], c[0], r0, r1]]
    for f in faces:
        mb.poly(mat, f)
    mb.poly("eave", [Vector((p.x, p.y, z_eave - t)) for p in c[::-1]])
    for k in range(4):
        a, b = c[k], c[(k + 1) % 4]
        mb.poly("gutter", [a - Vector((0, 0, t)), b - Vector((0, 0, t)), b, a])
        # gutter: a thin bronze trough along the edge (V02)
        A2, B2 = Vector((a.x, a.y)), Vector((b.x, b.y))
        _, tt, nn, LL = seg_frame(A2, B2) if (B2 - A2).length > 0.1 else (None, None, None, 0)
        if LL:
            mb.box("gutter", A2 - tt * 0.05 + nn * 0.14, tt, -nn, LL + 0.1, 0.16, z_eave - 0.12, z_eave + 0.04)


def gable_roof(mb, xw, xe, xr, y0, y1, zw, ze, zr, mat="roof", t=0.35):
    """N-S gable over the west range; its ends run into the block roofs, forming the valleys."""
    W0, W1 = Vector((xw, y0, zw)), Vector((xw, y1, zw))
    E0, E1 = Vector((xe, y0, ze)), Vector((xe, y1, ze))
    R0, R1 = Vector((xr, y0, zr)), Vector((xr, y1, zr))
    mb.poly(mat, [W0, R0, R1, W1][::-1])
    mb.poly(mat, [R0, E0, E1, R1][::-1])
    d = Vector((0, 0, 0.04))     # dark underside so no tile shows from below at the block junctions (review r03)
    mb.poly("eave", [W0 - d, R0 - d, R1 - d, W1 - d])
    mb.poly("eave", [R0 - d, E0 - d, E1 - d, R1 - d])
    # dark soffit under the deep west eave, parallel to the roof, back to the glazed wall; fascia at the edge
    zx = zw + (zr - zw) * (WEST_X - xw) / (xr - xw) - t
    mb.poly("eave", [Vector((xw, y0, zw - t)), Vector((WEST_X, y0, zx)), Vector((WEST_X, y1, zx)), Vector((xw, y1, zw - t))])
    mb.poly("eave", [W0 - Vector((0, 0, t)), W1 - Vector((0, 0, t)), W1, W0])


def eave_brackets(mb, wall_rect, eave_rect, z_eave, step=1.8):
    """Regularly spaced dark brackets under the end-block eaves, from the wall face to near the eave edge (V02)."""
    wx0, wx1, wy0, wy1 = wall_rect
    ex0, ex1, ey0, ey1 = eave_rect
    zb, zt = z_eave - 0.75, z_eave - 0.18
    for (fixed, a0, a1, out_from, out_to, axis) in ((wy1, wx0, wx1, wy1, ey1 - 0.15, "y"), (wy0, wx0, wx1, wy0, ey0 + 0.15, "y"),
                                                    (wx0, wy0, wy1, wx0, ex0 + 0.15, "x"), (wx1, wy0, wy1, wx1, ex1 - 0.15, "x")):
        n = int((a1 - a0) / step)
        for k in range(1, n):
            a = a0 + (a1 - a0) * k / n
            if axis == "y":
                mb.abox("eave", a - 0.09, a + 0.09, min(out_from, out_to), max(out_from, out_to), zb + 0.35, zt)
                mb.abox("eave", a - 0.09, a + 0.09, min(out_from, out_from + (out_to - out_from) * 0.35),
                        max(out_from, out_from + (out_to - out_from) * 0.35), zb, zt)
            else:
                mb.abox("eave", min(out_from, out_to), max(out_from, out_to), a - 0.09, a + 0.09, zb + 0.35, zt)
                mb.abox("eave", min(out_from, out_from + (out_to - out_from) * 0.35),
                        max(out_from, out_from + (out_to - out_from) * 0.35), a - 0.09, a + 0.09, zb, zt)


def downpipe(mb, wx, wy, nx, ny, z_eave, reach):
    """Downpipe fixed to the wall (at a brick pier) with a gooseneck out to the gutter (V02)."""
    px, py = wx + nx * 0.32, wy + ny * 0.32
    mb.cyl("gutter", px, py, 0.075, 0.25, z_eave - 0.6, n=8, cap=False)
    strut(mb, Vector((px, py, z_eave - 0.6)), Vector((wx + nx * (reach - 0.1), wy + ny * (reach - 0.1), z_eave - 0.1)), 0.15, 0.15,
          mat="gutter")


def roofs(mb):
    # end blocks: hipped tile roofs with ~1.8 m eaves (LiDAR eaves 17.1-17.6 m, ridges 21.8 / 22.4 m)
    NB_W, NB_E = (-16.9, 38.8, 23.6, 43.9), (-18.7, 40.6, 21.8, 45.7)
    SB_W, SB_E = (-16.6, 39.1, -39.7, -18.4), (-18.4, 41.8, -41.5, -16.6)
    hip_roof(mb, NB_E[0], NB_E[1], NB_E[2], NB_E[3], 17.3, 21.8)
    hip_roof(mb, SB_E[0], SB_E[1], SB_E[2], SB_E[3], 17.4, 22.4)
    eave_brackets(mb, NB_W, NB_E, 17.3)
    eave_brackets(mb, SB_W, SB_E, 17.4)
    # stone/brick fill between the wall plate and the eave soffit all round the blocks
    for (wr, ze) in ((NB_W, 17.3), (SB_W, 17.4)):
        x0, x1, y0, y1 = wr
        for (A, B) in (((x0, y0), (x1, y0)), ((x1, y0), (x1, y1)), ((x1, y1), (x0, y1)), ((x0, y1), (x0, y0))):
            wall(mb, Vector(A), Vector(B), TOP, ze - 0.15, 0.4, mat="brick", inner="brick")
            band(mb, Vector(A), Vector(B), ze - 0.5, ze - 0.15, proj=0.12)      # slim stone cornice under the soffit
    # downpipes on the brick piers of the north and south faces and at the corners (V02, V09)
    for xx in [-16.0] + [-16.9 + 55.7 * b / 8 for b in (2, 4, 6)] + [37.9]:
        downpipe(mb, xx, 43.9, 0, 1, 17.3, 1.8)
        downpipe(mb, xx, -39.7, 0, -1, 17.4, 1.8)
    # west range gable (LiDAR: west eave 15.9 m at x -16, ridge 19.6 m at x -6.3, east eave ~16 m at x 3.5)
    gable_roof(mb, -16.2, 3.5, -6.3, -22.5, 27.0, 15.9, 16.0, 19.6)
    # flat roof over the middle with the clerestory monitor (LiDAR 16.0 / 19.1 m)
    x0, x1, y0, y1 = MONITOR
    flat = ccw([(3.5, -16.6), (EAST_RECESS_X, -16.6), (EAST_RECESS_X, 21.8), (3.5, 21.8)])
    slab(mb, "flat", flat, [MONITOR], 16.0, z_under=TOP)
    for (A, B) in (((x0, y0), (x1, y0)), ((x1, y0), (x1, y1)), ((x1, y1), (x0, y1)), ((x0, y1), (x0, y0))):
        wall(mb, Vector(A), Vector(B), 16.0, 19.1, 0.25, [(0.2, (Vector(B) - Vector(A)).length - 0.2, 16.4, 18.8, "win")],
             mat="flat", mull=1.5, inner="white")
    mb.abox("flat", x0 - 0.3, x1 + 0.3, y0 - 0.3, y1 + 0.3, 19.1, 19.4)
    # SW angled bay (theatre stage house): flat roof with parapet just under the block eave
    bay = ccw([(-15.4, -39.7), (3.7, -39.7), (-0.9, -44.2), (-10.8, -44.3)])
    slab(mb, "flat", bay, [], TOP + 0.4, z_under=TOP)
    slab(mb, "flat", ccw([(EAST_RECESS_X, 17.6), (39.9, 17.6), (39.9, 21.8), (EAST_RECESS_X, 21.8)]), [], 16.0, z_under=TOP)


# ---------------------------------------------------------------- interior: floors, rooms, furniture
FLOOR_HOLES = {L2: [ATRIUM], L3: [ATRIUM, (-10.5, -2.2, -18.0, 16.6)]}
FLOOR_MAT = {LB: "carpet", L1: "woodfloor", L2: "carpet", L3: "carpet"}


def floors(mb):
    slab(mb, "slab", GROUND, [], LB - 0.05)
    slab(mb, FLOOR_MAT[L1], GROUND, [], L1, z_under=L1 - FLOOR_T, under_mat="white")
    slab(mb, FLOOR_MAT[L2], UPPER, FLOOR_HOLES[L2], L2, z_under=L2 - FLOOR_T, under_mat="white")
    slab(mb, FLOOR_MAT[L3], UPPER, FLOOR_HOLES[L3], L3, z_under=L3 - FLOOR_T, under_mat="white")
    # ceiling under the roofs on floor 3 (open over the atrium/monitor and the reading room)
    slab(mb, "white", UPPER, [ATRIUM, READING_VOID, MONITOR], TOP - 0.3, z_under=TOP - 0.31, under_mat="white")
    # atrium edge railings (glass with a steel cap; BSA N100/N105)
    for z in (L2, L3):
        x0, x1, y0, y1 = ATRIUM
        for (a, b) in (((x0, y0), (x1, y0)), ((x1, y0), (x1, y1)), ((x1, y1), (x0, y1)), ((x0, y1), (x0, y0))):
            A, B = Vector(a), Vector(b)
            _, t, n, L = seg_frame(A, B)
            mb.box("railglass", A, t, -n, L, 0.03, z, z + 1.05)
            mb.box("steel", A + n * 0.03, t, -n, L, 0.08, z + 1.05, z + 1.1)


def room_walls(mb, box, z0, z1, glass=False, doors=1, skip_ext=True):
    """Partition walls around a plan rectangle, clipped to stay inside the exterior walls (no stubs poking out);
    walls lying on the exterior wall line are skipped."""
    x0, x1, y0, y1 = box
    poly = UPPER if z0 >= L2 else GROUND
    edges = [((x0, y0), (x1, y0)), ((x1, y0), (x1, y1)), ((x1, y1), (x0, y1)), ((x0, y1), (x0, y0))]
    for (a, b) in edges:
        A, B = Vector(a), Vector(b)
        mid = (A + B) / 2
        if skip_ext and (not inside((mid.x + 0.9, mid.y), poly) or not inside((mid.x - 0.9, mid.y), poly)
                         or not inside((mid.x, mid.y + 0.9), poly) or not inside((mid.x, mid.y - 0.9), poly)):
            continue
        if skip_ext:   # keep the longest run of the edge that stays 0.5 m inside the building
            L0 = (B - A).length
            d = (B - A) / L0
            nrm = Vector((-d.y, d.x))
            ok = [all(inside(tuple(A + d * s + v), poly) for v in (nrm * 0.5, -nrm * 0.5, d * 0.5, -d * 0.5))
                  for s in [L0 * i / 40 for i in range(41)]]
            best, cur = (0, -1), None
            for i, f in enumerate(ok):
                if f and cur is None:
                    cur = i
                if (not f or i == 40) and cur is not None:
                    e = i if f else i - 1
                    if e - cur > best[1] - best[0]:
                        best = (cur, e)
                    cur = None
            if best[1] <= best[0]:
                continue
            A, B = A + d * (L0 * best[0] / 40), A + d * (L0 * best[1] / 40)
        _, t, n, L = seg_frame(A, B)
        h = z1 - z0
        door = doors and L > 4.0
        if glass and door:
            ops = [(0.1, L / 2 - 1.0, 0.0, h - 0.4, "win"), (L / 2 - 0.9, L / 2 + 0.9, 0.0, 2.4, "door"),
                   (L / 2 + 1.0, L - 0.1, 0.0, h - 0.4, "win")]
        elif glass:
            ops = [(0.1, L - 0.1, 0.0, h - 0.4, "win")]
        elif door:
            ops = [(L / 2 - 0.9, L / 2 + 0.9, 0.0, 2.4, "door")]
        else:
            ops = []
        ops = [(o[0], o[1], z0 + o[2], z0 + o[3], o[4]) for o in ops]
        wall(mb, A, B, z0, z1, 0.15, ops, mat="white", inset=0.07, mull=1.5, frame="steel")


def lights(mb, box, z):
    x0, x1, y0, y1 = box
    nx, ny = max(1, int((x1 - x0) / 3.6)), max(1, int((y1 - y0) / 3.6))
    for i in range(nx):
        for j in range(ny):
            cx, cy = x0 + (i + 0.5) * (x1 - x0) / nx, y0 + (j + 0.5) * (y1 - y0) / ny
            if not indoors(cx, cy, 1.2):
                continue
            mb.abox("light", cx - 0.15, cx + 0.15, cy - 1.0, cy + 1.0, z - 0.05, z)


FURN_POLY = None   # footprint of the floor being furnished; items outside it (e.g. at the angled bays) are skipped


def indoors(cx, cy, m=0.5):
    return FURN_POLY is None or all(inside((cx + dx, cy + dy), FURN_POLY) for dx, dy in ((m, 0), (-m, 0), (0, m), (0, -m)))


def chair(mb, cx, cy, z, ang, mat="chair"):
    if not indoors(cx, cy):
        return
    d = Vector((math.cos(ang), math.sin(ang)))
    p = Vector((-d.y, d.x))
    o = Vector((cx, cy)) - d * 0.22 - p * 0.22
    mb.box(mat, o, d, p, 0.44, 0.44, z + 0.42, z + 0.48)
    mb.box(mat, o - d * 0.02, d, p, 0.05, 0.44, z + 0.48, z + 0.92)
    mb.box("steel", Vector((cx, cy)) - d * 0.03 - p * 0.03, d, p, 0.06, 0.06, z, z + 0.42)


def round_table(mb, cx, cy, z, seats=6, r=0.8):
    if not indoors(cx, cy, 1.4):
        return
    mb.cyl("table", cx, cy, r, z + 0.72, z + 0.76, n=12)
    mb.cyl("steel", cx, cy, 0.06, z, z + 0.72, n=6, cap=False)
    for k in range(seats):
        a = 2 * math.pi * k / seats
        chair(mb, cx + math.cos(a) * (r + 0.45), cy + math.sin(a) * (r + 0.45), z, a + math.pi)


def rect_table(mb, cx, cy, z, lx, ly, mat="table", chairs=True):
    if not indoors(cx, cy, max(lx, ly) / 2 + 0.3):
        return
    mb.abox(mat, cx - lx / 2, cx + lx / 2, cy - ly / 2, cy + ly / 2, z + 0.72, z + 0.76)
    for sx in (-1, 1):
        for sy in (-1, 1):
            mb.abox("steel", cx + sx * (lx / 2 - 0.08) - 0.03, cx + sx * (lx / 2 - 0.08) + 0.03,
                    cy + sy * (ly / 2 - 0.08) - 0.03, cy + sy * (ly / 2 - 0.08) + 0.03, z, z + 0.72)
    if chairs:
        if lx >= ly:
            n = max(1, int(lx / 0.75))
            for k in range(n):
                xx = cx - lx / 2 + (k + 0.5) * lx / n
                chair(mb, xx, cy - ly / 2 - 0.4, z, math.pi / 2)
                chair(mb, xx, cy + ly / 2 + 0.4, z, -math.pi / 2)
        else:
            n = max(1, int(ly / 0.75))
            for k in range(n):
                yy = cy - ly / 2 + (k + 0.5) * ly / n
                chair(mb, cx - lx / 2 - 0.4, yy, z, 0.0)
                chair(mb, cx + lx / 2 + 0.4, yy, z, math.pi)


def grid(box, sx, sy, margin=1.2):
    x0, x1, y0, y1 = box
    nx, ny = max(1, int((x1 - x0 - 2 * margin) / sx)), max(1, int((y1 - y0 - 2 * margin) / sy))
    for i in range(nx):
        for j in range(ny):
            yield (x0 + margin + (i + 0.5) * (x1 - x0 - 2 * margin) / nx, y0 + margin + (j + 0.5) * (y1 - y0 - 2 * margin) / ny)


def tiered_arcs(mb, box, z, front, rows, rise, seats_mat="table", theatre=False):
    """Curved tiered rows facing `front` ('w','s','e','n'): arcs centred behind the front wall."""
    x0, x1, y0, y1 = box
    cx, cy = (x0 + x1) / 2, (y0 + y1) / 2
    dirs = {"w": Vector((-1, 0)), "e": Vector((1, 0)), "s": Vector((0, -1)), "n": Vector((0, 1))}
    f = dirs[front]
    depth = (x1 - x0) if abs(f.x) > 0.5 else (y1 - y0)
    width = (y1 - y0) if abs(f.x) > 0.5 else (x1 - x0)
    C = Vector((cx, cy)) + f * (depth / 2 + width * 0.6)     # arc centre beyond the front wall
    r0 = (C - (Vector((cx, cy)) + f * (depth / 2 - (3.5 if not theatre else 4.5)))).length
    step = (depth - (5.0 if not theatre else 6.0)) / rows
    half = math.asin(min(0.95, (width / 2 - 1.2) / (r0 + rows * step)))
    base = math.atan2(-f.y, -f.x)
    for i in range(rows):
        r = r0 + (i + 0.5) * step
        zr = z + (i + 1) * rise
        # tier platform
        a0, a1 = base - half, base + half
        nseg = 10
        for k in range(nseg):
            u0, u1 = a0 + (a1 - a0) * k / nseg, a0 + (a1 - a0) * (k + 1) / nseg
            pts = [C + Vector((math.cos(u0), math.sin(u0))) * (r - step / 2), C + Vector((math.cos(u1), math.sin(u1))) * (r - step / 2),
                   C + Vector((math.cos(u1), math.sin(u1))) * (r + step / 2), C + Vector((math.cos(u0), math.sin(u0))) * (r + step / 2)]
            mb.poly("carpet", [(p.x, p.y, zr) for p in pts])
            mb.poly("white", [(pts[0].x, pts[0].y, zr - rise), (pts[1].x, pts[1].y, zr - rise), (pts[1].x, pts[1].y, zr), (pts[0].x, pts[0].y, zr)])
        n = int((a1 - a0) * r / (0.6 if theatre else 0.75))
        for k in range(n):
            a = a0 + (a1 - a0) * (k + 0.5) / n
            p = C + Vector((math.cos(a), math.sin(a))) * r
            face = a + math.pi      # towards the front
            if theatre:
                d = Vector((math.cos(face), math.sin(face)))
                q = Vector((-d.y, d.x))
                o = p - d * 0.25 - q * 0.25
                mb.box("seat", o, d, q, 0.5, 0.5, zr + 0.40, zr + 0.48)
                mb.box("seat", o - d * 0.02, d, q, 0.08, 0.5, zr + 0.40, zr + 1.0)
                mb.box("wood", o, d, q, 0.5, 0.05, zr, zr + 0.65)
            else:
                d = Vector((math.cos(face), math.sin(face)))
                q = Vector((-d.y, d.x))
                mb.box(seats_mat, p + d * 0.45 - q * 0.37, d, q, 0.5, 0.74, zr + 0.72, zr + 0.76)
                chair(mb, p.x, p.y, zr, face)


def stacks(mb, box, z, along="x", gap=1.6):
    x0, x1, y0, y1 = box
    if along == "x":
        y = y0 + 1.5
        while y < y1 - 1.5:
            mb.abox("wood", x0 + 1.5, x1 - 4.5, y - 0.3, y + 0.3, z, z + 2.2)
            mb.abox("books", x0 + 1.55, x1 - 4.55, y - 0.32, y + 0.32, z + 0.15, z + 2.1)
            y += gap
        for (cx, cy) in grid((x1 - 4.2, x1 - 0.6, y0, y1), 1.8, 3.0, 0.8):   # study carrels by the windows (BSA N106)
            rect_table(mb, cx, cy, z, 1.4, 2.4, mat="tablewood")


def stair_tower(mb, box, zb, zt):
    """Enclosed switchback stair (plans: octagonal-cornered towers); walls, landings and two flights per storey."""
    x0, x1, y0, y1 = box
    room_walls(mb, box, zb, zt, doors=1)
    levels = [LB, L1, L2, L3]
    long_x = (x1 - x0) >= (y1 - y0)
    for za, zb2 in zip(levels, levels[1:]):
        if za < zb - 0.01:
            continue
        mid = (za + zb2) / 2
        n = 14
        for side, (s0, s1) in enumerate(((za, mid), (mid, zb2))):
            for k in range(n):
                f = k / n
                if long_x:
                    xx = x0 + 2.0 + (x1 - x0 - 4.0) * (f if side == 0 else 1 - f)
                    yy0, yy1 = (y0 + 0.3, (y0 + y1) / 2 - 0.1) if side == 0 else ((y0 + y1) / 2 + 0.1, y1 - 0.3)
                    mb.abox("slab", xx, xx + (x1 - x0 - 4.0) / n, yy0, yy1, s0 + (s1 - s0) * f, s0 + (s1 - s0) * (f + 1 / n))
                else:
                    yy = y0 + 2.0 + (y1 - y0 - 4.0) * (f if side == 0 else 1 - f)
                    xx0, xx1 = (x0 + 0.3, (x0 + x1) / 2 - 0.1) if side == 0 else ((x0 + x1) / 2 + 0.1, x1 - 0.3)
                    mb.abox("slab", xx0, xx1, yy, yy + (y1 - y0 - 4.0) / n, s0 + (s1 - s0) * f, s0 + (s1 - s0) * (f + 1 / n))
        if long_x:
            mb.abox("slab", x1 - 2.0, x1 - 0.3, y0 + 0.3, y1 - 0.3, mid - 0.2, mid)
        else:
            mb.abox("slab", x0 + 0.3, x1 - 0.3, y1 - 2.0, y1 - 0.3, mid - 0.2, mid)


def grand_stair(mb):
    """Open atrium stair: long straight flights with dark steel stringers and glass rails (BSA N100/N105, Turner 002)."""
    x0, x1, y0, y1 = ATRIUM
    for (xa, xb, ya, yb, za, zb) in ((x0 + 0.6, x0 + 2.6, y0 + 1.5, y1 - 2.5, L1, L2), (x1 - 2.6, x1 - 0.6, y1 - 1.5, y0 + 2.5, L2, L3)):
        n = 32
        for k in range(n):
            f0, f1 = k / n, (k + 1) / n
            yy0, yy1 = ya + (yb - ya) * f0, ya + (yb - ya) * f1
            mb.abox("woodfloor", xa, xb, min(yy0, yy1), max(yy0, yy1), za + (zb - za) * f1 - 0.05, za + (zb - za) * f1)
        for xs in (xa - 0.1, xb):
            A, B = Vector((xs, ya, za)), Vector((xs, yb, zb))
            mb.poly("steel", [A + Vector((0, 0, -0.45)), B + Vector((0, 0, -0.45)), B + Vector((0, 0, 0.05)), A + Vector((0, 0, 0.05))])
            mb.poly("steel", [A + Vector((0.1, 0, 0.05)), B + Vector((0.1, 0, 0.05)), B + Vector((0.1, 0, -0.45)), A + Vector((0.1, 0, -0.45))])
            mb.poly("railglass", [A + Vector((0.05, 0, 0.05)), B + Vector((0.05, 0, 0.05)), B + Vector((0.05, 0, 1.05)), A + Vector((0.05, 0, 1.05))])
    # historic power-plant mural on the atrium's east wall (Turner 002, BSA N105)
    mb.abox("mural", x1 + 0.4, x1 + 0.45, y0 + 1.0, y1 - 1.0, L1 + 0.5, L3 - 0.5)


def strut(mb, P, Q, w, d, mat="steel"):
    """Rectangular member from P to Q (3D): w across in the plane holding the member and Z, d along the normal."""
    a = (Q - P)
    L = a.length
    a.normalize()
    side = Vector((-a.y, a.x, 0)).normalized() if abs(a.z) < 0.99 else Vector((0, 1, 0))
    up = side.cross(a).normalized()
    c = [P + side * s * d / 2 + up * u * w / 2 for (s, u) in ((-1, -1), (1, -1), (1, 1), (-1, 1))]
    e = [p + a * L for p in c]
    for k in range(4):
        mb.poly(mat, [c[k], c[(k + 1) % 4], e[(k + 1) % 4], e[k]])
    mb.poly(mat, c[::-1])
    mb.poly(mat, e)


def reading_room(mb):
    """Second-floor reading room under the west range gable: dark steel king-post trusses, wood-slat vaulted ceiling,
    tall west windows, wood wainscot, long study tables with lamps, painting on the south end wall (BSA N103)."""
    x0, x1, y0, y1 = -10.2, 3.6, -17.8, 16.4
    xr, zr = -6.3, 18.6                      # ceiling ridge just under the roof ridge
    zw, ze = 14.5, 14.5                      # ceiling springing at the walls
    for (xa, za, xb, zb) in ((x0, zw, xr, zr), (xr, zr, x1, ze)):
        mb.poly("slats", [(xa, y0, za), (xb, y0, zb), (xb, y1, zb), (xa, y1, za)])
    # end walls up to the ceiling
    for yy in (y0, y1):
        mb.poly("white", [(x0, yy, L2), (x1, yy, L2), (x1, yy, ze), (xr, yy, zr), (x0, yy, zw)])
    # east wall: glass with steel X bracing at floor 2 (to the stacks/atrium side) and the floor-3 gallery front
    for (za, zb) in ((L2, L3 - FLOOR_T), (L3, TOP - 0.4)):
        mb.abox("railglass", x1, x1 + 0.03, y0, y1, za, zb)
        yy = y0
        while yy < y1 - 0.1:
            yn = min(y1, yy + 4.8)
            strut(mb, Vector((x1 - 0.1, yy, za)), Vector((x1 - 0.1, yy, zb)), 0.15, 0.15)
            strut(mb, Vector((x1 - 0.1, yy, za + 0.1)), Vector((x1 - 0.1, yn, zb - 0.1)), 0.15, 0.12)
            strut(mb, Vector((x1 - 0.1, yy, zb - 0.1)), Vector((x1 - 0.1, yn, za + 0.1)), 0.15, 0.12)
            yy = yn
    # dark steel trusses every 5 m: rafters under the ceiling, bottom chord, king post and two diagonals
    yy = y0 + 2.5
    zc = zw - 0.6
    while yy < y1 - 1.0:
        for (xa, za, xb, zb, w) in ((x0, zw - 0.05, xr, zr - 0.05, 0.3), (xr, zr - 0.05, x1, ze - 0.05, 0.3),
                                    (x0 + 0.3, zc, x1 - 0.3, zc, 0.25), (xr, zc, xr, zr - 0.1, 0.2),
                                    (x0 + 2.4, zc, xr, zr - 1.0, 0.18), (x1 - 2.4, zc, xr, zr - 1.0, 0.18)):
            strut(mb, Vector((xa, yy, za)), Vector((xb, yy, zb)), w, 0.22)
        for px in (xr - 3.5, xr, xr + 3.5):   # pendant lights
            mb.cyl("steel", px, yy + 2.4, 0.01, 11.0, zr - 0.5, n=4, cap=False)
            mb.cyl("lampshade", px, yy + 2.4, 0.22, 10.7, 11.0, n=8)
        yy += 5.0
    # wood wainscot and pilasters
    for yy in (y0 + 0.05, y1 - 0.25):
        mb.abox("wood", x0, x1, yy, yy + 0.2, L2, L2 + 3.0)
    mb.abox("painting", x0 + 4.0, x1 - 6.0, y0 + 0.05, y0 + 0.12, L2 + 4.0, L2 + 7.5)
    mb.abox("wood", x0 + 3.8, x1 - 5.8, y0 + 0.03, y0 + 0.1, L2 + 3.8, L2 + 7.7)
    # long study tables in two lines with lamps and chairs
    for cx in (-6.8, -1.6):
        yy = y0 + 2.5
        while yy < y1 - 3.0:
            rect_table(mb, cx, yy + 1.8, L2, 1.3, 3.6, mat="tablewood")
            for k in (0.6, 1.8, 3.0):
                mb.cyl("steel", cx, yy + k, 0.02, L2 + 0.76, L2 + 1.15, n=4, cap=False)
                mb.cyl("lampshade", cx, yy + k, 0.12, L2 + 1.15, L2 + 1.25, n=6)
            yy += 4.6


def lounge_ceiling(mb):
    """First-floor west lobby/lounge behind the piers: dark wood-slat ceiling, round concrete columns (Turner 003)."""
    x0, x1, y0, y1 = WEST_X + ARCADE_D + 0.4, X(745), -18.0, 16.4
    mb.abox("slats", x0, x1, y0, y1, L2 - 1.0, L2 - 0.95)
    for yy in [y0 + 3 + 6.2 * k for k in range(6)]:
        mb.cyl("column", x1 - 0.6, yy, 0.35, L1, L2 - 1.0, n=12)
    for (cx, cy) in grid((x0 + 0.5, x1 - 1.5, y0, y1), 3.5, 4.0, 1.0):
        mb.abox("fabric", cx - 0.9, cx + 0.9, cy - 0.4, cy + 0.4, L1, L1 + 0.45)
        mb.abox("fabric", cx - 0.9, cx + 0.9, cy - 0.45, cy - 0.3, L1 + 0.45, L1 + 1.0)
    for (cx, cy) in ((x0 + 1.0, y0 + 2.0), (x0 + 1.0, y1 - 2.0), (x0 + 1.0, 0.0)):   # red high-back pods
        mb.cyl("red", cx, cy, 0.6, L1, L1 + 1.6, n=10)


# room schedule traced from the furnished plans (pixel boxes on the 130 dpi renders; see R()). kinds drive furniture.
ROOMS = {
    L1: [("1121", R(165, 385, 210, 355), "round"), ("1132", R(160, 385, 385, 650), "arcs_s"), ("1087", R(165, 390, 655, 885), "round"),
         ("1018", R(540, 830, 205, 460), "lecture_w"), ("1055", R(890, 1190, 620, 860), "theatre"),
         ("study", R(530, 840, 630, 745), "study"), ("core_n1", R(195, 360, 660, 725), "core"),
         ("core_s1", R(920, 1140, 380, 610), "core"), ("offices_e1", R(1000, 1140, 205, 330), "office")],
    L2: [("2121", R(140, 255, 195, 330), "rows"), ("2127", R(255, 360, 195, 330), "rows"), ("2124", R(200, 360, 370, 490), "round"),
         ("2088", R(200, 360, 490, 640), "rows"), ("2087", R(140, 370, 655, 865), "tablet"), ("stacks", R(450, 900, 330, 490), "stacks"),
         ("2051", R(890, 1080, 700, 860), "round"), ("2007", R(980, 1140, 185, 380), "tablet"),
         ("core_s2", R(920, 1140, 380, 600), "core"), ("offices_s2", R(1080, 1190, 600, 860), "office")],
    L3: [("3121", R(150, 265, 205, 345), "rows"), ("3127", R(265, 380, 205, 345), "rows"), ("3122", R(185, 340, 385, 515), "round"),
         ("3132", R(340, 500, 385, 515), "rows"), ("3138", R(500, 620, 385, 515), "rows"), ("3148", R(620, 745, 385, 515), "rows"),
         ("3154", R(745, 905, 385, 515), "rows"), ("3090", R(185, 340, 515, 625), "rows"), ("3084", R(340, 470, 515, 625), "rows"),
         ("pods", R(470, 900, 625, 690), "pods"), ("3087", R(150, 380, 655, 890), "tablet"),
         ("offices_s3", R(905, 1190, 205, 600), "office"), ("core_s3", R(920, 1140, 380, 600), "core")],
    LB: [("B093", R(215, 475, 400, 520, dx=40), "round"), ("B091", R(215, 475, 520, 640, dx=40), "round"),
         ("B074", R(525, 660, 285, 500, dx=40), "round"), ("B066", R(660, 785, 285, 500, dx=40), "rows"),
         ("B058", R(785, 935, 285, 500, dx=40), "round"), ("commons", R(520, 935, 545, 690, dx=40), "study"),
         ("mech_n", R(190, 520, 645, 875, dx=40), "core"), ("mech_s", R(990, 1190, 235, 880, dx=40), "core")],
}
STAIRS = [R(390, 475, 210, 355), R(390, 475, 725, 855), R(895, 985, 205, 355)]


def furnish(mb, kind, box, z, h):
    x0, x1, y0, y1 = box
    if kind == "round":
        for (cx, cy) in grid(box, 3.6, 3.6):
            round_table(mb, cx, cy, z)
    elif kind == "rows":
        for (cx, cy) in grid(box, 3.2, 2.4):
            rect_table(mb, cx, cy, z, 1.6, 0.7)
    elif kind == "tablet":
        for (cx, cy) in grid(box, 0.9, 1.1, 1.6):
            chair(mb, cx, cy, z, -math.pi / 2)
            mb.abox("table", cx - 0.25, cx + 0.15, cy - 0.35, cy - 0.05, z + 0.7, z + 0.73)
    elif kind == "study":
        for (cx, cy) in grid(box, 4.0, 3.2):
            rect_table(mb, cx, cy, z, 2.4, 1.0)
    elif kind == "office":
        for (cx, cy) in grid(box, 3.2, 3.2):
            rect_table(mb, cx, cy, z, 1.6, 0.8, chairs=False)
            chair(mb, cx, cy - 0.8, z, math.pi / 2)
    elif kind == "pods":
        n = max(1, int((y1 - y0) / 4.0))
        for k in range(n):
            yy0 = y0 + k * (y1 - y0) / n
            room_walls(mb, (x0, x1, yy0, yy0 + (y1 - y0) / n), z, z + h, glass=True, doors=0, skip_ext=False)
            rect_table(mb, (x0 + x1) / 2, yy0 + (y1 - y0) / n / 2, z, 1.6, 0.9)
    elif kind == "stacks":
        stacks(mb, box, z)
    elif kind == "arcs_s":
        tiered_arcs(mb, box, z, "s", 3, 0.4)
    elif kind == "lecture_w":
        tiered_arcs(mb, box, z, "w", 4, 0.45)
    elif kind == "theatre":
        tiered_arcs(mb, (x0, x1, y0 + 6.0, y1), z, "s", 14, 0.16, theatre=True)
        # stage and gold curtain inside the angled SW bay (Turner 005); dark ceiling soffit over the seating
        mb.abox("wood", -11.3, -0.3, -43.4, -38.0, z, z + 1.0)
        mb.abox("curtain", -10.6, -1.0, -42.9, -42.7, z + 1.0, z + 6.5)
        mb.abox("eave", x0 + 0.2, x1 - 0.2, -38.0, y1 - 0.2, L2 + 2.0, L2 + 2.1)
    if kind in ("rows", "round", "study"):   # projection screen / display wall
        mb.abox("screen", x0 + 0.3, x0 + 0.35, (y0 + y1) / 2 - 2.0, (y0 + y1) / 2 + 2.0, z + 1.2, z + 3.0)


def clamp_box(box, poly, pad=0.6):
    """Keep a traced room inside the exterior walls: trim it to the polygon span through its centre lines."""
    x0, x1, y0, y1 = box
    cx, cy = (x0 + x1) / 2, (y0 + y1) / 2

    def span(c, along_x):
        hits = []
        n = len(poly)
        for k in range(n):
            a, b = poly[k], poly[(k + 1) % n]
            (ua, va), (ub, vb) = ((a[0], a[1]), (b[0], b[1])) if along_x else ((a[1], a[0]), (b[1], b[0]))
            if (va > c) != (vb > c):
                hits.append(ua + (c - va) * (ub - ua) / (vb - va))
        hits.sort()
        m = cx if along_x else cy
        for u0, u1 in zip(hits[0::2], hits[1::2]):
            if u0 <= m <= u1:
                return u0, u1
        return None
    sx, sy = span(cy, True), span(cx, False)
    if sx:
        x0, x1 = max(x0, sx[0] + pad), min(x1, sx[1] - pad)
    if sy:
        y0, y1 = max(y0, sy[0] + pad), min(y1, sy[1] - pad)
    return (x0, x1, y0, y1)


def interior(mb):
    floors(mb)
    heights = {LB: L1 - FLOOR_T, L1: L2 - FLOOR_T, L2: L3 - FLOOR_T, L3: TOP - 0.3}
    for z, rooms in ROOMS.items():
        global FURN_POLY
        FURN_POLY = UPPER if z >= L2 else GROUND
        for (name, box, kind) in rooms:
            box = clamp_box(box, FURN_POLY)
            if kind != "pods":
                room_walls(mb, box, z, heights[z], glass=kind in ("stacks", "study"))
            furnish(mb, kind, box, z, heights[z] - z)
            if kind != "theatre":
                lights(mb, box, heights[z])
    for box in STAIRS:
        stair_tower(mb, box, LB, TOP - 0.3)
    grand_stair(mb)
    reading_room(mb)
    lounge_ceiling(mb)
    # round concrete columns on a ~9 m grid through the open floors (BSA N106, Turner 003)
    for xx in (X(500) - 0.6, X(600) + 0.6):
        for yy in [Y(540) - 0.6 - 7.2 * k for k in range(4)]:
            for (za, zb) in ((L1, L2 - FLOOR_T), (L2, L3 - FLOOR_T), (L3, TOP - 0.3)):
                mb.cyl("column", xx, yy, 0.38, za, zb, n=12, cap=False)


# ---------------------------------------------------------------- main
def main():
    root = bpy.data.objects[ROOT]
    for ob in list(bpy.data.objects):
        if ob.name != ROOT:
            bpy.data.objects.remove(ob, do_unlink=True)
    for c in list(bpy.data.collections):
        if c.name != COLL and not c.all_objects:
            bpy.data.collections.remove(c)
    for coll in (bpy.data.curves, bpy.data.meshes, bpy.data.materials, bpy.data.images, bpy.data.node_groups):
        for d in list(coll):
            if d.users == 0:
                coll.remove(d)
    M = mats()
    mb = MB()
    exterior_walls(mb)
    mb.build("WALC_SP_Walls", M, root)
    west_range(mb)
    mb.build("WALC_SP_WestRange", M, root)
    roofs(mb)
    mb.build("WALC_SP_Roofs", M, root)
    interior(mb)
    mb.build("WALC_SP_Interior", M, root)
    name_letters(M, root)
    for m in list(bpy.data.materials):
        if m.users == 0:
            bpy.data.materials.remove(m)
    bpy.ops.wm.save_mainfile()
    print("WALC_SP_DONE", len(bpy.data.collections[COLL].objects))


main()
