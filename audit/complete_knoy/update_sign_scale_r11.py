import bpy
from pathlib import Path
p=r'C:\Users\Tobin\Documents\Blender\PurdueMap\modular\buildings\knoy_hall.blend'
bpy.ops.wm.open_mainfile(filepath=p)
o=bpy.data.objects['KNOY_Entrance_Sign_Lettering']
o.scale=(0.8,0.8,0.8)
o['estimated_text_height_m']=0.24
o['geometry_status']='Text and south entrance zone are photo-supported; size reduced to a conservative 0.24 m type scale after R10 reviewer noted oversized appearance. Exact scale and mounting position remain estimated from an uncalibrated photo.'
bpy.ops.wm.save_as_mainfile(filepath=p)
print('Saved sign scale',tuple(o.scale),'world origin',tuple(o.matrix_world.translation))
