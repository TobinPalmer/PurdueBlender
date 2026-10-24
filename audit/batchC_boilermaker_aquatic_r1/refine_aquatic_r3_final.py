import bpy
from pathlib import Path
from mathutils import Vector
p=Path(r'C:\Users\Tobin\Documents\Blender\PurdueMap\modular\buildings\morgan_j_burke_boilermaker_aquatic_center.blend')
bpy.ops.wm.open_mainfile(filepath=str(p))
# Improve the qualitative street approach angle, without asserting surveyed camera placement.
cam=bpy.data.objects['AQUA R3 | Street Approach Camera']; cam.location=(30,103,5); cam.rotation_euler=(Vector((0,49,4.5))-cam.location).to_track_quat('-Z','Y').to_euler(); cam.data.lens=35
# Reduce roof seam density so they read as standing seams rather than corrugation.
seams=bpy.data.objects['AQUA R3 | subtle standing seams on estimated roof']
for i in list(range(len(seams.data.splines)-1,-1,-1)):
 if i%2==1: seams.data.splines.remove(seams.data.splines[i])
# Eliminate lettering cast shadow that reads as duplicate ghost text on the brick.
letter=bpy.data.objects['AQUA R1 | north facade building name']
if hasattr(letter,'visible_shadow'): letter.visible_shadow=False
# Move lettering close to its facade plane while preserving the qualitative scale estimate.
letter.location.y=51.27
bpy.ops.wm.save_as_mainfile(filepath=str(p)); print('Saved final R3 visual refinements; seams=',len(seams.data.splines),'shadow toggle=',hasattr(letter,'visible_shadow'))
