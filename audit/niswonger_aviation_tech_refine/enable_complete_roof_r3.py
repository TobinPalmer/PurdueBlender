import bpy
from pathlib import Path
p=Path(r'C:/Users/Tobin/Documents/Blender/PurdueMap/modular/buildings/niswonger_aviation_tech.blend')
for n in ['NISW_Photographic_Sloping_Roof','NISW_Flat_Roof_Membrane']:
 o=bpy.data.objects.get(n); assert o;o.hide_render=False
 print(n,'hide_render',o.hide_render,'hide_viewport',o.hide_viewport,'visible_get',o.visible_get())
bpy.ops.wm.save_as_mainfile(filepath=str(p))
