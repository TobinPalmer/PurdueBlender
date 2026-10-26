from pathlib import Path
import bpy, hashlib, json
root = Path.cwd()
asset = root / 'modular/buildings/south_hall.blend'
expected = '9a848c6140c3abc6c6a1d7c7daa9d8c176d7a0452c3c489d56672812c573c410'
sha = hashlib.sha256(asset.read_bytes()).hexdigest()
bpy.ops.wm.open_mainfile(filepath=str(asset))
coll = bpy.data.collections.get('Asset_south_hall')
root_obj = bpy.data.objects.get('AssetRoot_south_hall')
if coll is None or root_obj is None:
    raise RuntimeError('Expected South Hall collection/root missing on fresh reopen')
objects = list(coll.all_objects)
meshes = [o for o in objects if o.type == 'MESH']
images = []
for image in bpy.data.images:
    if image.source == 'FILE':
        p = Path(bpy.path.abspath(image.filepath)) if image.filepath else None
        images.append({'name': image.name, 'filepath': image.filepath, 'packed': image.packed_file is not None, 'exists': bool(p and p.exists())})
materialless = [o.name for o in meshes if not o.data.materials or all(m is None for m in o.data.materials)]
world_points = [o.matrix_world @ __import__('mathutils').Vector(c) for o in meshes for c in o.bound_box]
bounds = [[min(p[i] for p in world_points), max(p[i] for p in world_points)] for i in range(3)] if world_points else None
report = {
  'asset': 'modular/buildings/south_hall.blend',
  'sha256': sha,
  'expected_sha256': expected,
  'hash_matches_expected': sha == expected,
  'fresh_reopen': True,
  'blender_version': bpy.app.version_string,
  'collection': coll.name,
  'collection_object_count': len(objects),
  'mesh_count': len(meshes),
  'material_count': len(bpy.data.materials),
  'materialless_meshes': materialless,
  'external_images': images,
  'missing_external_images': [i for i in images if not i['packed'] and not i['exists']],
  'root': {'name': root_obj.name, 'location': list(root_obj.location), 'rotation_euler': list(root_obj.rotation_euler), 'scale': list(root_obj.scale), 'matrix_world': [list(row) for row in root_obj.matrix_world]},
  'mesh_bounds_local_m': bounds,
  'scene_name': bpy.context.scene.name,
}
(root / 'audit/south_hall_refine/independent_reopen_r1.json').write_text(json.dumps(report, indent=2) + '\n', encoding='utf-8')
print(json.dumps(report, indent=2))
