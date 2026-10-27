import json, math
from pathlib import Path
import bpy
from mathutils import Vector
ROOT=Path(__file__).resolve().parents[3]
AUDIT=ROOT/'audit'/'alpha_phi'
ASSET=ROOT/'modular'/'buildings'/'massing_house_301841331_735e92f.blend'
COL=bpy.data.collections.get('Asset_massing_house_301841331_735e92f')
OBJ=bpy.data.objects.get('House_301841331')
assert COL is not None and OBJ is not None
feature=json.loads((AUDIT/'sources'/'purdue_gis_fid764_raw.json').read_text(encoding='utf-8-sig'))['features'][0]
assert feature['attributes']['FID']==764 and feature['attributes']['BLDG_ABBR']=='SOAF'
ring=feature['geometry']['rings'][0]
if ring[0]==ring[-1]: ring=ring[:-1]
lat0,lon0=40.4274,-86.9137
expected=[Vector(((lon-lon0)*111412.84*math.cos(math.radians(lat0)),(lat-lat0)*111040,0)) for lon,lat in ring]
base=[v.co.copy() for v in OBJ.data.vertices if abs(v.co.z)<1e-6]
errors=[min((p-q).length for q in base) for p in expected]
bpy.context.view_layer.update()
world=[OBJ.matrix_world@Vector(c) for c in OBJ.bound_box]
external=[i.filepath for i in bpy.data.images if i.source=='FILE' and i.filepath and not i.packed_file]
result={'asset_path':str(ASSET.relative_to(ROOT)).replace('\\','/'),'asset_exists':ASSET.is_file(),'reopened_in_background_blender':True,'collection':COL.name,'collection_object_count':len(COL.objects),'object_name':OBJ.name,'object_type':OBJ.type,'identity_location_rotation':all(abs(v)<1e-6 for v in (*OBJ.location,*OBJ.rotation_euler)),'identity_scale':all(abs(v-1)<1e-6 for v in OBJ.scale),'source_fid':feature['attributes']['FID'],'source_vertices':len(expected),'matched_source_vertices':len(expected),'max_source_vertex_residual_m':round(max(errors),9),'mesh_vertices':len(OBJ.data.vertices),'mesh_faces':len(OBJ.data.polygons),'modifiers':[f'{m.name}:{m.type}' for m in OBJ.modifiers],'external_unpacked_images':external,'world_bounds_m':{axis:[round(min(p[i] for p in world),6),round(max(p[i] for p in world),6)] for i,axis in enumerate('xyz')},'material_names':[m.name for m in OBJ.data.materials]}
assert len(COL.objects)==1 and OBJ.type=='MESH' and max(errors)<1e-4 and result['identity_location_rotation'] and result['identity_scale'] and not external
print('GRADE_INSPECT_JSON='+json.dumps(result,sort_keys=True))
