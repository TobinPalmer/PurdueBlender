import bpy
from pathlib import Path
from mathutils import Vector
p=Path(r'C:\Users\Tobin\Documents\Blender\PurdueMap\modular\buildings\morgan_j_burke_boilermaker_aquatic_center.blend')
bpy.ops.wm.open_mainfile(filepath=str(p))
letter=bpy.data.objects['AQUA R1 | north facade building name']; letter.location.z=6.65
cam=bpy.data.objects['AQUA R3 | Street Approach Camera']; cam.location=(-1.3,72.7,1.7); cam.rotation_euler=(Vector((15,59,4.2))-cam.location).to_track_quat('-Z','Y').to_euler(); cam.data.lens=24
bpy.data.objects['AQUA R3 | North Elevation Camera'].data.ortho_scale=78
# Retarget sign close-up around new direct-mounted lettering.
signcam=bpy.data.objects['AQUA R2 | North Sign Camera']; signcam.rotation_euler=(Vector((0,51.2,6.65))-signcam.location).to_track_quat('-Z','Y').to_euler()
bpy.ops.wm.save_as_mainfile(filepath=str(p));print('Saved camera/lettering adjustment')
