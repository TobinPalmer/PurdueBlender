import bpy,json
bpy.ops.wm.open_mainfile(filepath=r'C:\Users\Tobin\Documents\Blender\PurdueMap\modular\buildings\neil_armstrong_hall.blend')
out={}
for name in ['ARMS_East_Roof_Slab','ARMS_West_Roof_Slab']:
 o=bpy.data.objects[name]; rows=[]
 for p in o.data.polygons:
  if p.normal.z>.75:
   rows.append([list(o.matrix_world@o.data.vertices[i].co) for i in p.vertices])
 out[name]=rows
print(json.dumps(out))
