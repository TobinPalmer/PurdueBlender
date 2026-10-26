import bpy,json
bpy.ops.wm.open_mainfile(filepath='modular/buildings/bell_tower.blend')
c=bpy.data.collections['Asset_bell_tower']; d=bpy.context.evaluated_depsgraph_get(); out=[]
for o in c.objects:
 if o.name.startswith(('Ground_Limestone_Foot_','Ground_Limestone_Pier_')):
  e=o.evaluated_get(d); m=e.to_mesh(); ps=[e.matrix_world@v.co for v in m.vertices];e.to_mesh_clear()
  b=[[min(p[i] for p in ps),max(p[i] for p in ps)] for i in range(3)]
  out.append({'name':o.name,'bounds':b})
print(json.dumps(out,indent=2))
