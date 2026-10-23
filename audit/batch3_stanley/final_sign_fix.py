import bpy
from mathutils import Vector
p=r'C:\Users\Tobin\Documents\Blender\PurdueMap\modular\buildings\stanley_coulter_hall.blend'
bpy.ops.wm.open_mainfile(filepath=p)
t=bpy.data.objects['SC_Portico_3D_Text'];t.visible_shadow=False
# Sign remains visible, but does not project text onto the limestone lintel.
bpy.ops.wm.save_as_mainfile(filepath=p)
print('saved, sign_shadow_disabled',not t.visible_shadow)
