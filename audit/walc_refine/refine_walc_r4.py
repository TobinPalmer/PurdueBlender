"""WALC R4: turn the long ribbon façades into masonry-and-window bays."""
import bpy, hashlib, json, math
from pathlib import Path
from mathutils import Vector

ROOT = Path(__file__).resolve().parents[2]
ASSET = ROOT / 'modular/buildings/walc.blend'
EXPECTED = {
    'c9ca2cfe413898780445bade8e729e22510535aed123407c4d11e5c28f53ec65', # R3 review base
    '01f0ba7bd8fbdee2da267e85c8d35e327cf891d68a05cbeea5876b5b692b5dd4', # R4 final, idempotent rerun
}
actual = hashlib.sha256(ASSET.read_bytes()).hexdigest()
if actual not in EXPECTED:
    raise RuntimeError(f'WALC input is not the R3 baseline or final R4 asset: {actual}')

asset = bpy.data.collections['Asset_walc']
root = bpy.data.objects['AssetRoot_walc']
assert tuple(round(v, 6) for v in root.location) == (0, 0, 0)
assert tuple(round(v, 6) for v in root.rotation_euler) == (0, 0, 0)
assert tuple(round(v, 6) for v in root.scale) == (1, 1, 1)

refs=json.loads((ROOT/'audit/official_building_references.json').read_text(encoding='utf-8'))
source=next(b for b in refs['buildings'] if b.get('fid')==906)
ring=source['rings_xy_m'][0]
ring_area=sum(float(ring[i][0])*float(ring[(i+1)%len(ring)][1])-float(ring[(i+1)%len(ring)][0])*float(ring[i][1]) for i in range(len(ring)))/2

brick = bpy.data.materials['WALC_Reference_Brick']
stone = bpy.data.materials['WALC_Reference_Limestone']
glass = bpy.data.materials['WALC_Reference_Glass']
bronze = bpy.data.materials.get('Bronze.009')
brick.diffuse_color = (0.43, 0.145, 0.088, 1)
stone.diffuse_color = (0.79, 0.73, 0.61, 1)
glass.diffuse_color = (0.19, 0.32, 0.39, 1)

# Remove R3's narrow bronze blades. R4 replaces them with full-depth masonry
# wall fields and broad inter-window piers on the long source wall runs.
old = bpy.data.objects.get('WALC_Facade_Bay_Piers_R3')
if old:
    bpy.data.objects.remove(old, do_unlink=True)
for name in ('WALC_R4_Masonry_Bay_Fields', 'WALC_R4_Ground_Floor_Piers',
             'WALC_R4_Grouped_Window_Glazing', 'WALC_R4_Window_Frames',
             'WALC_R4_Window_Mullions'):
    o = bpy.data.objects.get(name)
    if o:
        bpy.data.objects.remove(o, do_unlink=True)
    me = bpy.data.meshes.get(name + '_Mesh')
    if me:
        bpy.data.meshes.remove(me)

verts_by_mat = {m: [] for m in (brick, stone, glass, bronze) if m is not None}
faces_by_mat = {m: [] for m in verts_by_mat}

def box(mat, origin, tangent, normal, s, d, z0, z1, width, depth):
    """Append a closed rectangular prism in facade-local coordinates."""
    arr = verts_by_mat[mat]
    faces = faces_by_mat[mat]
    base = len(arr)
    for zz in (z0, z1):
        for ss, dd in ((s-width/2, d-depth/2), (s+width/2, d-depth/2),
                       (s+width/2, d+depth/2), (s-width/2, d+depth/2)):
            p = origin + tangent*ss + normal*dd
            arr.append((p.x, p.y, zz))
    faces.extend(tuple(base+i for i in f) for f in (
        (0, 3, 2, 1), (4, 5, 6, 7), (0, 1, 5, 4),
        (1, 2, 6, 5), (2, 3, 7, 6), (3, 0, 4, 7)))

def make_obj(name, mat):
    verts = verts_by_mat[mat]
    faces = faces_by_mat[mat]
    if not faces:
        return None
    me = bpy.data.meshes.new(name + '_Mesh')
    me.from_pydata(verts, [], faces)
    me.update()
    obj = bpy.data.objects.new(name, me)
    asset.objects.link(obj)
    obj.data.materials.append(mat)
    obj['evidence_note'] = 'Visual façade interpretation from Purdue 2018 official exterior photo; bay spacing, window dimensions, and projection are image-estimated, not surveyed.'
    return obj

spans = {}
xycenters = []
for o in asset.all_objects:
    if o.type != 'MESH' or not o.name.startswith('WALC_Source906_Edge_'):
        continue
    if not any(o.name.endswith(f'_Band{k}') for k in (2, 4, 6)):
        continue
    pts = [o.matrix_world @ v.co for v in o.data.vertices]
    zmin = min(p.z for p in pts)
    bottom = [p for p in pts if abs(p.z-zmin) < 1e-4]
    xycenters.append(Vector((sum(p.x for p in bottom)/len(bottom), sum(p.y for p in bottom)/len(bottom))))
    if len(bottom) != 4:
        continue
    center = Vector((sum(p.x for p in bottom)/4, sum(p.y for p in bottom)/4))
    # Principal direction from the longest bottom-face diagonal; its small
    # across-wall component is removed by averaging endpoints below.
    pairs = [(bottom[i], bottom[j]) for i in range(4) for j in range(i+1,4)]
    a, b = max(pairs, key=lambda pair: (pair[0]-pair[1]).length)
    tangent = (Vector((b.x-a.x,b.y-a.y))).normalized()
    edge_id=int(o.name.split('_Edge_',1)[1].split('_Band',1)[0])
    # Match each facade normal to the cached official polygon winding. For a
    # concave polygon, a building-wide radial estimate can point inward; the
    # ordered source-ring direction provides the locally correct exterior side.
    src_a=ring[edge_id]; src_b=ring[(edge_id+1)%len(ring)]
    source_t=Vector((float(src_b[0])-float(src_a[0]),float(src_b[1])-float(src_a[1]))).normalized()
    # Use the GIS segment direction itself, not a vertex-to-vertex diagonal;
    # the latter crosses the wall thickness and would artificially widen a
    # shallow segment's facade.
    tangent=source_t
    normal=Vector((tangent.y,-tangent.x)) if ring_area>0 else Vector((-tangent.y,tangent.x))
    # Project the four corners to obtain true wall length and thickness.
    proj = [(p.x* tangent.x + p.y*tangent.y,
             p.x* normal.x + p.y*normal.y) for p in bottom]
    s_center = center.x*tangent.x + center.y*tangent.y
    d_center = center.x*normal.x + center.y*normal.y
    smin, smax = min(p[0] for p in proj)-s_center, max(p[0] for p in proj)-s_center
    dmin, dmax = min(p[1] for p in proj)-d_center, max(p[1] for p in proj)-d_center
    length = smax-smin
    if length < 4.0:
        continue
    # Use the wall's own midpoint, not building-wide bounds, as the local origin.
    origin = Vector((sum(p.x for p in bottom)/4, sum(p.y for p in bottom)/4))
    spans[o.name] = dict(center=center, origin=origin, tangent=tangent,
                         normal=normal, smin=smin, smax=smax,
                         length=length, thickness=dmax-dmin,
                         zmin=min(p.z for p in pts), zmax=max(p.z for p in pts))

# Per each long straight façade span: two upper storeys receive opaque brick
# fields and paired tall window groups. The ground storey retains its broad
# glazing, interrupted by aligned, substantial brick piers.
group_count_by_edge = {}
for name, sp in spans.items():
    o = bpy.data.objects[name]
    t, n = sp['tangent'], sp['normal']
    origin = sp['origin']
    length = sp['length']
    # The normal was selected from the official polygon winding above.
    sp['normal'] = n
    nwin = max(2, round(length / 4.55))
    spacing = length / nwin
    win_w = min(2.45, spacing * 0.61)
    group_count_by_edge[name] = nwin

    band = int(name.rsplit('_Band',1)[1])
    z0, z1 = sp['zmin'], sp['zmax']
    thickness = sp['thickness']
    outer = thickness/2
    if band in (4, 6):
        # Continuous brick cladding breaks the former glazed ribbon into solid
        # masonry wall fields; grouped window apertures are modeled on its face.
        box(brick, origin, t, n, 0, outer-0.055, z0, z1,
            length+0.02, 0.16)
        # Two lights in a common limestone surround, with dark bronze divisions.
        window_h = max(2.45, (z1-z0)-0.66)
        zc = (z0+z1)/2
        dframe = outer + 0.030
        dglass = outer + 0.020
        frame_depth = 0.065
        edge_w = 0.13
        inner_w = win_w - 2*edge_w
        pane_w = (inner_w-0.08)/2
        for k in range(nwin):
            s = sp['smin'] + spacing*(k+0.5)
            bot, top = zc-window_h/2, zc+window_h/2
            # Two tall panes in one grouped opening.
            box(glass, origin,t,n,s,dglass,bot+edge_w,top-edge_w,inner_w,0.035)
            # Limestone jambs, head and sill.
            box(stone,origin,t,n,s-win_w/2+edge_w/2,dframe,bot,top,edge_w,frame_depth)
            box(stone,origin,t,n,s+win_w/2-edge_w/2,dframe,bot,top,edge_w,frame_depth)
            box(stone,origin,t,n,s,dframe,top-edge_w/2,top+edge_w/2,win_w,frame_depth)
            box(stone,origin,t,n,s,dframe,bot-edge_w/2,bot+edge_w/2,win_w,frame_depth)
            # Central mullion and one transom make the tall group legible at distance.
            if bronze:
                box(bronze,origin,t,n,s,dframe+0.012,bot+edge_w,top-edge_w,0.055,0.03)
                box(bronze,origin,t,n,s,dframe+0.012,zc,zc+0.045,inner_w,0.03)
    elif band == 2:
        # Broad piers align with upper-storey masonry fields. Preserve storefront
        # glass between them; omit the pier nearest the photo-estimated main entry
        # on the south frontage (Edge 75, around 70% of its run).
        pier_w = min(0.92, spacing*0.23)
        for j in range(nwin+1):
            s = sp['smin'] + spacing*j
            if j == 0: s += pier_w/2
            elif j == nwin: s -= pier_w/2
            skip_entry = ('Edge_75_Band2' in name and abs((s-sp['smin'])/length-0.70) < 0.08)
            if skip_entry:
                continue
            box(brick,origin,t,n,s,outer-0.095,z0+0.03,z1-0.03,pier_w,0.24)

for mat, name in ((brick,'WALC_R4_Masonry_Bay_Fields'),
                  (stone,'WALC_R4_Window_Frames'),
                  (glass,'WALC_R4_Grouped_Window_Glazing')):
    make_obj(name, mat)
if bronze:
    make_obj('WALC_R4_Window_Mullions', bronze)
# Ground-floor piers share the brick aggregate with upper spandrel fields; keep
# a distinct semantic collection object by reassigning only the new Band2 boxes
# is unnecessary for viewing, so the main combined brick object carries both.

foliage = next((lib for lib in bpy.data.libraries if 'engineering_foliage_library.blend' in lib.filepath), None)
if foliage:
    foliage.filepath = '//../site/foliage_library/engineering_foliage_library.blend'

summary = {
    'source_hash': 'c9ca2cfe413898780445bade8e729e22510535aed123407c4d11e5c28f53ec65',
    'input_hash_for_this_save': actual,
    'selected_long_facade_spans': {k: round(v['length'],3) for k,v in spans.items() if k.endswith(('_Band2','_Band4','_Band6'))},
    'window_groups_by_span': group_count_by_edge,
    'upper_glazed_bands': [4, 6],
    'facade_geometry_note': 'Upper band fields are solid brick panels with paired tall windows and limestone surrounds; first-floor glass ribbons remain between deep brick piers. Approximate geometry from official exterior photo; not a measured elevation.',
    'roof': 'Unchanged; no authoritative measured roof plan/elevation found.',
    'interior': 'Unchanged. Compared with official classroom-floor-plan PDF and Purdue emergency plan; room program aligns schematically, but no scale registration/as-built layout verification was available.',
    'root_transform': {'location':list(root.location),'rotation':list(root.rotation_euler),'scale':list(root.scale)},
    'foliage_library': foliage.filepath if foliage else None,
}
bpy.ops.wm.save_as_mainfile(filepath=str(ASSET), compress=True)
summary['saved_hash'] = hashlib.sha256(ASSET.read_bytes()).hexdigest()
(ROOT/'audit/walc_refine/r4_change_set.json').write_text(json.dumps(summary,indent=2), encoding='utf-8')
print(json.dumps(summary,indent=2))
