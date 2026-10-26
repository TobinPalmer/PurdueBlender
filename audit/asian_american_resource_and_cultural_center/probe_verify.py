import bpy
import json
import os

HERE = os.path.dirname(os.path.abspath(__file__))
PROBE_PATH = os.path.join(HERE, 'aaarcc_collection_export_probe.blend')
OUT_PATH = os.path.join(HERE, 'collection_export_probe_verification.json')
COLLECTION = 'Asset_asian_american_resource_and_cultural_center'

bpy.ops.wm.open_mainfile(filepath=PROBE_PATH)
asset = bpy.data.collections.get(COLLECTION)
assert asset is not None
assert len(asset.objects) == 433, len(asset.objects)
assert not any(o.type in {'CAMERA', 'LIGHT'} for o in asset.objects)
assert all(o.type in {'MESH', 'FONT'} for o in asset.objects)
result = {
    'status': 'PASS',
    'probe_path': os.path.basename(PROBE_PATH),
    'collection': asset.name,
    'object_count': len(asset.objects),
    'type_counts': {kind: sum(o.type == kind for o in asset.objects) for kind in sorted({o.type for o in asset.objects})},
    'camera_or_light_count': sum(o.type in {'CAMERA', 'LIGHT'} for o in asset.objects),
    'opened_in_blender': bpy.app.version_string
}
with open(OUT_PATH, 'w', encoding='utf-8') as f:
    json.dump(result, f, indent=2)
print(json.dumps(result, indent=2))
