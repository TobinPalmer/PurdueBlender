import bpy, json, os, hashlib
asset=r'modular/buildings/american_railway_building.blend'
bpy.ops.wm.open_mainfile(filepath=asset)
c=bpy.data.collections['Asset_american_railway_building']
s=bpy.data.scenes.get('Building_american_railway_building')
objs=list(c.all_objects); meshes=[o for o in objs if o.type=='MESH']
missing=[]
for o in meshes:
 if not o.data.materials: missing.append(o.name)
images=[{'path':i.filepath,'packed':bool(i.packed_file)} for i in bpy.data.images if i.source=='FILE']
bounds=[[min((o.matrix_world@v.co)[i] for o in meshes for v in o.data.vertices),max((o.matrix_world@v.co)[i] for o in meshes for v in o.data.vertices)] for i in range(3)]
print(json.dumps({'asset':bpy.data.filepath,'scene':s.name if s else None,'collection':c.name,'objects':len(objs),'meshes':len(meshes),'unmaterialed_meshes':missing,'local_coordinates':c.get('local_coordinates'),'placement_origin_xy_m':[float(x) for x in c.get('placement_origin_xy_m',[])],'bounds':bounds,'images':images,'asset_exists':True},indent=2))
