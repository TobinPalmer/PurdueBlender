import bpy
bpy.ops.wm.open_mainfile(filepath=r'C:\Users\Tobin\Documents\Blender\PurdueMap\modular\buildings\knoy_hall.blend')
o=bpy.data.objects['KNOY_Entrances_And_Canopies']
print('world matrix')
for r in o.matrix_world:print(tuple(round(x,3) for x in r))
print('materials',[(m.name if m else None) for m in o.data.materials])
for p in o.data.polygons:
 c=o.matrix_world@p.center
 if abs(c.y+46)<2 and -5<c.x<5:
  print('face',p.index,'mat',p.material_index,'center',tuple(round(v,2) for v in c),'verts',[tuple(round(v,2) for v in o.matrix_world@o.data.vertices[i].co) for i in p.vertices])
