import bpy, os
p=os.path.abspath('modular/buildings/niswonger_aviation_tech.blend'); bpy.ops.wm.open_mainfile(filepath=p)
print('objects',len(bpy.data.objects),'scenes',[(s.name,s.camera.name if s.camera else None) for s in bpy.data.scenes])
for s in bpy.data.scenes:
 print('scene',s.name,'collections',len(s.collection.children),'layers',[l.name for l in s.view_layers])
for o in bpy.data.objects:
 if o.type=='MESH' and ('NISW_Walls' in o.name or 'NISW_Roof' in o.name or 'NISW_Site' in o.name):
  print('OBJ',o.name,'loc',tuple(round(v,2) for v in o.location),'dims',tuple(round(v,2) for v in o.dimensions),'hide',o.hide_render,'collections',[c.name for c in o.users_collection])

