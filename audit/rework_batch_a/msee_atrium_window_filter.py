import bpy, re
from mathutils import Vector
bpy.ops.wm.open_mainfile(filepath=r'modular/buildings/materials_science_and_electrical_engineering_msee.blend')
s=bpy.data.objects['MSEE_Max_W_Brown_two_story_glazed_atrium'];pts=[s.matrix_world@v.co for v in s.data.vertices];cen=sum(pts,Vector())/len(pts);t=Vector((.627,-.779,0)).normalized();n=Vector((-t.y,t.x,0))
for o in bpy.data.collections['Asset_materials_science_and_electrical_engineering_msee'].all_objects:
 if o.name.startswith(('MSEE_window_','MSEE_mullion_','MSEE_sill_')):
  # mesh bounding box transformed
  ps=[o.matrix_world@Vector(v) for v in o.bound_box]; c=sum(ps,Vector())/8; dt=(c-cen).dot(t); dn=(c-cen).dot(n)
  if abs(dt)<12 and dn<3 and dn>-5 and c.z<9:
   print(o.name, 't',round(dt,1),'d',round(dn,1),'z',round(c.z,1),'dim',tuple(round(v,1) for v in o.dimensions))
