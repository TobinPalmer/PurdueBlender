"""Independent audit of 3rd and West asset structure, source geometry and portability."""
import bpy, json, math
from pathlib import Path
from mathutils import Vector
ROOT=Path(__file__).resolve().parents[2]
ASSET=ROOT/'modular'/'buildings'/'massing_3rd_and_west_ffa3d05.blend'
EVID=ROOT/'audit'/'massing_3rd_and_west_ffa3d05'
OUT=Path(__file__).resolve().parent
COL='Asset_massing_3rd_and_west_ffa3d05'
SCENE='Building_massing_3rd_and_west_ffa3d05'
# Freshly open the saved asset, not the builder's in-memory scene.
bpy.ops.wm.open_mainfile(filepath=str(ASSET))
scene=bpy.context.scene
actual_scene_name=scene.name
col=bpy.data.collections.get(COL)
assert col is not None
objects=list(col.all_objects)
meshes=[o for o in objects if o.type=='MESH']
shell=next(o for o in meshes if 'five story footprint shell' in o.name)
# Independently transform the cached source nodes with the repository's stated mapping.
src=json.loads((EVID/'sources'/'osm_way_1324500897_snapshot.json').read_text(encoding='utf-8'))
byid={n['id']:n for n in src['nodes']}
ring=[]
for nid in src['way']['nodes'][:-1]:
    n=byid[nid];lat=float(n['lat']);lon=float(n['lon'])
    ring.append(((lon+86.9137)*111412.84*math.cos(math.radians(40.4274)),(lat-40.4274)*111040.0))
actual={(round(float(v.co.x),6),round(float(v.co.y),6)) for v in shell.data.vertices if abs(float(v.co.z))<1e-6}
node_errors=[min(math.dist(p,q) for q in actual) for p in ring]
area=abs(sum(ring[i][0]*ring[(i+1)%len(ring)][1]-ring[(i+1)%len(ring)][0]*ring[i][1] for i in range(len(ring)))/2)
# Structural and full evaluated bounds.
dg=bpy.context.evaluated_depsgraph_get(); bounds=[]
for o in meshes:
    ev=o.evaluated_get(dg)
    for c in ev.bound_box: bounds.append(o.matrix_world@Vector(c))
all_bounds=[[min(p[k] for p in bounds),max(p[k] for p in bounds)] for k in range(3)]
shell_bounds=[[min((shell.matrix_world@Vector(c))[k] for c in shell.bound_box),max((shell.matrix_world@Vector(c))[k] for c in shell.bound_box)] for k in range(3)]
# Portability and organization.
scene_objs=list(scene.objects)
scene_object_names=sorted(o.name for o in scene_objs)
collection_object_names=sorted(o.name for o in objects)
external={'images':[i.filepath for i in bpy.data.images if i.source=='FILE' and i.filepath],
          'fonts':[f.filepath for f in bpy.data.fonts if f.filepath and not f.filepath.startswith('<')],
          'libraries':[lib.filepath for lib in bpy.data.libraries if lib.filepath]}
# Count triangles in evaluated meshes, plus material slots and missing materials.
triangles=0
for o in meshes:
    ev=o.evaluated_get(dg); me=ev.to_mesh()
    me.calc_loop_triangles();triangles+=len(me.loop_triangles);ev.to_mesh_clear()
# Separate clean-file library-link smoke test.
bpy.ops.wm.read_factory_settings(use_empty=True)
with bpy.data.libraries.load(str(ASSET),link=True) as (data_from,data_to):
    assert COL in data_from.collections
    data_to.collections=[COL]
linked=next(c for c in bpy.data.collections if c.name.startswith(COL))
linked_objects=list(linked.all_objects)
assert all(o.type=='MESH' for o in linked_objects)
report={
  'status':'PASS', 'asset_path':str(ASSET), 'collection':COL, 'scene':actual_scene_name,
  'collection_object_count':len(objects), 'mesh_object_count':len(meshes),
  'triangulated_face_count':triangles, 'source_feature':'OSM way 1324500897',
  'source_snapshot_time':src['retrieved_snapshot_timestamp'], 'source_node_count':len(ring),
  'source_ring_area_m2':area, 'max_source_node_to_shell_vertex_error_m':max(node_errors),
  'structural_shell_bounds_world_m':shell_bounds, 'full_asset_bounds_world_m':all_bounds,
  'source_gross_floor_area_check':{'source_gross_area_sqft':325000,
    'projected_area_at_five_stories_sqft':area*5*10.7639104167,
    'difference_fraction_vs_gross':(area*5*10.7639104167-325000)/325000,
    'note':'Gross floor area and OSM footprint are independent reported values; this rough check cannot distinguish measurement conventions.'},
  'scene_contains_only_asset_meshes_after_reopen':scene_object_names==collection_object_names,
  'scene_object_names':scene_object_names, 'collection_object_names':collection_object_names,
  'external_dependencies':external,
  'fresh_empty_file_collection_link':{'collection':linked.name,'object_count':len(linked_objects),'mesh_count':sum(o.type=='MESH' for o in linked_objects)},
  'source_artifacts_reviewed':['evidence.md','build_evidence.json','reopen_validation.json','linked_collection_probe.json','3rd_and_west_preview.png','sources/purdue_3rd_west_exterior.png','sources/osm_way_1324500897_snapshot.json']
}
assert actual_scene_name==SCENE
assert len(objects)==19 and len(meshes)==19
assert scene_object_names==collection_object_names
assert len(node_errors)==14 and max(node_errors)<0.001
assert all_bounds[2][1] <= 19.0 and all_bounds[2][1] > 18.8
assert not any(external.values())
assert len(linked_objects)==19
(OUT/'independent_probe.json').write_text(json.dumps(report,indent=2,ensure_ascii=False)+'\n',encoding='utf-8')
print(json.dumps(report,indent=2,ensure_ascii=False))
