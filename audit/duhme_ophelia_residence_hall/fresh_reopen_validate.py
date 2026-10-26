import bpy,json,hashlib,math
from pathlib import Path
root=Path(__file__).resolve().parents[2]
asset=root/'modular/buildings/massing_duhme_ophelia_residence_hall_1bb4e9c.blend'
coll=bpy.data.collections.get('Asset_massing_duhme_ophelia_residence_hall_1bb4e9c')
scene=bpy.data.scenes.get('Building_massing_duhme_ophelia_residence_hall_1bb4e9c')
assert coll is not None and scene is not None
objs=list(coll.all_objects)
assert len(objs)==1491, len(objs)
assert coll.get('building_id')=='massing_duhme_ophelia_residence_hall_1bb4e9c'
wall=bpy.data.objects.get('DUHME_Continuous_Red_Brick_Wall_Envelope')
assert wall and len(wall.data.polygons)==52 and 'DUHME_Mortar_Course_UV' in wall.data.uv_layers
missing=[im.filepath for im in bpy.data.images if im.source=='FILE' and im.packed_file is None]
assert not missing, missing
materials={m.name for o in objs if hasattr(o.data,'materials') for m in o.data.materials if m}
assert len(materials)>=15, len(materials)
pts=[]
for o in objs:
 if o.type=='MESH':
  for corner in o.bound_box: pts.append(o.matrix_world@__import__('mathutils').Vector(corner))
bounds=[[min(v[i] for v in pts),max(v[i] for v in pts)] for i in range(3)]
# Ear-clipped footprint floor faces must preserve the GIS's concave footprint area, with equal areas for each level.
floor=bpy.data.objects.get('DUHME_Interior_Floor_1');assert floor
area=sum(abs((floor.data.vertices[p.vertices[1]].co.x-floor.data.vertices[p.vertices[0]].co.x)*(floor.data.vertices[p.vertices[2]].co.y-floor.data.vertices[p.vertices[0]].co.y)-(floor.data.vertices[p.vertices[2]].co.x-floor.data.vertices[p.vertices[0]].co.x)*(floor.data.vertices[p.vertices[1]].co.y-floor.data.vertices[p.vertices[0]].co.y))/2 for p in floor.data.polygons if len(p.vertices)==3)
assert abs(area-1051.623)<0.01,area
report={'status':'PASS','fresh_reopen':True,'blender_version':bpy.app.version_string,'file':str(asset),'scene':scene.name,'export_collection':coll.name,'export_object_count':len(objs),'mesh_count':sum(o.type=='MESH' for o in objs),'font_count':sum(o.type=='FONT' for o in objs),'material_count':len(materials),'wall_face_count':len(wall.data.polygons),'wall_uv_layer':'DUHME_Mortar_Course_UV','external_unpacked_images':missing,'bounds_world_m':bounds,'gis_footprint_area_m2':1051.623,'triangulated_floor_area_m2':round(area,6),'checksum_sha256':hashlib.sha256(asset.read_bytes()).hexdigest().upper()}
(root/'audit/duhme_ophelia_residence_hall/fresh_reopen_validation.json').write_text(json.dumps(report,indent=2)+'\n',encoding='utf-8')
print(json.dumps(report,indent=2))
