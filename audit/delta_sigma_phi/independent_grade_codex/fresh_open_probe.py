import bpy, hashlib, json, os
from mathutils import Vector

asset = os.path.abspath(bpy.data.filepath)
asset_id = 'massing_house_860826641_2c90f97'
scene_name = 'Building_' + asset_id
collection_name = 'Asset_' + asset_id
scene = bpy.context.scene
collection = bpy.data.collections.get(collection_name)
assert scene.name == scene_name, (scene.name, scene_name)
assert collection is not None, collection_name
objects = list(collection.objects)
meshes = [o for o in objects if o.type == 'MESH']
assert meshes, 'Expected mesh geometry'
depsgraph = bpy.context.evaluated_depsgraph_get()
evaluated_vertices = []
for obj in meshes:
    evaluated = obj.evaluated_get(depsgraph)
    mesh = evaluated.to_mesh()
    evaluated_vertices.extend(evaluated.matrix_world @ v.co for v in mesh.vertices)
    evaluated.to_mesh_clear()
bounds = [[min(v[i] for v in evaluated_vertices), max(v[i] for v in evaluated_vertices)] for i in range(3)]
materials = sorted({m.name for obj in meshes for m in obj.data.materials if m})
asset_sha = hashlib.sha256(open(asset, 'rb').read()).hexdigest()
external_images = [im.filepath for im in bpy.data.images if im.source == 'FILE' and im.filepath]
linked_libraries = [lib.filepath for lib in bpy.data.libraries]
report = {
    'independent_fresh_open': 'PASS',
    'blender_version': bpy.app.version_string,
    'asset': asset,
    'sha256': asset_sha,
    'scene': scene.name,
    'collection': collection.name,
    'collection_objects': len(objects),
    'mesh_objects': len(meshes),
    'mesh_vertices': sum(len(o.data.vertices) for o in meshes),
    'mesh_polygons': sum(len(o.data.polygons) for o in meshes),
    'materials': materials,
    'evaluated_bounds_local_m': bounds,
    'external_image_dependencies': external_images,
    'linked_library_dependencies': linked_libraries,
}
output = os.path.join(os.path.dirname(__file__), 'fresh_open_probe.json')
with open(output, 'w', encoding='utf-8') as f:
    json.dump(report, f, indent=2)
print(json.dumps(report, indent=2))
