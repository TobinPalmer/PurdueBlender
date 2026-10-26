import bpy
from pathlib import Path
from mathutils import Vector
root=Path(__file__).resolve().parents[2];s=bpy.context.scene
keep={'DUHME_Continuous_Red_Brick_Wall_Envelope','DUHME_Continuous_GIS_Footprint_Foundation'}
for o in bpy.data.objects:
 if o.name.startswith('DUHME_') and o.name not in keep: o.hide_render=True
cam=s.camera;target=Vector((-595,-202,7));cam.location=(-565,-250,35);cam.rotation_euler=(target-Vector(cam.location)).to_track_quat('-Z','Y').to_euler();cam.data.type='ORTHO';cam.data.ortho_scale=82
s.render.resolution_x=960;s.render.resolution_y=720;s.render.filepath=str(root/'audit/duhme_ophelia_residence_hall/shell_only.png');bpy.ops.render.render(write_still=True)
