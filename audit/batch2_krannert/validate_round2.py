import bpy, json, os
from mathutils import Vector

ROOT = r'C:/Users/Tobin/Documents/Blender/PurdueMap'
ASSET_PATH = ROOT + r'/modular/buildings/krannert_building.blend'
OUT = ROOT + r'/audit/batch2_krannert/validation_round2.json'
bpy.ops.wm.open_mainfile(filepath=ASSET_PATH)

asset = bpy.data.collections.get('Asset_krannert_building')
root = bpy.data.objects.get('AssetRoot_krannert_building')
issues = []

def bounds(o):
    pts = [o.matrix_world @ Vector(c) for c in o.bound_box]
    return [min(p.x for p in pts), max(p.x for p in pts),
            min(p.y for p in pts), max(p.y for p in pts),
            min(p.z for p in pts), max(p.z for p in pts)]

asset_objects = list(asset.all_objects) if asset else []
meshes = [o for o in asset_objects if o.type == 'MESH']
unmaterialed = [o.name for o in meshes if not o.data.materials]
bad_outputs = []
for ob in meshes:
    for mat in ob.data.materials:
        if mat is None or not mat.use_nodes or not any(n.type == 'OUTPUT_MATERIAL' for n in mat.node_tree.nodes):
            bad_outputs.append(ob.name)

r2 = [o for o in asset_objects if o.name.startswith('KRAN_R2_')]
prefix_counts = {
    'glass_panels': sum(o.name.startswith('KRAN_R2_DrawingRoom_Glass_Panel') for o in r2),
    'glass_mullions': sum(o.name.startswith('KRAN_R2_DrawingRoom_Glass_Mullion') for o in r2),
    'conference_door': sum(o.name.startswith('KRAN_R2_DrawingRoom_Glass_Door') for o in r2),
    'conference_chair_seats': sum(o.name.startswith('KRAN_R2_Conference_Chair_Seat') for o in r2),
    'conference_table_legs': sum(o.name.startswith('KRAN_R2_Conference_Table_Leg') for o in r2),
    'drawingroom_high_tables': sum(o.name.startswith('KRAN_R2_DrawingRoom_Window_HighTop') for o in r2),
    'high_stool_seats': sum(o.name.startswith('KRAN_R2_DrawingRoom_HighStool_Seat') for o in r2),
    'high_stool_foot_rings': sum(o.name.startswith('KRAN_R2_DrawingRoom_HighStool_FootRing') for o in r2),
    'parrish_monitors': sum(o.name.startswith('KRAN_R2_Parrish_Monitor_Screen') for o in r2),
    'parrish_chairs': sum(o.name.startswith('KRAN_R2_Parrish_Chair_Seat') for o in r2),
    'upholstery_pads_on_source_seats': sum(o.name.startswith('KRAN_R2_Chair_Upholstery_Pad') for o in r2),
}

carpet = bpy.data.objects.get('KRAN_New_DrawingRoom_Carpet')
carpet_bounds = bounds(carpet) if carpet else None
glass_panels = [o for o in r2 if o.name.startswith('KRAN_R2_DrawingRoom_Glass_Panel')]
glass_union = None
if glass_panels:
    bs = [bounds(o) for o in glass_panels]
    glass_union = [min(b[0] for b in bs), max(b[1] for b in bs),
                   min(b[2] for b in bs), max(b[3] for b in bs)]
    if carpet_bounds and (glass_union[0] < carpet_bounds[0] or glass_union[1] > carpet_bounds[1] or glass_union[2] < carpet_bounds[2] or glass_union[3] > carpet_bounds[3]):
        issues.append('Conference room glass extends beyond modeled Drawing Room carpet footprint')

root_identity = bool(root and all(abs(root.matrix_world[i][j] - (1.0 if i == j else 0.0)) < 1e-6 for i in range(4) for j in range(4)))
if not asset: issues.append('Export collection missing')
if not root_identity: issues.append('Asset root missing or changed from identity')
if unmaterialed: issues.append('Meshes have no assigned materials')
if bad_outputs: issues.append('Material node output audit failed')
if prefix_counts['conference_door'] != 1: issues.append('Expected one glazed conference-room door')
if prefix_counts['conference_chair_seats'] != 6: issues.append('Expected six conference seats')
if prefix_counts['drawingroom_high_tables'] != 2 or prefix_counts['high_stool_seats'] != 4 or prefix_counts['high_stool_foot_rings'] != 4: issues.append('High-top/table-stool component count mismatch')

conference_legs = [o for o in r2 if o.name.startswith('KRAN_R2_Conference_Table_Leg')]
support_bounds = [bounds(o) for o in conference_legs]
floor_z = 3.90
support_floor_gap = max((b[4] - floor_z for b in support_bounds), default=None)
if support_floor_gap is not None and support_floor_gap > 0.03:
    issues.append('Conference table legs appear to float above the floor')

external_images = [im.filepath for im in bpy.data.images if im.source == 'FILE' and im.filepath and not im.packed_file]
report = {
    'reopen': 'PASS',
    'asset_file': 'modular/buildings/krannert_building.blend',
    'export_collection': asset.name if asset else None,
    'root': root.name if root else None,
    'root_identity_transform': root_identity,
    'asset_object_count': len(asset_objects),
    'mesh_count': len(meshes),
    'round2_object_count': len(r2),
    'round2_component_counts': prefix_counts,
    'drawingroom_carpet_bounds_xy_m': carpet_bounds[:4] if carpet_bounds else None,
    'conference_glass_bounds_xy_m': glass_union,
    'conference_table_leg_max_gap_from_floor_m': support_floor_gap,
    'unmaterialed_mesh_count': len(unmaterialed),
    'material_output_issue_count': len(set(bad_outputs)),
    'external_unpacked_image_dependencies': external_images,
    'preview_renders': [
        'audit/batch2_krannert/drawingroom_r2.png',
        'audit/batch2_krannert/parrish_r2.png',
        'audit/batch2_krannert/drawingroom_plan_r2.png',
        'audit/batch2_krannert/parrish_plan_r2.png'
    ],
    'master_manifest_shared_files_edited': False,
    'issues': issues
}
with open(OUT, 'w', encoding='utf-8') as f:
    json.dump(report, f, indent=2)
print(json.dumps(report, indent=2))
