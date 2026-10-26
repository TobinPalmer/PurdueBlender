import bpy, hashlib, json, math, sys
from pathlib import Path

root = Path(__file__).resolve().parents[2]
asset = root / 'modular/buildings/rawls_hall.blend'
baseline_sig = root / 'audit/batch4_rawls/r11_baseline_signatures.json'
out = root / 'audit/batch4_rawls/independent_reopen_r11.json'
scene_objs = list(bpy.context.scene.objects)
mesh_objs = [o for o in scene_objs if o.type == 'MESH']
collection = bpy.data.collections.get('Asset_rawls_hall')
root_obj = bpy.data.objects.get('AssetRoot_rawls_hall')
glass = bpy.data.objects.get('RAWL_SE_Diagonal_CurtainWall_Glass')
shell = bpy.data.objects.get('RAWL_Masonry_Exterior_Walls')
plan_wall = bpy.data.objects.get('RAWL_2026_Plan1086_02_00')
if not all((collection, root_obj, glass, shell, plan_wall)):
    raise RuntimeError('Required Rawls collection/root/geometry missing on fresh reopen')

def geom_sig(o):
    if o.type != 'MESH':
        return {'type': o.type, 'matrix': [[round(float(o.matrix_world[r][c]), 8) for c in range(4)] for r in range(4)]}
    me = o.data
    return {
        'type': o.type,
        'matrix': [[round(float(o.matrix_world[r][c]), 8) for c in range(4)] for r in range(4)],
        'vertices': [[round(float(v.co.x), 8), round(float(v.co.y), 8), round(float(v.co.z), 8)] for v in me.vertices],
        'faces': [list(p.vertices) for p in me.polygons],
    }

structural = {o.name: geom_sig(o) for o in scene_objs if o.name.startswith('RAWL_2026_Plan1086_') or o.name in ('RAWL_SE_Diagonal_CurtainWall_Glass', 'RAWL_Masonry_Exterior_Walls')}
if '--baseline-signature' in sys.argv:
    baseline_sig.write_text(json.dumps(structural, sort_keys=True, separators=(',', ':')) + '\n', encoding='utf-8')
    print('Wrote baseline signatures:', len(structural))
    raise SystemExit(0)
if not baseline_sig.exists():
    raise RuntimeError('Baseline signature file absent; run once against R10 baseline first')
base = json.loads(baseline_sig.read_text(encoding='utf-8'))
changed = [name for name, sig in structural.items() if name not in base or base[name] != sig]
missing = sorted(set(base) - set(structural))
added = sorted(set(structural) - set(base))

def material_report():
    materialless = []
    invalid_slots = []
    images, missing_images = [], []
    for o in mesh_objs:
        mats = list(o.data.materials)
        if not mats or all(m is None for m in mats): materialless.append(o.name)
        if any(p.material_index >= len(mats) or mats[p.material_index] is None for p in o.data.polygons): invalid_slots.append(o.name)
    for mat in bpy.data.materials:
        if mat.use_nodes and mat.node_tree:
            for n in mat.node_tree.nodes:
                if n.type == 'TEX_IMAGE' and n.image and n.image.source == 'FILE':
                    fp = bpy.path.abspath(n.image.filepath)
                    images.append({'material': mat.name, 'image': n.image.name, 'packed': bool(n.image.packed_file), 'filepath': fp})
                    if not n.image.packed_file and not Path(fp).exists(): missing_images.append(fp)
    return materialless, invalid_slots, images, missing_images

counts = {
    'chair_objects': sum('Chair' in o.name and '1086' in o.name for o in scene_objs),
    'desk_objects': sum(('Desk' in o.name or 'desk' in o.name) and '1086' in o.name for o in scene_objs),
    'projection_surfaces': sum('Projection_Surface' in o.name for o in scene_objs),
    'projection_content_cues': sum('Projector_Content' in o.name for o in scene_objs),
    'lectern_parts': sum('1086' in o.name and 'Lectern' in o.name for o in scene_objs),
    'tier_platforms': sum('1086' in o.name and 'Tier_' in o.name for o in scene_objs),
    'glass_panes': len(glass.data.polygons),
}
ml, invalid, images, missing_images = material_report()
matrix = [[float(root_obj.matrix_world[r][c]) for c in range(4)] for r in range(4)]
report = {
  'validation': 'Independent fresh reopen of saved asset in Blender ' + bpy.app.version_string,
  'asset': str(asset), 'sha256': hashlib.sha256(asset.read_bytes()).hexdigest(), 'reopened_saved_asset': True,
  'baseline_asset_sha256_expected': 'd361f211a8177e234d475493d6242ad396981b7f3fed29dc57f37f54e1026d9e',
  'scene': bpy.context.scene.name, 'scene_object_count': len(scene_objs), 'scene_mesh_count': len(mesh_objs),
  'export_collection': collection.name, 'export_collection_object_count': len(collection.all_objects),
  'root_world_matrix': matrix, 'counts': counts,
  'baseline_structural_objects': len(base), 'structural_changed_from_r10': changed, 'structural_missing_vs_r10': missing, 'structural_added_vs_r10': added,
  'materialless_meshes': ml, 'invalid_material_meshes': invalid, 'external_image_nodes': images, 'missing_external_images': missing_images,
  'linked_libraries': [lib.filepath for lib in bpy.data.libraries],
  'used_material_names': sorted({m.name for o in collection.all_objects if o.type == 'MESH' for m in o.data.materials if m}),
  'limitations': ['Standalone asset review does not verify master placement.', '62 chair objects correspond to the guide seat count but do not establish an exact seat-by-seat arrangement; 42 fixed desk/table objects are schematic.', 'Dual projection panels and screen cues are schematic; their exact location, size and content are unverified.', 'Visual render shows residual reflection and partial facade obstruction.', 'The 44-pane facade and plan/shell geometry are inherited unchanged from R10 and remain unsurveyed.', 'No ray clearances or full-room visibility are asserted by this geometry comparison.']
}
out.write_text(json.dumps(report, indent=2) + '\n', encoding='utf-8')
print(json.dumps({k:v for k,v in report.items() if k not in ('external_image_nodes','used_material_names')}, indent=2))
