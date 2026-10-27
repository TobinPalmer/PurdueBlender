import bpy, json, hashlib
from pathlib import Path
root=Path(__file__).resolve().parents[3]
asset=root/'modular/buildings/massing_ralph_bettye_bailey_hall_406c4db.blend'
bpy.ops.wm.open_mainfile(filepath=str(asset))
obj=bpy.data.objects.get('Ralph & Bettye Bailey Hall')
scene=bpy.data.scenes.get('Building_massing_ralph_bettye_bailey_hall_406c4db')
coll=bpy.data.collections.get('Asset_massing_ralph_bettye_bailey_hall_406c4db')
assert obj and scene and coll and obj.name in coll.objects and len(coll.objects)==1
# Freshly inspect image inputs used by material node trees.
images=[]
for im in bpy.data.images:
 if im.source=='FILE':
  p=Path(bpy.path.abspath(im.filepath)) if im.filepath else None
  images.append({'name':im.name,'filepath':im.filepath,'exists':bool(p and p.is_file()),'packed':bool(im.packed_file)})
mesh=obj.data
report={'fresh_open':True,'blender':bpy.app.version_string,'asset':str(asset),'sha256':hashlib.sha256(asset.read_bytes()).hexdigest().upper(),'scene':scene.name,'collection':coll.name,'object':obj.name,'vertices':len(mesh.vertices),'faces':len(mesh.polygons),'materials':[m.name for m in mesh.materials if m],'images':images,'bbox_local':[[min(v.co[i] for v in mesh.vertices),max(v.co[i] for v in mesh.vertices)] for i in range(3)],'interior_face_count':sum(1 for p in mesh.polygons if p.material_index>=5),'object_props':{'gis_feature_id':obj.get('gis_feature_id'),'proposed_master_placement_xy_m':list(obj.get('proposed_master_placement_xy_m',[])),'interior_status':obj.get('interior_status')}}
out=Path(__file__).resolve().parent/'fresh_open.json';out.write_text(json.dumps(report,indent=2),encoding='utf-8');print(json.dumps(report,indent=2))


