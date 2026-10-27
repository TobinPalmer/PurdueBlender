import bpy,json,math
from pathlib import Path
ROOT=Path(__file__).resolve().parents[4]
ASSET=ROOT/'modular/buildings/massing_house_301841601_7ae6159.blend'
OUT=Path(__file__).resolve().parent/'blender_probe.json'
bpy.ops.wm.open_mainfile(filepath=str(ASSET))
col=bpy.data.collections.get('Asset_massing_house_301841601_7ae6159')
obj=bpy.data.objects.get('House_301841601')
assert col is not None and obj is not None
raw=json.loads((ROOT/'audit/delta_zeta/sources/purdue_gis_fid752_raw.json').read_text(encoding='utf8'))
f=raw['features'][0]; ring=f['geometry']['rings'][0][:-1]; lat0=40.4274; lon0=-86.9137
expected=[((lon-lon0)*111412.84*math.cos(math.radians(lat0)),(lat-lat0)*111040.) for lon,lat in ring]
base=[(v.co.x,v.co.y) for v in obj.data.vertices if abs(v.co.z)<1e-5]
residuals=[min(math.hypot(x-px,y-py) for x,y in base) for px,py in expected]
evalobj=obj.evaluated_get(bpy.context.evaluated_depsgraph_get()); mesh=evalobj.to_mesh(); verts=[evalobj.matrix_world@v.co for v in mesh.vertices]
bounds=[[min(v[i] for v in verts),max(v[i] for v in verts)] for i in range(3)]
external=[im.filepath for im in bpy.data.images if im.source=='FILE' and im.filepath]
probe={'blend_reopened':True,'asset_path':str(ASSET),'collection_exists':col.name,'collection_object_names':sorted(o.name for o in col.objects),'object_name':obj.name,'object_type':obj.type,'object_location':list(obj.location),'object_rotation_euler':list(obj.rotation_euler),'object_scale':list(obj.scale),'mesh_vertex_count':len(mesh.vertices),'mesh_face_count':len(mesh.polygons),'evaluated_bounds_xyz_m':bounds,'gis_fid':f['attributes']['FID'],'gis_name':f['attributes']['BUILDING_N'],'gis_address':f['attributes']['ADDRESS'],'gis_unique_vertices':len(expected),'gis_base_match_count':sum(r<=.0001 for r in residuals),'gis_max_base_residual_m':max(residuals),'gis_base_residuals_m':residuals,'external_image_paths':external,'material_names':[m.name if m else None for m in mesh.materials]}
evalobj.to_mesh_clear();OUT.write_text(json.dumps(probe,indent=2)+'\n',encoding='utf8');print(json.dumps(probe))
