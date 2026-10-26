import bpy,os
for f in ['south_hall','stewart_center','tarkington_hall','university_hall','walc']:
 bpy.ops.wm.open_mainfile(filepath=os.path.abspath(f'modular/buildings/{f}.blend'));print('\n',f)
 arr=[]
 for o in bpy.data.objects:
  if o.type!='MESH':continue
  zmax=max((o.matrix_world@__import__('mathutils').Vector(c)).z for c in o.bound_box)
  if zmax>10 and o.dimensions.x*o.dimensions.y>100:arr.append((zmax,o))
 for z,o in sorted(arr,key=lambda x:x[0],reverse=True)[:8]:print(round(z,1),o.name,tuple(round(v,1) for v in o.dimensions),[m.name for m in o.data.materials if m])
