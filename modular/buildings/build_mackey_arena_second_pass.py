"""Mackey Arena second-pass exterior rebuild (rank 1, Rossen second pass) - revision r3.

r3 changes (audit/mackey_arena/second_pass/change_log.md): drum re-proportioned (fascia underside 10.1 -> 10.95 m,
louvres up to 9.25 m, wider louvre slots), separate darker drum brick and corrected fascia / louvre / limestone
colours, east entrance recomposed (four portals, 44 / MACKEY ARENA / 59 banners on separate wall segments, blade
piers), SDAC curved glass lobby moved to the plan bend facing Weist Plaza.

Run headless on the saved library, which it edits in place and saves:
    blender -b modular/buildings/mackey_arena.blend --python modular/buildings/build_mackey_arena_second_pass.py

Idempotent: deletes every object named MACK_SP_* plus the first-pass exterior shell listed in
LEGACY_PREFIX, then rebuilds the exterior from the evidence. The interior bowl / court / roof-hung rig
objects are kept but given a recorded vertical offset (INTERIOR_DROP, stored as the custom property
`sp_orig_z`) because the arena floor is below grade and the r2 dome is lower than the first-pass one
(see change log). The asset root, collection name and local frame are preserved. All generated objects
are parented to AssetRoot_mackey_arena.

r2 evidence (audit/mackey_arena/second_pass/): Indiana 2017-2019 QL2 3DEP LiDAR normalized height model
(heights of ring, drum fascia, dome profile, wing, penthouses, annex, south blocks and all footprints),
the Purdue Athletics 2025 aerial from the west (pilaster count, drum proportions, north-west entrance,
west annex facade), Exponent 2025 drone photos, Herzog 2016 Commons photos, HNTB plaza photo and the
2023 orthophoto. Heights are LiDAR measurements (+-0.3-0.5 m); facade subdivisions are photo estimates.
"""
import bpy, bmesh, math
from mathutils import Vector

COLL = "Asset_mackey_arena"
ROOT = "AssetRoot_mackey_arena"
C = Vector((0.0, -14.1375))  # arena drum centre in the asset frame (first-pass GIS registration)

# ---------------------------------------------------------------- heights (LiDAR NDHM, see change log)
RING_ROOF = 4.4      # concourse ring roof surface
LOW_H = 5.3          # concourse ring / south block parapet (coping) top
DRUM_R = 47.5        # drum brick face
N_BAYS = 36          # pilaster bays (10 deg); pilasters on 6 + 10k deg
PIL0 = 6.0
# r3: fascia : channel-above-louvre : louvre = 0.28 : 0.38 : 1 measured on the same slotted bays in the 2025
# west aerial (m27) and drone_04, fitted between the LiDAR ring roof (4.4) and fascia top (12.2) -> drum
# 6.55 m (= 0.79 x the 10-deg bay chord, the r01 reviewer's 0.79-0.80 ratio), fascia 1.25 m (r2: 2.1 m).
DRUM_TOP = 10.95     # underside of the fascia
FASCIA_TOP = 12.2
FASCIA_R0, FASCIA_R1 = 48.0, 48.3
DOME_RIM_R = 47.8
LOUVRE_Z = (4.75, 9.25)  # louvre panels in the lower ~70 % of each channel (m27, drone_04)
CHAN_TOP = DRUM_TOP
# radial dome profile (r, z): median of the NDHM in 1 m rings around the drum centre
DOME_PROFILE = [(0.0, 24.70), (2.5, 24.62), (4.5, 24.43), (6.5, 24.32), (8.5, 24.19), (10.5, 24.09),
                (12.5, 23.80), (14.5, 23.48), (16.5, 23.15), (18.5, 22.84), (20.5, 22.49), (22.5, 21.91),
                (24.5, 21.36), (26.5, 20.79), (28.5, 20.20), (30.5, 19.58), (32.5, 18.80), (34.5, 18.05),
                (36.5, 17.28), (38.5, 16.54), (40.5, 15.58), (42.5, 14.58), (44.5, 13.56), (46.5, 12.65),
                (DOME_RIM_R, 12.08)]
CAP_R, CAP_TOP = 1.9, 26.0
INTERIOR_DROP = 7.5  # arena floor below grade (WJE: crew climbed >100 ft above the court; apex 24.6 m)
INTERIOR_PREFIX = ("MACK_Banner", "MACK_Bench", "MACK_Bowl", "MACK_Court", "MACK_Courtside", "MACK_Floodlight",
                   "MACK_Hoop", "MACK_KeadyCourt", "MACK_Lighting", "MACK_SB_", "MACK_Safety", "MACK_Scoreboard",
                   "Text_MACK")

# wing parapet tops / roof levels by y band (LiDAR: roof 10.0 / 9.5 / 8.7 m)
WING_LEVELS = [(-1e9, 40.0, 10.9, 10.1), (40.0, 93.0, 10.4, 9.6), (93.0, 1e9, 9.8, 8.9)]
ANNEX_H = 7.2

LEGACY_PREFIX = ("MACK_Buttress_Pylon_", "MACK_Concourse_Transom_", "MACK_Dome_", "MACK_Exterior_",
                 "MACK_North_Canopy_", "MACK_North_Pavilion_", "MACK_Revolving_Door_", "MACK_Canopy_Downlight_Trim_",
                 "MACK_Canopy_Light_", "MACK_Building_Lettering", "MACK_PERIM_", "MACK_SDAC_Bedford_Limestone",
                 "MACK_SDAC_Boilermaker_Black", "MACK_SDAC_Bronze_Mullion", "MACK_SDAC_SDAC_Brickwork_Procedural",
                 "MACK_SDAC_SDAC_Insulated_Glazing", "MACK_SDAC_Radial_Buttress_Concrete", "MACK_SDAC_Roof_Slab",
                 "MACK_SDAC_SDAC_Roof_Membrane", "MACK_SDAC_Level_", "MACK_SP_")


def wing_level(y):
    for y0, y1, top, roof in WING_LEVELS:
        if y0 <= y < y1:
            return top, roof
    return WING_LEVELS[-1][2:]


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


def brick_material(name, c1, c2, mortar):
    m, nt, b = principled(name, c1, rough=0.92, spec=0.15)
    uv = nt.nodes.new("ShaderNodeTexCoord")
    br = nt.nodes.new("ShaderNodeTexBrick")
    br.offset = 0.5
    br.inputs["Scale"].default_value = 1.0
    br.inputs["Brick Width"].default_value = 0.2032
    br.inputs["Row Height"].default_value = 0.0677
    br.inputs["Mortar Size"].default_value = 0.0045
    br.inputs["Color1"].default_value = (*c1, 1)
    br.inputs["Color2"].default_value = (*c2, 1)
    br.inputs["Mortar"].default_value = (*mortar, 1)
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
    """Base colours calibrated against audit/mackey_arena/second_pass/sources/color_samples.json and the
    r1 reviewer's colour comparison (review_r01/color_compare.json); see the r2 change log."""
    M = {}
    M["brick"] = brick_material("MACK_SP_Brick_Red", (0.58, 0.29, 0.13), (0.48, 0.23, 0.10), (0.50, 0.45, 0.34))
    # r3: the 1967 drum brick is darker/redder than the 2011 addition brick (2016_02 drum 173,133,99 vs
    # concourse 197,157,122; m27); r2 rendered the drum at 194,152,119 -> scaled per channel in linear space
    M["brick_d"] = brick_material("MACK_SP_Brick_Drum", (0.45, 0.216, 0.087), (0.373, 0.171, 0.067),
                                  (0.45, 0.40, 0.30))
    # r3 colour corrections from r2 render samples vs 2016_02 photo medians (see change log r3)
    M["lime"] = principled("MACK_SP_Limestone", (0.735, 0.635, 0.465), rough=0.85, spec=0.2)[0]
    M["copper"] = principled("MACK_SP_Dome_Copper_Coat", (0.74, 0.55, 0.39), rough=0.5, metal=0.2)[0]
    M["seam"] = principled("MACK_SP_Dome_Seam", (0.62, 0.45, 0.31), rough=0.45, metal=0.25)[0]
    M["fascia"] = principled("MACK_SP_Fascia_Bronze", (0.556, 0.361, 0.153), rough=0.6, metal=0.0)[0]
    M["louvre"] = principled("MACK_SP_Louvre_WarmGrey", (0.40, 0.36, 0.28), rough=0.55, metal=0.25)[0]
    M["louvre_back"] = principled("MACK_SP_Louvre_Back", (0.20, 0.19, 0.17), rough=0.7)[0]
    M["glass"] = principled("MACK_SP_Glass_Dark", (0.02, 0.03, 0.032), rough=0.08, metal=0.1)[0]
    M["glass_lit"] = principled("MACK_SP_Glass_Tower", (0.15, 0.22, 0.21), rough=0.1, metal=0.2)[0]
    M["frame"] = principled("MACK_SP_Frame_Alum", (0.50, 0.50, 0.48), rough=0.35, metal=0.7)[0]
    M["bronze"] = principled("MACK_SP_Frame_DarkBronze", (0.05, 0.04, 0.03), rough=0.4, metal=0.6)[0]
    M["metal"] = principled("MACK_SP_Metal_Panel_Grey", (0.42, 0.43, 0.43), rough=0.45, metal=0.5)[0]
    M["roof_w"] = principled("MACK_SP_Roof_White", (0.74, 0.76, 0.79), rough=0.8)[0]
    M["roof_g"] = principled("MACK_SP_Roof_Ring", (0.44, 0.42, 0.38), rough=0.95, spec=0.2)[0]
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
        if sx <= 1e-6 or sy <= 1e-6 or z1 - z0 <= 1e-6:
            return
        o = Vector((origin[0], origin[1]))
        a = Vector(ax) * sx
        b = Vector(ay) * sy
        c = [o, o + a, o + a + b, o + b]
        lo = [Vector((p.x, p.y, z0)) for p in c]
        hi = [Vector((p.x, p.y, z1)) for p in c]
        faces = {"bottom": [lo[0], lo[3], lo[2], lo[1]], "top": [hi[0], hi[1], hi[2], hi[3]],
                 "f0": [lo[0], lo[1], hi[1], hi[0]], "f1": [lo[1], lo[2], hi[2], hi[1]],
                 "f2": [lo[2], lo[3], hi[3], hi[2]], "f3": [lo[3], lo[0], hi[0], hi[3]]}
        # keep faces outward for either handedness of (ax, ay)
        flip = (a.x * b.y - a.y * b.x) < 0
        for k, f in faces.items():
            if k not in skip:
                self.quad(mat, f[::-1] if flip else f)

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
                if len(q) >= 3:
                    n = (q[1] - q[0]).cross(q[2] - q[0])
                else:
                    continue
                if n.length < 1e-9:
                    n = f.normal.copy()
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


def glazing(mb, P0, t, inw, u0, u1, za, zb, glass="glass", frame="bronze", nv=None, nh=None, inset=0.22,
            kind="win"):
    """Glass pane + frame + mullion grid in a wall opening. P0 is the wall-face origin of the segment."""
    mb.box(glass, P0 + t * u0 + inw * inset, t, inw, u1 - u0, 0.04, za, zb)
    fw = 0.06
    p = P0 + inw * (inset - 0.05)
    w = u1 - u0
    mb.box(frame, p + t * u0, t, inw, fw, 0.05, za, zb)
    mb.box(frame, p + t * (u1 - fw), t, inw, fw, 0.05, za, zb)
    mb.box(frame, p + t * u0, t, inw, w, 0.05, za, za + fw)
    mb.box(frame, p + t * u0, t, inw, w, 0.05, zb - fw, zb)
    nm = nv if nv is not None else max(0, int(round(w / 1.3)) - 1)
    for k in range(1, nm + 1):
        uu = u0 + w * k / (nm + 1) - 0.03
        mb.box(frame, p + t * uu, t, inw, 0.06, 0.05, za, zb)
    if kind == "door":
        mb.box(frame, p + t * u0, t, inw, w, 0.05, za + 2.6, za + 2.68)
    elif nh:
        for k in range(1, nh + 1):
            zt = za + (zb - za) * k / (nh + 1)
            mb.box(frame, p + t * u0, t, inw, w, 0.05, zt - 0.03, zt + 0.03)
    elif zb - za > 3.0:
        zt = za + (zb - za) * 0.78
        mb.box(frame, p + t * u0, t, inw, w, 0.05, zt, zt + 0.06)


def wall(mb, A, B, z0, z1, thick, openings=(), mat="brick", glass="glass", inset=0.22, frame="bronze",
         mullions=None, outward=True):
    """Straight wall A->B (outer face on the A-B line, thickness inward).
    openings: list of (u0, u1, zb, zt[, kind[, nv, nh]]) in metres along the segment.
    kind: win / door / void (hole only)."""
    A, t, n, L = seg_frame(A, B)
    inw = -n if outward else n
    for (u0, u1, za, zb) in rect_fill(0, L, z0, z1, [o[:4] for o in openings]):
        mb.box(mat, A + t * u0, t, inw, u1 - u0, thick, za, zb)
    for o in openings:
        u0, u1, za, zb = o[:4]
        kind = o[4] if len(o) > 4 else "win"
        if kind == "void":
            continue
        nv = o[5] if len(o) > 5 else mullions
        nh = o[6] if len(o) > 6 else None
        glazing(mb, A, t, inw, u0, u1, za, zb, glass=glass, frame=frame, nv=nv, nh=nh, inset=inset, kind=kind)
        # reveal / sill depth faces are provided by the surrounding wall boxes


def band(mb, A, B, z0, z1, proj=0.07, mat="lime", ext=0.0):
    A, t, n, L = seg_frame(A, B)
    mb.box(mat, A - t * ext + n * proj, t, -n, L + 2 * ext, proj + 0.05, z0, z1)


def pol(a_deg, r):
    a = math.radians(a_deg)
    return C + Vector((math.cos(a), math.sin(a))) * r


def arc_pts(r, a0, a1, step_deg=2.0):
    n = max(2, int(abs(a1 - a0) / step_deg) + 1)
    return [pol(a0 + (a1 - a0) * i / (n - 1), r) for i in range(n)]


def flat_poly(mb, mat, pts, z, flip=False):
    P = [Vector((p[0], p[1], z)) for p in pts]
    area = sum(P[i].x * P[(i + 1) % len(P)].y - P[(i + 1) % len(P)].x * P[i].y for i in range(len(P)))
    if (area < 0) != flip:
        P = P[::-1]
    mb.parts.setdefault(mat, []).append(P)


def clip_y(poly, y0, y1):
    """Sutherland-Hodgman clip of a polygon to y0 <= y <= y1."""
    def clip(pts, keep, inter):
        out = []
        for i in range(len(pts)):
            P, Q = pts[i], pts[(i + 1) % len(pts)]
            if keep(Q):
                if not keep(P):
                    out.append(inter(P, Q))
                out.append(Q)
            elif keep(P):
                out.append(inter(P, Q))
        return out

    def at_y(y):
        return lambda P, Q: Vector((P.x + (Q.x - P.x) * (y - P.y) / (Q.y - P.y), y))
    pts = [Vector(p) for p in poly]
    if y0 > -1e8:
        pts = clip(pts, lambda p: p.y >= y0, at_y(y0))
    if pts and y1 < 1e8:
        pts = clip(pts, lambda p: p.y <= y1, at_y(y1))
    return pts


def point_in_poly(p, poly):
    x, y = p
    inside = False
    for i in range(len(poly)):
        x1, y1 = poly[i]
        x2, y2 = poly[(i + 1) % len(poly)]
        if (y1 > y) != (y2 > y) and x < x1 + (y - y1) * (x2 - x1) / (y2 - y1):
            inside = not inside
    return inside


def letters(text, loc, rot_z, size, mat, M, parent, depth=0.05, name="MACK_SP_Sign_Text", rot_y=0.0, align="CENTER"):
    cu = bpy.data.curves.new(name, "FONT")
    cu.body = text
    cu.size = size
    cu.extrude = depth
    cu.align_x = align
    cu.align_y = "CENTER"
    ob = bpy.data.objects.new(name, cu)
    ob.location = loc
    ob.rotation_euler = (math.radians(90), rot_y, rot_z)
    cu.materials.append(M[mat])
    bpy.data.collections[COLL].objects.link(ob)
    ob.parent = parent
    return ob


def facing_rot(n):
    """rot_z so that text (rotation x=90, front facing -Y) faces outward normal n (2D)."""
    return math.atan2(n.y, n.x) + math.pi / 2


# ---------------------------------------------------------------- drum
NORTH_OPEN = (72.0, 137.0)          # no concourse ring: drum wall to the ground (LiDAR)
N_ENTRANCE_BAYS = (106.0, 116.0)    # north (Weist Plaza) entrance storefront bays (start angles); one plain +
                                    # one slotted bay, pilaster to the ground between (hntb_Purdue-2, 2025 aerial)
NW_ENTRANCE_BAYS = ()
SW_ENT = (207.0, 235.0)             # Morgan & Kate Burke southwest entrance (LiDAR canopy, 2016_02, drone_04)


def bay_kind(a0):
    """Slot / plain rhythm: two slotted bays then a plain bay; plain bay centred over the SW entrance
    (226-236 deg) just north of the SW entrance lettering, consistent with 2016_02, drone_04 (slotted bay over the
    lettering, plain bay to its right), hntb_Purdue-2 (plain bay over the north entrance, slotted bay right of it)
    and the 2025 west aerial (plain bay just left of the frontal pilaster)."""
    k = int(round((a0 - 226.0) / 10.0)) % 3
    return "plain" if k == 0 else "slot"


def build_drum(mb):
    thick = 0.45
    for k in range(N_BAYS):
        a0 = PIL0 + 10.0 * k
        a1 = a0 + 10.0
        am = (a0 + a1) / 2
        north = NORTH_OPEN[0] <= am <= NORTH_OPEN[1]
        z0 = 0.0
        A, B = pol(a0, DRUM_R), pol(a1, DRUM_R)
        Af, t, n, L = seg_frame(A, B)
        inw = -n
        ops = []
        kind = bay_kind(a0)
        chans = []
        if kind == "slot":
            pitch, cw = 1.06, 0.62   # m27 / 2016_02: louvre 0.62-0.65 m wide at 1.06 m pitch
            for j in range(5):
                c = L / 2 + (j - 2) * pitch
                chans.append((c - cw / 2, c + cw / 2))
                ops.append((c - cw / 2, c + cw / 2, LOUVRE_Z[0], CHAN_TOP, "void"))
        store = north and (a0 in N_ENTRANCE_BAYS or a0 in NW_ENTRANCE_BAYS)
        if store:
            ops.append((0.45, L - 0.45, 0.0, 3.45, "void"))
        wall(mb, A, B, z0, DRUM_TOP, thick, ops, mat="brick_d")
        # channel backs and louvres
        for (c0, c1) in chans:
            mb.box("brick_d", Af + t * c0 + inw * 0.16, t, inw, c1 - c0, 0.12, LOUVRE_Z[1], CHAN_TOP)
            mb.box("louvre_back", Af + t * c0 + inw * 0.2, t, inw, c1 - c0, 0.05, LOUVRE_Z[0], LOUVRE_Z[1])
            zz = LOUVRE_Z[0] + 0.05
            while zz < LOUVRE_Z[1] - 0.06:
                mb.box("louvre", Af + t * (c0 + 0.03) + inw * 0.06, t, inw, c1 - c0 - 0.06, 0.13, zz, zz + 0.075)
                zz += 0.125
            for zf in (LOUVRE_Z[0], (2 * LOUVRE_Z[0] + LOUVRE_Z[1]) / 3, (LOUVRE_Z[0] + 2 * LOUVRE_Z[1]) / 3,
                       LOUVRE_Z[1] - 0.06):
                mb.box("frame", Af + t * c0 + inw * 0.04, t, inw, c1 - c0, 0.04, zf, zf + 0.06)
        if store:
            glazing(mb, Af, t, inw, 0.45, L - 0.45, 0.0, 3.45, glass="glass", frame="frame", nv=6, kind="door",
                    inset=0.3)
            # projecting canopy / sign band over the storefront
            mb.box("lime", Af - t * 0.1 + n * 1.3, t, -n, L + 0.2, 1.3, 3.45, 3.6)
            mb.box("lime", Af - t * 0.1 + n * 1.3, t, -n, L + 0.2, 0.25, 3.6, 4.35)
        # base courses
        if north:
            band(mb, A, B, 0.0, 0.9, proj=0.10, ext=0.02)
            if not store:
                band(mb, A, B, 3.6, 3.75, proj=0.05, ext=0.02)
        band(mb, A, B, RING_ROOF, RING_ROOF + 0.35, proj=0.10, mat="lime", ext=0.02)
    # pilasters
    for k in range(N_BAYS):
        a = PIL0 + 10.0 * k
        rad = Vector((math.cos(math.radians(a)), math.sin(math.radians(a))))
        tan = Vector((-rad.y, rad.x))
        north = NORTH_OPEN[0] <= a <= NORTH_OPEN[1]
        zp = 0.0 if north else RING_ROOF
        base = pol(a, DRUM_R - 0.05) - tan * 0.375
        mb.box("lime", base, tan, rad, 0.75, 0.45, zp, DRUM_TOP)


def build_fascia_and_dome(mb):
    # vertically corrugated fascia band (slight flare), soffit and top cap
    M_SEG = 1440
    for i in range(M_SEG):
        a0 = 2 * math.pi * i / M_SEG
        a1 = 2 * math.pi * (i + 1) / M_SEG
        d0 = Vector((math.cos(a0), math.sin(a0)))
        d1 = Vector((math.cos(a1), math.sin(a1)))
        o0 = 0.06 if i % 2 == 0 else 0.0
        o1 = 0.06 if (i + 1) % 2 == 0 else 0.0
        pb0, pb1 = C + d0 * (FASCIA_R0 + o0), C + d1 * (FASCIA_R0 + o1)
        pt0, pt1 = C + d0 * (FASCIA_R1 + o0), C + d1 * (FASCIA_R1 + o1)
        mb.quad("fascia", [(pb0.x, pb0.y, DRUM_TOP), (pb1.x, pb1.y, DRUM_TOP), (pt1.x, pt1.y, FASCIA_TOP),
                           (pt0.x, pt0.y, FASCIA_TOP)])
    N = 288
    for i in range(N):
        a0 = 2 * math.pi * i / N
        a1 = 2 * math.pi * (i + 1) / N
        d0 = Vector((math.cos(a0), math.sin(a0)))
        d1 = Vector((math.cos(a1), math.sin(a1)))
        i0, i1 = C + d0 * (DRUM_R - 0.1), C + d1 * (DRUM_R - 0.1)
        b0, b1 = C + d0 * FASCIA_R0, C + d1 * FASCIA_R0
        mb.quad("fascia", [(i0.x, i0.y, DRUM_TOP), (i1.x, i1.y, DRUM_TOP), (b1.x, b1.y, DRUM_TOP),
                           (b0.x, b0.y, DRUM_TOP)][::-1])
        t0, t1 = C + d0 * (FASCIA_R1 + 0.06), C + d1 * (FASCIA_R1 + 0.06)
        r0, r1 = C + d0 * DOME_RIM_R, C + d1 * DOME_RIM_R
        mb.quad("fascia", [(t0.x, t0.y, FASCIA_TOP), (t1.x, t1.y, FASCIA_TOP), (r1.x, r1.y, FASCIA_TOP + 0.02),
                           (r0.x, r0.y, FASCIA_TOP + 0.02)])
        # gutter lip from the cap down to the dome rim
        mb.quad("fascia", [(r0.x, r0.y, FASCIA_TOP + 0.02), (r1.x, r1.y, FASCIA_TOP + 0.02),
                           (r1.x, r1.y, DOME_PROFILE[-1][1]), (r0.x, r0.y, DOME_PROFILE[-1][1])])

    def zr(r):
        P = DOME_PROFILE
        if r >= P[-1][0]:
            return P[-1][1]
        for (ra, za), (rb, zb) in zip(P, P[1:]):
            if ra <= r <= rb:
                return za + (zb - za) * (r - ra) / (rb - ra)
        return P[0][1]

    rings = sorted({DOME_RIM_R, *[p[0] for p in DOME_PROFILE if p[0] > CAP_R], CAP_R,
                    *[DOME_RIM_R - 1.0 * j for j in range(int(DOME_RIM_R - CAP_R))]}, reverse=True)
    rings = [r for r in rings if r >= CAP_R]
    for i in range(N):
        a0 = 2 * math.pi * i / N
        a1 = 2 * math.pi * (i + 1) / N
        d0 = Vector((math.cos(a0), math.sin(a0)))
        d1 = Vector((math.cos(a1), math.sin(a1)))
        for ra, rb2 in zip(rings, rings[1:]):
            p00, p01 = C + d0 * ra, C + d1 * ra
            p10, p11 = C + d0 * rb2, C + d1 * rb2
            mb.quad("copper", [(p00.x, p00.y, zr(ra)), (p01.x, p01.y, zr(ra)), (p11.x, p11.y, zr(rb2)),
                               (p10.x, p10.y, zr(rb2))])
    # standing-seam ribs between concentric seams (orthophoto ring radii; ~0.9-1.0 m rib pitch at the rim, 2025 aerial)
    zones = [(DOME_RIM_R - 0.1, 39.0, 288), (39.0, 29.0, 288), (29.0, 19.5, 144), (19.5, 10.5, 72), (10.5, CAP_R + 0.3, 36)]
    for r_out, r_in, cnt in zones:
        steps = max(3, int((r_out - r_in) / 2.0))
        for k in range(cnt):
            a = 2 * math.pi * (k + 0.5) / cnt
            d = Vector((math.cos(a), math.sin(a)))
            tn = Vector((-d.y, d.x)) * 0.04
            for s in range(steps):
                ra = r_out - (r_out - r_in) * s / steps
                rb2 = r_out - (r_out - r_in) * (s + 1) / steps
                pa, pb = C + d * ra, C + d * rb2
                za, zb = zr(ra) + 0.005, zr(rb2) + 0.005
                h = 0.08
                mb.quad("seam", [(pa.x - tn.x, pa.y - tn.y, za + h), (pa.x + tn.x, pa.y + tn.y, za + h),
                                 (pb.x + tn.x, pb.y + tn.y, zb + h), (pb.x - tn.x, pb.y - tn.y, zb + h)])
                mb.quad("seam", [(pa.x - tn.x, pa.y - tn.y, za), (pa.x - tn.x, pa.y - tn.y, za + h),
                                 (pb.x - tn.x, pb.y - tn.y, zb + h), (pb.x - tn.x, pb.y - tn.y, zb)])
                mb.quad("seam", [(pa.x + tn.x, pa.y + tn.y, za + h), (pa.x + tn.x, pa.y + tn.y, za),
                                 (pb.x + tn.x, pb.y + tn.y, zb), (pb.x + tn.x, pb.y + tn.y, zb + h)])
        pts = arc_pts(r_in, 0, 360, 1.5)
        for A, B in zip(pts, pts[1:]):
            z = zr(r_in)
            mb.quad("seam", [(A.x, A.y, z + 0.01), (B.x, B.y, z + 0.01), (B.x, B.y, z + 0.14), (A.x, A.y, z + 0.14)])
    # central cap / vent (NDHM 26.0 m at r < 2 m)
    zt = zr(CAP_R)
    capr = [(CAP_R, zt), (CAP_R, CAP_TOP - 0.25), (CAP_R * 0.7, CAP_TOP), (0.0, CAP_TOP)]
    for i in range(48):
        a0 = 2 * math.pi * i / 48
        a1 = 2 * math.pi * (i + 1) / 48
        d0 = Vector((math.cos(a0), math.sin(a0)))
        d1 = Vector((math.cos(a1), math.sin(a1)))
        for (ra, za), (rb2, zb) in zip(capr, capr[1:]):
            mb.quad("fascia", [((C + d0 * ra).x, (C + d0 * ra).y, za), ((C + d1 * ra).x, (C + d1 * ra).y, za),
                               ((C + d1 * rb2).x, (C + d1 * rb2).y, zb), ((C + d0 * rb2).x, (C + d0 * rb2).y, zb)])


# ---------------------------------------------------------------- concourse ring, south blocks, west annex
RING_R = 55.3
RING_A = (137.0, 262.0)


def low_wall_bands(mb, A, B, h=LOW_H, ext=0.02):
    band(mb, A, B, 0.0, 0.9, proj=0.10, ext=ext)              # limestone water table
    band(mb, A, B, 3.2, 3.33, proj=0.05, ext=ext)             # thin stripe
    band(mb, A, B, 4.0, 4.12, proj=0.05, ext=ext)             # thin stripe
    band(mb, A, B, h - 0.8, h, proj=0.10, ext=ext)            # wide limestone coping course


ANNEX = [(-56.4, -17.5), (-48.0, -15.7), (-51.0, 17.0), (-63.7, 23.6)]


def build_concourse_ring(mb, M, root):
    a_start, a_end = RING_A
    step = 2.0
    angs = [a_start + i * step for i in range(int((a_end - a_start) / step) + 1)]
    outer = [pol(a, RING_R) for a in angs]
    for a, A, B in zip(angs, outer, outer[1:]):
        am = a + step / 2
        L = (B - A).length
        mid = (A + B) / 2
        if point_in_poly((mid.x, mid.y), ANNEX):
            continue
        if SW_ENT[0] <= am <= SW_ENT[1]:
            # recessed entrance: sign band above the canopy soffit only
            wall(mb, A, B, 3.3, LOW_H, 0.4)
            band(mb, A, B, LOW_H - 0.8, LOW_H, proj=0.10, ext=0.02)
            continue
        ops = []
        if 256.0 <= am <= 258.5:
            ops = [(0.4, L - 0.4, 0.0, 2.9, "door", 1)]
        wall(mb, A, B, 0.0, LOW_H, 0.4, ops)
        low_wall_bands(mb, A, B)
    # ring roof (lighter membrane, orthophoto) inside the parapet
    inner = [pol(a, DRUM_R - 0.3) for a in angs]
    for i in range(len(angs) - 1):
        o0, o1, i0, i1 = pol(angs[i], RING_R - 0.35), pol(angs[i + 1], RING_R - 0.35), inner[i], inner[i + 1]
        mb.quad("roof_g", [(i0.x, i0.y, RING_ROOF), (i1.x, i1.y, RING_ROOF), (o1.x, o1.y, RING_ROOF),
                           (o0.x, o0.y, RING_ROOF)])
    # north-west end wall of the ring (ring stops at ~137 deg; LiDAR)
    a = a_start
    d = Vector((math.cos(math.radians(a)), math.sin(math.radians(a))))
    tn = Vector((-d.y, d.x))
    mb.box("brick", pol(a, DRUM_R), d, tn, RING_R - DRUM_R, 0.4, 0.0, LOW_H)
    mb.box("lime", pol(a, DRUM_R) - tn * 0.1, d, tn, RING_R - DRUM_R + 0.1, 0.5, 0.0, 0.9)
    mb.box("lime", pol(a, DRUM_R) - tn * 0.1, d, tn, RING_R - DRUM_R + 0.1, 0.5, LOW_H - 0.8, LOW_H)
    # SW entrance: canopy soffit, piers, recessed glazed doors near the drum line
    a0, a1 = SW_ENT
    can_o = arc_pts(RING_R, a0, a1, 1.0)
    can_i = arc_pts(DRUM_R + 0.6, a0, a1, 1.0)
    for i in range(len(can_o) - 1):
        o0, o1, i0, i1 = can_o[i], can_o[i + 1], can_i[i], can_i[i + 1]
        mb.quad("lime", [(i0.x, i0.y, 3.3), (o0.x, o0.y, 3.3), (o1.x, o1.y, 3.3), (i1.x, i1.y, 3.3)])
        mb.quad("roof_g", [(i0.x, i0.y, 4.0), (i1.x, i1.y, 4.0), (o1.x, o1.y, 4.0), (o0.x, o0.y, 4.0)])
    door_line = arc_pts(DRUM_R + 0.6, a0 + 0.5, a1 - 0.5, 1.0)
    for A, B in zip(door_line, door_line[1:]):
        L = (B - A).length
        wall(mb, A, B, 0.0, 3.3, 0.3, [(0.05, L - 0.05, 0.0, 3.0, "door", 1)], frame="frame")
    for a in (a0 + 0.6, a0 + 9.0, a0 + 14.5, a0 + 20.0, a1 - 0.6):
        d = Vector((math.cos(math.radians(a)), math.sin(math.radians(a))))
        tn = Vector((-d.y, d.x))
        mb.box("brick", C + d * (RING_R - 1.5) - tn * 0.7, tn, d, 1.4, 1.4, 0.0, 3.3)
        mb.box("lime", C + d * (RING_R - 1.55) - tn * 0.75, tn, d, 1.5, 1.5, 0.0, 0.9)
        mb.box("lime", C + d * (RING_R - 1.55) - tn * 0.75, tn, d, 1.5, 1.5, 2.6, 2.75)
    for a in (a0, a1):
        d = Vector((math.cos(math.radians(a)), math.sin(math.radians(a))))
        tn = Vector((-d.y, d.x))
        mb.box("brick", C + d * DRUM_R - tn * 0.2, tn, d, 0.4, RING_R - DRUM_R, 0.0, 3.3)
    sw = pol(221.0, RING_R + 0.12)
    nrm = Vector((math.cos(math.radians(221)), math.sin(math.radians(221))))
    letters("MACKEY ARENA", (sw.x, sw.y, 4.0), facing_rot(nrm), 0.5, "letter_m", M, root, depth=0.06,
            name="MACK_SP_SW_Entrance_Text")
    letters("MORGAN & KATE BURKE SOUTHWEST ENTRANCE", (sw.x, sw.y, 3.58), facing_rot(nrm), 0.2, "letter_m", M,
            root, depth=0.04, name="MACK_SP_SW_Entrance_Subtext")
    # north and north-west entrance lettering on the drum canopies
    for ang, sub, nm in ((114.0, "NORTH ENTRANCE", "N"),):
        p = pol(ang, DRUM_R + 1.32)
        nrm = Vector((math.cos(math.radians(ang)), math.sin(math.radians(ang))))
        letters("MACKEY ARENA", (p.x, p.y, 4.05), facing_rot(nrm), 0.42, "letter_m", M, root, depth=0.05,
                name=f"MACK_SP_{nm}_Entrance_Text")
        letters(sub, (p.x, p.y, 3.75), facing_rot(nrm), 0.17, "letter_m", M, root, depth=0.03,
                name=f"MACK_SP_{nm}_Entrance_Subtext")


def poly_walls(mb, pts, edges, h, roof_z, roof_mat="roof_g", bands=True, openings=None):
    for i in edges:
        A, B = Vector(pts[i]), Vector(pts[(i + 1) % len(pts)])
        ops = (openings or {}).get(i, [])
        wall(mb, A, B, 0.0, h, 0.4, ops)
        if bands:
            low_wall_bands(mb, A, B, h=h)
    flat_poly(mb, roof_mat, pts, roof_z)


def build_south_blocks(mb):
    """South concourse block (A, 4.4 m roof) and the 5.5 m block (B) between it and the SE wing (LiDAR)."""
    A_out = [pol(262.0, RING_R), Vector((-7.7, -75.0)), Vector((15.0, -75.0)), Vector((16.5, -71.0)),
             Vector((27.0, -70.0)), Vector((31.0, -66.5)), Vector((33.0, -58.5))]
    ang_end = math.degrees(math.atan2(-58.5 - C.y, 33.0 - C.x)) % 360
    A_in = arc_pts(DRUM_R - 0.3, ang_end, 262.0, 2.0)
    polyA = A_out + A_in
    L1 = (A_out[2] - A_out[1]).length
    opsA = {1: [(L1 * 0.30, L1 * 0.30 + 3.6, 0.0, 3.0, "door", 2), (L1 * 0.62, L1 * 0.62 + 1.8, 0.0, 2.9, "door", 1)]}
    poly_walls(mb, polyA, range(0, 6), LOW_H, RING_ROOF, openings=opsA)
    mb.box("unit", (-1.5, -73.5), (1, 0), (0, 1), 2.6, 3.2, RING_ROOF, 6.5)
    # block B
    def Lw(tt):
        return Vector((39.3, -42.7)) + (Vector((61.8, -71.0)) - Vector((39.3, -42.7))) * tt
    a_w = math.degrees(math.atan2(Lw(0.06).y - C.y, Lw(0.06).x - C.x)) % 360
    B_pts = [Vector((33.0, -58.5)), Vector((38.5, -66.0)), Vector((47.0, -69.5)), Lw(0.80), Lw(0.06)] + \
        arc_pts(DRUM_R - 0.3, a_w, ang_end, 2.0)
    poly_walls(mb, B_pts, range(0, 3), 5.9, 5.5, openings={1: [(2.0, 3.8, 0.0, 2.9, "door", 1)]})


def build_west_annex(mb):
    """One-storey annex west of the drum (LiDAR 6.6-7.1 m roof); west facade from the 2025 west aerial."""
    P = [Vector(p) for p in ANNEX]
    H = ANNEX_H
    for i in range(4):
        A, B = P[i], P[(i + 1) % 4]
        L = (B - A).length
        ops = []
        if i == 3:  # west face (north corner -> south corner): window groups and the entrance door
            def grp(u0, n, w=1.65, g=0.45, z0=0.9, z1=5.4):
                return [(u0 + j * (w + g), u0 + j * (w + g) + w, z0, z1, "win", 1, 3) for j in range(n)]
            ops = grp(2.4, 4) + grp(13.6, 4) + grp(24.6, 2) + grp(29.6, 2, z0=3.2) + \
                [(34.6, 36.6, 0.0, 3.0, "door", 1)]
        elif i == 0:  # south face onto the plaza: one window group (estimated)
            ops = [(1.6 + j * 2.1, 3.25 + j * 2.1, 0.9, 5.4, "win", 1, 3) for j in range(3)]
        wall(mb, A, B, 0.0, H - 0.4, 0.4, ops)
        band(mb, A, B, 0.0, 0.9, proj=0.10, ext=0.02)
        band(mb, A, B, 5.75, 5.9, proj=0.05, ext=0.02)
        band(mb, A, B, H - 1.15, H - 0.4, proj=0.08, ext=0.02)
    flat_poly(mb, "roof_w", [(p.x, p.y) for p in P], H - 0.9)
    # thin white roof slab overhanging the west and north faces (pointed north-west corner, aerial)
    slab = [P[0] + Vector((-1.0, -0.2)), P[1] + Vector((0.0, -0.2)), P[2] + Vector((0.4, 0.9)), P[3] + Vector((-1.6, 1.2))]
    flat_poly(mb, "roof_w", [(p.x, p.y) for p in slab], H)
    flat_poly(mb, "roof_w", [(p.x, p.y) for p in slab], H - 0.4, flip=True)
    for i in range(4):
        A, B = slab[i], slab[(i + 1) % 4]
        mb.quad("roof_w", [(A.x, A.y, H - 0.4), (B.x, B.y, H - 0.4), (B.x, B.y, H), (A.x, A.y, H)])


# ---------------------------------------------------------------- east / north wing
ENT_Y = (-31.5, 1.5)        # curved east-entrance front between the SE and E_entry_N towers
ENT_X_END, ENT_X_APEX = 64.0, 66.0
CAP_C, CAP_RAD = Vector((47.5, 129.5)), 9.5
# curved lobby (r3): tangent to the N-S face x = LOBBY_X at y = LOBBY_Y0, radius LOBBY_RAD, turning 40 deg to
# the NE, then a short straight glazed return meeting the 12.5-deg SDAC facade line through (26, 84)
LOBBY_X, LOBBY_Y0, LOBBY_RAD, LOBBY_TURN = 17.3, 59.0, 20.0, 40.0


def lobby_pts(n=14):
    """Lobby outline in CCW (southbound) order: facade corner -> arc end -> ... -> (LOBBY_X, LOBBY_Y0)."""
    cx, cy = LOBBY_X + LOBBY_RAD, LOBBY_Y0
    th = math.radians(LOBBY_TURN)
    end = Vector((cx - LOBBY_RAD * math.cos(th), cy + LOBBY_RAD * math.sin(th)))
    # straight at heading LOBBY_TURN from the arc end to the 12.5-deg facade line through (26, 84)
    d1 = Vector((math.sin(th), math.cos(th)))
    d2 = Vector((math.sin(math.radians(12.5)), math.cos(math.radians(12.5))))
    p2 = Vector((26.0, 84.0))
    # end + u d1 = p2 + v d2
    det = d1.x * (-d2.y) - d1.y * (-d2.x)
    rx, ry = p2.x - end.x, p2.y - end.y
    u = (rx * (-d2.y) - ry * (-d2.x)) / det
    corner = end + d1 * u
    pts = [corner]
    for i in range(n, -1, -1):
        a = th * i / n
        pts.append(Vector((cx - LOBBY_RAD * math.cos(a), cy + LOBBY_RAD * math.sin(a))))
    return pts[:-1]  # (LOBBY_X, LOBBY_Y0) is added by the caller with the next edge's tag

TOWERS = [  # penthouse / glass P towers (LiDAR boxes >12.3 m); x1 is the wing face at the tower
    {"name": "SE", "x0": 49.5, "y0": -42.0, "y1": -32.5, "top": 14.4},
    {"name": "E_entry_N", "x0": 46.5, "y0": 2.5, "y1": 14.5, "top": 14.3},
    {"name": "E_mid", "x0": 39.0, "y0": 48.0, "y1": 60.5, "top": 14.0},
    {"name": "N", "x0": 42.5, "y0": 94.0, "y1": 106.0, "top": 13.7},
]


def ent_arc_pts(n=24):
    y0, y1 = ENT_Y
    half = (y1 - y0) / 2
    s = ENT_X_APEX - ENT_X_END
    R = (half * half + s * s) / (2 * s)
    cx, cy = ENT_X_APEX - R, (y0 + y1) / 2
    a0 = math.atan2(y0 - cy, ENT_X_END - cx)
    a1 = math.atan2(y1 - cy, ENT_X_END - cx)
    return [Vector((cx + R * math.cos(a0 + (a1 - a0) * i / n), cy + R * math.sin(a0 + (a1 - a0) * i / n)))
            for i in range(n + 1)], Vector((cx, cy)), R


def wing_outline():
    """CCW outline as (point, tag of the edge starting there). Lean-free LiDAR trace (NDHM edges)."""
    E = []

    def add(p, tag):
        E.append((Vector(p), tag))
    add((61.8, -71.0), "se_tip")
    add((66.3, -62.0), "se_east")
    add((66.5, -42.0), "tower")
    add((66.5, -32.5), "plain")
    ent, _, _ = ent_arc_pts()
    for p in ent[:-1]:
        add(p, "entrance")
    add(ent[-1], "plain")
    add((63.6, 2.5), "tower")
    add((63.5, 14.5), "east")
    add((63.5, 27.0), "east")
    add((62.3, 30.0), "east")
    add((62.3, 40.0), "east")
    add((62.3, 48.0), "tower")
    add((61.0, 60.5), "east")
    add((61.0, 75.0), "east")
    add((61.0, 90.0), "east")
    add((59.5, 93.0), "east")
    add((59.5, 94.0), "tower")
    add((59.5, 106.0), "east")
    add((59.5, 120.0), "east")
    add((57.0, 129.5), "cap")
    for i in range(1, 12):
        a = math.pi * i / 12
        add(CAP_C + Vector((math.cos(a), math.sin(a))) * CAP_RAD, "cap")
    add((CAP_C.x - CAP_RAD, CAP_C.y), "sdac_west")
    for p in [(35.0, 121.0), (32.0, 108.0), (29.75, 99.0), (28.25, 93.0), (26.0, 84.0)]:
        add(p, "sdac_west")
    # r3: the two-storey curved glass lobby is the convex plan bend where the SDAC west facade turns from
    # NNE (12.5 deg) to due north (2023 orthophoto roof edge, relief-corrected; hntb_Purdue-2 shows it facing
    # the plaza between the SDAC brick facade and the short brick return to the drum). r2 had placed it in
    # the notch against the drum, where it is invisible from the plaza.
    for p in lobby_pts():
        add(p, "lobby")
    add((LOBBY_X, LOBBY_Y0), "sdac_sw")
    add((LOBBY_X, 31.3), "hidden")
    for a in range(62, -37, -4):
        add(pol(a, 48.6), "hidden")
    add(pol(-36.0, 48.6), "se_sw")
    return E


def bays(L, pitch):
    nb = max(1, int(round(L / pitch)))
    w = L / nb
    return [(i * w, (i + 1) * w) for i in range(nb)], w


# vertical zones of the two-storey wing (photo estimates scaled to the LiDAR parapet)
Z_GF = (0.8, 4.1)
Z_B1 = (4.3, 4.9)
Z_UP = (5.6, 8.3)
Z_B2 = (8.75, 8.95)


def wing_bands(mb, A, B, top, base=True):
    if base:
        band(mb, A, B, 0.0, 0.8, proj=0.10, ext=0.02)
    band(mb, A, B, Z_B1[0], Z_B1[1], proj=0.08, ext=0.02)
    band(mb, A, B, Z_B2[0], Z_B2[1], proj=0.05, ext=0.02)
    band(mb, A, B, top - 1.15, top - 1.0, proj=0.05, ext=0.02)
    band(mb, A, B, top - 0.35, top, proj=0.12, ext=0.02)


def facade_east(mb, A, B, top, pitch=8.2, upper="pairs"):
    """East (Northwestern Ave) wing facade: recessed ground-floor storefront arcade between brick piers on
    limestone bases, one row of paired upper windows with limestone heads/sills, banded parapet (drone_05)."""
    Af, t, n, L = seg_frame(A, B)
    inw = -n
    ups = []
    piers = []
    bl, w = bays(L, pitch)
    for (u0, u1) in bl:
        c = (u0 + u1) / 2
        if upper == "pairs" and w > 4.5:
            ups += [(c - 1.75, c - 0.55, Z_UP[0], Z_UP[1], "win", 1, 1), (c + 0.55, c + 1.75, Z_UP[0], Z_UP[1], "win", 1, 1)]
        elif w > 1.6:
            ups += [(c - 0.6, c + 0.6, Z_UP[0], Z_UP[1], "win", 1, 1)]
        piers.append(u0)
    piers.append(L)
    # upper wall (face line) from the arcade head up
    wall(mb, A, B, Z_B1[0], top, 0.45, ups)
    # piers + recessed storefront
    rec = 2.0
    pw = 1.3
    for u in piers:
        a = max(0.0, u - pw / 2)
        b = min(L, u + pw / 2)
        mb.box("brick", Af + t * a, t, inw, b - a, rec, 0.0, Z_B1[0])
        mb.box("lime", Af + t * (a - 0.05) - inw * 0.08, t, inw, b - a + 0.1, rec + 0.08, 0.0, 0.8)
    Rf = Af + inw * rec
    sops = []
    for u0, u1 in zip(piers, piers[1:]):
        a, b = u0 + pw / 2, u1 - pw / 2
        if b - a > 0.8:
            sops.append((a, b, 0.5, 3.7, "win", max(1, int((b - a) / 1.6)), 1))
    wall(mb, Rf, Rf + t * L, 0.0, Z_B1[0], 0.3, sops, frame="frame")
    mb.box("lime", Af, t, inw, L, rec, Z_B1[0] - 0.12, Z_B1[0])          # arcade soffit
    for (o0, o1, za, zb, *_r) in ups:                                    # limestone sills / heads
        mb.box("lime", Af + t * (o0 - 0.1) - inw * 0.06, t, inw, o1 - o0 + 0.2, 0.2, za - 0.18, za)
        mb.box("lime", Af + t * (o0 - 0.1) - inw * 0.06, t, inw, o1 - o0 + 0.2, 0.2, zb, zb + 0.3)
    band(mb, A, B, Z_B1[0], Z_B1[1], proj=0.08, ext=0.02)
    band(mb, A, B, Z_B2[0], Z_B2[1], proj=0.05, ext=0.02)
    band(mb, A, B, top - 1.15, top - 1.0, proj=0.05, ext=0.02)
    band(mb, A, B, top - 0.35, top, proj=0.12, ext=0.02)
    return ups


def facade_sdac_west(mb, A, B, top):
    """SDAC west (Weist Plaza) facade: flush storefront ground floor, ONE tier of tall upper windows
    alternating wide gridded units and narrow pairs, banded parapet (hntb_Purdue-2)."""
    Af, t, n, L = seg_frame(A, B)
    ops = []
    bl, w = bays(L, 3.7)
    for i, (u0, u1) in enumerate(bl):
        c = (u0 + u1) / 2
        if w < 2.0:
            continue
        ops.append((c - w / 2 + 0.45, c + w / 2 - 0.45, Z_GF[0] - 0.2, 4.0, "win", 2, 1))
        if i % 3 == 2:
            ops += [(c - 0.85, c - 0.15, 5.4, 8.6, "win", 0, 2), (c + 0.15, c + 0.85, 5.4, 8.6, "win", 0, 2)]
        else:
            ops.append((c - 1.15, c + 1.15, 5.4, 8.6, "win", 2, 2))
    wall(mb, A, B, 0.0, top, 0.45, ops)
    band(mb, A, B, 0.0, 0.6, proj=0.10, ext=0.02)
    band(mb, A, B, 4.35, 4.8, proj=0.08, ext=0.02)
    band(mb, A, B, top - 1.15, top - 1.0, proj=0.05, ext=0.02)
    band(mb, A, B, top - 0.35, top, proj=0.12, ext=0.02)


def inlays(mb, A, B, us, top):
    """Small limestone accent inlays in the attic band above openings (2016_01)."""
    Af, t, n, L = seg_frame(A, B)
    for u in us:
        for du in (-0.28, 0.28):
            mb.box("lime", Af + t * (u + du - 0.07) + n * 0.03, t, -n, 0.14, 0.08, top - 2.0, top - 1.4)


def facade_lobby(mb, A, B, top):
    """One chord of the convex two-storey curtain-wall lobby (hntb_Purdue-2): clear glazing on a limestone
    curb, aluminium mullions ~1 m apart, door-head and sill transoms, a solid metal floor-slab band at the
    second floor, two upper transoms, and a projecting flat roof with a deep light metal fascia."""
    Af, t, n, L = seg_frame(A, B)
    inw = -n
    zt = top - 1.3
    mb.box("glass_lit", Af + inw * 0.12, t, inw, L, 0.04, 0.3, zt)
    mb.box("lime", Af - n * 0.05, t, inw, L, 0.45, 0.0, 0.3)
    k = max(1, int(round(L / 1.05)))
    for j in range(k):
        mb.box("frame", Af + t * (L * j / k - 0.04) + n * 0.02, t, inw, 0.08, 0.16, 0.3, zt)
    for zz in (0.3, 2.65, 6.4, 7.8, zt - 0.08):
        mb.box("frame", Af + n * 0.02, t, inw, L, 0.14, zz, zz + 0.08)
    mb.box("metal", Af + n * 0.06, t, inw, L, 0.2, Z_B1[0], Z_B1[1] + 0.1)      # second-floor slab band
    mb.box("roof_w", Af + n * 0.6, t, inw, L, 0.6 + 0.3, zt, zt + 0.25)          # projecting roof slab
    mb.box("frame", Af + n * 0.62, t, inw, L, 0.12, zt, top - 0.2)               # deep metal fascia


def build_wing(mb, M, root):
    E = wing_outline()
    pts = [p for p, _ in E]
    nE = len(E)
    for i in range(nE):
        A, tag = E[i]
        B = E[(i + 1) % nE][0]
        L = (B - A).length
        if L < 0.05 or tag in ("hidden", "tower", "entrance"):
            continue
        mid = (A + B) / 2
        top, roof = wing_level(mid.y)
        if tag == "east":
            facade_east(mb, A, B, top)
        elif tag == "sdac_west":
            facade_sdac_west(mb, A, B, top)
        elif tag == "cap":
            # rounded SDAC north end: not seen in any daylight photo -> SDAC vocabulary continued (estimated)
            ops = [(0.3, L - 0.3, Z_GF[0] - 0.2, 4.0, "win", 1, 1), (L / 2 - 0.6, L / 2 + 0.6, 5.4, 8.6, "win", 0, 2)]
            wall(mb, A, B, 0.0, top, 0.45, ops)
            wing_bands(mb, A, B, top)
        elif tag == "lobby":
            facade_lobby(mb, A, B, top)
        elif tag == "sdac_sw":
            # short west-facing brick return between the lobby and the drum, seen only at a grazing angle in
            # hntb_Purdue-2: banded brick, a few narrow windows, recessed full-height glazed slot at the drum
            # end (window count/positions estimated)
            Af, t, n, _ = seg_frame(A, B)
            ops = []
            for u in (4.0, 4.9, 11.0, 11.9):
                ops += [(u, u + 0.5, 1.0, 3.9, "win", 0), (u, u + 0.5, 5.6, 8.4, "win", 0)]
            ops.append((L - 3.6, L - 1.2, 0.0, top - 1.3, "win", 1, 3))
            wall(mb, A, B, 0.0, top, 0.45, ops, inset=0.4)
            wing_bands(mb, A, Af + t * (L - 3.7), top)
        elif tag == "se_tip":
            # SE tip: raised corner mass with a glazed corner bay in a grey metal surround on both floors,
            # then four aligned narrow slit windows per floor (2016_01)
            top2 = top + 0.6
            ops = [(0.5, 2.9, 0.9, 4.0, "win", 1, 1), (0.5, 2.9, 5.5, 8.4, "win", 1, 1)]
            slits = [4.6 + j * 1.25 for j in range(4)]
            for u in slits:
                ops += [(u, u + 0.42, 0.9, 3.9, "win", 0), (u + 0.0, u + 0.42, 5.4, 8.4, "win", 0)]
            Af, t, n, _ = seg_frame(A, B)
            wall(mb, A, B, 0.0, top, 0.45, ops)
            mb.box("brick", Af, t, -n, 3.4, 0.45, top, top2)
            band(mb, Af, Af + t * 3.4, top2 - 0.35, top2, proj=0.12, ext=0.02)
            for (za, zb) in ((0.9, 4.0), (5.5, 8.4)):
                mb.box("metal", Af + t * 0.25 + n * 0.22, t, -n, 0.3, 0.3, za - 0.25, zb + 0.25)
                mb.box("metal", Af + t * 2.85 + n * 0.22, t, -n, 0.3, 0.3, za - 0.25, zb + 0.25)
                mb.box("metal", Af + t * 0.25 + n * 0.22, t, -n, 2.9, 0.3, za - 0.25, za)
                mb.box("metal", Af + t * 0.25 + n * 0.22, t, -n, 2.9, 0.3, zb, zb + 0.25)
            mb.box("metal", Af + t * 0.25 + n * 0.1, t, -n, 2.9, 0.2, 4.0, 5.5)
            wing_bands(mb, A, B, top)
            inlays(mb, A, B, [u + 0.21 for u in slits], top)
        elif tag == "se_east":
            # first part: brick + inlays; rest: projecting second floor over a recessed ground-floor arcade
            Af, t, n, _ = seg_frame(A, B)
            inw = -n
            a_start = 3.0
            ups = [(a_start + 2.0 + j * 4.6 - 0.65, a_start + 2.0 + j * 4.6 + 0.65, Z_UP[0], Z_UP[1], "win", 1, 1)
                   for j in range(4) if a_start + 2.0 + j * 4.6 + 0.65 < L - 0.5]
            wall(mb, A, B, Z_B1[0], top, 0.45, ups)
            wall(mb, A, Af + t * a_start, 0.0, Z_B1[0], 0.45, [])
            rec = 2.4
            pier_us = [a_start + j * 4.6 for j in range(5) if a_start + j * 4.6 < L - 0.6] + [L - 0.6]
            for u in pier_us:
                mb.box("brick", Af + t * u, t, inw, 0.6, 0.6, 0.0, Z_B1[0])
                mb.box("lime", Af + t * (u - 0.05) - inw * 0.06, t, inw, 0.7, 0.72, 0.0, 0.7)
            Rf = Af + inw * rec
            wall(mb, Rf + t * a_start, Rf + t * L, 0.0, Z_B1[0], 0.3,
                 [(0.4 + j * 3.2, 0.4 + j * 3.2 + 2.6, 0.5, 3.7, "win", 2, 1) for j in range(int((L - a_start - 0.6) / 3.2))],
                 frame="frame")
            mb.box("lime", Af + t * a_start, t, inw, L - a_start, rec, Z_B1[0] - 0.15, Z_B1[0])
            for (o0, o1, za, zb, *_r) in ups:
                mb.box("lime", Af + t * (o0 - 0.1) - inw * 0.06, t, inw, o1 - o0 + 0.2, 0.2, za - 0.18, za)
            wing_bands(mb, A, B, top, base=False)
            band(mb, A, Af + t * a_start, 0.0, 0.8, proj=0.10, ext=0.02)
            inlays(mb, A, B, [(o[0] + o[1]) / 2 for o in ups], top)
        elif tag == "se_sw":
            # SW face of the SE wing above block B (lower tier hidden by block B except near the tip)
            ops = []
            bl, w = bays(L, 4.6)
            for (u0, u1) in bl:
                c = (u0 + u1) / 2
                ops.append((c - 0.65, c + 0.65, 6.1, Z_UP[1], "win", 1, 1))
                if u0 > 0.82 * L:
                    ops.append((c - 0.65, c + 0.65, 1.0, 3.9, "win", 1, 1))
            wall(mb, A, B, 0.0, top, 0.45, ops)
            wing_bands(mb, A, B, top)
            inlays(mb, A, B, [(o[0] + o[1]) / 2 for o in ops if o[2] > 5], top)
        else:  # plain brick returns
            wall(mb, A, B, 0.0, top, 0.45, [])
            wing_bands(mb, A, B, top)
    # roofs by level (white membrane) + step walls between levels
    for y0, y1, top, roof in WING_LEVELS:
        piece = clip_y(pts, y0, y1)
        if len(piece) >= 3:
            flat_poly(mb, "roof_w", [(p.x, p.y) for p in piece], roof)
    for yb, (hi, lo) in ((40.0, (10.1, 9.6)), (93.0, (9.6, 8.9))):
        xs = []
        for i in range(len(pts)):
            P, Q = pts[i], pts[(i + 1) % len(pts)]
            if (P.y - yb) * (Q.y - yb) < 0:
                xs.append(P.x + (Q.x - P.x) * (yb - P.y) / (Q.y - P.y))
        if len(xs) >= 2:
            mb.box("brick", (min(xs), yb - 0.15), (1, 0), (0, 1), max(xs) - min(xs), 0.3, lo, hi + 0.3)
    build_east_entrance(mb, M, root)
    build_towers(mb, M, root)
    # rooftop units seen in the orthophoto
    for (x, y, sx, sy) in [(50.5, -27.0, 2.6, 3.6), (50.8, -15.0, 2.4, 3.2), (35.0, 84.0, 3.4, 2.4), (50.0, 77.0, 2.4, 2.4)]:
        _, roof = wing_level(y)
        mb.box("unit", (x, y), (1, 0), (0, 1), sx, sy, roof, roof + 1.2)
    # skylight units on the roof next to the drum (drone_05)
    for a in (2.0, 9.0, 26.0, 33.0):
        p = pol(a, 50.4)
        d = Vector((math.cos(math.radians(a)), math.sin(math.radians(a))))
        tn = Vector((-d.y, d.x))
        mb.box("frame", p - tn * 1.6, tn, d, 3.2, 1.6, 10.1, 10.7)


def build_east_entrance(mb, M, root):
    """Convex curved east-entrance front on Northwestern Ave (2025 state, exponent_drone_2025_05 close crop).
    South -> north along the curve: end pier (KEADY COURT banner) | '44' wall segment over a portal | blade pier
    (vertical MACKEY ARENA banner) | central segment with the curved MACKEY ARENA banner over two portals split
    by a pier, EAST ENTRANCE lettering on the portal-head band | blade pier (MACKEY ARENA) | '59' segment over
    a portal | end pier (KEADY COURT). Four deep portals lead to recessed glazed doors. Segment widths are
    photo proportions scaled to the 33.3 m LiDAR/orthophoto arc (estimates, +-0.5 m)."""
    top, _ = wing_level(-15.0)
    arc, cc, R = ent_arc_pts(24)
    a_start = math.atan2(arc[0].y - cc.y, arc[0].x - cc.x)
    S = R * (math.atan2(arc[-1].y - cc.y, arc[-1].x - cc.x) - a_start)

    def P(s, off=0.0):
        a = a_start + s / R
        return Vector((cc.x + (R + off) * math.cos(a), cc.y + (R + off) * math.sin(a)))

    def nrm(s):
        a = a_start + s / R
        return Vector((math.cos(a), math.sin(a)))

    def arc_box(mat, s0, s1, z0, z1, off, depth, step=1.0):
        """Curved slab between radii R+off (outer) and R+off-depth, s0..s1, z0..z1 (chord boxes)."""
        k = max(1, int(math.ceil((s1 - s0) / step)))
        for i in range(k):
            a, b = s0 + (s1 - s0) * i / k, s0 + (s1 - s0) * (i + 1) / k
            Af, t, n, L = seg_frame(P(a, off), P(b, off))
            mb.box(mat, Af, t, -n, L, depth, z0, z1)

    PH = 4.1                     # portal head
    BAN = (5.05, 10.0)           # banner band
    xb = 58.5                    # recessed door wall
    piers = [(0.0, 2.2, "end"), (8.2, 9.4, "blade"), (16.15, 17.25, "mid"), (23.95, 25.15, "blade"),
             (31.1, S, "end")]
    portals = [(2.2, 8.2), (9.4, 16.15), (17.25, 23.95), (25.15, 31.1)]
    # upper wall over the whole curve (portal head to parapet)
    arc_box("brick", 0.0, S, PH, top, 0.0, 0.45)
    arc_box("lime", 0.0, S, top - 0.35, top, 0.12, 0.6)                 # coping
    arc_box("lime", 0.0, S, PH, PH + 0.3, 0.1, 0.55)                    # portal-head band
    arc_box("lime", 0.0, S, BAN[0] - 0.35, BAN[0] - 0.2, 0.06, 0.5)     # thin stripe under the banners
    # piers: brick from the door wall to 0.3-0.4 m proud of the face; end and blade piers full height
    for (s0, s1, kind) in piers:
        proj = 0.4 if kind == "end" else 0.3
        zt = top if kind in ("end", "blade") else PH
        arc_box("brick", s0, s1, 0.0, zt if kind != "mid" else PH, proj, proj + 0.01, step=0.6)
        k = max(1, int(math.ceil((s1 - s0) / 0.6)))
        for i in range(k):                                              # pier body back to the door wall
            a, b = s0 + (s1 - s0) * i / k, s0 + (s1 - s0) * (i + 1) / k
            pa, pb = P(a), P(b)
            x1 = min(pa.x, pb.x)
            mb.box("brick", (xb, pa.y), (1, 0), (0, 1), x1 - xb, pb.y - pa.y, 0.0, PH)
        arc_box("lime", s0 - 0.05, s1 + 0.05, 0.0, 0.8, proj + 0.06, proj + 0.1, step=0.6)
        arc_box("lime", s0 - 0.05, s1 + 0.05, 2.9, 3.05, proj + 0.04, proj + 0.1, step=0.6)
        if kind in ("end", "blade"):
            for zz in (PH + 0.0, 7.3):
                arc_box("lime", s0 - 0.03, s1 + 0.03, zz, zz + 0.15, proj + 0.04, proj + 0.1, step=0.6)
    # portals: soffit, paving, recessed glazed door wall
    for (s0, s1) in portals:
        k = max(1, int(math.ceil((s1 - s0) / 0.8)))
        for i in range(k):
            a, b = s0 + (s1 - s0) * i / k, s0 + (s1 - s0) * (i + 1) / k
            pa, pb = P(a), P(b)
            mb.quad("lime", [(pa.x, pa.y, PH - 0.02), (pb.x, pb.y, PH - 0.02), (xb, pb.y, PH - 0.02),
                             (xb, pa.y, PH - 0.02)])
            mb.quad("paving", [(xb, pa.y, 0.03), (xb, pb.y, 0.03), (pb.x, pb.y, 0.03), (pa.x, pa.y, 0.03)])
    y_lo, y_hi = P(0.0).y, P(S).y
    dops = []
    for (s0, s1) in portals:
        u0, u1 = P(s0).y - y_lo + 0.35, P(s1).y - y_lo - 0.35
        dops.append((u0, u1, 0.0, 3.3, "door", max(2, int((u1 - u0) / 1.2))))
    wall(mb, Vector((xb, y_lo)), Vector((xb, y_hi)), 0.0, PH, 0.3, dops, frame="frame")
    # banners flat on the wall: 44 / central MACKEY ARENA / 59
    banners = [(2.5, 7.9), (9.75, 23.6), (25.45, 30.8)]
    for (s0, s1) in banners:
        arc_box("sign", s0, s1, BAN[0], BAN[1], 0.08, 0.1, step=0.8)
    sc = (banners[1][0] + banners[1][1]) / 2
    pc, nc = P(sc, 0.12), nrm(sc)
    letters("MACKEY ARENA", (pc.x, pc.y, 8.45), facing_rot(nc), 1.3, "letter_w", M, root,
            name="MACK_SP_E_Banner_Text")
    letters("HOME OF PURDUE BASKETBALL", (pc.x, pc.y, 7.25), facing_rot(nc), 0.42, "letter_w", M, root,
            name="MACK_SP_E_Banner_Subtext")
    letters("P", (pc.x, pc.y, 6.25), facing_rot(nc), 0.75, "gold", M, root, depth=0.05, name="MACK_SP_E_Banner_P")
    for (s0, s1), big, cap in ((banners[0], "44", "BIG TEN\nCHAMPIONSHIPS"), (banners[2], "59", "ALL-AMERICA\nHONORS")):
        sm = (s0 + s1) / 2
        p, nn = P(sm, 0.12), nrm(sm)
        letters(big, (p.x, p.y, 8.15), facing_rot(nn), 2.3, "letter_w", M, root, name=f"MACK_SP_E_Banner_{big}")
        letters(cap, (p.x, p.y, 6.15), facing_rot(nn), 0.32, "letter_w", M, root, name=f"MACK_SP_E_Banner_{big}_cap")
    pe, ne = P(14.6, 0.14), nrm(14.6)
    letters("EAST ENTRANCE", (pe.x, pe.y, PH + 0.15), facing_rot(ne), 0.22, "letter_m", M, root, depth=0.03,
            name="MACK_SP_E_Entrance_Text")
    # vertical banners hung flat on the end and blade piers (read top to bottom)
    for (s0, s1, kind) in piers:
        if kind == "mid":
            continue
        txt = "KEADY COURT" if kind == "end" else "MACKEY ARENA"
        sm = (s0 + s1) / 2
        proj = 0.4 if kind == "end" else 0.3
        arc_box("sign", sm - 0.45, sm + 0.45, 4.75, 10.05, proj + 0.07, 0.07, step=0.9)
        p, nn = P(sm, proj + 0.08), nrm(sm)
        letters(txt, (p.x, p.y, 7.4), facing_rot(nn), 0.42, "letter_w", M, root, depth=0.01,
                name="MACK_SP_E_Blade_Text", rot_y=math.radians(90))


def build_towers(mb, M, root):
    """Glass P towers / penthouses: storefront base between brick piers, glazing, grey horizontal-louvre band
    carrying the Purdue P, glazing above and a glazed penthouse level; penthouse sides in grey metal panels
    (drone_05). Box extents and tops from the LiDAR penthouse blobs."""
    for T in TOWERS:
        y0, y1 = T["y0"], T["y1"]
        top = T["top"]
        wtop, roof = wing_level((y0 + y1) / 2)
        # wing face at the tower (the outline edge tagged "tower" that starts at y0)
        E = wing_outline()
        k = next(i for i, (p, tag) in enumerate(E) if tag == "tower" and abs(p.y - y0) < 0.6)
        A = E[k][0] + Vector((0.3, 0.0))
        B = E[k + 1][0] + Vector((0.3, 0.0))
        xf = max(A.x, B.x)
        x0 = T["x0"]
        Af, t, n, L = seg_frame(A, B)
        inw = -n
        # east face: structure of piers + bands; glazing zones
        wall(mb, A, B, 0.0, top, 0.3,
             [(1.1, L - 1.1, 0.8, 4.1, "win", 3, 1), (0.3, L - 0.3, 4.9, 6.0, "win", 4),
              (0.3, L - 0.3, 6.0, 8.4, "void"), (0.3, L - 0.3, 8.4, wtop - 0.4, "win", 4),
              (0.3, L - 0.3, wtop + 0.1, top - 0.7, "win", 5, 1)], mat="metal", glass="glass_lit", frame="frame")
        for u in (0.0, L - 1.1):
            mb.box("brick", Af + t * u - inw * 0.25, t, inw, 1.1, 0.6, 0.0, 4.3)
            mb.box("lime", Af + t * (u - 0.05) - inw * 0.3, t, inw, 1.2, 0.65, 0.0, 0.8)
        band(mb, A, B, 4.3, 4.9, proj=0.1, ext=0.02)
        # grey horizontal-louvre band carrying the P
        mb.box("metal", Af + t * 0.3 + inw * 0.05, t, inw, L - 0.6, 0.1, 6.0, 8.4)
        zz = 6.05
        while zz < 8.35:
            mb.box("metal", Af + t * 0.3 - inw * 0.06, t, inw, L - 0.6, 0.12, zz, zz + 0.07)
            zz += 0.16
        pm = (A + B) / 2 + n * 0.08
        letters("P", (pm.x, pm.y, 7.15), facing_rot(n), 4.2, "gold", M, root, depth=0.12, name="MACK_SP_Tower_P")
        mb.box("metal", Af - inw * 0.05, t, inw, L, 0.35, top - 0.7, top)       # coping
        # penthouse (above the wing roof): glazed for 4 m behind the east face, then metal panels
        for (P0, P1) in ((Vector((B.x, y1)), Vector((x0, y1))), (Vector((x0, y0)), Vector((A.x, y0)))):
            Pf, tt, nn, LL = seg_frame(P0, P1)
            if P0.x > P1.x:   # north face runs east->west: glazed part at its start
                ops = [(0.3, 4.0, roof + 0.4, top - 0.7, "win", 2, 1)]
            else:             # south face runs west->east: glazed part at its end
                ops = [(LL - 4.0, LL - 0.3, roof + 0.4, top - 0.7, "win", 2, 1)]
            wall(mb, P0, P1, roof - 0.2, top, 0.25, ops, mat="metal", glass="glass_lit", frame="frame")
            for k in range(int(LL / 0.9)):
                u = 0.45 + k * 0.9
                if any(o[0] - 0.1 < u < o[1] + 0.1 for o in ops):
                    continue
                mb.box("metal", Pf + tt * u + nn * 0.04, tt, -nn, 0.06, 0.06, roof, top - 0.7)
        wall(mb, Vector((x0, y1)), Vector((x0, y0)), roof - 0.2, top, 0.25, [], mat="metal")
        flat_poly(mb, "unit", [(A.x, y0), (B.x, y1), (x0, y1), (x0, y0)], top - 0.05)
        mb.box("metal", (x0 - 0.1, y0 - 0.1), (1, 0), (0, 1), xf - x0 + 0.2, y1 - y0 + 0.2, top - 0.7, top)


# ---------------------------------------------------------------- site props / interior offset
def move_site_props():
    """Weist Plaza deck/furniture removed (r1); Wooden statue + Pyramid of Success kept on the plaza west of
    the SDAC (estimated positions, unchanged from r1)."""
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


def drop_interior():
    """Arena floor below grade: interior bowl / court / roof rig lowered by INTERIOR_DROP (recorded)."""
    n = 0
    for ob in bpy.data.collections[COLL].all_objects:
        if ob.name.startswith(INTERIOR_PREFIX) and not ob.name.startswith("MACK_SP_"):
            if "sp_orig_z" not in ob:
                ob["sp_orig_z"] = ob.location.z
            ob.location.z = ob["sp_orig_z"] - INTERIOR_DROP
            n += 1
    return n


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
    build_concourse_ring(mb, M, root)
    mb.build("MACK_SP_Concourse", M, root)
    build_south_blocks(mb)
    mb.build("MACK_SP_SouthBlock", M, root)
    build_west_annex(mb)
    mb.build("MACK_SP_WestAnnex", M, root)
    build_wing(mb, M, root)
    mb.build("MACK_SP_Wing", M, root)
    move_site_props()
    nd = drop_interior()
    build_plaza(mb)
    mb.build("MACK_SP_Plaza", M, root)
    for m in list(bpy.data.materials):
        if m.users == 0:
            bpy.data.materials.remove(m)
    bpy.ops.wm.save_mainfile()
    print("MACKEY_SP_DONE", len(bpy.data.collections[COLL].objects), "interior_dropped", nd)


main()
