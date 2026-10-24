import bpy, hashlib, json
from pathlib import Path

ROOT = Path(r'C:\Users\Tobin\Documents\Blender\PurdueMap')
ASSET = ROOT / 'modular/buildings/knoy_hall.blend'
OUT = ROOT / 'audit/complete_knoy/r20_geometry_baseline_for_r21.json'
bpy.ops.wm.open_mainfile(filepath=str(ASSET))

def object_record(obj):
    rec = {
        'type': obj.type,
        'world': [[round(float(v), 7) for v in row] for row in obj.matrix_world],
    }
    if obj.type == 'MESH':
        rec['verts'] = [[round(float(c), 7) for c in v.co] for v in obj.data.vertices]
        rec['faces'] = [list(p.vertices) for p in obj.data.polygons]
    return rec

records = {obj.name: object_record(obj) for obj in bpy.data.objects}
digest = hashlib.sha256(json.dumps(records, sort_keys=True, separators=(',', ':')).encode()).hexdigest()
result = {
    'baseline_revision': 20,
    'captured_from': 'modular/buildings/knoy_hall.blend',
    'scene_object_count': len(bpy.data.objects),
    'mesh_object_count': sum(obj.type == 'MESH' for obj in bpy.data.objects),
    'all_object_mesh_and_world_matrix_sha256': digest,
    'method': 'Reopened R20 source in Blender; hash covers each scene object type and world matrix plus every mesh vertex coordinate and polygon vertex index. No file was saved or modified by capture.'
}
OUT.write_text(json.dumps(result, indent=2) + '\n', encoding='utf-8')
print(json.dumps(result, indent=2))
