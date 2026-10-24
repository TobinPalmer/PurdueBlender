import bpy
from mathutils import Vector
bpy.ops.wm.open_mainfile(filepath=r'modular/buildings/materials_science_and_electrical_engineering_msee.blend')
s=bpy.data.objects['MSEE_Max_W_Brown_two_story_glazed_atrium']; pts=[s.matrix_world@v.co for v in s.data.vertices]; cen=sum(pts,Vector())/len(pts); t=Vector((.627,-.779,0)).normalized(); n=Vector((-t.y,t.x,0))
print('coordinate',cen,'inward',n)
for o in bpy.data.collections['Asset_materials_science_and_electrical_engineering_msee'].all_objects:
 if any(x in o.name.lower() for x in ('partition','floor','lab','gallery','atrium','interior','room','stair','study','table','screen','bench')) and o.type=='MESH':
  c=o.matrix_world.translation; d=(c-cen).dot(n)
  if -3<d<22:
   print(round(d,1),round(c.z,1),o.name)
