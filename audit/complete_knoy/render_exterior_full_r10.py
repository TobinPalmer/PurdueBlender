import bpy
from pathlib import Path
p=r'C:\Users\Tobin\Documents\Blender\PurdueMap\modular\buildings\knoy_hall.blend';bpy.ops.wm.open_mainfile(filepath=p)
s=bpy.context.scene;c=bpy.data.objects.get('KNOY_Audit_Exterior');assert c
s.camera=c;s.render.engine='BLENDER_EEVEE';s.render.resolution_x=1400;s.render.resolution_y=1000;s.render.resolution_percentage=100;s.render.filepath=r'C:\Users\Tobin\Documents\Blender\PurdueMap\audit\complete_knoy\knoy_exterior_full_r10.png'
bpy.ops.render.render(write_still=True)
