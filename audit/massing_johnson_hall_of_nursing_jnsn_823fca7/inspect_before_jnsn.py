import bpy,json,os,math
ID='massing_johnson_hall_of_nursing_jnsn_823fca7'
coll=bpy.data.collections.get('Asset_'+ID); scene=bpy.data.scenes.get('Building_'+ID)
assert coll and scene
objs=list(coll.objects)
rows=[]
for o in objs:
 if o.type=='MESH':
  deps=bpy.context.evaluated_depsgraph_get(); ev=o.evaluated_get(deps); m=ev.to_mesh(); vs=[ev.matrix_world@v.co for v in m.vertices]
  b=[[min(v[k] for v in vs),max(v[k] for v in vs)] for k in range(3)]
  rows.append({'name':o.name,'type':o.type,'verts':len(m.vertices),'faces':len(m.polygons),'bounds':b,'dimensions':[q[1]-q[0] for q in b],'location':list(o.location),'modifiers':[x.name for x in o.modifiers],'materials':[x.name if x else None for x in m.materials]})
  ev.to_mesh_clear()
print(json.dumps({'scene':scene.name,'collection':coll.name,'objects':rows},indent=2))
