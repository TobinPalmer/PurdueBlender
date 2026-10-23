import bpy
from pathlib import Path
R=Path(r'C:/Users/Tobin/Documents/Blender/PurdueMap');bpy.context.scene.view_settings.exposure=0;bpy.context.scene.view_settings.view_transform='AgX';bpy.ops.wm.save_as_mainfile(filepath=str(R/'modular/buildings/mechanical_engineering.blend'))
