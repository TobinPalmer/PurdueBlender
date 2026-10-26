import bpy, json, os
from mathutils import Vector

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..'))
ASSET = os.path.join(ROOT, 'modular', 'buildings', 'massing_hawkins_hall_282335f.blend')
OUT = os.path.join(os.path.dirname(__file__), 'final_validation.json')
bpy.ops.wm.open_mainfile(filepath=ASSET)
asset_id = 'massing_hawkins_hall_282335f'
coll_name = 'Asset_' + asset_id
scene_name = 'Building_' + asset_id
coll = bpy.data.collections.get(coll_name)
scene = bpy.data.scenes.get(scene_name)
assert coll is not None and scene is not None
assert scene.get('building_id') == asset_id
deps = bpy.context.evaluated_depsgraph_get()
points=[]
for obj in coll.objects:
    if obj.type != 'MESH':
        continue
    evaluated=obj.evaluated_get(deps)
    mesh=evaluated.to_mesh()
    points.extend([evaluated.matrix_world @ v.co for v in mesh.vertices])
    evaluated.to_mesh_clear()
assert points
mins=[min(v[i] for v in points) for i in range(3)]
maxs=[max(v[i] for v in points) for i in range(3)]
external_assets=[]
for img in bpy.data.images:
    if img.source == 'FILE' and img.filepath and not img.packed_file:
        external_assets.append({'path':img.filepath,'resolved_exists':os.path.exists(bpy.path.abspath(img.filepath))})
mesh_objects=[o for o in coll.objects if o.type=='MESH']
result={
    'asset':os.path.relpath(ASSET, ROOT).replace('\\','/'),
    'scene':scene.name,
    'collection':coll.name,
    'object_count':len(coll.objects),
    'mesh_object_count':len(mesh_objects),
    'object_names':[o.name for o in coll.objects],
    'bounds_m':{'x':[mins[0],maxs[0]],'y':[mins[1],maxs[1]],'z':[mins[2],maxs[2]]},
    'dimensions_m':[maxs[i]-mins[i] for i in range(3)],
    'relative_external_images':external_assets,
    'scene_height_note':scene.get('height_note'),
    'save_reopened':True,
}
assert len(coll.objects)==7, f'Unexpected exported collection count: {len(coll.objects)}'
assert abs(mins[2])<1e-5 and abs(maxs[2]-42.737)<0.002
assert all(img['path'].startswith('//') and img['resolved_exists'] for img in external_assets)
with open(OUT,'w',encoding='utf-8') as f: json.dump(result,f,indent=2)
print('HAWKINS_FINAL_VALIDATION',json.dumps(result))
