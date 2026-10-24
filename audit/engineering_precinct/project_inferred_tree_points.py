import bpy, math
from mathutils import Vector
from bpy_extras.object_utils import world_to_camera_view
scene=bpy.context.scene
cd=bpy.data.cameras.new('tmp');cam=bpy.data.objects.new('tmp',cd);scene.collection.objects.link(cam);cam.location=(55,185,13);cam.rotation_euler=(Vector((-9.3,108.4,-4))-cam.location).to_track_quat('-Z','Y').to_euler();cd.lens=24;scene.camera=cam;scene.render.resolution_x=1280;scene.render.resolution_y=960;bpy.context.view_layer.update()
def gp(u,v,z=.06):
 sx=36;sy=sx*960/1280
 local=Vector(((2*u-1)*sx/(2*cd.lens),(2*v-1)*sy/(2*cd.lens),-1))
 ray=cam.rotation_euler.to_quaternion()@local;t=(z-cam.location.z)/ray.z
 return cam.location+ray*t
for v in [.25,.30,.35,.40,.45,.50]:
 for u in [.48,.58,.68,.78]:
  pt=gp(u,v); top=world_to_camera_view(scene,cam,pt+Vector((0,0,10)))
  print('uv',u,v,'xy',round(pt.x,1),round(pt.y,1),'top',round(top.x,2),round(top.y,2),'depth',round((pt-cam.location).length,1))
