import bpy, json
p=r'modular/buildings/massing_the_moosehead_lounge_f81529e.blend'
bpy.ops.wm.open_mainfile(filepath=p)
print('SCENE',[(s.name,len(s.objects)) for s in bpy.data.scenes])
for c in bpy.data.collections:
 if c.name=='Asset_massing_the_moosehead_lounge_f81529e':
  print('COLL',c.name)
  for o in c.objects:
   print('OBJ',o.name,o.type,'loc',list(o.location),'scale',list(o.scale),'dims',list(o.dimensions),'verts',len(o.data.vertices) if o.type=='MESH' else None,'faces',len(o.data.polygons) if o.type=='MESH' else None)
   if o.type=='MESH':
    print('LOCAL VERTS',json.dumps([list(v.co) for v in o.data.vertices]))
