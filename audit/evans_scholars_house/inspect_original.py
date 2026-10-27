import bpy,json
p='modular/buildings/massing_house_301841610_b6ad6ed.blend'
bpy.ops.wm.open_mainfile(filepath=p)
objs=[]
for o in bpy.data.objects:
 if o.type=='MESH':
  coords=[o.matrix_world @ v.co for v in o.data.vertices]
  if coords:
   mn=[min(v[i] for v in coords) for i in range(3)]; mx=[max(v[i] for v in coords) for i in range(3)]
   objs.append({'name':o.name,'collection':[c.name for c in o.users_collection],'verts':len(o.data.vertices),'faces':len(o.data.polygons),'bounds_min':mn,'bounds_max':mx,'loc':list(o.location),'dims':list(o.dimensions)})
print(json.dumps({'scene':bpy.context.scene.name,'objects':objs},indent=2))
