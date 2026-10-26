import bpy, json, math, os
from pathlib import Path
ROOT = Path(__file__).resolve().parents[2]
ASSET_ID = 'massing_chi_omega_a9eb08d'
ASSET = ROOT/'modular'/'buildings'/f'{ASSET_ID}.blend'
GIS = ROOT/'audit'/'chi_omega'/'sources'/'purdue_gis_fid781_chi_omega_2026-10-26.json'
ORTHO = ROOT/'audit'/'chi_omega'/'sources'/'indiana_ortho_chi_omega_close_2022_2025.jpg'
SOURCE_RECORD = ROOT/'audit'/'chi_omega'/'sources'/'source_record.json'
OUT = ROOT/'audit'/'chi_omega_independent_grade'/'reopen_probe.json'
ORIGIN_LAT, ORIGIN_LON = 40.4274, -86.9137
bpy.ops.wm.open_mainfile(filepath=str(ASSET))
scene = bpy.data.scenes.get('Building_'+ASSET_ID)
coll = bpy.data.collections.get('Asset_'+ASSET_ID)
assert scene and coll, 'expected named scene and asset collection missing'
objects = list(coll.objects)
meshes = [o for o in objects if o.type == 'MESH']
assert len(objects) == 1 and len(meshes) == 1, f'expected one mesh, got objects={[(o.name,o.type) for o in objects]}'
obj = meshes[0]
assert obj.name == 'Chi Omega'
coords = [obj.matrix_world @ v.co for v in obj.data.vertices]
bounds = [[min(p[i] for p in coords), max(p[i] for p in coords)] for i in range(3)]
gis = json.loads(GIS.read_text(encoding='utf-8'))['features'][0]
a = gis['attributes']
ring = gis['geometry']['rings'][0][:-1]
def local_xy(lon,lat): return ((lon-ORIGIN_LON)*111412.84*math.cos(math.radians(ORIGIN_LAT)), (lat-ORIGIN_LAT)*111040.0)
source_xy = [local_xy(lon,lat) for lon,lat in ring]
expected = {(round(x,4),round(y,4)) for x,y in source_xy}
actual = {(round(p.x,4),round(p.y,4)) for p in coords if abs(p.z)<1e-6}
errors = [min(math.hypot(x-ax,y-ay) for ax,ay in actual) for x,y in expected]
reverse_errors = [min(math.hypot(x-ax,y-ay) for x,y in expected) for ax,ay in actual]
max_error = max(errors+reverse_errors, default=0)
expected_bounds = [[min(x for x,y in source_xy),max(x for x,y in source_xy)],[min(y for x,y in source_xy),max(y for x,y in source_xy)]]
ground_points = [(float(v.co.x),float(v.co.y)) for v in obj.data.vertices if abs(v.co.z)<1e-6]
ordered_errors = [math.hypot(ground_points[i][0]-source_xy[-1-i][0],ground_points[i][1]-source_xy[-1-i][1]) for i in range(len(source_xy))]
ordered_error = max(ordered_errors, default=0)
ground_bounds = [[min(x for x,y in ground_points),max(x for x,y in ground_points)],[min(y for x,y in ground_points),max(y for x,y in ground_points)]]
libs = [lib.filepath for lib in bpy.data.libraries]
external_images = [im.filepath for im in bpy.data.images if im.filepath and not im.packed_file]
mods = [m.name for m in obj.modifiers]
result = {
 'asset_path': str(ASSET.relative_to(ROOT)).replace('\\','/'), 'asset_id': ASSET_ID,
 'blender_version': bpy.app.version_string, 'scene':scene.name,'collection':coll.name,
 'objects_in_asset_collection':len(objects),'mesh_object_count':len(meshes),'mesh_name':obj.name,
 'object_world_matrix':[[round(float(v),8) for v in row] for row in obj.matrix_world],
 'modifier_names':mods,'linked_libraries':libs,'unpacked_external_images':external_images,
 'evaluated_vertex_bounds_m':bounds,'mesh_vertices':len(obj.data.vertices),'mesh_faces':len(obj.data.polygons),
 'identity':{'GIS_feature_id':a['FID'],'GIS_name':a['BUILDING_N'],'GIS_address':a['ADDRESS'],'asset_property_id':obj.get('building_id')},
 'footprint':{'GIS_ring_vertices':len(ring),'unique_ground_vertices':len(actual),'ground_ring_symmetric_vertex_error_m':max_error,'ordered_reversed_ring_max_error_m':ordered_error,'ordered_ring_match':ordered_error<0.02,'expected_bounds_xy_m':expected_bounds,'actual_ground_ring_bounds_xy_m':ground_bounds,'GIS_shape_area_attribute_m2':a.get('Shape__Area')},
 'source_height_fields':{'NUM_LEVELS':a.get('NUM_LEVELS'),'CountOfFLO':a.get('CountOfFLO'),'Extrution':a.get('Extrution'),'units_declared':False},
 'height_status':'wall eave and roof peak are explicitly estimated in build script; no verified elevation source found',
 'roof_evidence':'Indiana orthophoto supports roof zone segmentation only; height and exact roof section remain estimates',
 'facade_evidence':'no elevation or building-specific facade photo in evidence; material and repeated windows are expressly illustrative; entrance not modeled/verified',
 'evidence_snapshot_files':[str(p.relative_to(ROOT)).replace('\\','/') for p in [GIS,ORTHO,SOURCE_RECORD]],
 'reopened_in_fresh_blender_process':True
}
OUT.write_text(json.dumps(result,indent=2)+'\n',encoding='utf-8')
print(json.dumps(result,indent=2))
