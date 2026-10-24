import bpy, json, hashlib
from pathlib import Path

ROOT = Path(r'C:\Users\Tobin\Documents\Blender\PurdueMap')
ASSET = ROOT / 'modular/buildings/knoy_hall.blend'
OUT = ROOT / 'audit/complete_knoy/validation_round20.json'
R19 = json.loads((ROOT / 'audit/complete_knoy/validation_round19.json').read_text(encoding='utf-8'))

def fingerprint(obj):
    payload = {
        'verts': [tuple(round(v, 7) for v in p.co) for p in obj.data.vertices],
        'faces': [tuple(p.vertices) for p in obj.data.polygons],
        'world': [tuple(round(v, 7) for v in row) for row in obj.matrix_world],
    }
    return hashlib.sha256(json.dumps(payload, sort_keys=True).encode()).hexdigest()

bpy.ops.wm.open_mainfile(filepath=str(ASSET))
required = list(R19['fingerprints'])
assert all(bpy.data.objects.get(name) for name in required)
assert bpy.context.scene.get('knoy_r20_review_status', '').startswith('Corrected R19 pano/ray mismatch')
assert 'ROUND 20' in bpy.data.texts['EVIDENCE_AND_INTERIOR_NOTES.txt'].as_string()
assert 'June 2009' in bpy.data.objects['KNOY_Fenestration_Ribbon_Glass']['r20_sightline_correction']
current = {name: fingerprint(bpy.data.objects[name]) for name in required}
assert current == R19['fingerprints'], {'expected': R19['fingerprints'], 'actual': current}
unpacked = [img.filepath for img in bpy.data.images if img.source == 'FILE' and img.filepath and not img.packed_file]
assert not unpacked, unpacked

result = {
    'revision': 20,
    'passed': True,
    'reopened_saved_asset': True,
    'blender_version': bpy.app.version_string,
    'scope': 'R20 corrected panorama/ray source metadata only. Four primary facade mesh fingerprints and world transforms match R19 exactly; no geometry, materials, or placement changed.',
    'scene_object_count': len(bpy.data.objects),
    'mesh_object_count': sum(obj.type == 'MESH' for obj in bpy.data.objects),
    'r19_baseline_fingerprints_match': True,
    'fingerprints': current,
    'unpacked_external_images': unpacked,
}
OUT.write_text(json.dumps(result, indent=2) + '\n', encoding='utf-8')
print(json.dumps(result, indent=2))
