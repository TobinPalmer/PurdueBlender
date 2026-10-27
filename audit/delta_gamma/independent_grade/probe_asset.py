import bpy,json,math
from pathlib import Path
root=Path(__file__).resolve().parents[3]
asset=root/'modular/buildings/massing_house_301840872_582df9d.blend'
raw=json.load(open(root/'audit/delta_gamma/sources/purdue_gis_fid783_raw.json',encoding='utf8'))
ring=raw['features'][0]['geometry']['rings'][0][:-1];lat0=40.4274;lon0=-86.9137
expected=[((x-lon0)*111412.84*math.cos(math.radians(lat0)),(y-lat0)*111040.) for x,y in ring]
bpy.ops.wm.open_mainfile(filepath=str(asset))
col=bpy.data.collections.get('Asset_massing_house_301840872_582df9d')
objs=list(col.objects) if col else []
assert col and len(objs)==1
obj=objs[0]
base=[(v.co.x,v.co.y) for v in obj.data.vertices if abs(v.co.z)<1e-5]
nearest=[min(math.hypot(x-p[0],y-p[1]) for x,y in base) for p in expected]
assert max(nearest)<0.0001,max(nearest)
assert obj.name=='House_301840872' and obj.type=='MESH'
assert tuple(obj.location)==(0.,0.,0.) and tuple(obj.rotation_euler)==(0.,0.,0.) and tuple(obj.scale)==(1.,1.,1.)
bpy.context.view_layer.update(); ev=obj.evaluated_get(bpy.context.evaluated_depsgraph_get());mesh=ev.to_mesh();coords=[ev.matrix_world@v.co for v in mesh.vertices]
bounds=[[min(v[i] for v in coords),max(v[i] for v in coords)] for i in range(3)]
report={'asset_opened':True,'asset_path':'modular/buildings/massing_house_301840872_582df9d.blend','manifest_expected_id':'massing_house_301840872_582df9d','expected_collection_present':True,'collection_objects':[o.name for o in objs],'object_type':obj.type,'identity_transform':{'location':list(obj.location),'rotation':list(obj.rotation_euler),'scale':list(obj.scale)},'mesh_vertices':len(mesh.vertices),'mesh_faces':len(mesh.polygons),'modifiers':[m.name for m in obj.modifiers],'parent':obj.parent.name if obj.parent else None,'evaluated_bounds_xyz_m':bounds,'gis_feature_id':raw['features'][0]['attributes']['FID'],'gis_unique_vertices':len(expected),'gis_nearest_residuals_m':nearest,'max_footprint_vertex_residual_m':max(nearest),'external_file_images':[im.filepath for im in bpy.data.images if im.source=='FILE' and im.filepath],'expected_structure_verified':True}
ev.to_mesh_clear()
out=root/'audit/delta_gamma/independent_grade/blender_probe.json';out.write_text(json.dumps(report,indent=2)+'\n',encoding='utf8');print(json.dumps(report))
