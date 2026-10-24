import bpy
bpy.ops.wm.open_mainfile(filepath=r'C:\Users\Tobin\Documents\Blender\PurdueMap\modular\site\campus_site.blend')
for n in ['EngFountain_Aerated_Base_Foam_Pool','EngFountain_Sculpted_Waterfall_Curtain_135','Engineering_Fountain_Parabolic_Pylon_135','Fountain_Plaza_Concentric_Brick_Ring']:
 o=bpy.data.objects.get(n); print(n, 'loc',tuple(o.location), 'parent',o.parent.name if o.parent else None,'matrix',tuple(o.matrix_world.translation),'bound',tuple(o.bound_box[0]))
