import bpy,json,math,hashlib
from pathlib import Path
from mathutils import Vector
base=Path.cwd(); asset=(base/'modular/buildings/massing_wood_street_garage_pgw_2fa056e.blend').resolve(); root=base/'audit/purdue_wood_street_garage_pgw/independent_grade'
if Path(bpy.data.filepath).resolve()!=asset: raise RuntimeError('Fresh-open path mismatch')
asset_id='massing_wood_street_garage_pgw_2fa056e'; scene=bpy.data.scenes.get('Building_'+asset_id); col=bpy.data.collections.get('Asset_'+asset_id)
assert scene and col and col.name in [c.name for c in scene.collection.children]
mesh=[o for o in col.objects if o.type=='MESH']; geom=[o for o in col.objects if o.type in {'MESH','CURVE','FONT'}]
pts=[o.matrix_world@Vector(c) for o in geom for c in o.bound_box]; bounds=[[min(float(p[i]) for p in pts),max(float(p[i]) for p in pts)] for i in range(3)]
source=json.loads((base/'audit/purdue_wood_street_garage_pgw/raw_arcgis_fid254.json').read_text(encoding='utf-8-sig')); ring=source['features'][0]['geometry']['rings'][0]; R=6378137.0; xy=[]
for e,n in ring:
 lon=math.degrees(e/R);lat=math.degrees(math.atan(math.sinh(n/R)));xy.append(((lon+86.9137)*111412.84*math.cos(math.radians(40.4274)),(lat-40.4274)*111040.0))
anchor=list(scene.get('world_anchor_m')); expected={(round(x-anchor[0],4),round(y-anchor[1],4)) for x,y in xy[:-1]}
deck=bpy.data.objects.get('PGW deck 01'); observed={(round(float(v.co.x),4),round(float(v.co.y),4)) for v in deck.data.vertices[:len(ring)-1]} if deck else set()
levels=[]
for i in range(1,9):
 o=bpy.data.objects.get(f'PGW deck {i:02d}')
 if o:
  levels.append({'name':o.name,'z_min':round(min((o.matrix_world@v.co).z for v in o.data.vertices),4),'z_max':round(max((o.matrix_world@v.co).z for v in o.data.vertices),4)})
materials={m.name for o in geom if getattr(o.data,'materials',None) for m in o.data.materials if m}
images=[{'name':i.name,'path':i.filepath,'source':i.source} for i in bpy.data.images if i.source=='FILE' and i.filepath]
ramps=[o.name for o in col.objects if 'ramp' in o.name.lower()]; stairs=[o.name for o in col.objects if 'stair' in o.name.lower()]; text=[getattr(o.data,'body','') for o in col.objects if o.type=='FONT']
result={'asset_path':str(asset),'sha256':hashlib.sha256(asset.read_bytes()).hexdigest(),'scene':scene.name,'scene_building_id':scene.get('building_id'),'collection':col.name,'root_collection_member':col.name in [c.name for c in scene.collection.children],'object_count':len(col.objects),'mesh_count':len(mesh),'bounds_local_m':bounds,'world_anchor_m':anchor,'gis_feature_id':scene.get('gis_feature_id'),'gis_ring_vertices':len(ring)-1,'footprint_vertices_expected':len(expected),'footprint_vertices_observed':len(observed),'footprint_missing_count':len(expected-observed),'footprint_extra_count':len(observed-expected),'footprint_vertex_tolerance_m':0.0001,'deck_levels':levels,'ramp_object_count':len(ramps),'ramp_objects':ramps,'stair_object_count':len(stairs),'stair_objects':stairs,'font_text':text,'used_materials':sorted(materials),'external_file_images':images,'linked_libraries':[lib.filepath for lib in bpy.data.libraries if lib.filepath]}
(root/'model_probe.json').write_text(json.dumps(result,indent=2),encoding='utf-8');print(json.dumps(result,indent=2))
if result['footprint_missing_count'] or result['footprint_extra_count']:raise RuntimeError('GIS footprint vertex set differs')

