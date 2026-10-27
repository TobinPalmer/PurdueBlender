import bpy, json
p=r'modular/buildings/massing_purdue_village_administration_building_3faae6c.blend'
bpy.ops.wm.open_mainfile(filepath=p)
objs=[]
for o in bpy.context.scene.objects:
 if o.type=='MESH':
  deps=bpy.context.evaluated_depsgraph_get(); ev=o.evaluated_get(deps); mesh=ev.to_mesh()
  coords=[o.matrix_world @ v.co for v in mesh.vertices]
  bounds=[[min(v[i] for v in coords),max(v[i] for v in coords)] for i in range(3)] if coords else []
  objs.append({'name':o.name,'loc':list(o.location),'dims':list(o.dimensions),'bounds':bounds,'verts':len(mesh.vertices),'faces':len(mesh.polygons)})
  ev.to_mesh_clear()
print(json.dumps({'file':p,'scene':bpy.context.scene.name,'objects':objs,'collections':[(c.name,len(c.objects)) for c in bpy.data.collections]},indent=2))
