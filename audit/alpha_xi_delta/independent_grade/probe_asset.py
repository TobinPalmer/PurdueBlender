import bpy,json,math
from pathlib import Path
P=Path(__file__).resolve().parents[1]
asset=Path('modular/buildings/massing_house_301841248_fe939c7.blend').resolve()
bpy.ops.wm.open_mainfile(filepath=str(asset))
collection=bpy.data.collections.get('Asset_massing_house_301841248_fe939c7')
assert collection is not None
objects=list(collection.objects);assert len(objects)==1
obj=objects[0];assert obj.name=='House_301841248' and obj.type=='MESH'
assert tuple(round(x,6) for x in obj.location)==(0.,0.,0.)
assert tuple(round(x,6) for x in obj.rotation_euler)==(0.,0.,0.)
assert tuple(round(x,6) for x in obj.scale)==(1.,1.,1.)
raw=json.load(open(P/'sources/purdue_gis_fid788_raw.json',encoding='utf8'))
f=raw['features'][0];ring=f['geometry']['rings'][0][:-1]
lat0=40.4274;lon0=-86.9137;expected=[((lon-lon0)*111412.84*math.cos(math.radians(lat0)),(lat-lat0)*111040.0) for lon,lat in ring]
base=[(v.co.x,v.co.y) for v in obj.data.vertices if abs(v.co.z)<1e-6]
residuals=[math.sqrt(min((x-p[0])**2+(y-p[1])**2 for x,y in base)) for p in expected]
assert max(residuals)<0.0001
# Independent evaluated world bounds and material/path checks.
bpy.context.view_layer.update(); dg=bpy.context.evaluated_depsgraph_get(); ev=obj.evaluated_get(dg); me=ev.to_mesh()
coords=[ev.matrix_world@v.co for v in me.vertices]
bounds=[[min(c[i] for c in coords),max(c[i] for c in coords)] for i in range(3)]
images=[i.filepath for i in bpy.data.images if i.source=='FILE' and i.filepath]
result={'model_reopened':True,'asset_path':'modular/buildings/massing_house_301841248_fe939c7.blend','collection':collection.name,'collection_object_count':len(objects),'object_name':obj.name,'object_type':obj.type,'object_transform':{'location':list(obj.location),'rotation_euler':list(obj.rotation_euler),'scale':list(obj.scale)},'evaluated_bounds_xyz_m':bounds,'dimensions_xyz_m':[bounds[i][1]-bounds[i][0] for i in range(3)],'mesh_vertices':len(me.vertices),'mesh_faces':len(me.polygons),'material_names':[m.name if m else None for m in me.materials],'gis_fid':f['attributes']['FID'],'gis_name':f['attributes']['BUILDING_N'],'gis_address':f['attributes']['ADDRESS'],'gis_unique_ring_vertices':len(expected),'base_point_max_residual_m':max(residuals),'base_point_mean_residual_m':sum(residuals)/len(residuals),'external_file_images':images}
ev.to_mesh_clear()
(P/'independent_grade'/'blender_probe.json').write_text(json.dumps(result,indent=2)+'\n',encoding='utf8')
print(json.dumps(result))
