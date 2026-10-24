"""Reopen the saved Math Sciences library and verify R8 story alignment."""
import bpy, json, math
from pathlib import Path
from mathutils import Vector

ROOT=Path(r'C:\Users\Tobin\Documents\Blender\PurdueMap')
ASSET=ROOT/'modular/buildings/math_sciences.blend'
MANIFEST=ROOT/'modular/manifest.json'
GIS=ROOT/'audit/batch3_math/gis_fid227.geojson'
OUT=ROOT/'audit/batch3_math/round8_validation.json'
bpy.ops.wm.open_mainfile(filepath=str(ASSET))
manifest=json.loads(MANIFEST.read_text(encoding='utf-8'))
entry=next(x for x in manifest['assets'] if x['id']=='math_sciences')
asset=bpy.data.collections.get(entry['collection'])
required={n:bpy.data.objects.get(n) for n in (
 'MATH_Corrected_GIS_Wall_Envelope','MATH_2026_Typical_Floor_03',
 'MATH_Lib_Floor_Terrazzo','MATH_2026_Third_Floor_Stair_Treads',
 'MATH_2026_Third_Floor_Elevator_Doors','MATH_2026_Third_Floor_Core_Connector')}
if asset is None or any(o is None for o in required.values()):
    raise RuntimeError('R8 asset collection or expected shell/floor/core object missing')
shell=required['MATH_Corrected_GIS_Wall_Envelope']
def bounds(obj):
    pts=[obj.matrix_world@Vector(c) for c in obj.bound_box]
    return [[min(p[i] for p in pts),max(p[i] for p in pts)] for i in range(3)]
shell_bounds=bounds(shell)
origin=entry['placement_origin_xy_m']
feature=json.loads(GIS.read_text(encoding='utf-8'))['features'][0]
ring=feature['geometry']['coordinates'][0]
projected=[[(lon+86.9137)*111412.84*math.cos(math.radians(40.4274))-origin[0],(lat-40.4274)*111040.0-origin[1]] for lon,lat in ring]
gis_bounds=[[min(p[i] for p in projected),max(p[i] for p in projected)] for i in range(2)]
gis_delta=[[shell_bounds[i][j]-gis_bounds[i][j] for j in range(2)] for i in range(2)]
finish=bounds(required['MATH_Lib_Floor_Terrazzo'])
slab=bounds(required['MATH_2026_Typical_Floor_03'])
stair=bounds(required['MATH_2026_Third_Floor_Stair_Treads'])
elevator=bounds(required['MATH_2026_Third_Floor_Elevator_Doors'])
connector=bounds(required['MATH_2026_Third_Floor_Core_Connector'])
aligned_objects=[o for o in asset.all_objects if 'r8_vertical_alignment_dz_m' in o]
unpacked=[i.filepath for i in bpy.data.images if i.source=='FILE' and i.filepath and not i.packed_file]
expected={
 'collection':entry['collection'],'collection_object_count':len(asset.all_objects),
 'direct_objects':len(asset.objects),'aligned_objects':len(aligned_objects),
 'gis_feature_id':feature['id'],'manifest_origin_xy_m':origin,
 'shell_world_bounds_m':shell_bounds,'gis_local_bounds_m':gis_bounds,
 'shell_minus_gis_bbox_edges_m':gis_delta,
 'max_abs_gis_bbox_edge_delta_m':max(abs(x) for row in gis_delta for x in row),
 'F03_slab_world_z_m':slab[2],'library_finish_world_z_m':finish[2],
 'third_floor_stairs_world_z_m':stair[2],'elevator_doors_world_z_m':elevator[2],
 'core_connector_world_bounds_m':connector,
 'east_sign_absent':bpy.data.objects.get('MATH_Signage_East') is None,
 'unpacked_external_images':unpacked,
 'asset_changed_master':False,
 'uncertainty':'F03 absolute elevation/story spacing and corridor width remain estimates; plan supports third-floor use and connection, not as-built coordinates.'}
assert expected['max_abs_gis_bbox_edge_delta_m']<0.005
assert abs(slab[2][1]-finish[2][1])<0.002
assert abs(finish[2][1]-6.58)<0.002
assert abs(stair[2][0]-6.605)<0.01 and abs(stair[2][1]-9.545)<0.01
assert abs(elevator[2][0]-6.685)<0.01 and abs(elevator[2][1]-8.885)<0.01
assert abs(connector[2][0]-6.582)<0.002 and abs(connector[2][1]-6.600)<0.002
assert expected['aligned_objects']>=249 and expected['east_sign_absent'] and not unpacked
expected['opened_saved_asset']=True
expected['passed']=True
OUT.write_text(json.dumps(expected,indent=2)+'\n',encoding='utf-8')
print(json.dumps(expected,indent=2))
