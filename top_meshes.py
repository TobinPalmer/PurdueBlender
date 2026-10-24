import bpy,os
for f in ['south_hall','stewart_center','tarkington_hall','university_hall','walc']:
 bpy.ops.wm.open_mainfile(filepath=os.path.abspath(f'modular/buildings/{f}.blend'));print('\n',f)
 objs=[o for o in bpy.data.objects if o.type=='MESH' and max(o.dimensions)<200]
 objs=sorted(objs,key=lambda o:o.dimensions.x*o.dimensions.y,reverse=True)[:12]
 for o in objs:
  mats=[m.name for m in o.data.materials if m]
  print(o.name,tuple(round(v,1) for v in o.dimensions),tuple(round(v,1) for v in o.location),mats[:3])
