import bpy, json, math, os

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..'))
ASSET = os.path.join(ROOT, 'modular', 'buildings', 'native_american_educational_and_cultural_center_nacc.blend')
OUT = os.path.join(os.path.dirname(__file__), 'reopen_validation.json')
bpy.ops.wm.open_mainfile(filepath=ASSET)
collection = bpy.data.collections.get('Asset_native_american_educational_and_cultural_center_nacc')
objects = list(collection.all_objects) if collection else []
meshes = [obj for obj in objects if obj.type == 'MESH']
coordinates = [obj.matrix_world @ vertex.co for obj in meshes for vertex in obj.data.vertices]
bounds = [[round(min(point[axis] for point in coordinates), 3), round(max(point[axis] for point in coordinates), 3)] for axis in range(3)] if coordinates else []
materials = {material for obj in objects if hasattr(obj.data, 'materials') for material in obj.data.materials if material}
material_checks = []
for material in materials:
    nodes = list(material.node_tree.nodes) if material.use_nodes and material.node_tree else []
    material_checks.append({'material': material.name, 'noise': any(node.type == 'TEX_NOISE' for node in nodes), 'bump': any(node.type == 'BUMP' for node in nodes), 'principled': any(node.type == 'BSDF_PRINCIPLED' for node in nodes)})
names = {obj.name for obj in objects}
required_features = {
    'Fifth_Street_front_door': 'NACC_fifth_street_front_door' in names,
    'parking_lot_accessible_door': 'NACC_parking_lot_access_door' in names,
    'alley_rear_kitchen_door': 'NACC_alley_rear_kitchen_door' in names,
    'detached_storage_garage': 'NACC_detached_single_car_storage_garage' in names,
    'accessible_ramp': 'NACC_accessibility_ramp' in names,
    'source_described_room_110_back_porch': all(name in names for name in ('NACC_back_porch_room_110_deck', 'NACC_back_porch_room_110_roof')),
    'schematic_interior_collection': bpy.data.collections.get('NACC_SCHEMATIC_INTERIOR_NOT_AS_BUILT') is not None,
    'undocumented_front_porch_removed': not any(name.startswith('NACC_front_porch') for name in names),
}
external_images = [image.filepath for image in bpy.data.images if image.source == 'FILE' and image.filepath]
result = {
    'validation': 'reopened saved asset in Blender 5.2.3 LTS',
    'asset_file': os.path.relpath(ASSET, ROOT),
    'collection_found': collection is not None,
    'collection': collection.name if collection else None,
    'objects': len(objects),
    'mesh_objects': len(meshes),
    'local_bounds_m': bounds,
    'material_count': len(materials),
    'materials_all_procedural_noise_bump_principled': all(all(check[key] for key in ('noise', 'bump', 'principled')) for check in material_checks),
    'feature_checks': required_features,
    'external_image_paths': external_images,
    'result': 'PASS' if collection and len(meshes) > 500 and all(required_features.values()) and all(all(check[key] for key in ('noise', 'bump', 'principled')) for check in material_checks) and not external_images else 'FAIL',
}
with open(OUT, 'w', encoding='utf-8') as stream:
    json.dump(result, stream, indent=2)
print(json.dumps(result, indent=2))
