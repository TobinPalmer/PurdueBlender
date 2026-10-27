"""Fresh-process validation for the local-coordinate Bailey Hall asset."""
import bpy, hashlib, json
from pathlib import Path

root = Path(__file__).resolve().parents[2]
asset_path = root / 'modular/buildings/massing_ralph_bettye_bailey_hall_406c4db.blend'
report_path = Path(__file__).resolve().parent / 'fresh_open_validation.json'
bpy.ops.wm.open_mainfile(filepath=str(asset_path))
scene_name = 'Building_massing_ralph_bettye_bailey_hall_406c4db'
collection_name = 'Asset_massing_ralph_bettye_bailey_hall_406c4db'
obj = bpy.data.objects.get('Ralph & Bettye Bailey Hall')
scene = bpy.data.scenes.get(scene_name)
collection = bpy.data.collections.get(collection_name)
assert obj and obj.type == 'MESH' and scene and collection
assert obj.name in collection.objects and len(collection.objects) == 1
assert tuple(round(v, 6) for v in obj.location) == (0.0, 0.0, 0.0)
assert tuple(round(v, 6) for v in obj.rotation_euler) == (0.0, 0.0, 0.0)
assert tuple(round(v, 6) for v in obj.scale) == (1.0, 1.0, 1.0)
origin = list(obj.get('proposed_master_placement_xy_m', []))
assert len(origin) == 2 and obj.get('gis_feature_id') == 411
coords = [v.co for v in obj.data.vertices]
bounds = [[min(v[i] for v in coords), max(v[i] for v in coords)] for i in range(3)]
materials = [m.name for m in obj.data.materials if m]
images = []
for image in bpy.data.images:
    if image.source == 'FILE' and image.filepath:
        path = bpy.path.abspath(image.filepath)
        images.append({'path': image.filepath, 'exists': Path(path).is_file(), 'packed': bool(image.packed_file)})
result = {
    'fresh_open': True,
    'blender_version': bpy.app.version_string,
    'asset_path': str(asset_path),
    'sha256': hashlib.sha256(asset_path.read_bytes()).hexdigest().upper(),
    'scene': scene.name,
    'collection': collection.name,
    'collection_object_count': len(collection.objects),
    'object': obj.name,
    'asset_id': obj.get('asset_id'),
    'source_fid': obj.get('gis_feature_id'),
    'root_transform': {'location': list(obj.location), 'rotation': list(obj.rotation_euler), 'scale': list(obj.scale)},
    'proposed_master_placement_xy_m': origin,
    'local_geometry_bounds_xyz_m': bounds,
    'world_bounds_if_placed_at_proposed_origin_xyz_m': [[bounds[0][0]+origin[0],bounds[0][1]+origin[0]],[bounds[1][0]+origin[1],bounds[1][1]+origin[1]],bounds[2]],
    'mesh_vertices': len(obj.data.vertices),
    'mesh_faces': len(obj.data.polygons),
    'material_count': len(materials),
    'materials': materials,
    'interior_face_count': sum(1 for p in obj.data.polygons if p.material_index >= 5),
    'image_dependencies': images,
    'interior_status': obj.get('interior_status'),
}
report_path.write_text(json.dumps(result, indent=2), encoding='utf-8')
print(json.dumps(result, indent=2))
