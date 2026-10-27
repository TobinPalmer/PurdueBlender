import bpy
for o in bpy.data.objects:
 if o.name in {'Facade glazing | repeated vision panels','Continuous horizontal facade banding'} or 'mullion' in o.name.lower():
  bb=[o.matrix_world @ __import__('mathutils').Vector(c) for c in o.bound_box]
  print(o.name, 'loc',tuple(round(v,3) for v in o.location),'dims',tuple(round(v,3) for v in o.dimensions),'bounds',[[round(min(v[i] for v in bb),3),round(max(v[i] for v in bb),3)] for i in range(3)])
