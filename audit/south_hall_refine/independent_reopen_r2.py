from pathlib import Path
import hashlib, json
import bpy
from mathutils import Vector

root = Path.cwd()
asset = root / 'modular/buildings/south_hall.blend'
expected = '89fbdcf4959174fc91f9477822084de73b38149cfda55cb6ad17348a9289ed06'
sha_before = hashlib.sha256(asset.read_bytes()).hexdigest()
bpy.ops.wm.open_mainfile(filepath=str(asset))
coll = bpy.data.collections.get('Asset_south_hall')
root_obj = bpy.data.objects.get('AssetRoot_south_hall')
if coll is None or root_obj is None:
    raise RuntimeError('Expected South Hall collection/root missing on fresh reopen')
objects = list(coll.all_objects)
meshes = [o for o in objects if o.type == 'MESH']
depsgraph = bpy.context.evaluated_depsgraph_get()
points = []
for obj in meshes:
    evaluated = obj.evaluated_get(depsgraph)
    mesh = evaluated.to_mesh()
    try:
        points.extend(evaluated.matrix_world @ vertex.co for vertex in mesh.vertices)
    finally:
        evaluated.to_mesh_clear()
bounds = [[min(p[i] for p in points), max(p[i] for p in points)] for i in range(3)] if points else None
materialless = [o.name for o in meshes if not o.data.materials or all(m is None for m in o.data.materials)]
external_images = []
for image in bpy.data.images:
    if image.source == 'FILE':
        p = Path(bpy.path.abspath(image.filepath)) if image.filepath else None
        external_images.append({'name': image.name, 'filepath': image.filepath, 'packed': image.packed_file is not None, 'exists': bool(p and p.exists())})
report = {
    'asset': 'modular/buildings/south_hall.blend',
    'sha256': sha_before,
    'expected_sha256': expected,
    'hash_matches_expected': sha_before == expected,
    'fresh_reopen': True,
    'blender_version': bpy.app.version_string,
    'collection': coll.name,
    'collection_object_count': len(objects),
    'mesh_count': len(meshes),
    'material_count': len(bpy.data.materials),
    'materialless_meshes': materialless,
    'external_images': external_images,
    'missing_external_images': [i for i in external_images if not i['packed'] and not i['exists']],
    'root': {'name': root_obj.name, 'location': list(root_obj.location), 'rotation_euler': list(root_obj.rotation_euler), 'scale': list(root_obj.scale), 'matrix_world': [list(row) for row in root_obj.matrix_world]},
    'evaluated_mesh_bounds_local_m': bounds,
    'scene_name': bpy.context.scene.name,
}
(root / 'audit/south_hall_refine/independent_reopen_r2.json').write_text(json.dumps(report, indent=2) + '\n', encoding='utf-8')
print(json.dumps(report, indent=2))
