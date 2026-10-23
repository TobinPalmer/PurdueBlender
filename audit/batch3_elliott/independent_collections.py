import bpy,json
p=r'C:/Users/Tobin/Documents/Blender/PurdueMap/modular/buildings/elliott_hall_of_music.blend';bpy.ops.wm.open_mainfile(filepath=p)
out=[]
for c in bpy.data.collections:
 objs=list(c.objects)
 if objs: out.append({'collection':c.name,'direct_objects':len(objs),'samples':[o.name for o in objs[:8]],'visible':c.hide_viewport,'render':c.hide_render,'children':[x.name for x in c.children]})
print(json.dumps(out,indent=2))
