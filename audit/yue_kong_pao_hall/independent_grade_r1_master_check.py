import bpy,json,os
p=r'C:\Users\Tobin\Documents\Blender\PurdueMap\purdue_campus_master.blend'; bpy.ops.wm.open_mainfile(filepath=p)
terms=('yue','pao','visual and performing arts')
libs=[{'filepath':l.filepath,'name':l.name} for l in bpy.data.libraries]
objs=[]
for o in bpy.data.objects:
 if any(t in o.name.lower() for t in terms):
  objs.append({'name':o.name,'type':o.type,'location':list(o.location),'rotation':list(o.rotation_euler),'scale':list(o.scale),'instance_collection':o.instance_collection.name if o.instance_collection else None,'library':o.library.filepath if o.library else None,'users_collection':[c.name for c in o.users_collection]})
for c in bpy.data.collections:
 if any(t in c.name.lower() for t in terms): objs.append({'collection':c.name,'objects':len(c.objects),'children':[x.name for x in c.children]})
out={'file':p,'libraries':libs,'matches':objs}
outp=r'C:\Users\Tobin\Documents\Blender\PurdueMap\audit\yue_kong_pao_hall\independent_grade_r1_master_check.json'; open(outp,'w').write(json.dumps(out,indent=2)); print(json.dumps(out,indent=2))
