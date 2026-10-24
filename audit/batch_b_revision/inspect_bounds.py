import bpy
from pathlib import Path
for k,f in [('ford','ford_dining_court.blend'),('heine','heine_pharmacy.blend'),('physics','physics_building_phys_3bf42f3.blend'),('flex','flex_lab.blend')]:
 p=Path(r'C:\Users\Tobin\Documents\Blender\PurdueMap\modular\buildings')/f; bpy.ops.wm.open_mainfile(filepath=str(p)); print('\n',k)
 for o in bpy.data.objects:
  if any(s in o.name.lower() for s in ['pitched standing','estimated sloped red','flat roof cap','roof cap','high-bay research','roof monitor','bridge']):
   pts=[o.matrix_world @ __import__('mathutils').Vector(c) for c in o.bound_box]; bounds=[(min(x[i] for x in pts),max(x[i] for x in pts)) for i in range(3)]; print(o.name, tuple(round(x,2) for x in o.dimensions),[(round(a,2),round(b,2)) for a,b in bounds])
