import bpy,json
bpy.ops.wm.open_mainfile(filepath=r'C:/Users/Tobin/Documents/Blender/PurdueMap/modular/buildings/elliott_hall_of_music.blend');c=bpy.data.collections['Asset_elliott_hall_of_music']
for o in c.objects:
 if any(k in o.name.lower() for k in ('access_north','access_south','doorleaf','handle')):
  pts=[o.matrix_world@v.co for v in o.data.vertices] if o.type=='MESH' else []
  if not pts:continue
  print(o.name,[[round(min(p[i] for p in pts),3) for i in range(3)],[round(max(p[i] for p in pts),3) for i in range(3)]],[m.name for m in o.data.materials])
