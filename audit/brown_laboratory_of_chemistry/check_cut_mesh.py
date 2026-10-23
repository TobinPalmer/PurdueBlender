import bpy
from pathlib import Path
bpy.ops.wm.open_mainfile(filepath=r'C:\Users\Tobin\Documents\Blender\PurdueMap\modular\buildings\brown_laboratory_of_chemistry.blend')
for n in ('Exterior_Brickwork_EW','Exterior_Brickwork_NS','Exterior_Concrete_Piers_and_Coping','Exterior_Glazing','Exterior_Window_Frames'):
 o=bpy.data.objects.get(n)
 if not o: print(n,'MISSING'); continue
 ys=[(o.matrix_world@__import__('mathutils').Vector(v.co)).y for v in o.data.vertices]
 candidates=[]
 for p in o.data.polygons:
  c=p.center
  if abs(p.normal.y)>.8 and .05<c.z<16.3: candidates.append((round(c.y,3),round(p.normal.y,1),round(c.z,2)))
 print(n, 'boundsY', min(ys),max(ys),'facadefaces',len(candidates),'ySamples',sorted(candidates)[:6])
