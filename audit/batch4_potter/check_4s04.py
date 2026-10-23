import bpy,json
from mathutils import Vector
P=r'C:/Users/Tobin/Documents/Blender/PurdueMap/modular/buildings/potter_engineering.blend';bpy.ops.wm.open_mainfile(filepath=P);c=bpy.data.collections['Asset_potter_engineering'];mass=c.objects['POTR_Historic2016_Room401_Penthouse_Massing'];en=[o for o in c.all_objects if o.name.startswith('POTR_4S04_')];x=min(v.co.x for v in mass.data.vertices);out=[]
for y in (35.3,34.7,35.9):
 origin=Vector((x-1,y,14.4));d=Vector((1,0,0));hit=mass.ray_cast(origin,d,distance=3)[0];eh=[]
 for o in en:
  inv=o.matrix_world.inverted();lo=inv@origin;ld=(inv.to_3x3()@d).normalized();eh.append(o.ray_cast(lo,ld,distance=3)[0])
 out.append({'y':y,'room401_wall_hit':hit,'any_4S04_wall_hit':any(eh)})
print(json.dumps({'west_wall_x':x,'door_tests':out},indent=2))
