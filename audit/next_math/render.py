import bpy
from pathlib import Path
from mathutils import Vector
D=Path(r'C:/Users/Tobin/Documents/Blender/PurdueMap/audit/next_math')
c=bpy.data.collections['Asset_math_sciences'];s=bpy.data.scenes.new('IsolatedReview');s.collection.children.link(c);bpy.context.window.scene=s
for o in list(c.all_objects):
 if o:o.hide_render=False
c.hide_render=False
s.world=bpy.data.worlds.new('ReviewWorld');s.world.color=(.3,.3,.3)
exec(open(r'C:/Users/Tobin/Documents/Blender/PurdueMap/audit/next_math/finish.py').read().split("camd=bpy.data.cameras.new")[1].split("D.joinpath")[0].join(["camd=bpy.data.cameras.new",'']))



