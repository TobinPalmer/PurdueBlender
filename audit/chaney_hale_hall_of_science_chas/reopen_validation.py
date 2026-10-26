import bpy, json, math
from pathlib import Path
ROOT=Path(__file__).resolve().parents[2]
asset_id='massing_chaney_hale_hall_of_science_chas_6bb9ef7'
asset=ROOT/'modular'/'buildings'/f'{asset_id}.blend'
source=ROOT/'audit'/'chaney_hale_hall_of_science_chas'/'sources'/'purdue_gis_fid945_live.json'
out=ROOT/'audit'/'chaney_hale_hall_of_science_chas'/'reopen_validation.json'
with open(source,encoding='utf8') as f: data=json.load(f)
feature=next(x for x in data['features'] if x['attributes'].get('FID')==945)
ring=feature['geometry']['rings'][0]
source_xy=[((lon+86.9137)*111412.84*math.cos(math.radians(40.4274)),(lat-40.4274)*111040.0) for lon,lat in ring]
if source_xy[0]==source_xy[-1]: source_xy.pop()
scene=bpy.context.scene
coll=bpy.data.collections.get(f'Asset_{asset_id}')
objs=list(coll.objects) if coll else []
obj=bpy.data.objects.get('Chaney-Hale Hall of Science (CHAS)')
assert coll and len(objs)==1 and obj and obj.type=='MESH'
assert scene.name==f'Building_{asset_id}'
assert obj.name==objs[0].name and not obj.modifiers
mesh=obj.evaluated_get(bpy.context.evaluated_depsgraph_get()).to_mesh()
verts=[obj.matrix_world@v.co for v in mesh.vertices]
obj.evaluated_get(bpy.context.evaluated_depsgraph_get()).to_mesh_clear()
base=[(v.x,v.y) for v in verts if abs(v.z)<1e-5]
base_unique=[]
for p in base:
 if not any(math.dist(p,q)<1e-5 for q in base_unique): base_unique.append(p)
nearest=[min(math.dist(p,q) for q in base_unique) for p in source_xy]
# A bottom ring point appears as a vertex in each adjacent wall face.
source_missing=[p for p in source_xy if min((math.dist(p,q) for q in base_unique),default=1e9)>1e-4]
bounds=[[min(v[i] for v in verts),max(v[i] for v in verts)] for i in range(3)]
res={
 'asset_path':str(asset.relative_to(ROOT)).replace('\\','/'),
 'reopened_in_blender':bpy.app.version_string,
 'scene':scene.name,
 'collection':coll.name,
 'object_count_in_export_collection':len(objs),
 'objects':[{'name':o.name,'type':o.type,'vertices':len(o.data.vertices),'polygons':len(o.data.polygons),'modifiers':[m.name for m in o.modifiers],'materials':[m.name for m in o.data.materials]} for o in objs],
 'evaluated_bounds_world_m':bounds,
 'source_ring_vertices':len(source_xy),
 'unique_shell_vertices_at_ground_z':len(base_unique),
 'max_source_to_shell_nearest_vertex_error_m':max(nearest) if nearest else None,
 'missing_source_ring_points_over_0_1mm':[list(p) for p in source_missing],
 'object_location':[float(x) for x in obj.location],
 'object_rotation_euler':[float(x) for x in obj.rotation_euler],
 'object_scale':[float(x) for x in obj.scale],
 'external_image_paths':[im.filepath for im in bpy.data.images if im.source=='FILE' and im.filepath],
 'checks':{
  'stable_scene_collection_object':True,
  'single_mesh_object':len(objs)==1 and obj.type=='MESH',
  'evaluated_geometry_has_vertices':len(verts)>0,
  'source_ground_ring_present_within_0_1mm':not source_missing,
  'no_modifiers':not obj.modifiers,
  'no_external_images':not [im.filepath for im in bpy.data.images if im.source=='FILE' and im.filepath],
  'identity_object_transform':all(abs(x)<1e-7 for x in obj.location) and all(abs(x)<1e-7 for x in obj.rotation_euler) and all(abs(x-1)<1e-7 for x in obj.scale)
 },
 'result':'PASS' if not source_missing else 'FAIL'
}
out.write_text(json.dumps(res,indent=2)+'\n',encoding='utf8')
print(json.dumps(res,indent=2))
assert res['result']=='PASS'
