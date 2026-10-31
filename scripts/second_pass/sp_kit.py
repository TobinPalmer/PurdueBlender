"""Second-pass exterior construction kit (bpy, Blender 4.x/5.x).

Shared, building-agnostic helpers used by modular/buildings/second_pass/build_<id>.py
builders. A builder opens the saved asset, removes the old exterior objects in the
exported Asset_<id> collection (keeping AssetRoot and any requested interior objects),
rebuilds the exterior from wing/facade specifications, and saves the same file.

Coordinates are asset-local metres (X east, Y north, Z up), the same frame as the
existing asset. Nothing here changes the asset's collection name or local origin.
"""
import math
import re
import bpy
import bmesh
from mathutils import Vector

# ----------------------------------------------------------------------------
# Scene / asset management
# ----------------------------------------------------------------------------

class Asset:
    def __init__(self, blend_path, building_id, keep_regex=None, prefix=None):
        bpy.ops.wm.open_mainfile(filepath=blend_path)
        self.path = blend_path
        self.id = building_id
        self.col = bpy.data.collections['Asset_' + building_id]
        self.prefix = prefix or building_id.upper()[:6]
        keep = re.compile(keep_regex) if keep_regex else None
        root = None
        for o in list(self.col.all_objects):
            if o.name.startswith('AssetRoot'):
                root = o
                continue
            if keep and keep.search(o.name):
                continue
            bpy.data.objects.remove(o, do_unlink=True)
        # purge emptied sub-collections that only held exterior objects
        for c in list(self.col.children_recursive):
            if len(c.all_objects) == 0:
                bpy.data.collections.remove(c)
        self.root = root
        for blk in (bpy.data.meshes, bpy.data.materials, bpy.data.curves, bpy.data.images, bpy.data.cameras, bpy.data.lights):
            for d in list(blk):
                if d.users == 0:
                    blk.remove(d)
        self.mats = {}
        self.parts = {}   # name -> bmesh accumulator

    # ------------------------------------------------------------------
    def mat(self, key):
        return self.mats[key]

    def bm(self, part):
        if part not in self.parts:
            self.parts[part] = []
        return self.parts[part]

    def add_mesh(self, name, bm, mats=None):
        me = bpy.data.meshes.new(name)
        bm.to_mesh(me)
        bm.free()
        ob = bpy.data.objects.new(name, me)
        self.col.objects.link(ob)
        if self.root is not None:
            ob.parent = self.root
        for m in (mats or []):
            me.materials.append(m)
        return ob

    def save(self):
        for blk in (bpy.data.meshes, bpy.data.materials, bpy.data.images):
            for d in list(blk):
                if d.users == 0:
                    blk.remove(d)
        bpy.ops.file.pack_all()
        bpy.ops.wm.save_as_mainfile(filepath=self.path, compress=True)


# ----------------------------------------------------------------------------
# Materials (procedural, portable — no external images)
# ----------------------------------------------------------------------------

def _principled(m):
    m.use_nodes = True
    nt = m.node_tree
    return nt, nt.nodes.get('Principled BSDF')


def mat_plain(name, rgb, rough=0.6, metal=0.0, alpha=1.0):
    m = bpy.data.materials.new(name)
    nt, p = _principled(m)
    p.inputs['Base Color'].default_value = (*rgb, 1)
    p.inputs['Roughness'].default_value = rough
    p.inputs['Metallic'].default_value = metal
    m.diffuse_color = (*rgb, 1)
    return m


def mat_glass(name, rgb=(0.05, 0.07, 0.09), rough=0.06):
    m = mat_plain(name, rgb, rough)
    nt, p = _principled(m)
    try:
        p.inputs['Specular IOR Level'].default_value = 0.9
    except KeyError:
        pass
    return m


def mat_brick(name, rgb, mortar=(0.42, 0.40, 0.37), var=0.12, brick_w=0.215, course=0.0762, rough=0.85, stretch=1.0):
    """UV-based running-bond brick: UV u = metres along wall, v = metres up."""
    m = bpy.data.materials.new(name)
    nt, p = _principled(m)
    p.inputs['Roughness'].default_value = rough
    tc = nt.nodes.new('ShaderNodeTexCoord')
    bt = nt.nodes.new('ShaderNodeTexBrick')
    bt.offset = 0.5
    bt.squash = 1.0
    bt.inputs['Scale'].default_value = 1.0
    bt.inputs['Brick Width'].default_value = brick_w * stretch
    bt.inputs['Row Height'].default_value = course
    bt.inputs['Mortar Size'].default_value = 0.009
    bt.inputs['Bias'].default_value = 0.0
    c1 = tuple(min(1, x * (1 + var)) for x in rgb)
    c2 = tuple(x * (1 - var) for x in rgb)
    bt.inputs['Color1'].default_value = (*c1, 1)
    bt.inputs['Color2'].default_value = (*c2, 1)
    bt.inputs['Mortar'].default_value = (*mortar, 1)
    nt.links.new(tc.outputs['UV'], bt.inputs['Vector'])
    nt.links.new(bt.outputs['Color'], p.inputs['Base Color'])
    m.diffuse_color = (*rgb, 1)
    return m


def mat_tile(name, rgb, var=0.15, rough=0.7):
    """Clay/slate roof tile courses on UV (u along eave, v up-slope)."""
    m = bpy.data.materials.new(name)
    nt, p = _principled(m)
    p.inputs['Roughness'].default_value = rough
    tc = nt.nodes.new('ShaderNodeTexCoord')
    bt = nt.nodes.new('ShaderNodeTexBrick')
    bt.offset = 0.5
    bt.inputs['Scale'].default_value = 1.0
    bt.inputs['Brick Width'].default_value = 0.3
    bt.inputs['Row Height'].default_value = 0.22
    bt.inputs['Mortar Size'].default_value = 0.012
    c1 = tuple(min(1, x * (1 + var)) for x in rgb)
    c2 = tuple(x * (1 - var) for x in rgb)
    bt.inputs['Color1'].default_value = (*c1, 1)
    bt.inputs['Color2'].default_value = (*c2, 1)
    bt.inputs['Mortar'].default_value = (*(x * 0.55 for x in rgb), 1)
    nt.links.new(tc.outputs['UV'], bt.inputs['Vector'])
    nt.links.new(bt.outputs['Color'], p.inputs['Base Color'])
    m.diffuse_color = (*rgb, 1)
    return m


def standard_materials(A, brick=(0.36, 0.13, 0.08), stone=(0.72, 0.66, 0.55), frame=(0.06, 0.055, 0.05),
                       glass=(0.05, 0.07, 0.09), roof=(0.42, 0.14, 0.09), membrane=(0.33, 0.33, 0.33), extra=None):
    p = A.prefix
    A.mats.update({
        'brick': mat_brick(p + '_SP_Brick', brick),
        'stone': mat_plain(p + '_SP_Limestone', stone, 0.75),
        'frame': mat_plain(p + '_SP_WindowFrame', frame, 0.45, 0.3),
        'glass': mat_glass(p + '_SP_Glass', glass),
        'roof': mat_tile(p + '_SP_RoofTile', roof),
        'membrane': mat_plain(p + '_SP_RoofMembrane', membrane, 0.9),
        'metal': mat_plain(p + '_SP_MetalTrim', (0.12, 0.12, 0.12), 0.5, 0.6),
        'dark': mat_plain(p + '_SP_DarkRecess', (0.03, 0.03, 0.03), 0.8),
    })
    for k, v in (extra or {}).items():
        A.mats[k] = v
    return A.mats


# ----------------------------------------------------------------------------
# 2D polygon helpers
# ----------------------------------------------------------------------------

def poly_area(P):
    return 0.5 * sum(P[i][0] * P[(i + 1) % len(P)][1] - P[(i + 1) % len(P)][0] * P[i][1] for i in range(len(P)))


def ccw(P):
    return P if poly_area(P) > 0 else list(reversed(P))


def edge_frame(P, i):
    """Return (start Vector2, unit tangent, outward normal, length) for CCW polygon edge i."""
    a = Vector(P[i]); b = Vector(P[(i + 1) % len(P)])
    t = (b - a); L = t.length; t = t / L
    n = Vector((t.y, -t.x))  # outward for CCW
    return a, t, n, L


def offset_poly(P, d):
    """Miter offset of a CCW polygon; d>0 outward."""
    n = len(P); out = []
    for i in range(n):
        a0, t0, n0, _ = edge_frame(P, (i - 1) % n)
        a1, t1, n1, _ = edge_frame(P, i)
        p0 = a0 + n0 * d; p1 = a1 + n1 * d
        den = t0.x * t1.y - t0.y * t1.x
        if abs(den) < 1e-6:
            out.append(tuple(p1)); continue
        s = ((p1.x - p0.x) * t1.y - (p1.y - p0.y) * t1.x) / den
        q = p0 + t0 * s
        if (q - (a1 + n1 * 0)).length > 4 * abs(d) + 1e-6:   # spike guard on sharp/short edges
            q = a1 + (n0 + n1).normalized() * abs(d) * (1 if d > 0 else -1) if (n0 + n1).length > 1e-6 else p1
        out.append((q.x, q.y))
    return out


def rect(cx, cy, length, width, ang_deg):
    """Rectangle centred at (cx,cy), length along angle, CCW."""
    a = math.radians(ang_deg)
    u = Vector((math.cos(a), math.sin(a))); v = Vector((-math.sin(a), math.cos(a)))
    c = Vector((cx, cy)); hl = length / 2; hw = width / 2
    pts = [c - u * hl - v * hw, c + u * hl - v * hw, c + u * hl + v * hw, c - u * hl + v * hw]
    return [(p.x, p.y) for p in pts]


def frame_pts(origin, ang_deg, pts_uv):
    """Map points given in a rotated (u along ang, v left) frame to local XY."""
    a = math.radians(ang_deg)
    u = Vector((math.cos(a), math.sin(a))); v = Vector((-math.sin(a), math.cos(a)))
    o = Vector(origin)
    return [tuple(o + u * p[0] + v * p[1]) for p in pts_uv]


# ----------------------------------------------------------------------------
# Low-level bmesh primitives
# ----------------------------------------------------------------------------

def bm_prism(bm, P, z0, z1, mat_index=0, cap_top=True, cap_bottom=True):
    P = ccw(P)
    bot = [bm.verts.new((x, y, z0)) for x, y in P]
    top = [bm.verts.new((x, y, z1)) for x, y in P]
    n = len(P)
    for i in range(n):
        f = bm.faces.new((bot[i], bot[(i + 1) % n], top[(i + 1) % n], top[i]))
        f.material_index = mat_index
    if cap_top:
        f = bm.faces.new(top); f.material_index = mat_index
    if cap_bottom:
        f = bm.faces.new(list(reversed(bot))); f.material_index = mat_index
    return bm


def bm_box_oriented(bm, origin, t, n, u0, u1, z0, z1, d0, d1, mat_index=0):
    """Box spanning u in [u0,u1] along tangent t, depth d in [d0,d1] along normal n, z in [z0,z1]."""
    o = Vector((origin[0], origin[1]))
    t = Vector((t[0], t[1])); n = Vector((n[0], n[1]))
    c = [o + t * u0 + n * d0, o + t * u1 + n * d0, o + t * u1 + n * d1, o + t * u0 + n * d1]
    P = [(p.x, p.y) for p in c]
    return bm_prism(bm, P, z0, z1, mat_index)


def bm_profile_extrude(bm, origin, t, n, prof_uz, d0, d1, mat_index=0, cap=True):
    """Extrude a facade-plane profile (list of (u,z)) along normal from d0 to d1."""
    o = Vector((origin[0], origin[1])); t = Vector(t); n = Vector(n)
    def P(u, z, d):
        q = o + t * u + n * d
        return (q.x, q.y, z)
    # ensure profile CCW when viewed from outside (+n): u right, z up
    area = 0.5 * sum(prof_uz[i][0] * prof_uz[(i + 1) % len(prof_uz)][1] - prof_uz[(i + 1) % len(prof_uz)][0] * prof_uz[i][1] for i in range(len(prof_uz)))
    if area < 0:
        prof_uz = list(reversed(prof_uz))
    front = [bm.verts.new(P(u, z, d1)) for u, z in prof_uz]
    back = [bm.verts.new(P(u, z, d0)) for u, z in prof_uz]
    k = len(prof_uz)
    # outside view: +n towards viewer, t to the right => (t, z, n) is left-handed? t x z = -n for outward
    # so CCW in (u,z) seen from +n needs reversed ordering for a +n facing normal; handle by recalc later
    for i in range(k):
        f = bm.faces.new((front[i], front[(i + 1) % k], back[(i + 1) % k], back[i]))
        f.material_index = mat_index
    if cap:
        f = bm.faces.new(front); f.material_index = mat_index
        f = bm.faces.new(list(reversed(back))); f.material_index = mat_index
    return front, back


def arch_profile(w, h, spring=None, segs=12, kind='round'):
    """Opening profile in (u,z) local to opening bottom-centre. kind: rect|round|segment|gothic."""
    hw = w / 2
    if kind == 'rect' or kind is None:
        return [(-hw, 0), (hw, 0), (hw, h), (-hw, h)]
    if kind == 'round':
        zs = h - hw if spring is None else spring
        pts = [(-hw, 0), (hw, 0), (hw, zs)]
        for i in range(1, segs):
            a = math.pi * i / segs
            pts.append((hw * math.cos(a), zs + hw * math.sin(a)))
        pts.append((-hw, zs))
        return pts
    if kind == 'segment':
        rise = h - (spring if spring is not None else h * 0.85)
        zs = h - rise
        R = (hw * hw + rise * rise) / (2 * rise)
        cz = h - R
        a0 = math.asin(hw / R)
        pts = [(-hw, 0), (hw, 0), (hw, zs)]
        for i in range(1, segs):
            a = -a0 + 2 * a0 * i / segs
            pts.append((R * math.sin(-a), cz + R * math.cos(a)))
        pts.append((-hw, zs))
        return pts
    if kind == 'gothic':
        zs = h - w * 0.86 if spring is None else spring
        R = w
        pts = [(-hw, 0), (hw, 0), (hw, zs)]
        apex = zs + math.sqrt(R * R - (R - hw * 0) ** 2 + (R) ** 2 - R * R) if False else h
        for i in range(1, segs // 2):
            f = i / (segs // 2)
            a = math.acos(1 - 0.0) * 0
            x = hw - R * (1 - math.cos(f * math.radians(60)))
            z = zs + R * math.sin(f * math.radians(60))
            pts.append((x, min(z, h)))
        pts.append((0, h))
        for i in range(segs // 2 - 1, 0, -1):
            f = i / (segs // 2)
            x = hw - R * (1 - math.cos(f * math.radians(60)))
            z = zs + R * math.sin(f * math.radians(60))
            pts.append((-x, min(z, h)))
        pts.append((-hw, zs))
        return pts
    raise ValueError(kind)


# ----------------------------------------------------------------------------
# Building wings
# ----------------------------------------------------------------------------

class Wing:
    """A wall prism with facades. edges: per-edge facade spec dict keyed by edge index."""

    def __init__(self, A, name, poly, z0, z1, wall_mat='brick', thickness=None):
        self.A = A; self.name = name; self.P = ccw(poly); self.z0 = z0; self.z1 = z1
        self.wall_mat = wall_mat
        self.cutters = []          # (origin,t,n,prof_uz,u_center,z_base,depth)
        self.glass = bmesh.new(); self.frames = bmesh.new(); self.stone = bmesh.new()
        self.extra = {}            # material key -> bmesh
        self.recess_mat = {}

    def part(self, key):
        if key == 'glass':
            return self.glass
        if key == 'frame':
            return self.frames
        if key == 'stone':
            return self.stone
        if key not in self.extra:
            self.extra[key] = bmesh.new()
        return self.extra[key]

    def edge(self, i):
        return edge_frame(self.P, i % len(self.P))

    def edge_len(self, i):
        return self.edge(i)[3]

    def longest_edges(self):
        return sorted(range(len(self.P)), key=lambda i: -self.edge_len(i))

    # ------------------------------------------------------------------
    def opening(self, i, u, zb, w, h, kind='rect', depth=0.22, mull=(1, 1), frame_w=0.06,
                sill=True, sill_mat='stone', head=None, head_mat='stone', spring=None, glass_mat='glass',
                transom=None, door=False, surround=None, frame_mat='frame', keystone=False):
        """Recessed opening centred at u (m from edge start) on edge i, base zb, width w, height h.
        mull=(cols, rows) glazing divisions. head: height of a lintel band above (rect) or arch ring width."""
        a, t, n, L = self.edge(i)
        prof = [(u + pu, zb + pz) for pu, pz in arch_profile(w, h, spring, kind=kind)]
        self.cutters.append((a, t, n, prof, depth))
        # glass pane slightly in front of pocket bottom
        gd = -depth + 0.03
        bm_profile_extrude(self.part(glass_mat), a, t, n, prof, gd - 0.01, gd, 0)
        fr = self.part(frame_mat)
        # perimeter frame
        fd0, fd1 = gd - 0.005, gd + 0.05
        hw = w / 2
        zs = zb + h if kind in ('rect', None) else zb + (spring if spring is not None else h - hw)
        bm_box_oriented(fr, a, t, n, u - hw, u - hw + frame_w, zb, zs, fd0, fd1)
        bm_box_oriented(fr, a, t, n, u + hw - frame_w, u + hw, zb, zs, fd0, fd1)
        bm_box_oriented(fr, a, t, n, u - hw, u + hw, zb, zb + frame_w, fd0, fd1)
        if kind in ('rect', None):
            bm_box_oriented(fr, a, t, n, u - hw, u + hw, zb + h - frame_w, zb + h, fd0, fd1)
        else:
            bm_box_oriented(fr, a, t, n, u - hw, u + hw, zs - frame_w / 2, zs + frame_w / 2, fd0, fd1)
            # radial muntins in arch head
            segs = 4
            R = hw
            for k in range(1, segs):
                ang = math.pi * k / segs
                cx, cz = u + R * 0.5 * math.cos(ang), zs + R * 0.5 * math.sin(ang)
                # thin bar approximated by small box at mid-radius oriented vertically (simplified)
                bm_box_oriented(fr, a, t, n, cx - frame_w / 3, cx + frame_w / 3, zs, zs + R * math.sin(ang) * 0.98, fd0, fd1)
        cols, rows = mull
        body_top = zs
        for c in range(1, cols):
            x = u - hw + w * c / cols
            bm_box_oriented(fr, a, t, n, x - frame_w / 3, x + frame_w / 3, zb, body_top, fd0, fd1)
        if transom is not None:
            bm_box_oriented(fr, a, t, n, u - hw, u + hw, zb + transom - frame_w / 2, zb + transom + frame_w / 2, fd0, fd1)
        for r in range(1, rows):
            z = zb + (body_top - zb) * r / rows
            bm_box_oriented(fr, a, t, n, u - hw, u + hw, z - frame_w / 3, z + frame_w / 3, fd0, fd1)
        st = self.part(sill_mat)
        if sill and not door:
            bm_box_oriented(st, a, t, n, u - hw - 0.08, u + hw + 0.08, zb - 0.1, zb, -0.02, 0.07)
        if head:
            hm = self.part(head_mat)
            if kind in ('rect', None):
                bm_box_oriented(hm, a, t, n, u - hw - 0.1, u + hw + 0.1, zb + h, zb + h + head, -0.01, 0.03)
            else:
                # voussoir ring
                ring = []
                R0, R1 = hw, hw + head
                segs = 13
                outer = [(u + R1 * math.cos(math.pi * k / segs), zs + R1 * math.sin(math.pi * k / segs)) for k in range(segs + 1)]
                inner = [(u + R0 * math.cos(math.pi * k / segs), zs + R0 * math.sin(math.pi * k / segs)) for k in range(segs + 1)]
                prof_r = outer + list(reversed(inner))
                bm_profile_extrude(hm, a, t, n, prof_r, -0.01, 0.05, 0)
                if keystone:
                    kw = head * 0.8
                    bm_profile_extrude(hm, a, t, n, [(u - kw / 2, zs + R0 - 0.02), (u + kw / 2, zs + R0 - 0.02), (u + kw * 0.65, zs + R1 + 0.12), (u - kw * 0.65, zs + R1 + 0.12)], -0.01, 0.1, 0)
        if surround:
            sm = self.part(surround.get('mat', 'stone'))
            sw = surround.get('w', 0.18); sp = surround.get('proj', 0.05)
            bm_box_oriented(sm, a, t, n, u - hw - sw, u - hw, zb - (0.1 if not door else 0), zs, -0.01, sp)
            bm_box_oriented(sm, a, t, n, u + hw, u + hw + sw, zb - (0.1 if not door else 0), zs, -0.01, sp)
            if kind in ('rect', None):
                bm_box_oriented(sm, a, t, n, u - hw - sw, u + hw + sw, zb + h, zb + h + sw, -0.01, sp)

    def row(self, i, zb, w, h, positions=None, n=None, margin=1.0, **kw):
        """Place a row of openings on edge i: explicit u positions or n evenly spaced."""
        L = self.edge_len(i)
        if positions is None:
            if n is None or n <= 0:
                return []
            if n == 1:
                positions = [L / 2]
            else:
                span = L - 2 * margin
                positions = [margin + span * k / (n - 1) for k in range(n)]
        for u in positions:
            self.opening(i, u, zb, w, h, **kw)
        return positions

    def bays(self, i, n, margin=1.0, skip=()):
        L = self.edge_len(i)
        if n == 1:
            return [L / 2]
        step = (L - 2 * margin) / n
        return [margin + step * (k + 0.5) for k in range(n) if k not in skip]

    # ------------------------------------------------------------------
    def band(self, z, h, proj=0.06, mat='stone', edges=None, inset=0.0):
        """Horizontal course around listed edges (default all)."""
        bmx = self.part(mat)
        E = range(len(self.P)) if edges is None else edges
        for i in E:
            a, t, n, L = self.edge(i)
            bm_box_oriented(bmx, a, t, n, -proj, L + proj, z, z + h, -0.02 - inset, proj)

    def pier(self, i, u, w, z0, z1, proj=0.08, mat=None):
        bmx = self.part(mat or self.wall_mat)
        a, t, n, L = self.edge(i)
        bm_box_oriented(bmx, a, t, n, u - w / 2, u + w / 2, z0, z1, -0.02, proj)

    def panel(self, i, u0, u1, z0, z1, proj=0.03, mat='stone'):
        bmx = self.part(mat)
        a, t, n, L = self.edge(i)
        bm_box_oriented(bmx, a, t, n, u0, u1, z0, z1, -0.02, proj)

    def build(self, solver='EXACT'):
        A = self.A
        bm = bmesh.new()
        bm_prism(bm, self.P, self.z0, self.z1, 0)
        wall = A.add_mesh(f'{A.prefix}_{self.name}_Walls', bm, [A.mat(self.wall_mat), A.mat('stone')])
        if self.cutters:
            cb = bmesh.new()
            for a, t, n, prof, depth in self.cutters:
                bm_profile_extrude(cb, a, t, n, prof, -depth, 0.5, 0)
            bmesh.ops.recalc_face_normals(cb, faces=cb.faces)
            cut = A.add_mesh(f'{A.prefix}_{self.name}_Cutter', cb, [A.mat(self.wall_mat)])
            mod = wall.modifiers.new('cut', 'BOOLEAN'); mod.operation = 'DIFFERENCE'; mod.object = cut
            mod.solver = solver
            try:
                mod.use_self = False
            except Exception:
                pass
            bpy.context.view_layer.objects.active = wall
            dg = bpy.context.evaluated_depsgraph_get()
            ev = wall.evaluated_get(dg)
            newme = bpy.data.meshes.new_from_object(ev)
            old = wall.data
            wall.modifiers.clear()
            wall.data = newme
            bpy.data.meshes.remove(old)
            bpy.data.objects.remove(cut, do_unlink=True)
        uv_walls(wall)
        for key, b in [('glass', self.glass), ('frame', self.frames), ('stone', self.stone)] + list(self.extra.items()):
            if len(b.verts):
                bmesh.ops.recalc_face_normals(b, faces=b.faces)
                ob = A.add_mesh(f'{A.prefix}_{self.name}_{key.capitalize()}', b, [A.mat(key)])
                uv_walls(ob)
            else:
                b.free()
        return wall


def uv_walls(ob, scale=1.0):
    """Planar metric UVs: walls get (along-face, z); flat faces get (x, y)."""
    me = ob.data
    bm = bmesh.new(); bm.from_mesh(me)
    uvl = bm.loops.layers.uv.verify()
    for f in bm.faces:
        nrm = f.normal
        if abs(nrm.z) > 0.7:
            for l in f.loops:
                l[uvl].uv = (l.vert.co.x * scale, l.vert.co.y * scale)
        else:
            h = Vector((nrm.x, nrm.y))
            if h.length < 1e-6:
                h = Vector((1, 0))
            h.normalize(); tg = Vector((-h.y, h.x))
            for l in f.loops:
                c = l.vert.co
                l[uvl].uv = ((c.x * tg.x + c.y * tg.y) * scale, c.z * scale)
    bm.to_mesh(me); bm.free()


# ----------------------------------------------------------------------------
# Roofs
# ----------------------------------------------------------------------------

def hip_roof(A, name, poly, z_eave, pitch_deg, overhang=0.6, flat_top=None, mat='roof', top_mat='membrane',
             fascia=0.25, ridge_axis=None):
    """Hipped roof over a convex/orthogonal polygon.
    flat_top: horizontal run (m) of the slopes before a flat deck; None = full hip (rectangles only)."""
    P = ccw(poly)
    base = offset_poly(P, overhang)
    tanp = math.tan(math.radians(pitch_deg))
    bm = bmesh.new()
    if flat_top is not None:
        run = flat_top + overhang
        top = offset_poly(P, -flat_top)
        zt = z_eave + run * tanp
        bv = [bm.verts.new((x, y, z_eave)) for x, y in base]
        tv = [bm.verts.new((x, y, zt)) for x, y in top]
        k = len(P)
        for i in range(k):
            f = bm.faces.new((bv[i], bv[(i + 1) % k], tv[(i + 1) % k], tv[i])); f.material_index = 0
        f = bm.faces.new(tv); f.material_index = 1
        f = bm.faces.new(list(reversed(bv))); f.material_index = 0
        top_z = zt
    else:
        assert len(P) == 4, 'full hip roof requires a rectangle'
        e0 = edge_frame(base, 0); e1 = edge_frame(base, 1)
        if e0[3] >= e1[3]:
            long_i = 0
        else:
            long_i = 1
        a, t, n, L = edge_frame(base, long_i)
        W = edge_frame(base, long_i + 1)[3]
        half = W / 2
        zt = z_eave + half * tanp
        # ridge from (half along) to (L-half)
        c0 = Vector(base[long_i]) + t * half - n * half
        c1 = Vector(base[long_i]) + t * (L - half) - n * half
        if L - 2 * half < 0.01:
            c1 = c0
        bv = [bm.verts.new((x, y, z_eave)) for x, y in base]
        r0 = bm.verts.new((c0.x, c0.y, zt)); r1 = bm.verts.new((c1.x, c1.y, zt)) if c1 != c0 else r0
        i0 = long_i; i1 = (long_i + 1) % 4; i2 = (long_i + 2) % 4; i3 = (long_i + 3) % 4
        if r1 is r0:
            for (p, q) in [(i0, i1), (i1, i2), (i2, i3), (i3, i0)]:
                bm.faces.new((bv[p], bv[q], r0))
        else:
            bm.faces.new((bv[i0], bv[i1], r1, r0))
            bm.faces.new((bv[i1], bv[i2], r1))
            bm.faces.new((bv[i2], bv[i3], r0, r1))
            bm.faces.new((bv[i3], bv[i0], r0))
        bm.faces.new(list(reversed(bv)))
        top_z = zt
    bmesh.ops.recalc_face_normals(bm, faces=bm.faces)
    ob = A.add_mesh(f'{A.prefix}_{name}_Roof', bm, [A.mat(mat), A.mat(top_mat)])
    uv_roof(ob)
    if fascia:
        fb = bmesh.new()
        bm_prism(fb, base, z_eave - fascia, z_eave + 0.02, 0)
        A.add_mesh(f'{A.prefix}_{name}_Fascia', fb, [A.mat('metal' if 'fascia_mat' not in A.mats else 'fascia_mat')])
    return top_z


def gable_roof(A, name, poly_rect, z_eave, pitch_deg, overhang=0.5, mat='roof', along=0):
    """Gable roof over a rectangle; ridge parallel to edge `along` (0 or 1)."""
    P = ccw(poly_rect)
    base = offset_poly(P, overhang)
    a, t, n, L = edge_frame(base, along)
    W = edge_frame(base, along + 1)[3]
    zt = z_eave + W / 2 * math.tan(math.radians(pitch_deg))
    o = Vector(base[along])
    q = [o, o + t * L, o + t * L - n * W, o - n * W]
    r0 = o - n * W / 2; r1 = o + t * L - n * W / 2
    bm = bmesh.new()
    v = [bm.verts.new((p.x, p.y, z_eave)) for p in q]
    ra = bm.verts.new((r0.x, r0.y, zt)); rb = bm.verts.new((r1.x, r1.y, zt))
    bm.faces.new((v[0], v[1], rb, ra)); bm.faces.new((v[2], v[3], ra, rb))
    bm.faces.new((v[1], v[2], rb)); bm.faces.new((v[3], v[0], ra))
    bm.faces.new(list(reversed(v)))
    bmesh.ops.recalc_face_normals(bm, faces=bm.faces)
    ob = A.add_mesh(f'{A.prefix}_{name}_Roof', bm, [A.mat(mat)])
    uv_roof(ob)
    return zt


def flat_roof(A, name, poly, z, parapet=0.9, coping=0.08, wall_mat='brick', coping_mat='stone', deck_mat='membrane', thick=0.35):
    P = ccw(poly)
    bm = bmesh.new()
    bm_prism(bm, offset_poly(P, -thick) if parapet else P, z - 0.05, z + 0.04, 0)
    A.add_mesh(f'{A.prefix}_{name}_Deck', bm, [A.mat(deck_mat)])
    if parapet:
        bm = bmesh.new()
        outer = P; inner = offset_poly(P, -thick)
        k = len(P)
        ob_ = [bm.verts.new((x, y, z)) for x, y in outer]; ot = [bm.verts.new((x, y, z + parapet)) for x, y in outer]
        ib = [bm.verts.new((x, y, z)) for x, y in inner]; it = [bm.verts.new((x, y, z + parapet)) for x, y in inner]
        for i in range(k):
            j = (i + 1) % k
            bm.faces.new((ob_[i], ob_[j], ot[j], ot[i]))
            bm.faces.new((ib[j], ib[i], it[i], it[j]))
            bm.faces.new((ot[i], ot[j], it[j], it[i]))
        o = A.add_mesh(f'{A.prefix}_{name}_Parapet', bm, [A.mat(wall_mat)])
        uv_walls(o)
        if coping:
            cb = bmesh.new()
            outer2 = offset_poly(P, 0.05); inner2 = offset_poly(P, -thick - 0.03)
            ov = [cb.verts.new((x, y, z + parapet)) for x, y in outer2]; ovt = [cb.verts.new((x, y, z + parapet + coping)) for x, y in outer2]
            iv = [cb.verts.new((x, y, z + parapet)) for x, y in inner2]; ivt = [cb.verts.new((x, y, z + parapet + coping)) for x, y in inner2]
            for i in range(k):
                j = (i + 1) % k
                cb.faces.new((ov[i], ov[j], ovt[j], ovt[i])); cb.faces.new((iv[j], iv[i], ivt[i], ivt[j]))
                cb.faces.new((ovt[i], ovt[j], ivt[j], ivt[i])); cb.faces.new((ov[j], ov[i], iv[i], iv[j]))
            A.add_mesh(f'{A.prefix}_{name}_Coping', cb, [A.mat(coping_mat)])
    return z + parapet


def uv_roof(ob):
    me = ob.data
    bm = bmesh.new(); bm.from_mesh(me)
    uvl = bm.loops.layers.uv.verify()
    for f in bm.faces:
        nrm = f.normal
        h = Vector((nrm.x, nrm.y))
        if h.length < 1e-4:
            for l in f.loops:
                l[uvl].uv = (l.vert.co.x, l.vert.co.y)
            continue
        h.normalize(); tg = Vector((-h.y, h.x))
        for l in f.loops:
            c = l.vert.co
            l[uvl].uv = (c.x * tg.x + c.y * tg.y, -(c.x * h.x + c.y * h.y) / max(0.2, math.sqrt(max(1e-6, 1 - nrm.z * nrm.z))) * 1.0)
    bm.to_mesh(me); bm.free()


def box(A, name, poly, z0, z1, mat):
    bm = bmesh.new(); bm_prism(bm, poly, z0, z1, 0)
    ob = A.add_mesh(f'{A.prefix}_{name}', bm, [A.mat(mat)])
    uv_walls(ob)
    return ob


def arch_portal(A, name, origin, t, n, u, zb, w_open, h_spring, ring=0.55, pier_w=0.6, depth=0.5,
                proj=0.35, keystone=True, mat='stone', cap=True, entab=None):
    """Free-standing stone arch surround projecting from a facade at (origin,t,n), centred at u.
    h_spring: spring height above zb. Returns top z."""
    bmx = bmesh.new()
    hw = w_open / 2
    zs = zb + h_spring
    # piers
    bm_box_oriented(bmx, origin, t, n, u - hw - pier_w, u - hw, zb, zs, -0.02, proj)
    bm_box_oriented(bmx, origin, t, n, u + hw, u + hw + pier_w, zb, zs, -0.02, proj)
    if cap:
        bm_box_oriented(bmx, origin, t, n, u - hw - pier_w - 0.06, u - hw + 0.04, zs - 0.18, zs, -0.02, proj + 0.06)
        bm_box_oriented(bmx, origin, t, n, u + hw - 0.04, u + hw + pier_w + 0.06, zs - 0.18, zs, -0.02, proj + 0.06)
    segs = 16
    R0, R1 = hw, hw + ring
    outer = [(u + R1 * math.cos(math.pi * k / segs), zs + R1 * math.sin(math.pi * k / segs)) for k in range(segs + 1)]
    inner = [(u + R0 * math.cos(math.pi * k / segs), zs + R0 * math.sin(math.pi * k / segs)) for k in range(segs + 1)]
    bm_profile_extrude(bmx, origin, t, n, outer + list(reversed(inner)), -0.02, proj)
    if keystone:
        kw = ring * 0.7
        bm_profile_extrude(bmx, origin, t, n, [(u - kw / 2, zs + R0 - 0.05), (u + kw / 2, zs + R0 - 0.05), (u + kw * 0.7, zs + R1 + 0.15), (u - kw * 0.7, zs + R1 + 0.15)], -0.02, proj + 0.08)
    if entab:
        bm_box_oriented(bmx, origin, t, n, u - hw, u + hw, zb + entab - 0.12, zb + entab + 0.12, -0.3, proj * 0.6)
    bmesh.ops.recalc_face_normals(bmx, faces=bmx.faces)
    A.add_mesh(f'{A.prefix}_{name}', bmx, [A.mat(mat)])
    return zs + R1
