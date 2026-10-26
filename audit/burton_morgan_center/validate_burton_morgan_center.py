"""Reopen and validate the Burton D. Morgan library and collection export."""
import bpy, json, math
from pathlib import Path
from mathutils import Vector

ROOT = Path(__file__).resolve().parents[2]
ASSET = ROOT / 'modular' / 'buildings' / 'burton_morgan_center.blend'
EXPORT = ROOT / 'audit' / 'burton_morgan_center' / 'burton_morgan_center_collection_export.blend'
REPORT = ROOT / 'audit' / 'burton_morgan_center' / 'validation.json'
RENDER = ROOT / 'audit' / 'burton_morgan_center' / 'reopened_validation.png'
MANIFEST = json.loads((ROOT / 'modular' / 'manifest.json').read_text(encoding='utf-8'))
contract = next(x for x in MANIFEST['assets'] if x.get('id') == 'burton_morgan_center')
expected = contract['objects']
asset = bpy.data.collections.get(contract['collection'])
assert asset is not None, 'Expected collection is absent after reopening main library'
all_objects = list(asset.all_objects)
actual_short = {o.name for o in all_objects}
assert len(all_objects) == len(expected) == 384
assert sum(o.type == 'MESH' for o in all_objects) == 382
assert len(asset.children.get('Interior').objects) == 100
for name in expected:
    assert name in actual_short or any(o.get('manifest_object_name') == name for o in all_objects), name

def bounds(objects):
    coords = [o.matrix_basis @ Vector(corner) for o in objects if o.type == 'MESH' for corner in o.bound_box]
    return {'min': [min(p[i] for p in coords) for i in range(3)],
            'max': [max(p[i] for p in coords) for i in range(3)]}

main_bounds = bounds(all_objects)
assert abs(main_bounds['min'][0] - (-12.824)) < .02
assert abs(main_bounds['max'][0] - 12.824) < .02
assert abs(main_bounds['min'][1] - (-31.85)) < .03  # canopy/entry, beyond GIS structural perimeter
assert abs(main_bounds['max'][1] - 29.32) < .03
assert abs(main_bounds['max'][2] - 8.82) < .02
assert bpy.data.scenes.get('Scene') is not None

# Independently import the collection from the library export and verify its contents.
# Reserve the canonical IDs from Blender's global name allocator so the imported
# collection can be compared without automatic .001 suffixes. This is in-memory
# validation only; the saved source library is never changed by this step.
asset.name = 'Main file validation copy'
for i, obj in enumerate(all_objects):
    obj.name = f'MAIN_CHECK_{i:03d}'
with bpy.data.libraries.load(str(EXPORT), link=False) as (src, dst):
    assert contract['collection'] in src.collections
    dst.collections = [contract['collection']]
export_collection = next(c for c in dst.collections if c and c.name == contract['collection'])
export_objects = list(export_collection.all_objects)
assert len(export_objects) == len(all_objects)
assert sum(o.type == 'MESH' for o in export_objects) == 382
export_names = {o.name for o in export_objects}
for name in expected:
    assert name in export_names or any(o.get('manifest_object_name') == name for o in export_objects), name
export_bounds = bounds(export_objects)
print('MAIN_BOUNDS', json.dumps(main_bounds))
print('EXPORT_BOUNDS', json.dumps(export_bounds))
assert all(abs(main_bounds[k][i] - export_bounds[k][i]) < .01 for k in ('min', 'max') for i in range(3))

external_images = []
for material in bpy.data.materials:
    if material.node_tree:
        for node in material.node_tree.nodes:
            if node.type == 'TEX_IMAGE' and node.image and not node.image.packed_file:
                external_images.append(node.image.filepath)
assert not external_images, f'Unpacked external image dependencies: {external_images}'

scene = bpy.data.scenes['Scene']
scene.render.resolution_x = 900
scene.render.resolution_y = 630
scene.render.resolution_percentage = 100
scene.cycles.samples = 12
scene.render.filepath = str(RENDER)
bpy.ops.render.render(write_still=True)

report = {
    'building_id': 'burton_morgan_center',
    'asset_path': 'modular/buildings/burton_morgan_center.blend',
    'collection': contract['collection'],
    'main_file_reopened': True,
    'scene_present': True,
    'object_count': len(all_objects),
    'mesh_count': sum(o.type == 'MESH' for o in all_objects),
    'interior_collection_object_count': len(asset.children.get('Interior').objects),
    'manifest_names_verified': len(expected),
    'long_names_preserved_as_custom_properties': sum(1 for name in expected if name not in actual_short),
    'local_bounds_m': main_bounds,
    'bounds_note': 'Overall Y minimum includes the projecting entrance/canopy; source GIS structural perimeter begins near -29.185 m.',
    'collection_export_reopened_and_verified': True,
    'export_object_count': len(export_objects),
    'export_mesh_count': sum(o.type == 'MESH' for o in export_objects),
    'export_local_bounds_m': export_bounds,
    'export_bounds_tolerance_m': 0.01,
    'unpacked_external_image_dependencies': external_images,
    'reopened_render': 'audit/burton_morgan_center/reopened_validation.png',
    'validation_script': 'audit/burton_morgan_center/validate_burton_morgan_center.py',
}
REPORT.write_text(json.dumps(report, indent=2), encoding='utf-8')
print(json.dumps(report, indent=2))
