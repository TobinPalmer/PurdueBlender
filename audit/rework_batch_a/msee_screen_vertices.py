import bpy
from mathutils import Vector
bpy.ops.wm.open_mainfile(filepath=r'modular/buildings/materials_science_and_electrical_engineering_msee.blend')
o=bpy.data.objects['MSEE_Max_W_Brown_two_story_glazed_atrium']
pts={tuple(round(v,3) for v in o.matrix_world@v.co) for v in o.data.vertices}
for p in sorted(pts):print(p)
