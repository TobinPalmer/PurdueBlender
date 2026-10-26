import bpy, json, hashlib, math
from pathlib import Path
from mathutils import Vector

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
ASSET = ROOT / 'modular/buildings/massing_wang_hall_wang_0dac5ab.blend'
SRC = ROOT / 'audit/wang_hall/sources/wang_hall_osm_way_301932787_full_2026-10-26.json'
OUT = HERE / 'blender_probe.json'
bpy.ops.wm.open_mainfile(filepath=str(ASSET))
coll = bpy.data.collections.get('Asset_massing_wang_hall_wang_0dac5ab')
scene = bpy.data.scenes.get('Building_massing_wang_hall_wang_0dac5ab')
assert coll is not None and scene is not None

def mesh_world(obj):
    deps = bpy.context.evaluated_depsgraph_get()
    ev = obj.evaluated_get(deps)
    if ev.type != 'MESH': return []
    me = ev.to_mesh()
    pts = [tuple(ev.matrix_world @ v.co) for v in me.vertices]
    ev.to_mesh_clear()
    return pts

deps = bpy.context.evaluated_depsgraph_get()
objs=[]; all_pts=[]; materials={}
for o in coll.objects:
    pts=mesh_world(o); all_pts.extend(pts)
    for m in getattr(o.data,'materials',[]) or []:
        if not m: continue
        nt=m.node_tree
        nodes=[]
        if nt:
            for n in nt.nodes:
                row={'type':n.bl_idname,'name':n.name}
                if n.type=='TEX_IMAGE' and n.image:
                    row['image_filepath']=n.image.filepath
                    row['image_packed']=bool(n.image.packed_file)
                nodes.append(row)
        materials[m.name]={'nodes':nodes,'external_images':[{'path':n.get('image_filepath'),'packed':n.get('image_packed')} for n in nodes if n.get('image_filepath')]}
    if pts:
        bounds={a:[min(p[i] for p in pts),max(p[i] for p in pts)] for i,a in enumerate('xyz')}
    else: bounds=None
    objs.append({'name':o.name,'type':o.type,'vertex_count_evaluated':len(pts),'bounds_m':bounds,'materials':[m.name for m in getattr(o.data,'materials',[]) or [] if m]})
assert all_pts
all_bounds={a:[min(p[i] for p in all_pts),max(p[i] for p in all_pts)] for i,a in enumerate('xyz')}
# Compare source outline against the actual exported structural footprint mesh's ground-level XY vertices.
source=json.loads(SRC.read_text(encoding='utf-8'))
way=next(e for e in source['elements'] if e.get('type')=='way' and e.get('id')==301932787)
nodes={e['id']:e for e in source['elements'] if e.get('type')=='node'}
raw=[((nodes[i]['lon']+86.9137)*111412.84*math.cos(math.radians(40.4274)),(nodes[i]['lat']-40.4274)*111040.0) for i in way['nodes']]
center=((min(x for x,y in raw)+max(x for x,y in raw))/2,(min(y for x,y in raw)+max(y for x,y in raw))/2)
ring=[(x-center[0],y-center[1]) for x,y in raw[:-1]]
struct_name='Wang Hall | source-backed structural footprint'
struct=next(o for o in coll.objects if o.name==struct_name)
struct_pts=mesh_world(struct)
# Nearest XY from each outline vertex to any exported mesh vertex; report per-vertex and max/min/mean.
nearest=[]
for x,y in ring:
    nearest.append(min(math.hypot(x-p[0],y-p[1]) for p in struct_pts))
# inspect file dependency references and collection transform
ext_libraries=[{'name':lib.name,'filepath':lib.filepath} for lib in bpy.data.libraries]
images=[{'name':im.name,'filepath':im.filepath,'packed':bool(im.packed_file)} for im in bpy.data.images]
placement=[o.name for o in bpy.data.objects if o.name.startswith('Placement_')]
result={
 'asset_path':str(ASSET), 'asset_sha256':hashlib.sha256(ASSET.read_bytes()).hexdigest(),
 'scene':scene.name,'asset_collection':coll.name,'asset_objects':len(coll.objects),'objects':objs,
 'evaluated_bounds_local_m':all_bounds,'source':{'way_id':301932787,'closed_ring_vertices':len(ring),'center_xy_m':list(center),'outline_vertices_centered_xy_m':[list(p) for p in ring]},
 'structural_outline_nearest_mesh_vertex_error_m':{'per_source_vertex':nearest,'maximum':max(nearest),'mean':sum(nearest)/len(nearest)},
 'anchor_xy_m':[98.2954902278031,339.9100960000692],
 'placement_markers_in_asset':placement,'materials':materials,'images':images,'external_libraries':ext_libraries,
 'probe_blender_version':bpy.app.version_string
}
OUT.write_text(json.dumps(result,indent=2),encoding='utf-8')
print('INDEPENDENT_WANG_PROBE',json.dumps({'sha256':result['asset_sha256'],'objects':len(coll.objects),'bounds':all_bounds,'ring_vertex_nearest_error_max':max(nearest),'placement_markers':placement,'libraries':len(ext_libraries),'blender':bpy.app.version_string}))
