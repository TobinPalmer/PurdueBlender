import bpy,json
bpy.ops.wm.open_mainfile(filepath=r'C:/Users/Tobin/Documents/Blender/PurdueMap/modular/buildings/elliott_hall_of_music.blend')
coll=bpy.data.collections['Asset_elliott_hall_of_music']
terms=('stage','seat','balcony','aisle','ceiling','shell','curtain','screen','floor','orchestra','wall')
out=[]
for o in coll.objects:
 if any(t in o.name.lower() for t in terms):
  pts=[o.matrix_world@v.co for v in o.data.vertices] if o.type=='MESH' else []
  if pts:
   mins=[min(p[i] for p in pts) for i in range(3)];maxs=[max(p[i] for p in pts) for i in range(3)]
   out.append((o.name,[round(x,1) for x in mins],[round(x,1) for x in maxs]))
print(json.dumps(out,indent=2))
