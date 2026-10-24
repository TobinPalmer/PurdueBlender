import bpy
from bpy_extras.object_utils import world_to_camera_view
from mathutils import Vector
s=bpy.context.scene;c=s.camera
for p in [Vector((-7.8042,137.9294,0)),Vector((-7.8042,137.9294,8)),Vector((-31.12,-12.98,10)),Vector((-49.8,78.2,5)),Vector((59.6,122.3,10))]:
 print(tuple(p),tuple(round(float(v),3) for v in world_to_camera_view(s,c,p)))
for o in s.objects:
 if 'Fountain' in o.name or 'Tower' in o.name or 'Hovde' in o.name:
  if o.type=='MESH':
   p=world_to_camera_view(s,c,o.matrix_world.translation)
   print(o.name,tuple(round(float(v),3) for v in p))
