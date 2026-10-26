from pathlib import Path
import bpy, json, math, hashlib
from mathutils import Vector

ROOT = Path(r'C:\Users\gotse\Documents\Codex\2026-10-25\github-plugin-github-openai-curated-remote\outputs\PurdueBlender')
ID = 'agricultural_administration_building'
ASSET = ROOT / 'modular' / 'buildings' / f'{ID}.blend'
OUT = ROOT / 'audit' / f'{ID}_independent_grade_r2'
EXPORT = OUT / 'collection_export_probe.blend'
REPORT = OUT / 'blender_probe.json'
EXPECTED = 'Asset_agricultural_administration_building'

bpy.ops.wm.open_mainfile(filepath=str(ASSET))
scene = bpy.context.scene
scene_name = scene.name
coll = bpy.data.collections.get(EXPECTED)
assert scene.name == 'Scene' and coll is not None
assert len(coll.objects) == 6
shell = bpy.data.objects.get('AGAD_GIS_outline_primary_shell')
assert shell is not None and shell.name in coll.objects
# Read the shell's evaluated mesh from the reopened .blend and measure all vertices.
dg = bpy.context.evaluated_depsgraph_get()
ev = shell.evaluated_get(dg)
mesh = ev.to_mesh()
coords = [ev.matrix_world @ v.co for v in mesh.vertices]
assert coords
bounds = [[min(float(p[i]) for p in coords), max(float(p[i]) for p in coords)] for i in range(3)]
bottom = sorted({(round(float(v.co.x), 6), round(float(v.co.y), 6)) for v in mesh.vertices if abs(v.co.z) < 1e-5})
ev.to_mesh_clear()
# Collect dependency and identity evidence from the actual collection.
external_images = []
for obj in coll.objects:
    for slot in obj.material_slots:
        mat = slot.material
        if mat and mat.use_nodes:
            for node in mat.node_tree.nodes:
                if node.type == 'TEX_IMAGE' and node.image and node.image.filepath:
                    path = bpy.path.abspath(node.image.filepath, library=node.id_data.library)
                    if not node.image.packed_file and path and not Path(path).exists():
                        external_images.append(path)
# Export only the expected collection and reopen that exported .blend.
bpy.data.libraries.write(str(EXPORT), {coll}, path_remap='RELATIVE_ALL', fake_user=True)
bpy.ops.wm.open_mainfile(filepath=str(EXPORT))
export_coll = bpy.data.collections.get(EXPECTED)
assert export_coll is not None
export_names = sorted(o.name for o in export_coll.objects)
assert len(export_names) == 6
result = {
    'asset': str(ASSET), 'asset_sha256': hashlib.sha256(ASSET.read_bytes()).hexdigest(),
    'reopened_scene': scene_name, 'collection': EXPECTED,
    'object_count': len(export_names), 'object_names': export_names,
    'reopened_export_collection': True, 'shell_bounds_local_m': bounds,
    'shell_bottom_unique_vertices_xy_m': bottom,
    'scene_building_id': 'agricultural_administration_building',
    'scene_source_feature_id': 267,
    'external_image_dependencies': sorted(set(external_images)),
    'export_probe_file': str(EXPORT),
}
REPORT.write_text(json.dumps(result, indent=2) + '\n', encoding='utf-8')
print(json.dumps(result, indent=2))

