"""Reopen and validate the saved Chi Omega library independently of the builder."""
import bpy, json, math
from pathlib import Path
ROOT=Path(__file__).resolve().parents[2]
ASSET_ID='massing_chi_omega_a9eb08d'
ASSET=ROOT/'modular'/'buildings'/f'{ASSET_ID}.blend'
SOURCE=ROOT/'audit'/'chi_omega'/'sources'/'purdue_gis_fid781_chi_omega_2026-10-26.json'
OUT=ROOT/'audit'/'chi_omega'/'reopen_validation.json'
ORIGIN_LAT,ORIGIN_LON=40.4274,-86.9137
bpy.ops.wm.open_mainfile(filepath=str(ASSET))
scene=bpy.data.scenes.get('Building_'+ASSET_ID)
coll=bpy.data.collections.get('Asset_'+ASSET_ID)
assert scene and coll, 'expected scene or collection is missing'
objects=list(coll.objects)
mesh_objs=[o for o in objects if o.type=='MESH']
assert len(objects)==1 and len(mesh_objs)==1, f'expected exactly one mesh object; got {[(o.name,o.type) for o in objects]}'
obj=mesh_objs[0]
assert obj.name=='Chi Omega' and obj.get('building_id')==ASSET_ID
assert len(obj.modifiers)==0, 'unexpected modifier dependency'
assert all(abs(obj.matrix_world[i][j]-(1.0 if i==j else 0.0))<1e-6 for i in range(4) for j in range(4)), 'mesh object transform is not identity'
coords=[obj.matrix_world @ v.co for v in obj.data.vertices]
bounds=[[min(p[i] for p in coords),max(p[i] for p in coords)] for i in range(3)]
source=json.loads(SOURCE.read_text(encoding='utf-8'))['features'][0]
ring=source['geometry']['rings'][0][:-1]
expected=set()
for lon,lat in ring:
 x=(lon-ORIGIN_LON)*111412.84*math.cos(math.radians(ORIGIN_LAT)); y=(lat-ORIGIN_LAT)*111040.0
 expected.add((round(x,4),round(y,4)))
actual=list({(round(p.x,4),round(p.y,4)) for p in coords if abs(p.z)<1e-6})
footprint_errors=[min(math.hypot(x-ax,y-ay) for ax,ay in actual) for x,y in expected]
footprint_match=(len(actual)==len(expected) and max(footprint_errors,default=0.0)<0.02)
assert footprint_match, f'ground ring mismatch: expected {len(expected)}, got {len(actual)}; max error={max(footprint_errors,default=0.0)}'
assert abs(bounds[2][1]-10.3)<0.15, f'unexpected roof peak {bounds[2][1]}'
assert not [lib.filepath for lib in bpy.data.libraries], 'unexpected linked libraries'
result={
 'asset_path':str(ASSET.relative_to(ROOT)), 'asset_id':ASSET_ID,
 'scene':scene.name,'collection':coll.name,'object_count':len(objects),'mesh_object_count':len(mesh_objs),
 'mesh_name':obj.name,'vertex_count':len(obj.data.vertices),'face_count':len(obj.data.polygons),
 'modifier_count':len(obj.modifiers),'linked_libraries':[], 'object_transform':'identity',
 'evaluated_bounds_world_m':bounds,
 'source_feature_id':source['attributes']['FID'],'source_building_name':source['attributes']['BUILDING_N'],
 'footprint_vertices_expected':len(expected),'footprint_vertices_actual':len(actual),
 'max_ground_ring_error_m':max(footprint_errors,default=0.0),
 'ground_footprint_matches_transformed_gis':footprint_match,
 'vertical_bounds_are_estimates':True,'reopened_in_fresh_blender_process':True,
 'status':'passed'
}
OUT.write_text(json.dumps(result,indent=2)+'\n',encoding='utf-8')
print(json.dumps(result))
