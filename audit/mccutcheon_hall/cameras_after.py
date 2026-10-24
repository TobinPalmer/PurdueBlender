import bpy,json
out=[]
for o in bpy.data.objects:
 if o.type=='CAMERA':
  out.append({'name':o.name,'location':list(o.location),'rotation':list(o.rotation_euler),'lens':o.data.lens,'parent':o.parent.name if o.parent else None,'world':list(o.matrix_world.translation)})
print(json.dumps(out))
