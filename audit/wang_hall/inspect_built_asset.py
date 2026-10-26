import bpy
p=r'C:\Users\Tobin\Documents\Blender\PurdueMap\modular\buildings\massing_wang_hall_wang_0dac5ab.blend'; bpy.ops.wm.open_mainfile(filepath=p)
for c in bpy.data.collections:
 print('COL',c.name)
 for o in c.objects:
  print(o.name,o.type,tuple(round(v,2) for v in o.location),tuple(round(v,2) for v in o.dimensions), 'mats',[m.name if m else None for m in getattr(o.data,'materials',[])])
  if o.name.endswith('facade glazing and storefront'):
   for m in o.data.materials:
    idx=o.data.materials.find(m.name); polys=[p for p in o.data.polygons if p.material_index==idx]
    print('MATCOUNT',m.name,len(polys))
