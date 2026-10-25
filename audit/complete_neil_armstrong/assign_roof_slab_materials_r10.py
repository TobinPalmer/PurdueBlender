import bpy, hashlib, json, os

ROOT = r'C:\Users\Tobin\Documents\Blender\PurdueMap'
BASE = os.path.join(ROOT, 'audit', 'complete_neil_armstrong')
ASSET = os.path.join(ROOT, 'modular', 'buildings', 'neil_armstrong_hall.blend')
EXPECTED_R9 = '3ebc944ae939c1bc1056f8d5ebc9397dd8ca7bd37c50ae119036b01071413a0a'
actual = hashlib.sha256(open(ASSET, 'rb').read()).hexdigest()
if actual != EXPECTED_R9:
    raise RuntimeError('Neil asset changed after R9 review: ' + actual)
bpy.ops.wm.open_mainfile(filepath=ASSET)
with open(os.path.join(BASE, 'roof_slab_material_samples_r10.json'), encoding='utf-8') as f:
    samples = json.load(f)
pale = bpy.data.materials['ARMS_R9_Light_Roof_Surface']
red = bpy.data.materials['ARMS_Mayflower_Red_ACM']
changes = {}
for name, rows in samples.items():
    obj = bpy.data.objects[name]
    index_by_name = {m.name: i for i, m in enumerate(obj.data.materials) if m}
    for material in (pale, red):
        if material.name not in index_by_name:
            obj.data.materials.append(material)
            index_by_name[material.name] = len(obj.data.materials) - 1
    ids = {int(r['face_index']): r['material_class'] for r in rows}
    if len(ids) != 96:
        raise RuntimeError(f'Unexpected top face count for {name}: {len(ids)}')
    for poly in obj.data.polygons:
        if poly.index in ids:
            poly.material_index = index_by_name[pale.name if ids[poly.index] == 'pale' else red.name]
    obj['roof_surface_material_r10'] = 'Top-face appearance sampled at each face centroid from the registered Indiana 2023 orthophoto; clear red-family pixels retain red ACM, remaining neutral/shadow pixels use a pale neutral appearance. This does not identify actual roof substrate.'
    changes[name] = {'top_faces': len(ids), 'pale_faces': sum(v == 'pale' for v in ids.values()), 'red_faces': sum(v == 'red' for v in ids.values())}
    obj.data.update()
bpy.ops.wm.save_as_mainfile(filepath=ASSET)
print(json.dumps({'revision': 'R10', 'changes': changes, 'asset_sha256': hashlib.sha256(open(ASSET, 'rb').read()).hexdigest()}, indent=2))
