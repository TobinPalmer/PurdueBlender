import bpy, math
from pathlib import Path
from mathutils import Vector
root=Path(__file__).resolve().parents[2]
out=Path(__file__).resolve().parent/'roof_zones_topdown.png'
obj=bpy.data.objects['Animal Holding Facility']
pts=[obj.matrix_world @ v.co for v in obj.data.vertices]
xy=[(p.x,p.y) for p in pts]
cx=sum(x for x,y in xy)/len(xy); cy=sum(y for x,y in xy)/len(xy)
scene=bpy.context.scene
cam_data=bpy.data.cameras.new('AHF audit top camera'); cam=bpy.data.objects.new('AHF audit top camera',cam_data); scene.collection.objects.link(cam)
cam.location=(cx,cy,75); cam.rotation_euler=(0,0,0); cam_data.type='ORTHO'; cam_data.ortho_scale=100; scene.camera=cam
scene.render.engine='BLENDER_EEVEE_NEXT'; scene.render.resolution_x=1200; scene.render.resolution_y=1200; scene.render.resolution_percentage=100
scene.render.image_settings.file_format='PNG'; scene.render.filepath=str(out)
scene.world.color=(0.16,0.17,0.18)
bpy.ops.render.render(write_still=True)
print(out)
