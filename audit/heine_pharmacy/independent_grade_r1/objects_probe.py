import bpy,json
from mathutils import Vector
for name in ['RHPH | tall entry arcade pier 0','RHPH | stone arcade arch 0','RHPH | stone arcade arch 1','RHPH | stone arcade arch 2','RHPH | stone arcade arch 3','Heine evidence facade | seven vertical window stacks','Heine evidence facade | limestone window surrounds and spandrels','Heine evidence facade | vertical sash mullions','Facade glazing | repeated vision panels','RHPH structural shell | GIS outline','Continuous horizontal facade banding']:
 o=bpy.data.objects.get(name)
 if not o:
  print('NOT FOUND',name);continue
 bb=[o.matrix_world@Vector(c) for c in o.bound_box]
 bounds=[[round(min(p[i] for p in bb),3),round(max(p[i] for p in bb),3)] for i in range(3)]
 print(name,'type',o.type,'bounds',bounds,'verts',len(o.data.vertices) if o.type=='MESH' else '-')
