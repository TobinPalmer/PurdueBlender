import bpy, hashlib, json, os

ROOT = r'C:\Users\Tobin\Documents\Blender\PurdueMap'
ASSET = os.path.join(ROOT, 'modular', 'buildings', 'neil_armstrong_hall.blend')
R8 = ASSET + '1'
OUT = os.path.join(ROOT, 'audit', 'complete_neil_armstrong', 'validation_r9.json')

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

r8_data, r8_root, r8_count = snapshot(R8)
r9_data, r9_root, r9_count = snapshot(ASSET)
added = sorted(set(r9_data) - set(r8_data))
removed = sorted(set(r8_data) - set(r9_data))
geometry_changed = sorted(name for name in set(r8_data) & set(r9_data)
                         if r8_data[name] != r9_data[name])
if added or removed or geometry_changed or r8_root != r9_root or r8_count != r9_count:
    raise RuntimeError(json.dumps({
        'added': added, 'removed': removed, 'geometry_or_transform_changed': geometry_changed,
        'roots': [r8_root, r9_root], 'object_counts': [r8_count, r9_count]
    }, indent=2))

col = bpy.data.collections['Asset_neil_armstrong_hall']
roof = {}
for name in ('ARMS_R5_Coarse_LiDAR_wing_low', 'ARMS_R5_Coarse_LiDAR_roof_high',
             'ARMS_R5_Coarse_LiDAR_wing_mid'):
    obj = bpy.data.objects[name]
    roof[name] = {
        'material_slots': [m.name if m else None for m in obj.data.materials],
        'r9_note': obj.get('roof_surface_material_r9'),
    }
if bpy.data.materials.get('ARMS_R9_Light_Roof_Surface') is None:
    raise RuntimeError('R9 pale roof appearance material missing after reopen')
if r9_root != (0.0, 0.0, 0.0) or r9_count != 445:
    raise RuntimeError('Unexpected source root placement or collection count')

result = {
    'building_id': 'neil_armstrong_hall',
    'revision': 'R9',
    'parent_revision': 'R8',
    'asset': 'modular/buildings/neil_armstrong_hall.blend',
    'asset_sha256': hashlib.sha256(open(ASSET, 'rb').read()).hexdigest(),
    'comparison_reference': 'modular/buildings/neil_armstrong_hall.blend1 (pre-save R8 snapshot)',
    'save_reopen': 'Passed: R9 source reopened from disk through Blender background process.',
    'geometry_and_transforms': 'All 445 collection objects match R8 mesh vertices, polygon indices and object transforms exactly at recorded precision.',
    'root_local_location': list(r9_root),
    'object_count': r9_count,
    'roof_materials_after_reopen': roof,
    'geometry_or_placement_changed': False,
}
with open(OUT, 'w', encoding='utf-8') as f:
    json.dump(result, f, indent=2)
    f.write('\n')
print(json.dumps(result, indent=2))
