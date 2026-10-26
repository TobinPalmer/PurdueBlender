import bpy, bmesh, json, math, os
from mathutils import Vector
from mathutils.geometry import tessellate_polygon

folder = os.path.dirname(__file__)
with open(os.path.join(folder, 'build_config.json'), encoding='utf-8-sig') as f:
    cfg = json.load(f)
with open(os.path.join(folder, 'source_mesh_snapshot.json'), encoding='utf-8-sig') as f:
    source = json.load(f)

obj = bpy.data.objects.get(cfg['object_name'])
coll = bpy.data.collections.get(cfg['collection_name'])
if not bpy.data.filepath or obj is None or coll is None or obj not in coll.objects[:] or len(coll.objects) != 1:
    raise RuntimeError('Assigned church collection mismatch')

old_mesh = obj.data
world = obj.matrix_world.copy()
inv = world.inverted_safe()
# The preserved import snapshot supplies the exact original ring. Rebuild from it so
# rerunning this script replaces this building's generated details instead of stacking them.
ring_local = []
for v in source['vertices_local']:
    p = Vector(v)
    if abs(p.z) < 1e-6:
        xy = (round(p.x, 6), round(p.y, 6))
        if xy not in {(round(q.x, 6), round(q.y, 6)) for q in ring_local}:
            ring_local.append(p.copy())
ring = [world @ p for p in ring_local]
if len(ring) != 24:
    raise RuntimeError(f'Expected the 24-node source ring, found {len(ring)}')

eaves = float(cfg['wall_eaves_m'])
peak = float(cfg['gable_peak_m'])
gable = cfg['main_gable_bounds_xy_m']
x0, x1 = float(gable['min_x']), float(gable['max_x'])
y0, y1 = float(gable['min_y']), float(gable['max_y'])
xc = (x0 + x1) / 2.0
if not (eaves < peak and x0 < xc < x1 and y0 < y1):
    raise RuntimeError('Invalid gable dimensions')

# Verify the approximate raised gable stays inside the mapped source footprint.
def inside_polygon(x, y):
    inside = False
    for i, a in enumerate(ring):
        b = ring[i - 1]
        if (a.y > y) != (b.y > y) and x < (b.x - a.x) * (y - a.y) / (b.y - a.y) + a.x:
            inside = not inside
    return inside
for corner in ((x0,y0),(x1,y0),(x1,y1),(x0,y1)):
    if not inside_polygon(*corner):
        raise RuntimeError(f'Approximate gable bounds leave the source footprint at {corner}')

# Keep all materials local to this building asset.
tag = cfg['asset_id']
def material(name, color, roughness=0.78, metallic=0.0):
    m = bpy.data.materials.get(tag + '_' + name) or bpy.data.materials.new(tag + '_' + name)
    m.diffuse_color = (*color, 1.0)
    m.use_nodes = True
    bsdf = m.node_tree.nodes.get('Principled BSDF')
    if bsdf:
        bsdf.inputs['Base Color'].default_value = (*color, 1.0)
        bsdf.inputs['Roughness'].default_value = roughness
        bsdf.inputs['Metallic'].default_value = metallic
    return m
wall = material('Masonry', (0.34, 0.12, 0.075))
stone = material('Limestone', (0.62, 0.55, 0.44))
glass = material('Glazing', (0.025, 0.08, 0.12), 0.22, 0.05)
roof = material('Shingle_Roof', (0.12, 0.105, 0.09), 0.9)
annex_roof = material('Low_Roof', (0.24, 0.22, 0.20), 0.9)
mats = [wall, stone, glass, roof, annex_roof]
verts, faces, mat_ids = [], [], []
def add_face(indices, mat_id):
    faces.append(tuple(indices))
    mat_ids.append(mat_id)
def add_quad(points, mat_id):
    start = len(verts)
    verts.extend(tuple(inv @ p) for p in points)
    add_face((start, start+1, start+2, start+3), mat_id)
def add_triangle(points, mat_id):
    start = len(verts)
    verts.extend(tuple(inv @ p) for p in points)
    add_face((start, start+1, start+2), mat_id)
def add_box(center, tangent, normal, width, depth, height, mat_id):
    c = Vector(center)
    t = Vector((tangent.x, tangent.y, 0.0)).normalized()
    n = Vector((normal.x, normal.y, 0.0)).normalized()
    z = Vector((0.0, 0.0, 1.0))
    hw, hd, hh = width/2, depth/2, height/2
    offsets = [(-hw,-hd,-hh),(hw,-hd,-hh),(hw,hd,-hh),(-hw,hd,-hh),
               (-hw,-hd,hh),(hw,-hd,hh),(hw,hd,hh),(-hw,hd,hh)]
    start = len(verts)
    verts.extend(tuple(inv @ (c+t*a+n*b+z*h)) for a,b,h in offsets)
    for f in ((0,3,2,1),(4,5,6,7),(0,1,5,4),(1,2,6,5),(2,3,7,6),(3,0,4,7)):
        add_face(tuple(start+i for i in f), mat_id)

# Exact OSM ring remains the wall plan; only the vertical treatment changes.
area2 = sum(ring[i].x*ring[(i+1)%len(ring)].y-ring[(i+1)%len(ring)].x*ring[i].y for i in range(len(ring)))
sign = 1.0 if area2 > 0 else -1.0
for i, a0 in enumerate(ring):
    b0 = ring[(i+1)%len(ring)]
    delta = b0-a0
    length = Vector((delta.x, delta.y, 0.0)).length
    if length < 0.05:
        continue
    tangent = Vector((delta.x/length, delta.y/length, 0.0))
    normal = Vector((tangent.y, -tangent.x, 0.0))*sign
    a = Vector((a0.x,a0.y,0.0)); b = Vector((b0.x,b0.y,0.0))
    at = Vector((a0.x,a0.y,eaves)); bt = Vector((b0.x,b0.y,eaves))
    add_quad((a,b,bt,at), 0)
    # Repeated small sanctuary windows follow the source polygon perimeter.
    if length >= 5.0:
        count = max(1, int((length-2.0)//7.0))
        spacing = length/(count+1)
        width = min(1.45, spacing*0.58)
        pane_h = 1.35
        zc = min(2.7, eaves-pane_h/2-0.3)
        for k in range(count):
            p = a.lerp(b, (k+1)/(count+1))
            c = Vector((p.x,p.y,zc))+normal*0.055
            add_box(c,tangent,normal,width*0.76,0.07,pane_h,2)
            fc = c+normal*0.055
            bw = 0.075
            add_box(fc+Vector((0,0,pane_h/2)),tangent,normal,width,0.13,bw,1)
            add_box(fc-Vector((0,0,pane_h/2)),tangent,normal,width,0.13,bw,1)
            add_box(fc-tangent*(width/2-bw/2),tangent,normal,bw,0.13,pane_h,1)
            add_box(fc+tangent*(width/2-bw/2),tangent,normal,bw,0.13,pane_h,1)

# Low roof over the rest of the irregular source footprint (annex roof form unverified).
xy = [Vector((p.x,p.y)) for p in ring]
for tri in tessellate_polygon([xy]):
    add_triangle([Vector((xy[int(i)].x,xy[int(i)].y,eaves)) for i in tri],4)

# A single raised gable records the church form visible in the 2017 exterior photograph.
overhang = 0.30
left, right = x0-overhang, x1+overhang
front, back = y0-overhang, y1+overhang
z0, zr = eaves, peak
ridge0 = Vector((xc,front,zr)); ridge1 = Vector((xc,back,zr))
add_quad((Vector((left,front,z0)),ridge0,ridge1,Vector((left,back,z0))),3)
add_quad((ridge0,Vector((right,front,z0)),Vector((right,back,z0)),ridge1),3)
# Gable end infill at both ends of the ridge.
add_triangle((Vector((left,front,z0)),Vector((right,front,z0)),ridge0),0)
add_triangle((Vector((left,back,z0)),ridge1,Vector((right,back,z0))),0)
# The south gable gets a restrained clerestory and paired-door marker; both are approximate.
front_normal = Vector((0,1,0)); tangent = Vector((1,0,0))
add_box((xc,front+0.10,6.95),tangent,front_normal,1.55,0.08,2.70,2)
add_box((xc,front+0.17,1.38),tangent,front_normal,2.15,0.12,2.65,2)
add_box((xc-1.16,front+0.16,1.43),tangent,front_normal,0.12,0.16,2.70,1)
add_box((xc+1.16,front+0.16,1.43),tangent,front_normal,0.12,0.16,2.70,1)
add_box((xc,front+0.16,2.91),tangent,front_normal,2.42,0.16,0.14,1)

old_name = old_mesh.name
new_mesh = bpy.data.meshes.new(old_name+'_gable_revision')
new_mesh.from_pydata(verts, [], faces)
for m in mats:
    new_mesh.materials.append(m)
new_mesh.update()
for poly, mat_id in zip(new_mesh.polygons, mat_ids):
    poly.material_index = mat_id
bm = bmesh.new()
bm.from_mesh(new_mesh)
bmesh.ops.recalc_face_normals(bm, faces=list(bm.faces))
bm.to_mesh(new_mesh)
bm.free()
new_mesh.update()
obj.data = new_mesh
if old_mesh.users == 0:
    bpy.data.meshes.remove(old_mesh)
new_mesh.name = old_name
bpy.ops.wm.save_as_mainfile(filepath=bpy.data.filepath)
coords = [world @ v.co for v in new_mesh.vertices]
result = {
    'asset_id': cfg['asset_id'],
    'source_way': 473799725,
    'collection_objects': len(coll.objects),
    'source_ring_vertices': len(ring),
    'mesh_vertices': len(new_mesh.vertices),
    'mesh_faces': len(new_mesh.polygons),
    'height_m': round(max(v.z for v in coords)-min(v.z for v in coords),3),
    'height_status': cfg['modeled_height_status'],
    'gable_bounds_xy_m': [left,right,front,back],
    'footprint_preserved': True,
}
print('BUILD_RESULT_JSON='+json.dumps(result))
