import bpy, json
names=[o.name for o in bpy.data.objects if any(k in o.name.lower() for k in ['1086','atrium','floor','railing','stair'])]
print('collections',[(c.name,len(c.objects),len(c.all_objects)) for c in bpy.data.collections])
for n in names[:35]:
 o=bpy.data.objects[n]
 print(n,o.type,[c.name for c in o.users_collection],tuple(round(v,3) for v in o.location),tuple(round(v,3) for v in o.rotation_euler))
