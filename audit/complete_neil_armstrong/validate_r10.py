import bpy, hashlib, json, os

ROOT = r'C:\Users\Tobin\Documents\Blender\PurdueMap'
ASSET = os.path.join(ROOT, 'modular', 'buildings', 'neil_armstrong_hall.blend')
R9 = ASSET + '1'
OUT = os.path.join(ROOT, 'audit', 'complete_neil_armstrong', 'validation_r10.json')

def snapshot(path):
    bpy.ops.wm.open_mainfile(filepath=path)
    col = bpy.data.collections['Asset_neil_armstrong_hall']
    root = bpy.data.objects['AssetRoot_neil_armstrong_hall']
    data = {}
    for obj in col.objects:
        mesh = None
        if obj.type == 'MESH':
            mesh = (
                tuple((round(v.co.x, 6), round(v.co.y, 6), round(v.co.z, 6)) for v in obj.data.vertices),
                tuple(tuple(p.vertices) for p in obj.data.polygons),
            )
        data[obj.name] = {
            'type': obj.type,
            'matrix': tuple(round(float(x), 8) for row in obj.matrix_basis for x in row),
            'mesh': mesh,
        }
    return data, tuple(root.location), len(col.objects)

r9_data, r9_root, r9_count = snapshot(R9)
r10_data, r10_root, r10_count = snapshot(ASSET)
added = sorted(set(r10_data) - set(r9_data))
removed = sorted(set(r9_data) - set(r10_data))
geometry_changed = sorted(name for name in set(r9_data) & set(r10_data)
                         if r9_data[name] != r10_data[name])
if added or removed or geometry_changed or r9_root != r10_root or r9_count != r10_count:
    raise RuntimeError(json.dumps({
        'added': added, 'removed': removed, 'geometry_or_transform_changed': geometry_changed,
        'roots': [r9_root, r10_root], 'object_counts': [r9_count, r10_count]
    }, indent=2))

col = bpy.data.collections['Asset_neil_armstrong_hall']
face_counts = {}
for name in ('ARMS_East_Roof_Slab', 'ARMS_West_Roof_Slab'):
    obj = bpy.data.objects[name]
    counts = {'pale': 0, 'red': 0}
    for poly in obj.data.polygons:
        if poly.normal.z > 0.75:
            mat = obj.data.materials[poly.material_index].name
            if mat == 'ARMS_R9_Light_Roof_Surface': counts['pale'] += 1
            elif mat == 'ARMS_Mayflower_Red_ACM': counts['red'] += 1
    if counts != {'pale': 83, 'red': 13}:
        raise RuntimeError(f'Unexpected material assignment for {name}: {counts}')
    face_counts[name] = counts
if r10_root != (0.0, 0.0, 0.0) or r10_count != 445:
    raise RuntimeError('Unexpected source root placement or collection count')

result = {
    'building_id': 'neil_armstrong_hall',
    'revision': 'R10',
    'parent_revision': 'R9',
    'asset': 'modular/buildings/neil_armstrong_hall.blend',
    'asset_sha256': hashlib.sha256(open(ASSET, 'rb').read()).hexdigest(),
    'comparison_reference': 'modular/buildings/neil_armstrong_hall.blend1 (pre-save R9 snapshot)',
    'save_reopen': 'Passed: Blender reopened R10 from disk.',
    'geometry_and_transforms': 'All 445 collection objects match R9 mesh vertices, polygon indices and object transforms exactly at recorded precision.',
    'root_local_location': list(r10_root),
    'object_count': r10_count,
    'roof_slab_top_material_face_counts': face_counts,
    'geometry_or_placement_changed': False,
}
with open(OUT, 'w', encoding='utf-8') as f:
    json.dump(result, f, indent=2)
    f.write('\n')
print(json.dumps(result, indent=2))
