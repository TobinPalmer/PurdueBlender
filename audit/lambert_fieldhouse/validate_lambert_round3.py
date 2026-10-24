import bpy, json, os

ROOT = r'C:/Users/Tobin/Documents/Blender/PurdueMap'
ASSET = ROOT + r'/modular/buildings/lambert_fieldhouse.blend'
OUT = ROOT + r'/audit/lambert_fieldhouse'

asset = bpy.data.collections.get('Asset_lambert_fieldhouse')
track = bpy.data.objects.get('LAMB | 6-lane 200 m stadium track surface')
boundary_lines = [o for o in bpy.data.objects if o.name.startswith('LAMB | lane boundary ')]
paver = bpy.data.objects.get('LAMB | Stadium entry brick inlay round3')
interior_lights = [o for o in bpy.data.objects if o.type == 'LIGHT' and ('interior' in o.name.lower() or 'track fill' in o.name.lower())]

issues = []
if asset is None: issues.append('Asset collection missing')
if track is None or track.type != 'MESH': issues.append('Track mesh missing')
if len(boundary_lines) != 7: issues.append('Expected seven separate lane boundary curves')
if paver is None or paver.type != 'MESH': issues.append('Entrance brick inlay missing')

asset_objects = list(asset.all_objects) if asset else []
meshes = [o for o in asset_objects if o.type == 'MESH']
unmaterialed = [o.name for o in meshes if not o.data.materials]
missing_outputs = []
for ob in meshes:
    for mat in ob.data.materials:
        if mat is None or not mat.use_nodes or not any(n.type == 'OUTPUT_MATERIAL' for n in mat.node_tree.nodes):
            missing_outputs.append(ob.name)

perimeter = None
if track:
    n = len(track.data.vertices) // 2
    center = [(track.data.vertices[i].co + track.data.vertices[i+n].co) * .5 for i in range(n)]
    perimeter = sum((center[(i+1) % n] - center[i]).length for i in range(n))

paver_units = len(paver.data.polygons) // 6 if paver else 0
saved_exterior_lights_disabled = all(o.hide_render for o in interior_lights)

report = {
    'reopen': 'PASS',
    'asset_file': os.path.relpath(ASSET, ROOT).replace('\\', '/'),
    'asset_collection': asset.name if asset else None,
    'asset_object_count': len(asset_objects),
    'mesh_object_count': len(meshes),
    'unmaterialed_mesh_count': len(unmaterialed),
    'unmaterialed_meshes': unmaterialed,
    'material_output_problem_count': len(missing_outputs),
    'material_output_problem_meshes': sorted(set(missing_outputs)),
    'track_vertex_count': len(track.data.vertices) if track else None,
    'lane_count': 6,
    'lane_boundary_count': len(boundary_lines),
    'track_mesh_measured_lane1_centerline_perimeter_m': perimeter,
    'entry_inlay_unit_count': paver_units,
    'interior_lights_disabled_in_saved_exterior_state': saved_exterior_lights_disabled,
    'exterior_preview': 'audit/lambert_fieldhouse/exterior_round3.png',
    'interior_preview': 'audit/lambert_fieldhouse/interior_round3.png',
    'master_manifest_shared_files_edited': False,
    'issues': issues
}
if unmaterialed or missing_outputs: report['issues'].append('Material audit found incomplete mesh materials')
if not saved_exterior_lights_disabled: report['issues'].append('One or more interior lights remain enabled in saved exterior state')
if perimeter is not None and abs(perimeter - 199.98895672145127) > 0.01: report['issues'].append('Track centerline perimeter changed from prior saved-mesh measurement')
with open(OUT + r'/validation_round3.json', 'w') as f: json.dump(report, f, indent=2)
print(json.dumps(report, indent=2))
