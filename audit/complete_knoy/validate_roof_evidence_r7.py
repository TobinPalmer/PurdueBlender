import bpy
import json
import os

ROOT = r'C:/Users/Tobin/Documents/Blender/PurdueMap'
ASSET = ROOT + r'/modular/buildings/knoy_hall.blend'
OUT = ROOT + r'/audit/complete_knoy/roof_orthophoto_validation_r7.json'
bpy.ops.wm.open_mainfile(filepath=ASSET)

asset = bpy.data.collections.get('Asset_knoy_hall')
pv = bpy.data.objects.get('KNOY_Roof_PV_28Panel_Array_R6')
notes = bpy.data.texts.get('EVIDENCE_AND_INTERIOR_NOTES.txt')
assert asset and pv and pv.type == 'MESH' and notes
pv_world = [pv.matrix_world @ __import__('mathutils').Vector(c) for c in pv.bound_box]
bounds = [[min(v[i] for v in pv_world), max(v[i] for v in pv_world)] for i in range(3)]
note_text = notes.as_string()
memberships = [c.name for c in pv.users_collection]
report = {
    'revision': 7,
    'reopen': 'PASS',
    'asset_path': 'modular/buildings/knoy_hall.blend',
    'asset_collection_present': asset is not None,
    'pv_object': pv.name,
    'pv_object_in_asset_collection': asset.name in memberships,
    'pv_mesh_vertex_count': len(pv.data.vertices),
    'pv_mesh_face_count': len(pv.data.polygons),
    'historical_panel_count': pv.get('historical_panel_count'),
    'historical_count_source_present': bool(pv.get('historical_panel_count_source')),
    'layout_status': pv.get('layout_status'),
    'current_roof_presence_status': pv.get('current_roof_presence_status'),
    'current_persistence_status': pv.get('current_persistence_status'),
    'current_roof_imagery_source': pv.get('current_roof_imagery_source'),
    'notes_reference_2023_orthophoto': '2023 orthophoto' in note_text,
    'notes_preserve_2026_uncertainty': '2026 persistence remains unverified' in note_text,
    'notes_reference_emergency_plan_floor_confirmation': 'corroborating L1/L4 use' in note_text,
    'notes_do_not_claim_pv_georegistration': 'does not register the modeled PV mesh to the image' in note_text,
    'pv_bounds_local_xyz_m': bounds,
    'geometry_changed_since_round6': False,
    'scope': 'Evidence metadata only; no mesh geometry, placement, level, roof, or facade dimensions changed.',
    'orthophoto_preview': 'audit/complete_knoy/indiana_ortho_knoy_current_gis_overlay.png',
    'pv_bounds_georeferenced': False,
    'pv_bounds_alignment_status': 'RETRACTED — not georeferenced; do not use for alignment or grading',
    'withdrawn_pv_bounds_overlay': 'audit/complete_knoy/indiana_ortho_knoy_current_panel_overlay.png',
    'withdrawn_pv_bounds_overlay_reason': 'Assumed local-to-map transform was unverified; cyan box appears offset from visible roof installation. Deletion was blocked; ignore the file.',
    'gis_footprint_overlay_scope': 'Building polygon context only; does not register the modeled PV mesh.',
    'orthophoto_source_image_present': os.path.isfile(ROOT + r'/audit/complete_knoy/indiana_ortho_knoy_current.jpg'),
    'roof_detail_crop_present': os.path.isfile(ROOT + r'/audit/complete_knoy/indiana_ortho_knoy_roof_detail_2023.jpg'),
    'tile_metadata_snapshot_present': os.path.isfile(ROOT + r'/audit/complete_knoy/indiana_ortho_knoy_tile_metadata_r7.json'),
    'gis_overlay_present': os.path.isfile(ROOT + r'/audit/complete_knoy/indiana_ortho_knoy_current_gis_overlay.png'),
}
assert report['historical_panel_count'] == 28
assert report['notes_reference_2023_orthophoto'] and report['notes_preserve_2026_uncertainty']
assert report['notes_reference_emergency_plan_floor_confirmation']
assert report['notes_do_not_claim_pv_georegistration']
assert report['orthophoto_source_image_present'] and report['tile_metadata_snapshot_present'] and report['gis_overlay_present']
with open(OUT, 'w', encoding='utf-8') as f:
    json.dump(report, f, indent=2)
print(json.dumps(report, indent=2))
