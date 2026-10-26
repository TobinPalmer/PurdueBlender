import bpy, bmesh, json, hashlib, math
from pathlib import Path
from mathutils import Vector

ROOT = Path.cwd()
ASSET = ROOT / 'modular' / 'buildings' / 'massing_university_lutheran_church_20903f1.blend'
EVIDENCE = ROOT / 'audit' / 'university_lutheran_church'
OUT = EVIDENCE / 'independent_grade_final' / 'fresh_open_probe.json'
EXPECTED_SCENE = 'Building_massing_university_lutheran_church_20903f1'
EXPECTED_COLLECTION = 'Asset_massing_university_lutheran_church_20903f1'

# Explicit fresh open of the exact library under review.
bpy.ops.wm.open_mainfile(filepath=str(ASSET))
scene = bpy.data.scenes.get(EXPECTED_SCENE)
collection = bpy.data.collections.get(EXPECTED_COLLECTION)
errors = []
if scene is None: errors.append('expected scene missing after fresh open')
if collection is None: errors.append('expected exported collection missing after fresh open')
objs = list(collection.all_objects) if collection else []
meshes = [o for o in objs if o.type == 'MESH']
mesh_materialless = [o.name for o in meshes if not o.data.materials or all(m is None for m in o.data.materials)]

all_points = []
for obj in objs:
    if obj.type not in {'MESH','CURVE','FONT','SURFACE','META'}: continue
    all_points.extend(obj.matrix_world @ Vector(c) for c in obj.bound_box)
world_bounds = [[min(p[i] for p in all_points), max(p[i] for p in all_points)] for i in range(3)] if all_points else None

# Recompute the target footprint directly from the raw OSM snapshot and compare the closed shell's ground ring.
osm = json.loads((EVIDENCE/'sources'/'osm_way_301932784.json').read_text(encoding='utf-8'))
way = next(e for e in osm['elements'] if e.get('type') == 'way' and e.get('id') == 301932784)
nodes = {e['id']: e for e in osm['elements'] if e.get('type') == 'node'}
lat0, lon0 = 40.4274, -86.9137
projected = [((nodes[n]['lon']-lon0)*111412.84*math.cos(math.radians(lat0)), (nodes[n]['lat']-lat0)*111040.0) for n in way['nodes'][:-1]]
envelope = bpy.data.objects.get('ULu | brick building envelope and sloped roof')
source_ring_xy = None
shell_ring_xy = None
hausdorff = None
shell_bounds = None
shell_topology = None
if envelope and envelope.type == 'MESH':
    mat = envelope.matrix_world
    bottom_z = min((mat @ v.co)[2] for v in envelope.data.vertices)
    shell_ring_xy = sorted({(round((mat @ v.co).x, 6), round((mat @ v.co).y, 6)) for v in envelope.data.vertices if abs((mat @ v.co).z-bottom_z)<1e-5})
    source_ring_xy = sorted({(round(x,6), round(y,6)) for x,y in projected})
    if source_ring_xy and shell_ring_xy:
        def directed(a,b): return max(min(math.hypot(x-u,y-v) for u,v in b) for x,y in a)
        hausdorff = max(directed(source_ring_xy,shell_ring_xy), directed(shell_ring_xy,source_ring_xy))
    ep = [mat @ Vector(c) for c in envelope.bound_box]
    shell_bounds = [[min(p[i] for p in ep),max(p[i] for p in ep)] for i in range(3)]
    bm=bmesh.new(); bm.from_mesh(envelope.data)
    shell_topology={'vertices':len(bm.verts),'edges':len(bm.edges),'faces':len(bm.faces),'boundary_edges':sum(e.is_boundary for e in bm.edges),'nonmanifold_edges':sum(not e.is_manifold for e in bm.edges),'loose_vertices':sum(not v.link_edges for v in bm.verts)}
    bm.free()
else:
    errors.append('source-matched structural shell missing')

# Inspect facade feature pattern in the saved geometry rather than trusting the builder report.
glass_windows = [o for o in meshes if 'ULu | main street bay' in o.name and 'dark glass' in o.name]
bay_names = sorted({o.name.split(' dark glass')[0] for o in glass_windows})
front_groups = sorted({int(name.split('bay ')[1].split(' ')[0]) for name in bay_names})
front_floors = sorted({int(name.rsplit('floor ',1)[1]) for name in bay_names})
road_glass_bounds=[]
for obj in glass_windows:
    pts=[obj.matrix_world @ Vector(c) for c in obj.bound_box]
    road_glass_bounds.append({'object':obj.name,'bounds_world_m':[[min(p[i] for p in pts),max(p[i] for p in pts)] for i in range(3)]})
texts=[]
for obj in objs:
    if obj.type=='FONT' and any(k in obj.name for k in ['UNIVERSITY sign lettering','LUTHERAN sign lettering','Fuel lettering']):
        texts.append({'name':obj.name,'body':obj.data.body,'size_m':obj.data.size,'object_bounds_m':[[min((obj.matrix_world@Vector(c))[i] for c in obj.bound_box),max((obj.matrix_world@Vector(c))[i] for c in obj.bound_box)] for i in range(3)]})

mats=sorted({m.name for o in objs if hasattr(o.data,'materials') for m in o.data.materials if m})
brick=next((m for m in bpy.data.materials if m.name=='ULu | mixed red-brown brick'),None)
brick_nodes=[]
if brick and brick.use_nodes and brick.node_tree:
    brick_nodes=sorted(n.type for n in brick.node_tree.nodes)
images=[{'name':i.name,'path':bpy.path.abspath(i.filepath),'packed':bool(i.packed_file)} for i in bpy.data.images if i.source=='FILE']
libraries=[bpy.path.abspath(l.filepath) for l in bpy.data.libraries]
missing_paths=[p for p in libraries if not Path(p).exists()]
used_obj_names={o.name for o in objs}
program_features={name:sum(name in o.name.lower() for o in objs) for name in ['sanctuary pew','altar','pulpit','fellowship table','cafe table','service counter','office desk','partition']}

source_register=json.loads((EVIDENCE/'source_register.json').read_text(encoding='utf-8'))
model_evidence=json.loads((EVIDENCE/'model_evidence.json').read_text(encoding='utf-8'))
expected_bounds=model_evidence['outline_bounds_xy_m']
bounds_err=max(abs(shell_bounds[i][j]-expected_bounds[i][j]) for i in range(2) for j in range(2)) if shell_bounds else None
for required in ['preview_three_quarter.png','preview_street_elevation.png','preview_top.png']:
    if not (EVIDENCE/required).exists(): errors.append('required preview missing: '+required)
for rel in model_evidence.get('validation',{}).get('fresh_open',{}).get('report',''),:
    pass
if not way.get('tags',{}).get('name','').startswith('University Lutheran Church'):
    errors.append('OSM way identity does not match the named building')
if len(front_groups)!=3 or len(front_floors)!=3 or len(glass_windows)!=9:
    errors.append(f'expected 3x3 broad street bay glazing; found {len(front_groups)} groups, {len(front_floors)} floors, {len(glass_windows)} glass objects')
if hausdorff is not None and hausdorff > 0.001: errors.append(f'footprint shell Hausdorff mismatch {hausdorff}')
if shell_topology and (shell_topology['boundary_edges'] or shell_topology['nonmanifold_edges']): errors.append('structural shell is not watertight')

sha=hashlib.sha256(ASSET.read_bytes()).hexdigest()
report={
 'asset_path':str(ASSET), 'asset_sha256':sha, 'fresh_open':True,
 'scene':scene.name if scene else None,'expected_scene_present':scene is not None,
 'collection':collection.name if collection else None,'expected_collection_present':collection is not None,
 'collection_object_count':len(objs),'mesh_count':len(meshes),'world_bounds_m':world_bounds,
 'osm_feature':{'id':way['id'],'name':way.get('tags',{}).get('name'),'address':way.get('tags',{}).get('addr:street'),'source_nodes':len(way['nodes'])-1,'projected_footprint_vertex_count':len(source_ring_xy or []),'structural_shell_ground_vertex_count':len(shell_ring_xy or []),'symmetric_hausdorff_m':hausdorff,'shell_bounds_world_m':shell_bounds,'shell_bounds_vs_evidence_max_error_m':bounds_err,'shell_topology':shell_topology},
 'street_facade':{'glass_bay_count':len(glass_windows),'bay_groups':front_groups,'floors_with_large_bays':front_floors,'window_bounds':road_glass_bounds,'signs':texts,'model_evidence_bay_groups':model_evidence.get('street_frontage',{}).get('main_window_bay_groups'),'road_source':model_evidence.get('street_frontage',{}).get('road_source')},
 'materials':mats,'brick_shader_nodes':brick_nodes,'materialless_meshes':mesh_materialless,
 'interior_program_object_counts':program_features,
 'file_dependencies':{'file_images':images,'linked_libraries':libraries,'missing_library_paths':missing_paths},
 'source_register_count':len(source_register.get('sources',[])),'source_snapshot_paths':model_evidence.get('validation',{}).get('source_snapshot_paths',[]),
 'errors':errors,'result':'PASS' if not errors and bounds_err is not None and bounds_err < 0.001 else 'FAIL'
}
OUT.write_text(json.dumps(report,indent=2)+'\n',encoding='utf-8')
print(json.dumps(report,indent=2))
