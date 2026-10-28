import bpy, json, os

root = os.path.dirname(os.path.dirname(os.path.dirname(bpy.data.filepath)))
asset_id = 'massing_shealy_frances_m_residence_hall_a210e50'
obj_name = 'Shealy (Frances M.) Residence Hall'
collection_name = 'Asset_' + asset_id
scene_name = 'Building_' + asset_id
obj = bpy.data.objects.get(obj_name)
coll = bpy.data.collections.get(collection_name)
scene = bpy.data.scenes.get(scene_name)
if obj is None or coll is None or scene is None:
    raise RuntimeError('Expected object, collection or scene missing on fresh open')
mesh = obj.data
bounds = [[min(v.co[i] for v in mesh.vertices), max(v.co[i] for v in mesh.vertices)] for i in range(3)]
result = {
    'fresh_open': True,
    'blend_file': bpy.data.filepath,
    'asset_id': asset_id,
    'scene': scene.name,
    'collection': coll.name,
    'collection_object_count': len(coll.objects),
    'object': obj.name,
    'object_type': obj.type,
    'vertices': len(mesh.vertices),
    'faces': len(mesh.polygons),
    'uv_layers': [uv.name for uv in mesh.uv_layers],
    'materials': [m.name for m in mesh.materials],
    'bounds_local_m': bounds,
    'external_image_paths': [im.filepath for im in bpy.data.images if im.source == 'FILE' and im.filepath and not im.packed_file],
}
if len(coll.objects) != 1 or obj not in coll.objects[:]:
    raise RuntimeError('Export collection object contract failed')
out = os.path.join(os.path.dirname(__file__), 'fresh_open_validation.json')
with open(out, 'w', encoding='utf-8') as f:
    json.dump(result, f, indent=2)
print('FRESH_OPEN_VALIDATION=' + json.dumps(result))
