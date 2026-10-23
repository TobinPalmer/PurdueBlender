import bpy,json
bpy.ops.wm.open_mainfile(filepath=r'C:/Users/Tobin/Documents/Blender/PurdueMap/modular/buildings/elliott_hall_of_music.blend');c=bpy.data.collections['Asset_elliott_hall_of_music'];out=[]
for o in c.objects:
 if o.type!='MESH':continue
 pts=[o.matrix_world@v.co for v in o.data.vertices]; lo=[min(v[i] for v in pts) for i in range(3)];hi=[max(v[i] for v in pts) for i in range(3)]
 if lo[0]<47 and hi[0]>41 and lo[1]<12 and hi[1]>6 and lo[2]<8 and hi[2]>3.5:
  out.append({'name':o.name,'bounds':[[round(x,3) for x in lo],[round(x,3) for x in hi]],'mat':[m.name for m in o.data.materials]})
print(json.dumps(out,indent=2))
