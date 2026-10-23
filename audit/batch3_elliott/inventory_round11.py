import bpy
bpy.ops.wm.open_mainfile(filepath=r'C:/Users/Tobin/Documents/Blender/PurdueMap/modular/buildings/elliott_hall_of_music.blend');c=bpy.data.collections['Asset_elliott_hall_of_music'];
for o in c.objects:
 if any(k in o.name.lower() for k in ('fly','tower','roof','tile','apse','exit','stair','stage')):
  if o.type=='MESH':
   pts=[o.matrix_world@v.co for v in o.data.vertices];lo=[min(p[i] for p in pts) for i in range(3)];hi=[max(p[i] for p in pts) for i in range(3)];print(o.name,[[round(x,2) for x in lo],[round(x,2) for x in hi]],[m.name for m in o.data.materials])
