"""Open the delivered ATO library in a clean Blender process and report invariants."""
import bpy, hashlib, json
from pathlib import Path

root_path = Path(__file__).resolve().parents[2]
asset_path = root_path / 'modular/buildings/massing_house_301840870_c45a5f4.blend'
report_path = Path(__file__).resolve().parent / 'fresh_open_validation.json'
bpy.ops.wm.open_mainfile(filepath=str(asset_path))
collection_name = 'Asset_massing_house_301840870_c45a5f4'
scene_name = 'Building_massing_house_301840870_c45a5f4'
col = bpy.data.collections.get(collection_name)
scene = bpy.data.scenes.get(scene_name)
obj = bpy.data.objects.get('House_301840870')
assert col and scene and obj and obj.name in col.objects and obj.type == 'MESH'
external = []
missing_external = []
for image in bpy.data.images:
    if image.source == 'FILE' and image.filepath and not image.packed_file:
        absolute = bpy.path.abspath(image.filepath)
        external.append({'stored_path': image.filepath, 'resolved_path': absolute, 'exists': Path(absolute).is_file()})
        if not Path(absolute).is_file():
            missing_external.append(absolute)
coords = [obj.matrix_world @ v.co for v in obj.data.vertices]
depsgraph = bpy.context.evaluated_depsgraph_get()
asset_coords = []
for item in col.objects:
    evaluated = item.evaluated_get(depsgraph)
    if evaluated.type != 'MESH':
        continue
    mesh = evaluated.to_mesh()
    asset_coords.extend(item.matrix_world @ vertex.co for vertex in mesh.vertices)
    evaluated.to_mesh_clear()
result = {
    'fresh_open': True,
    'asset': str(asset_path),
    'sha256': hashlib.sha256(asset_path.read_bytes()).hexdigest().upper(),
    'scene': scene.name,
    'collection': col.name,
    'root_object': obj.name,
    'root_location': list(obj.location),
    'root_rotation_radians': list(obj.rotation_euler),
    'root_scale': list(obj.scale),
    'asset_collection_object_count': len(col.objects),
    'asset_object_names': sorted(o.name for o in col.objects),
    'root_mesh_vertices': len(obj.data.vertices),
    'root_mesh_polygons': len(obj.data.polygons),
    'root_bounds_xyz_m': [[min(v[i] for v in coords), max(v[i] for v in coords)] for i in range(3)],
    'whole_collection_bounds_xyz_m': [[min(v[i] for v in asset_coords), max(v[i] for v in asset_coords)] for i in range(3)],
    'materials': sorted({m.name for o in col.objects for m in o.data.materials if m}),
    'external_unpacked_images': external,
    'missing_external_images': missing_external,
    'all_materials_nodes': all(m.use_nodes for m in bpy.data.materials),
}
report_path.write_text(json.dumps(result, indent=2), encoding='utf-8')
print(json.dumps(result, indent=2))
