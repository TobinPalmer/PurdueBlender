import bpy
from mathutils import Vector
p=r'C:/Users/Tobin/Documents/Blender/PurdueMap/modular/buildings/krannert_building.blend'
bpy.ops.wm.open_mainfile(filepath=p)
for n in ['KRAN_Exterior_Masonry_Walls','KRAN_Vertical_Limestone_Piers']:
    o=bpy.data.objects[n]
    pts=[o.matrix_world @ Vector(c) for c in o.bound_box]
    print(n,'loc',list(o.location),'parent',o.parent.name if o.parent else None,'bounds',[(min(getattr(v,a) for v in pts),max(getattr(v,a) for v in pts)) for a in 'xyz'])
for n in ['Cam_KRAN_02_SW_StateSt_Entrance','Cam_KRAN_03_SE_GrantSt_Corner']:
    o=bpy.data.objects[n]
    print(n,'world',list(o.matrix_world.translation),'dir',list(o.matrix_world.to_3x3() @ Vector((0,0,-1))))
