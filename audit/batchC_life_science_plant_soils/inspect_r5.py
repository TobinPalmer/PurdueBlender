import bpy
f=r'C:\Users\Tobin\Documents\Blender\PurdueMap\modular\buildings\life_science_plant_and_soils_laboratory.blend'
bpy.ops.wm.open_mainfile(filepath=f)
for c in ['LSPS_Facade','LSPS_Structure']:
 co=bpy.data.collections.get(c); print('\nCOLL',c, len(co.objects) if co else None)
 if co:
  for o in list(co.objects)[:40]:
   if o.type=='MESH':
    bb=[o.matrix_world@__import__('mathutils').Vector(v) for v in o.bound_box]
    mn=[min(v[i] for v in bb) for i in range(3)]; mx=[max(v[i] for v in bb) for i in range(3)]
    print(o.name, 'bounds', [round(x,2) for x in mn], [round(x,2) for x in mx], 'mats',[m.name if m else None for m in o.data.materials])
