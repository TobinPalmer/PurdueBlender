import bpy
p=r'C:\Users\Tobin\Documents\Blender\PurdueMap\modular\site\campus_site.blend'; bpy.ops.wm.open_mainfile(filepath=p)
for o in bpy.data.objects:
 x,y,z=o.location
 if abs(x)<100 and 120<y<370 and any(t in o.name.lower() for t in ['engineering_mall','fountain','tree','walk','promenade','lawn','path','landscape']):
  bb=[o.matrix_world @ __import__('mathutils').Vector(c) for c in o.bound_box]
  mn=[min(v[i] for v in bb) for i in range(3)]; mx=[max(v[i] for v in bb) for i in range(3)]
  print(o.name,o.type,'loc',tuple(round(v,1) for v in o.location),'dim',tuple(round(mx[i]-mn[i],1) for i in range(3)),'mat',','.join(m.name for m in o.data.materials if m) if o.type=='MESH' else '')
