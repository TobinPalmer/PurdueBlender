import bpy
from mathutils import Vector
bpy.ops.wm.open_mainfile(filepath=r'C:/Users/Tobin/Documents/Blender/PurdueMap/modular/buildings/elliott_hall_of_music.blend');dg=bpy.context.evaluated_depsgraph_get();s=bpy.context.scene
for x,y,z in [(43.45,9.7,5.5),(43.7,9.4,5.6),(43.6,9.65,5.55),(43.4,9.7,5.9)]:
 origin=Vector((x+10*.7743,y+10*.6328,z));direction=Vector((-.7743,-.6328,0));hits=[]
 for _ in range(12):
  ok,loc,norm,face,ob,mat=s.ray_cast(dg,origin,direction)
  if not ok:break
  hits.append((ob.name,tuple(round(v,3) for v in loc)))
  origin=loc+direction*.002
 print((x,y,z),hits)
