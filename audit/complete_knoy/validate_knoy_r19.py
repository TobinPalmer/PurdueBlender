import bpy, json, hashlib
from pathlib import Path

ROOT = Path(r'C:\Users\Tobin\Documents\Blender\PurdueMap')
ASSET = ROOT / 'modular/buildings/knoy_hall.blend'
OUT = ROOT / 'audit/complete_knoy/validation_round19.json'

def fingerprint(obj):
    payload = {
        'verts': [tuple(round(v, 7) for v in p.co) for p in obj.data.vertices],
        'faces': [tuple(p.vertices) for p in obj.data.polygons],
        'world': [tuple(round(v, 7) for v in row) for row in obj.matrix_world],
    }
    return hashlib.sha256(json.dumps(payload, sort_keys=True).encode()).hexdigest()

bpy.ops.wm.open_mainfile(filepath=str(ASSET))
required = ['KNOY_Fenestration_Ribbon_Glass', 'KNOY_Fenestration_Bronze_Mullions',
            'KNOY_Facade_Brick_Spandrels_R17', 'KNOY_Exterior_Masonry_Walls']
assert all(bpy.data.objects.get(n) for n in required)
assert 'ROUND 19' in bpy.data.texts['EVIDENCE_AND_INTERIOR_NOTES.txt'].as_string()
assert 'edge 18' in bpy.data.objects['KNOY_Fenestration_Ribbon_Glass']['r19_source_sightline']
assert bpy.context.scene.get('knoy_r19_review_status') == 'Targeted facade/archive research; no geometry changes.'

baseline = {
    'KNOY_Fenestration_Ribbon_Glass': '8df87255c1286d8f2b54f42a451751170f1d264fa2cf5065b53b887f03b49f68',
    'KNOY_Fenestration_Bronze_Mullions': '880ec03d0ba8cccacf0943aa9f4d3a0fb3d57cf3801e55b09a394c318ad4868e',
    'KNOY_Facade_Brick_Spandrels_R17': '6f9ac62c4c585a5cbee47e99e13d85f0acd014566d0bdd00861e57ef75bd71f2',
    'KNOY_Exterior_Masonry_Walls': 'b2dd838cac65ee448485e188d15cf661b5cd3f0776674cd5479bd1eb76eafffb',
}
current = {n: fingerprint(bpy.data.objects[n]) for n in required}
assert current == baseline, {'expected': baseline, 'actual': current}
unpacked = [img.filepath for img in bpy.data.images if img.source == 'FILE' and img.filepath and not img.packed_file]
assert not unpacked, unpacked

result = {
    'revision': 19,
    'passed': True,
    'reopened_saved_asset': True,
    'blender_version': bpy.app.version_string,
    'scope': 'R19 added only source/audit metadata. Four primary facade mesh fingerprints match the validated R18 baseline; no mesh geometry or world transforms changed.',
    'scene_object_count': len(bpy.data.objects),
    'mesh_object_count': sum(o.type == 'MESH' for o in bpy.data.objects),
    'r18_baseline_fingerprints_match': True,
    'fingerprints': current,
    'unpacked_external_images': unpacked,
}
OUT.write_text(json.dumps(result, indent=2) + '\n', encoding='utf-8')
print(json.dumps(result, indent=2))
