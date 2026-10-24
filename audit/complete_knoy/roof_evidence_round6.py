import bpy
import json
import math
import os
from mathutils import Vector

ROOT = r'C:/Users/Tobin/Documents/Blender/PurdueMap'
SOURCE = ROOT + r'/modular/buildings/knoy_hall.blend'
CANDIDATE = ROOT + r'/audit/complete_knoy/knoy_hall_round6_candidate.blend'
OUT = ROOT + r'/audit/complete_knoy'

bpy.ops.wm.open_mainfile(filepath=SOURCE)
asset = bpy.data.collections.get('Asset_knoy_hall')
assert asset is not None, 'Knoy export collection is missing'
pv = (bpy.data.objects.get('KNOY_Roof_PV_28Panel_Array_R6')
      or bpy.data.objects.get('KNOY_Roof_Solar_Photovoltaic_Array'))
assert pv is not None and pv.type == 'MESH', 'Existing Knoy PV array not found'
assert pv.name in asset.objects, 'Existing PV object is outside Knoy asset collection'

# The university's 2017 installation post documents 28 PV panels. Keep the
# existing roof-zone center as a placement estimate, but replace the old,
# unsupported 5 x 18 (90 panel) display with a 4 x 7 schematic array.
world_points = [pv.matrix_world @ Vector(corner) for corner in pv.bound_box]
cx = (min(p.x for p in world_points) + max(p.x for p in world_points)) * 0.5
cy = (min(p.y for p in world_points) + max(p.y for p in world_points)) * 0.5
roof_z = 19.202
panel_count = 28
cols, rows = 7, 4
panel_w, panel_len = 0.99, 1.72
gap_x, pitch_y = 0.13, 2.18
tilt = math.radians(28.0)  # illustrative rack angle; not a sourced measurement
span_x = cols * panel_w + (cols - 1) * gap_x
world_to_pv = pv.matrix_world.inverted()
panel_mesh = bpy.data.meshes.new('KNOY_Roof_PV_28Panel_ModuleMesh_R6')
verts, faces = [], []
for row in range(rows):
    row_center_y = cy + (row - (rows - 1) / 2.0) * pitch_y
    y0 = row_center_y - (panel_len * math.cos(tilt)) / 2.0
    y1 = row_center_y + (panel_len * math.cos(tilt)) / 2.0
    z0 = roof_z + 0.18
    z1 = z0 + panel_len * math.sin(tilt)
    for col in range(cols):
        x0 = cx - span_x / 2.0 + col * (panel_w + gap_x)
        x1 = x0 + panel_w
        # Thin rectangular module with front, back, and edge faces.
        base = len(verts)
        t = 0.035
        verts.extend([
            tuple(world_to_pv @ Vector((x0, y0, z0))),
            tuple(world_to_pv @ Vector((x1, y0, z0))),
            tuple(world_to_pv @ Vector((x1, y1, z1))),
            tuple(world_to_pv @ Vector((x0, y1, z1))),
            tuple(world_to_pv @ Vector((x0, y0, z0 - t))),
            tuple(world_to_pv @ Vector((x1, y0, z0 - t))),
            tuple(world_to_pv @ Vector((x1, y1, z1 - t))),
            tuple(world_to_pv @ Vector((x0, y1, z1 - t))),
        ])
        faces.extend([
            (base+0,base+1,base+2,base+3), (base+7,base+6,base+5,base+4),
            (base+0,base+4,base+5,base+1), (base+1,base+5,base+6,base+2),
            (base+2,base+6,base+7,base+3), (base+3,base+7,base+4,base+0),
        ])
panel_mesh.from_pydata(verts, [], faces)
panel_mesh.update()
old_mesh = pv.data
pv.data = panel_mesh
if old_mesh.users == 0:
    bpy.data.meshes.remove(old_mesh)
pv.name = 'KNOY_Roof_PV_28Panel_Array_R6'
pv.data.materials.clear()
solar_mat = bpy.data.materials.get('KNOY_Solar_Panel')
assert solar_mat is not None, 'Knoy solar panel material not found'
pv.data.materials.append(solar_mat)
solar_mat.diffuse_color = (0.025, 0.075, 0.17, 1.0)
solar_shader = next((n for n in solar_mat.node_tree.nodes if n.type == 'BSDF_PRINCIPLED'), None)
if solar_shader:
    solar_shader.inputs['Base Color'].default_value = (0.025, 0.075, 0.17, 1.0)
    solar_shader.inputs['Metallic'].default_value = 0.42
    solar_shader.inputs['Roughness'].default_value = 0.24
pv['evidence_status'] = 'Panel count source-supported for 2017 installation; current 2026 persistence, precise layout, position, orientation, tilt and rack dimensions unverified.'
pv['source_url'] = 'https://old.polytechnic.purdue.edu/newsroom/new-knoy-rooftop-solar-array-generates-more-power-learning-opportunities-and-research'
pv['source_date'] = 'Published 2017-05-22; installation reported 2017-04-18'
pv['documented_panel_count'] = panel_count
pv['modeled_panel_count'] = panel_count
pv['arrangement_assumption'] = '4 x 7 for legible schematic representation; source confirms total count only.'
pv['placement_method'] = 'Kept the prior modeled roof-zone center; exact roof position is not dimensioned in the source.'
pv['rack_tilt_degrees'] = 28.0
pv['rack_tilt_status'] = 'Illustrative only; not source measured.'
pv['panel_mesh_face_count'] = len(panel_mesh.polygons)

# Add a compact support frame as separately inspectable, visibly metallic rails.
support = bpy.data.objects.get('KNOY_Roof_PV_Racking_R6')
if support:
    bpy.data.objects.remove(support, do_unlink=True)
rack_mesh = bpy.data.meshes.new('KNOY_Roof_PV_RackingMesh_R6')
rverts, rfaces = [], []
def add_box(center, size):
    x,y,z = center; dx,dy,dz = [v*0.5 for v in size]; b=len(rverts)
    rverts.extend([(x-dx,y-dy,z-dz),(x+dx,y-dy,z-dz),(x+dx,y+dy,z-dz),(x-dx,y+dy,z-dz),
                   (x-dx,y-dy,z+dz),(x+dx,y-dy,z+dz),(x+dx,y+dy,z+dz),(x-dx,y+dy,z+dz)])
    rfaces.extend([(b,b+1,b+2,b+3),(b+4,b+7,b+6,b+5),(b,b+4,b+5,b+1),
                    (b+1,b+5,b+6,b+2),(b+2,b+6,b+7,b+3),(b+3,b+7,b+4,b)])

# Long cross-rails support each row at both panel edges; repeated short feet
# show a lightweight rack without implying exact structural specifications.
full_x = span_x + 0.12
for row in range(rows):
    row_center_y = cy + (row - (rows - 1) / 2.0) * pitch_y
    low_y = row_center_y - (panel_len * math.cos(tilt)) / 2.0
    high_y = row_center_y + (panel_len * math.cos(tilt)) / 2.0
    high_z = roof_z + 0.18 + panel_len * math.sin(tilt)
    add_box((cx, low_y, roof_z+0.12), (full_x, 0.06, 0.08))
    add_box((cx, high_y, high_z-0.11), (full_x, 0.06, 0.08))
    for foot_x in [cx - span_x*0.42, cx, cx + span_x*0.42]:
        add_box((foot_x, low_y, roof_z+0.09), (0.07,0.07,0.18))
        add_box((foot_x, high_y, roof_z+0.18 + panel_len*math.sin(tilt)-0.10), (0.07,0.07,0.30))
rack_mesh.from_pydata(rverts, [], rfaces); rack_mesh.update()
rack_obj = bpy.data.objects.new('KNOY_Roof_PV_Racking_R6', rack_mesh)
asset.objects.link(rack_obj)
steel = bpy.data.materials.get('KNOY_PV_Rack_Aluminum_R6')
if steel is None:
    steel = bpy.data.materials.new('KNOY_PV_Rack_Aluminum_R6')
    steel.use_nodes = True
    nodes = steel.node_tree.nodes
    shader = next(n for n in nodes if n.type == 'BSDF_PRINCIPLED')
    shader.inputs['Base Color'].default_value = (0.36, 0.39, 0.41, 1.0)
    shader.inputs['Metallic'].default_value = 0.72
    shader.inputs['Roughness'].default_value = 0.3
rack_mesh.materials.append(steel)
rack_obj['evidence_status'] = 'Support/racking type is photo-visible; exact member layout and sizes are schematic.'
rack_obj['source_url'] = pv['source_url']

# Do not infer equipment that imagery and records do not resolve. Keep the
# existing penthouse geometry unchanged, but make the source limitation clear.
penthouse = bpy.data.objects.get('KNOY_Roof_Mechanical_Penthouse')
if penthouse:
    penthouse['evidence_status'] = 'Unverified schematic placeholder. No source found in this review that establishes current presence, footprint, height, facade, or roof placement. Geometry intentionally retained unchanged.'
    penthouse['uncertainty_source_review_date'] = '2026-10-24'
for ob in asset.all_objects:
    if 'cooling' in ob.name.lower() or 'tower' in ob.name.lower():
        ob['evidence_status'] = 'No current authoritative source located; review required.'

scene = bpy.context.scene
scene['roof_equipment_review_date'] = '2026-10-24'
scene['pv_source_url'] = pv['source_url']
scene['pv_source_fact'] = 'Purdue Polytechnic reported a 28-panel PV array installed on the Knoy roof in April 2017, replacing the previous 24-panel array.'
scene['pv_geometry_uncertainty'] = 'The 28-panel count is sourced; array position, orientation, rack tilt and present-day persistence are not verified.'
scene['roof_penthouse_uncertainty'] = 'Existing penthouse remains a schematic placeholder with no source found for its dimensions or presence.'
scene['cooling_tower_status'] = 'No cooling-tower geometry is present in the reopened asset; no source found to justify adding it.'
scene['levels_conflict_note'] = '2018 Gateway planning sheet depicts and labels existing Levels 1-4 at 14 ft 8 in floor-to-floor; GIS record reports five levels and 48 ft extrusion. L5 and roof datum interpretation remains unresolved; no slab/height geometry changed in this round.'

status_text = bpy.data.texts.get('KNOY_Roof_And_Level_Evidence_R6') or bpy.data.texts.new('KNOY_Roof_And_Level_Evidence_R6')
status_text.clear()
status_text.write('''KNOY HALL — ROOF AND VERTICAL DATUM SOURCE REVIEW (2026-10-24)\n\nVerified roof fact: Purdue Polytechnic's 2017 report says the rooftop PV installation was upgraded to 28 panels, replacing a 24-panel system installed in 2000. The panel count is source-backed for the 2017 installation. The model represents 28 panels in a schematic 4 x 7 arrangement; the report does not provide a dimensioned roof plan, orientation, tilt, exact position, rack dimensions, or proof the array remains unchanged in 2026.\n\nSources:\n- Purdue Polytechnic Institute, 2017-05-22, “New Knoy rooftop solar array generates more power, learning opportunities and research”; reports a 28-panel array and notes installation on 2017-04-18: https://old.polytechnic.purdue.edu/newsroom/new-knoy-rooftop-solar-array-generates-more-power-learning-opportunities-and-research\n- Purdue Polytechnic Institute, 2013-11-15, “Knoy Hall first on campus to use solar power”; says rooftop PV had been installed since 2000: https://old.polytechnic.purdue.edu/newsroom/knoy-hall-first-campus-use-solar-power\n- Purdue University Archives, Knoy Hall records; identifies construction records and a floor plan in UA 141; access is research-room based, and this review did not inspect the physical folder: https://archives.lib.purdue.edu/repositories/2/resources/1490\n- Purdue Gateway planning study, 2018-05-31, page 24: existing Knoy elevations label Levels 1-4 at 14 ft 8 in floor-to-floor; this is planning-study material, not a current as-built survey: https://engineering.purdue.edu/~frosch/Renderings/Gateway/2018-05-31%20MASSING%20STUDIES%20DRAFT%20INCLUDING%20LANDSCAPE.pdf\n\nUnresolved roof/level evidence: no reviewed source establishes current penthouse size/location, cooling-tower presence, exact roof equipment, or as-built Level 5/roof arrangement. The existing penthouse placeholder, five-level slabs and roof datum were retained unchanged; cooling-tower geometry was not added. Existing plan/elevation evidence conflicts with the GIS five-level attribute. Do not treat estimated heights, levels, or roof equipment as survey-verified.\n''')

# Replace the legacy embedded narrative, which made unsupported vertical and
# roof-equipment claims, with a concise source/estimate status for this asset.
legacy = bpy.data.texts.get('EVIDENCE_AND_INTERIOR_NOTES.txt')
if legacy:
    legacy.clear()
    legacy.write('''MAURICE G. KNOY HALL OF TECHNOLOGY — CURRENT EVIDENCE STATUS
Reviewed 2026-10-24. Stable building ID knoy_hall; GIS feature 243.

FOOTPRINT AND FRAME
The detailed asset preserves its source frame and exported collection Asset_knoy_hall. The GIS polygon is used for the exterior footprint; GIS fit does not verify facade details, floor heights or roof form. The master Placement_knoy_hall marker remains coordinator-controlled and was not edited here.

HEIGHT AND FLOOR LEVELS
Purdue's 2018 Gateway planning study (PDF page 24) labels existing Knoy Levels 1-4 at 14 ft 8 in floor-to-floor. The current modeled L1-L4 datum intervals are 4.481, 4.480 and 4.481 m, about 0.010 m above that planning note. This is not an as-built survey. Purdue GIS feature 243 reports five levels and 48 ft extrusion, but those attributes do not resolve the 2018 sheet's four-level labeling or provide a roof elevation. L5, roof-deck, parapet and penthouse heights remain uncertain; the related geometry was retained unchanged.

ROOF
Purdue Polytechnic's May 2017 report documents 28 PV panels installed on the roof on April 18, replacing an older 24-panel array. This model now uses 28 modules. The 4 x 7 arrangement, exact position, orientation, tilt, rack dimensions and current 2026 persistence are estimates. The modeled penthouse is an unverified schematic placeholder. No cooling-tower geometry is present; no source reviewed here establishes it.

FACADE
A Purdue-hosted profile photo provides qualitative cues for the entrance, red brick, glazing, lettering, canopy and planting. It is not calibrated. Exact facade rhythm and dimensions remain unverified and were not changed in this round.

INTERIOR
L2-L4 partitions were traced from the Purdue Gateway typical plan with approximately +/-1 m manual registration uncertainty. L1 partitions were traced from a dissertation plan with approximately +/-1.5 m uncertainty. Door gaps, door leaves, stairs and clearances are illustrative unless a source plan resolves them. L5, basement connectivity, room labels, furnishings and interior finishes remain unverified where source evidence is absent.

Sources and detailed limits: audit/complete_knoy/roof_levels_sources_r6.json and audit/complete_knoy/REVIEW.md. Reopen/material checks and PV counts: audit/complete_knoy/roof_equipment_validation_r6.json.
''')

# Add an independent inspection camera for a saved/reopened roof audit render.
cam_obj = bpy.data.objects.get('KNOY_R6_Roof_Evidence_Camera')
if cam_obj:
    bpy.data.objects.remove(cam_obj, do_unlink=True)
cam_data = bpy.data.cameras.new('KNOY_R6_Roof_Evidence_Camera')
cam_obj = bpy.data.objects.new('KNOY_R6_Roof_Evidence_Camera', cam_data)
scene.collection.objects.link(cam_obj)
cam_obj.location = (32.0, -54.0, 58.0)
target = Vector((cx, cy, 19.8))
direction = target - cam_obj.location
cam_obj.rotation_euler = direction.to_track_quat('-Z','Y').to_euler()
cam_data.lens = 50
cam_data.clip_end = 500
cam_obj['render_only_audit_camera'] = True
scene.camera = cam_obj
scene.render.engine = 'BLENDER_EEVEE'
scene.render.resolution_x = 1440
scene.render.resolution_y = 1000
scene.render.resolution_percentage = 100
scene.render.image_settings.file_format = 'PNG'
scene.render.filepath = OUT + r'/knoy_roof_equipment_audit_r6.png'
scene.render.film_transparent = False
bpy.ops.wm.save_as_mainfile(filepath=CANDIDATE)
bpy.ops.wm.open_mainfile(filepath=CANDIDATE)

# Reopened-source checks and view generation.
asset = bpy.data.collections.get('Asset_knoy_hall')
pv = bpy.data.objects.get('KNOY_Roof_PV_28Panel_Array_R6')
rack_obj = bpy.data.objects.get('KNOY_Roof_PV_Racking_R6')
penthouse = bpy.data.objects.get('KNOY_Roof_Mechanical_Penthouse')
assert asset and pv and rack_obj and penthouse
assert pv['modeled_panel_count'] == 28
assert pv.name in asset.objects and rack_obj.name in asset.objects
assert len(pv.data.polygons) == 28 * 6
assert not any('cooling' in ob.name.lower() or 'tower' in ob.name.lower() for ob in asset.all_objects)
assert penthouse['evidence_status'].startswith('Unverified schematic placeholder')
unmaterialed = [o.name for o in asset.all_objects if o.type == 'MESH' and len(o.data.materials) == 0]
bad_mats = []
for ob in asset.all_objects:
    if ob.type != 'MESH':
        continue
    for mat in ob.data.materials:
        if mat is None or not mat.use_nodes or not any(n.type == 'OUTPUT_MATERIAL' for n in mat.node_tree.nodes):
            bad_mats.append(ob.name)
assert not unmaterialed, unmaterialed[:8]
assert not bad_mats, bad_mats[:8]

bpy.context.scene.render.filepath = OUT + r'/knoy_roof_equipment_audit_r6.png'
bpy.ops.render.render(write_still=True)

report = {
    'round': 6,
    'reopened': True,
    'asset_file': 'modular/buildings/knoy_hall.blend',
    'candidate_saved_as': 'audit/complete_knoy/knoy_hall_round6_candidate.blend',
    'export_collection': asset.name,
    'asset_object_count': len(list(asset.all_objects)),
    'pv_object': pv.name,
    'pv_panel_count_from_source': pv['documented_panel_count'],
    'pv_panel_count_modeled': pv['modeled_panel_count'],
    'pv_panel_faces': len(pv.data.polygons),
    'pv_layout': '4x7 schematic arrangement; source confirms count, not layout',
    'pv_center_local_xy_m': [round(cx,3), round(cy,3)],
    'pv_bounds_asset_xy_m': [
        round(min((pv.matrix_world @ v.co).x for v in pv.data.vertices),3),
        round(max((pv.matrix_world @ v.co).x for v in pv.data.vertices),3),
        round(min((pv.matrix_world @ v.co).y for v in pv.data.vertices),3),
        round(max((pv.matrix_world @ v.co).y for v in pv.data.vertices),3),
    ],
    'pv_rack_tilt_degrees': pv['rack_tilt_degrees'],
    'pv_rack_tilt_status': pv['rack_tilt_status'],
    'pv_source_url': pv['source_url'],
    'pv_date_limitation': '2017 installation evidence; current 2026 configuration unverified',
    'penthouse_status': penthouse['evidence_status'],
    'cooling_tower_geometry_present': False,
    'cooling_tower_status': bpy.context.scene['cooling_tower_status'],
    'level_conflict': bpy.context.scene['levels_conflict_note'],
    'level_elevation_comparison': {
        '2018_purdue_source_floor_to_floor_m': 14.6666666667 * 0.3048,
        '2018_purdue_source_floor_to_floor_ft_in': '14 ft 8 in',
        'source_levels': 'Existing Levels 1-4',
        'modeled_floor_datums_m': {'L1':0.0,'L2':4.481,'L3':8.961,'L4':13.442},
        'model_intervals_L1_to_L4_m': [
            4.481,4.480,4.481
        ],
        'interval_differences_from_2018_source_m': [0.0106,0.0096,0.0106],
        'status': 'L1-L4 modeled datum spacing is within 0.011 m of the 2018 planning note; the source is not an as-built survey and does not resolve L5 or the roof.'
    },
    'unmaterialed_mesh_count': len(unmaterialed),
    'material_output_problem_count': len(set(bad_mats)),
    'preview': 'audit/complete_knoy/knoy_roof_equipment_audit_r6.png',
    'master_and_shared_files_edited': False,
    'issues': []
}
with open(OUT + r'/roof_equipment_validation_r6.json','w',encoding='utf-8') as f:
    json.dump(report,f,indent=2)
print(json.dumps(report,indent=2))
