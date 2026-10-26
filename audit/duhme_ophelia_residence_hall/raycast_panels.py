import bpy
from mathutils import Vector
s=bpy.context.scene;c=s.camera;deps=bpy.context.evaluated_depsgraph_get();origin=c.matrix_world.translation
for py in [0.35,0.45,0.55,0.65,0.75]:
 for px in [0.48,0.55,0.62,0.69,0.76]:
  frame=c.data.view_frame(scene=s);left=frame[0];right=frame[1];top=frame[2];bottom=frame[0]
  # interpolate camera-local point from bottom edge to top edge
  bl=frame[0];br=frame[1];tr=frame[2];tl=frame[3]
  bottomp=bl.lerp(br,px);topp=tl.lerp(tr,px);loc=topp.lerp(bottomp,py)
  direction=(c.matrix_world.to_3x3()@loc).normalized()
  hit,pt,no,face,obj,m=s.ray_cast(deps,origin,direction)
  print(round(px,2),round(py,2),obj.name if hit and obj else '-')
