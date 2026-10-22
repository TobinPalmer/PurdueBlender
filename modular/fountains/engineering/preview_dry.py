import bpy
from pathlib import Path
D=Path(__file__).parent;bpy.ops.wm.open_mainfile(filepath=str(D/'engineering.blend'));s=bpy.context.scene
s.frame_set(1);bpy.data.objects['EF_Liquid_domain'].hide_render=True;s.render.filepath=str(D/'attempt1_dry.png');s.cycles.samples=12;bpy.ops.render.render(write_still=True)
