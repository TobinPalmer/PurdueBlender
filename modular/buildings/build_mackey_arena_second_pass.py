"""Mackey Arena second-pass exterior rebuild (rank 1, Rossen second pass).

Run headless on the saved library, which it edits in place and saves:
    blender -b modular/buildings/mackey_arena.blend --python modular/buildings/build_mackey_arena_second_pass.py

Idempotent: deletes every object named MACK_SP_* plus the first-pass exterior shell listed in
LEGACY_EXTERIOR, then rebuilds the exterior. Interior bowl/court/scoreboard objects, the asset root,
collection name and local frame are preserved. All generated objects are parented to
AssetRoot_mackey_arena. Evidence: audit/mackey_arena/second_pass/ (reference index, coverage matrix,
discrepancy checklist, change log). Dimensions are photo/orthophoto estimates, not survey values.
"""
import bpy, bmesh, math
from mathutils import Vector

COLL = "Asset_mackey_arena"
ROOT = "AssetRoot_mackey_arena"
C = Vector((0.0, -14.1375))  # arena drum centre in the asset frame (first-pass GIS registration)

# ---------------------------------------------------------------- heights (estimates; see change log)
LOW_H = 5.8        # one-storey concourse ring / perimeter additions (parapet top)
DRUM_R = 47.5      # drum outer brick face
DRUM_TOP = 17.4    # top of brick drum / underside of fascia
FASCIA_TOP = 19.6
DOME_RIM_R = 47.7
DOME_RIM_Z = 19.4
DOME_APEX = 27.9
WING_H = 14.0      # east/north wing (SDAC) parapet top

LEGACY_PREFIX = ("MACK_Buttress_Pylon_", "MACK_Concourse_Transom_", "MACK_Dome_", "MACK_Exterior_",
                 "MACK_North_Canopy_", "MACK_North_Pavilion_", "MACK_Revolving_Door_", "MACK_Canopy_Downlight_Trim_",
                 "MACK_Canopy_Light_", "MACK_Building_Lettering", "MACK_PERIM_", "MACK_SDAC_Bedford_Limestone",
                 "MACK_SDAC_Boilermaker_Black", "MACK_SDAC_Bronze_Mullion", "MACK_SDAC_SDAC_Brickwork_Procedural",
                 "MACK_SDAC_SDAC_Insulated_Glazing", "MACK_SDAC_Radial_Buttress_Concrete", "MACK_SDAC_Roof_Slab",
                 "MACK_SDAC_SDAC_Roof_Membrane", "MACK_SDAC_Level_", "MACK_SP_")


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


def brick_material():
    m, nt, b = principled("MACK_SP_Brick_Red", (0.30, 0.16, 0.095), rough=0.92, spec=0.15)
    uv = nt.nodes.new("ShaderNodeTexCoord")
    br = nt.nodes.new("ShaderNodeTexBrick")
    br.offset = 0.5
    br.inputs["Scale"].default_value = 1.0
    br.inputs["Brick Width"].default_value = 0.2032
    br.inputs["Row Height"].default_value = 0.0677
    br.inputs["Mortar Size"].default_value = 0.0045
    br.inputs["Color1"].default_value = (0.40, 0.175, 0.077, 1)
    br.inputs["Color2"].default_value = (0.325, 0.135, 0.061, 1)
    br.inputs["Mortar"].default_value = (0.40, 0.36, 0.27, 1)
    br.inputs["Bias"].default_value = 0.0
    nt.links.new(uv.outputs["UV"], br.inputs["Vector"])
    nz = nt.nodes.new("ShaderNodeTexNoise")
    nz.inputs["Scale"].default_value = 3.0
    mix = nt.nodes.new("ShaderNodeMix")
    mix.data_type = "RGBA"
    mix.inputs[0].default_value = 0.06
    nt.links.new(br.outputs["Color"], mix.inputs[6])
    nt.links.new(nz.outputs["Color"], mix.inputs[7])
    nt.links.new(mix.outputs[2], b.inputs["Base Color"])
    bump = nt.nodes.new("ShaderNodeBump")
    bump.inputs["Strength"].default_value = 0.25
    nt.links.new(br.outputs["Fac"], bump.inputs["Height"])
    nt.links.new(bump.outputs["Normal"], b.inputs["Normal"])
    return m


def mats():
    """Base colours from audit/mackey_arena/second_pass/sources/color_samples.json (daylight photo
    medians, scaled ~0.8 from sunlit appearance to albedo; see change log)."""
    M = {}
    M["brick"] = brick_material()
    M["lime"] = principled("MACK_SP_Limestone", (0.64, 0.58, 0.45), rough=0.85, spec=0.2)[0]
    M["copper"] = principled("MACK_SP_Dome_Copper_Coat", (0.60, 0.45, 0.33), rough=0.45, metal=0.25)[0]
    M["seam"] = principled("MACK_SP_Dome_Seam", (0.52, 0.38, 0.27), rough=0.4, metal=0.3)[0]
    M["fascia"] = principled("MACK_SP_Fascia_Bronze", (0.50, 0.35, 0.21), rough=0.4, metal=0.35)[0]
    M["glass"] = principled("MACK_SP_Glass_Dark", (0.012, 0.018, 0.022), rough=0.08, metal=0.1)[0]
    M["glass_lit"] = principled("MACK_SP_Glass_Tower", (0.20, 0.27, 0.30), rough=0.1, metal=0.2)[0]
    M["frame"] = principled("MACK_SP_Frame_Alum", (0.50, 0.50, 0.48), rough=0.35, metal=0.7)[0]
    M["bronze"] = principled("MACK_SP_Frame_DarkBronze", (0.05, 0.04, 0.03), rough=0.4, metal=0.6)[0]
    M["roof_w"] = principled("MACK_SP_Roof_White", (0.74, 0.76, 0.79), rough=0.8)[0]
    M["roof_g"] = principled("MACK_SP_Roof_Grey", (0.14, 0.15, 0.16), rough=0.95, spec=0.2)[0]
    M["unit"] = principled("MACK_SP_Rooftop_Unit", (0.55, 0.56, 0.57), rough=0.5, metal=0.4)[0]
    M["sign"] = principled("MACK_SP_Sign_Black", (0.015, 0.015, 0.018), rough=0.5)[0]
    M["letter_w"] = principled("MACK_SP_Letter_White", (0.85, 0.85, 0.85), rough=0.4, emit=(0.25, 0.25, 0.25))[0]
    M["gold"] = principled("MACK_SP_Purdue_Gold", (0.62, 0.45, 0.12), rough=0.35, metal=0.3, emit=(0.15, 0.1, 0.02))[0]
    M["letter_m"] = principled("MACK_SP_Letter_Metal", (0.035, 0.035, 0.04), rough=0.35, metal=0.7)[0]
    M["paving"] = principled("MACK_SP_Paving", (0.42, 0.40, 0.37), rough=0.9)[0]
    return M


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


def arc_pts(r, a0, a1, step_deg=2.0):
    n = max(2, int(abs(a1 - a0) / step_deg) + 1)
    return [C + Vector((math.cos(math.radians(a0 + (a1 - a0) * i / (n - 1))),
                        math.sin(math.radians(a0 + (a1 - a0) * i / (n - 1))))) * r for i in range(n)]


def flat_poly(mb, mat, pts, z, flip=False):
    """Triangle-fan-free flat face via bmesh face (works for simple polygons)."""
    P = [Vector((p[0], p[1], z)) for p in pts]
    if flip:
        P = P[::-1]
    mb.parts.setdefault(mat, []).append(P)


# ---------------------------------------------------------------- building parts
def build_drum(mb):
    """Brick drum, 24 limestone pilasters, slot-window groups (two slotted bays then a plain bay)."""
    bays = 24
    sub = 12
    thick = 0.5
    z0 = LOW_H - 0.4
    for k in range(bays):
        plain = (k % 3 == 1)
        for s in range(sub):
            a0 = math.radians(k * 15 + s * 15 / sub)
            a1 = math.radians(k * 15 + (s + 1) * 15 / sub)
            A = C + Vector((math.cos(a0), math.sin(a0))) * DRUM_R
            B = C + Vector((math.cos(a1), math.sin(a1))) * DRUM_R
            L = (B - A).length
            ops = []
            if not plain and 3 <= s <= 8:
                ops.append((L / 2 - 0.26, L / 2 + 0.26, 7.2, 16.3))
            wall(mb, A, B, z0, DRUM_TOP, thick, ops, glass="glass", frame="frame", mullions=0, inset=0.3)
        # pilaster on the bay boundary
        a = math.radians(k * 15)
        rad = Vector((math.cos(a), math.sin(a)))
        tan = Vector((-rad.y, rad.x))
        base = C + rad * DRUM_R - tan * 0.6
        mb.box("lime", base, tan, rad, 1.2, 0.45, z0, DRUM_TOP)
    # drum base sill and dark band above the concourse roof
    pts = arc_pts(DRUM_R, 0, 360, 2.5)
    for A, B in zip(pts, pts[1:]):
        band(mb, B, A, LOW_H - 0.1, LOW_H + 0.35, proj=0.12, mat="lime", ext=0.02)
        band(mb, B, A, DRUM_TOP - 0.55, DRUM_TOP, proj=0.06, mat="brick", ext=0.02)


def build_fascia_and_dome(mb):
    # fascia band (slightly flared) + soffit
    N = 192
    for i in range(N):
        a0 = 2 * math.pi * i / N
        a1 = 2 * math.pi * (i + 1) / N
        d0 = Vector((math.cos(a0), math.sin(a0)))
        d1 = Vector((math.cos(a1), math.sin(a1)))
        rb, rt = 48.05, 48.35
        pb0, pb1 = C + d0 * rb, C + d1 * rb
        pt0, pt1 = C + d0 * rt, C + d1 * rt
        mb.quad("fascia", [(pb0.x, pb0.y, DRUM_TOP), (pb1.x, pb1.y, DRUM_TOP), (pt1.x, pt1.y, FASCIA_TOP), (pt0.x, pt0.y, FASCIA_TOP)])
        i0, i1 = C + d0 * (DRUM_R - 0.1), C + d1 * (DRUM_R - 0.1)
        mb.quad("fascia", [(i0.x, i0.y, DRUM_TOP), (i1.x, i1.y, DRUM_TOP), (pb1.x, pb1.y, DRUM_TOP), (pb0.x, pb0.y, DRUM_TOP)][::-1])
        # fascia top cap to dome rim
        r0, r1 = C + d0 * DOME_RIM_R, C + d1 * DOME_RIM_R
        mb.quad("fascia", [(pt0.x, pt0.y, FASCIA_TOP), (pt1.x, pt1.y, FASCIA_TOP), (r1.x, r1.y, DOME_RIM_Z), (r0.x, r0.y, DOME_RIM_Z)])
        # fascia horizontal reveal lines (two thin seams)
        for zz in (18.1, 18.9):
            f = (zz - DRUM_TOP) / (FASCIA_TOP - DRUM_TOP)
            rr = rb + (rt - rb) * f + 0.03
            q0, q1 = C + d0 * rr, C + d1 * rr
            mb.quad("seam", [(q0.x, q0.y, zz), (q1.x, q1.y, zz), (q1.x, q1.y, zz + 0.06), (q0.x, q0.y, zz + 0.06)])
    # spherical-cap dome
    rise = DOME_APEX - DOME_RIM_Z
    Rs = (DOME_RIM_R ** 2 + rise ** 2) / (2 * rise)
    zc = DOME_APEX - Rs

    def zr(r):
        return zc + math.sqrt(max(Rs * Rs - r * r, 0))
    rings = [DOME_RIM_R * (1 - i / 44) for i in range(45)]
    rings = [r for r in rings if r >= 2.0] + [2.0]
    for i in range(N):
        a0 = 2 * math.pi * i / N
        a1 = 2 * math.pi * (i + 1) / N
        d0 = Vector((math.cos(a0), math.sin(a0)))
        d1 = Vector((math.cos(a1), math.sin(a1)))
        for ra, rb2 in zip(rings, rings[1:]):
            p00, p01 = C + d0 * ra, C + d1 * ra
            p10, p11 = C + d0 * rb2, C + d1 * rb2
            mb.quad("copper", [(p00.x, p00.y, zr(ra)), (p01.x, p01.y, zr(ra)), (p11.x, p11.y, zr(rb2)), (p10.x, p10.y, zr(rb2))])
    # standing-seam ribs: 192 / 96 / 48 / 24 between concentric seams (orthophoto ring radii)
    zones = [(DOME_RIM_R, 39.0, 192), (39.0, 29.0, 192), (29.0, 19.5, 96), (19.5, 10.5, 48), (10.5, 3.0, 24)]
    for r_out, r_in, cnt in zones:
        steps = max(3, int((r_out - r_in) / 2.0))
        for k in range(cnt):
            a = 2 * math.pi * (k + 0.5) / cnt
            d = Vector((math.cos(a), math.sin(a)))
            tn = Vector((-d.y, d.x)) * 0.05
            for s in range(steps):
                ra = r_out - (r_out - r_in) * s / steps
                rb2 = r_out - (r_out - r_in) * (s + 1) / steps
                pa, pb = C + d * ra, C + d * rb2
                za, zb = zr(ra) + 0.01, zr(rb2) + 0.01
                h = 0.11
                mb.quad("seam", [(pa.x - tn.x, pa.y - tn.y, za + h), (pa.x + tn.x, pa.y + tn.y, za + h),
                                 (pb.x + tn.x, pb.y + tn.y, zb + h), (pb.x - tn.x, pb.y - tn.y, zb + h)])
                mb.quad("seam", [(pa.x - tn.x, pa.y - tn.y, za), (pa.x - tn.x, pa.y - tn.y, za + h),
                                 (pb.x - tn.x, pb.y - tn.y, zb + h), (pb.x - tn.x, pb.y - tn.y, zb)])
                mb.quad("seam", [(pa.x + tn.x, pa.y + tn.y, za + h), (pa.x + tn.x, pa.y + tn.y, za),
                                 (pb.x + tn.x, pb.y + tn.y, zb), (pb.x + tn.x, pb.y + tn.y, zb + h)])
        # concentric seam ring
        pts = arc_pts(r_in, 0, 360, 2.0)
        for A, B in zip(pts, pts[1:]):
            z = zr(r_in)
            mb.quad("seam", [(A.x, A.y, z + 0.02), (B.x, B.y, z + 0.02), (B.x, B.y, z + 0.16), (A.x, A.y, z + 0.16)])
    # central cap / vent
    zt = zr(2.0)
    capr = [(2.0, zt), (2.0, zt + 0.7), (1.3, zt + 0.95), (0.0, zt + 1.0)]
    for i in range(48):
        a0 = 2 * math.pi * i / 48
        a1 = 2 * math.pi * (i + 1) / 48
        d0 = Vector((math.cos(a0), math.sin(a0)))
        d1 = Vector((math.cos(a1), math.sin(a1)))
        for (ra, za), (rb2, zb) in zip(capr, capr[1:]):
            mb.quad("fascia", [((C + d0 * ra).x, (C + d0 * ra).y, za), ((C + d1 * ra).x, (C + d1 * ra).y, za),
                               ((C + d1 * rb2).x, (C + d1 * rb2).y, zb), ((C + d0 * rb2).x, (C + d0 * rb2).y, zb)])


def low_wall_bands(mb, A, B, h=LOW_H, ext=0.0):
    band(mb, A, B, 0.0, 0.85, proj=0.10, ext=ext)              # water table
    band(mb, A, B, 2.15, 2.30, proj=0.05, ext=ext)            # thin stripe
    band(mb, A, B, 3.55, 3.75, proj=0.05, ext=ext)            # thin stripe
    band(mb, A, B, h - 0.45, h, proj=0.12, ext=ext)           # coping course


def build_concourse_ring(mb, M):
    """One-storey brick concourse wrap around the drum (west, south and north arcs).
    Sector -96..-38 deg is the south block; -38..71 deg lies under the east wing."""
    def r_out(a):
        a = (a + 360) % 360
        if 75 <= a <= 130:
            return 51.6          # narrower between drum and the Brees Center
        if a > 290 or a < 75:
            return 51.6          # under/behind the east wing
        return 54.0
    sw_ent = (226.0, 252.0)    # Morgan & Kate Burke southwest entrance (recessed, canopied)
    n_ent = (98.0, 116.0)      # north (Weist Plaza) entrance storefront
    a_start, a_end = 71.0, 264.0
    step = 2.0
    angs = [a_start + i * step for i in range(int((a_end - a_start) / step) + 1)]
    outer = []
    for a in angs:
        r = r_out(a)
        outer.append(C + Vector((math.cos(math.radians(a)), math.sin(math.radians(a)))) * r)
    # walls (counter-clockwise around the drum => outward normal points away from the drum)
    for a, A, B in zip(angs, outer, outer[1:]):
        am = a + step / 2
        L = (B - A).length
        if sw_ent[0] <= am <= sw_ent[1]:
            # recessed entrance: wall only above canopy soffit, doors at the drum line
            wall(mb, A, B, 4.55, LOW_H, 0.4)
            band(mb, A, B, LOW_H - 0.45, LOW_H, proj=0.12, ext=0.02)
            continue
        ops = []
        if n_ent[0] <= am <= n_ent[1]:
            ops = [(0.15, L - 0.15, 0.0, 3.6, "door")]
        wall(mb, A, B, 0.0, LOW_H, 0.4, ops)
        low_wall_bands(mb, A, B, ext=0.02)
    # roof of the ring
    inner = [C + Vector((math.cos(math.radians(a)), math.sin(math.radians(a)))) * (DRUM_R - 0.3) for a in angs]
    for i in range(len(angs) - 1):
        o0, o1, i0, i1 = outer[i], outer[i + 1], inner[i], inner[i + 1]
        mb.quad("roof_g", [(i0.x, i0.y, LOW_H - 0.35), (o0.x, o0.y, LOW_H - 0.35), (o1.x, o1.y, LOW_H - 0.35), (i1.x, i1.y, LOW_H - 0.35)][::-1])
    # southwest entrance: canopy soffit, piers, recessed glazed doors at the drum line, lettering
    a0, a1 = sw_ent
    can_o = arc_pts(54.0, a0, a1, 1.0)
    can_i = arc_pts(DRUM_R, a0, a1, 1.0)
    for i in range(len(can_o) - 1):
        o0, o1, i0, i1 = can_o[i], can_o[i + 1], can_i[i], can_i[i + 1]
        mb.quad("lime", [(i0.x, i0.y, 4.55), (o0.x, o0.y, 4.55), (o1.x, o1.y, 4.55), (i1.x, i1.y, 4.55)])
    door_line = arc_pts(DRUM_R + 0.15, a0 + 1, a1 - 1, 1.0)
    for A, B in zip(door_line, door_line[1:]):
        L = (B - A).length
        wall(mb, A, B, 0.0, 4.55, 0.3, [(0.05, L - 0.05, 0.0, 3.4, "door")], mullions=1)
    for a in (a0 + 0.4, a0 + 9.0, a0 + 17.5, a1 - 0.4):
        d = Vector((math.cos(math.radians(a)), math.sin(math.radians(a))))
        tn = Vector((-d.y, d.x))
        mb.box("brick", C + d * 52.6 - tn * 0.7, tn, d, 1.4, 1.4, 0.0, 4.55)
        mb.box("lime", C + d * 52.55 - tn * 0.75, tn, d, 1.5, 1.5, 0.0, 0.85)
    for a in (a0, a1):  # cheek walls closing the recess
        d = Vector((math.cos(math.radians(a)), math.sin(math.radians(a))))
        tn = Vector((-d.y, d.x))
        mb.box("brick", C + d * DRUM_R - tn * 0.2, tn, d, 0.4, 54.0 - DRUM_R, 0.0, 4.55)
    # south-block-side end wall of ring at 264 deg and north end at 71 deg
    for a in (a_end,):
        d = Vector((math.cos(math.radians(a)), math.sin(math.radians(a))))
        tn = Vector((-d.y, d.x))
        mb.box("brick", C + d * DRUM_R, d, tn, r_out(a) - DRUM_R, 0.4, 0.0, LOW_H)


def letters(text, loc, rot_z, size, mat, M, parent, depth=0.05, name="MACK_SP_Sign_Text"):
    cu = bpy.data.curves.new(name, "FONT")
    cu.body = text
    cu.size = size
    cu.extrude = depth
    cu.align_x = "CENTER"
    cu.align_y = "CENTER"
    ob = bpy.data.objects.new(name, cu)
    ob.location = loc
    ob.rotation_euler = (math.radians(90), 0, rot_z)
    cu.materials.append(M[mat])
    bpy.data.collections[COLL].objects.link(ob)
    ob.parent = parent
    return ob


def build_south_block(mb):
    """One-storey south concourse block between the ring and the SE wing (orthophoto trace)."""
    outline = [Vector(p) for p in [(-5.7, -73.8), (49.7, -73.8), (54.0, -60.9)]]
    arc = arc_pts(DRUM_R - 0.3, -38.0, -96.9, 2.0)  # inner edge hidden against the drum
    poly = outline + [Vector((40.6, -45.8))] + arc
    # outward walls: (-5.7,-67.7)->(-5.7,-73.8)->(49.7,-73.8)->(54,-60.9)
    seq = [Vector((-5.7, C.y - 53.7)), outline[0], outline[1], outline[2]]
    for A, B in zip(seq, seq[1:]):
        L = (B - A).length
        ops = []
        if L > 30:  # long south face: service doors and a few high windows
            for k in range(6):
                u = 4 + k * (L - 8) / 5
                ops.append((u - 0.9, u + 0.9, 2.6, 3.4))
            ops.append((L * 0.62, L * 0.62 + 3.6, 0.0, 3.0, "door"))
        wall(mb, A, B, 0.0, LOW_H, 0.4, ops)
        low_wall_bands(mb, A, B, ext=0.02)
    flat_poly(mb, "roof_g", [(p.x, p.y) for p in poly][::-1], LOW_H - 0.3)
    # raised clerestory strip seen in the orthophoto along the south edge
    mb.box("roof_g", (0.0, -71.0), (1, 0), (0, 1), 34.0, 3.2, LOW_H - 0.3, LOW_H + 0.9)


def build_west_annex(mb):
    """One-storey white-roofed annex west of the drum (orthophoto trace, lean-corrected)."""
    P = [Vector(p) for p in [(-56.4, -17.5), (-48.0, -15.7), (-51.0, 17.0), (-63.7, 23.6)]]
    H = 6.4
    for i in range(4):
        A, B = P[i], P[(i + 1) % 4]
        L = (B - A).length
        ops = []
        if i == 3:  # west face onto John R. Wooden Drive: entrance and windows
            ops = [(L * 0.45, L * 0.45 + 3.2, 0.0, 3.2, "door")]
            for k in range(5):
                u = 3 + k * 6.5
                if abs(u - L * 0.45 - 1.6) > 3 and u + 1.8 < L:
                    ops.append((u, u + 1.8, 1.4, 3.3))
        wall(mb, A, B, 0.0, H, 0.4, ops)
        low_wall_bands(mb, A, B, h=H, ext=0.02)
    flat_poly(mb, "roof_w", [(p.x, p.y) for p in P], H - 0.35)


# east / north wing (Mackey Complex + Student-Athlete Development Center), CCW outline
WING_EAST = [(62.4, -69.0), (65.4, -59.9), (65.0, -33.3), (61.8, -28.5), (61.8, 1.75), (61.2, 44.2),
             (59.3, 64.8), (57.5, 94.9), (55.7, 132.3)]
WING_WEST = [(36.9, 132.8), (28.0, 101.9), (23.2, 82.6), (18.4, 65.7), (17.2, 53.7), (17.8, 37.7)]
NORTH_CAP_C = (47.6, 132.3)
NORTH_CAP_R = 7.1


def wing_outline():
    pts = [Vector(p) for p in WING_EAST]
    for i in range(1, 12):  # north rounded end (semicircle) from east to west
        a = math.pi * i / 12
        pts.append(Vector(NORTH_CAP_C) + Vector((math.cos(a), math.sin(a))) * NORTH_CAP_R)
    pts.append(Vector((NORTH_CAP_C[0] - NORTH_CAP_R, NORTH_CAP_C[1])))
    pts += [Vector(p) for p in WING_WEST]
    arc = arc_pts(51.5, 71.0, -38.0, 3.0)
    pts += arc
    return pts, len(pts) - len(arc)


def facade_openings(L, mid_y, east_entrance=False):
    """Bay rhythm from the HNTB / Herzog / Exponent photographs: storefront ground floor,
    alternating single and paired upper windows, SDAC (north) third-floor windows, attic bands elsewhere."""
    ops = []
    pitch = 4.3
    nb = max(1, int(L / pitch))
    w = L / nb
    sdac = mid_y > 55.0
    for b in range(nb):
        u = b * w
        c = u + w / 2
        if w > 2.6:
            ops.append((c - 1.25, c + 1.25, 0.85, 4.45))
            if b % 2 == 0:
                ops.append((c - 0.5, c + 0.5, 6.1, 9.2))
                if sdac:
                    ops.append((c - 0.5, c + 0.5, 10.3, 12.8))
            else:
                ops.append((c - 1.1, c - 0.15, 6.1, 9.2))
                ops.append((c + 0.15, c + 1.1, 6.1, 9.2))
                if sdac:
                    ops.append((c - 1.1, c - 0.15, 10.3, 12.8))
                    ops.append((c + 0.15, c + 1.1, 10.3, 12.8))
    return ops


def wing_bands(mb, A, B, sdac):
    band(mb, A, B, 0.0, 0.80, proj=0.10, ext=0.02)
    band(mb, A, B, 4.75, 5.45, proj=0.08, ext=0.02)
    band(mb, A, B, 9.45, 9.75, proj=0.06, ext=0.02)
    if not sdac:
        band(mb, A, B, 11.6, 11.8, proj=0.05, ext=0.02)
    band(mb, A, B, WING_H - 0.4, WING_H, proj=0.12, ext=0.02)


TOWERS = [  # glazed stair/lobby towers with Purdue P (orthophoto penthouse boxes, lean-corrected)
    {"name": "SE", "x0": 54.0, "x1": 65.0, "y0": -44.0, "y1": -30.5, "face": "E"},
    {"name": "E_entry_N", "x0": 49.5, "x1": 61.8, "y0": 2.0, "y1": 12.5, "face": "E"},
    {"name": "E_mid", "x0": 42.0, "x1": 59.0, "y0": 51.0, "y1": 62.5, "face": "E"},
    {"name": "N", "x0": 45.0, "x1": 57.5, "y0": 95.0, "y1": 105.0, "face": "E"},
]
EAST_ENTRY = (-26.5, 0.0)  # recessed east (Northwestern Ave) entrance with MACKEY ARENA banner


def build_wing(mb, M, root):
    pts, n_out = wing_outline()
    n = len(pts)
    for i in range(n_out):
        A, B = pts[i], pts[(i + 1) % n]
        L = (B - A).length
        if L < 0.3:
            continue
        mid = (A + B) / 2
        sdac = mid.y > 55.0
        ops = facade_openings(L, mid.y)
        # skip openings that fall behind a glass tower face or the east entrance
        _, t, nn, _ = seg_frame(A, B)
        keep = []
        for o in ops:
            p = A + t * ((o[0] + o[1]) / 2)
            if abs(nn.x) > 0.8 and EAST_ENTRY[0] - 1 < p.y < EAST_ENTRY[1] + 1:
                continue
            if any(T["x0"] - 1.5 < p.x < T["x1"] + 1.5 and T["y0"] - 0.5 < p.y < T["y1"] + 0.5 for T in TOWERS):
                continue
            keep.append(o)
        if abs(nn.x) > 0.8 and A.y < EAST_ENTRY[1] and B.y > EAST_ENTRY[0]:
            # east entrance: three two-storey-height portal openings under a banner panel
            ua = EAST_ENTRY[0] - A.y
            ub = EAST_ENTRY[1] - A.y
            span = ub - ua
            for k in range(3):
                q0 = ua + 1.6 + k * (span - 3.2) / 3 + 0.9
                q1 = ua + 1.6 + (k + 1) * (span - 3.2) / 3 - 0.9
                keep.append((q0, q1, 0.0, 5.6, "void"))
        # curved-glass lobby at the SDAC south-west corner facing Weist Plaza (HNTB photo)
        if A.x < 20 and 37 < mid.y < 58:
            keep = [(0.3, L - 0.3, 0.0, 9.4, "win")]
        wall(mb, A, B, 0.0, WING_H, 0.45, keep)
        wing_bands(mb, A, B, sdac)
    # east entrance recess: back wall of doors, soffit, banner panel and lettering
    x_face = 61.8
    y0, y1 = EAST_ENTRY
    wall(mb, Vector((x_face - 5.0, y0 + 1.6)), Vector((x_face - 5.0, y1 - 1.6)), 0.0, 5.6, 0.3,
         [(0.6, (y1 - y0) - 3.8, 0.0, 3.3, "door")], mullions=6)
    mb.box("lime", (x_face - 5.0, y0 + 1.6), (1, 0), (0, 1), 5.0, (y1 - y0) - 3.2, 5.45, 5.6)
    for k in range(4):  # cheek / pier returns within the recess
        yy = y0 + 1.6 + k * ((y1 - y0) - 3.2) / 3 - 0.45
        mb.box("brick", (x_face - 5.0, yy), (1, 0), (0, 1), 5.0, 0.9, 0.0, 5.6)
    mb.box("sign", (x_face + 0.05, y0 + 4.5), (1, 0), (0, 1), 0.12, (y1 - y0) - 9.0, 6.0, 12.6)
    letters("MACKEY ARENA", (x_face + 0.2, (y0 + y1) / 2, 10.6), math.radians(90), 2.2, "letter_w", M, root)
    letters("HOME OF PURDUE BASKETBALL", (x_face + 0.2, (y0 + y1) / 2, 8.4), math.radians(90), 0.9, "letter_w", M, root)
    for yy, txt in ((y0 + 2.0, "44"), (y1 - 2.0, "59")):
        mb.box("sign", (x_face + 0.05, yy - 1.3), (1, 0), (0, 1), 0.12, 2.6, 5.9, 12.4)
        letters(txt, (x_face + 0.2, yy, 10.4), math.radians(90), 1.6, "letter_w", M, root)
    # roof (white membrane) inside the parapet
    flat_poly(mb, "roof_w", [(p.x, p.y) for p in pts], WING_H - 0.6)
    # glass towers
    for T in TOWERS:
        x0, x1, y0t, y1t = T["x0"], T["x1"], T["y0"], T["y1"]
        top = WING_H + 3.8
        corners = [Vector((x1, y0t)), Vector((x1, y1t)), Vector((x0, y1t)), Vector((x0, y0t))]
        for i in range(4):
            A, B = corners[i], corners[(i + 1) % 4]
            L = (B - A).length
            zb = 0.0 if i == 0 else WING_H - 0.6
            wall(mb, A + Vector((0.35, 0)) * (1 if i == 0 else 0), B + Vector((0.35, 0)) * (1 if i == 0 else 0),
                 zb, top, 0.25, [(0.4, L - 0.4, zb + 0.9, top - 0.7, "win")], glass="glass_lit", frame="frame")
        flat_poly(mb, "unit", [(p.x, p.y) for p in corners][::-1], top)
        mb.box("frame", (x0 - 0.1, y0t - 0.1), (1, 0), (0, 1), x1 - x0 + 0.55, y1t - y0t + 0.2, top - 0.5, top)
        # Purdue motion-P sign on the outward (east) face, upper level
        letters("P", (x1 + 0.6, (y0t + y1t) / 2, WING_H - 2.5), math.radians(90), 3.2, "gold", M, root, depth=0.12,
                name="MACK_SP_Tower_P")
    # a few rooftop units seen in the orthophoto
    for (x, y, sx, sy) in [(50.5, -27.0, 2.6, 3.6), (50.8, -15.0, 2.4, 3.2), (47.5, 18.0, 3.0, 2.2),
                           (35.0, 84.0, 3.4, 2.4), (50.0, 77.0, 2.4, 2.4)]:
        mb.box("unit", (x, y), (1, 0), (0, 1), sx, sy, WING_H - 0.6, WING_H + 1.2)


def move_site_props():
    """First-pass Weist Plaza deck/furniture and the Wooden statue + Pyramid of Success sat inside the
    orthophoto wing footprint. Furniture is removed (location unverified); the two memorials move onto the
    plaza west of the SDAC (estimated positions, see change log)."""
    targets = {("MACK_Statue_Wooden", "MACK_Wooden_", "MACK_Light_Wooden"): Vector((-11.6, 15.8, 0.0)),
               ("MACK_Pyramid_Success",): Vector((-8.1, 25.8, 0.0))}
    for ob in list(bpy.data.objects):
        if ob.name.startswith(("MACK_Weist_Plaza", "MACK_Plaza_")):
            bpy.data.objects.remove(ob, do_unlink=True)
            continue
        for pre, off in targets.items():
            if ob.name.startswith(pre):
                if "sp_orig" not in ob:
                    prev = Vector((ob.get("sp_moved", 0.0), 0.0, 0.0))
                    ob["sp_orig"] = list(ob.location - prev)
                ob.location = Vector(ob["sp_orig"]) + off
                if "sp_moved" in ob:
                    del ob["sp_moved"]


def build_plaza(mb):
    poly = [(4.0, 41.0), (16.8, 38.5), (17.0, 53.5), (18.2, 65.5), (23.0, 82.5), (27.8, 101.8), (36.0, 134.0),
            (4.0, 134.0)]
    flat_poly(mb, "paving", poly, 0.06)


def main():
    root = bpy.data.objects[ROOT]
    for ob in list(bpy.data.objects):
        if ob.name.startswith(LEGACY_PREFIX):
            bpy.data.objects.remove(ob, do_unlink=True)
    for cu in list(bpy.data.curves):
        if cu.users == 0:
            bpy.data.curves.remove(cu)
    for me in list(bpy.data.meshes):
        if me.users == 0:
            bpy.data.meshes.remove(me)
    M = mats()
    mb = MB()
    build_drum(mb)
    mb.build("MACK_SP_Drum", M, root)
    build_fascia_and_dome(mb)
    mb.build("MACK_SP_Dome", M, root)
    build_concourse_ring(mb, M)
    sw = C + Vector((math.cos(math.radians(239)), math.sin(math.radians(239)))) * 54.2
    letters("MACKEY ARENA", (sw.x, sw.y, 5.32), math.radians(239 + 90), 0.62, "letter_m", M, root, depth=0.06,
            name="MACK_SP_SW_Entrance_Text")
    letters("MORGAN & KATE BURKE SOUTHWEST ENTRANCE", (sw.x, sw.y, 4.86), math.radians(239 + 90), 0.24, "letter_m", M,
            root, depth=0.04, name="MACK_SP_SW_Entrance_Subtext")
    mb.build("MACK_SP_Concourse", M, root)
    build_south_block(mb)
    mb.build("MACK_SP_SouthBlock", M, root)
    build_west_annex(mb)
    mb.build("MACK_SP_WestAnnex", M, root)
    build_wing(mb, M, root)
    mb.build("MACK_SP_Wing", M, root)
    move_site_props()
    build_plaza(mb)
    mb.build("MACK_SP_Plaza", M, root)
    for m in list(bpy.data.materials):
        if m.users == 0:
            bpy.data.materials.remove(m)
    bpy.ops.wm.save_mainfile()
    print("MACKEY_SP_DONE", len(bpy.data.collections[COLL].objects))


main()
