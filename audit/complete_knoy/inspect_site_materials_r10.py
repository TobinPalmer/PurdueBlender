import bpy,collections
bpy.ops.wm.open_mainfile(filepath=r'C:\Users\Tobin\Documents\Blender\PurdueMap\modular\buildings\knoy_hall.blend')
for name in ['KNOY_Entrances_And_Canopies','KNOY_Plaza_Paving_And_Site']:
 o=bpy.data.objects[name];print('\n',name,len(o.data.vertices),len(o.data.polygons),[m.name if m else None for m in o.data.materials]);counts=collections.Counter(p.material_index for p in o.data.polygons);print('indices',counts)
 for i,m in enumerate(o.data.materials):
  print('mat',i,m.name if m else None,'faces',counts.get(i,0))
