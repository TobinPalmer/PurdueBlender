import bpy
from mathutils import Vector
bpy.ops.wm.open_mainfile(filepath=r'C:/Users/Tobin/Documents/Blender/PurdueMap/modular/buildings/krannert_building.blend')
C=bpy.data.collections['Asset_krannert_building']
for n in ['KRAN_FloorSlab_SubBasement','KRAN_FloorSlab_Basement','KRAN_FloorSlab_Ground_L0','KRAN_FloorSlab_Floor_L1','KRAN_FloorSlab_Floor_L2','KRAN_FloorSlab_Floor_L3','KRAN_FloorSlab_Floor_L4','KRAN_FloorSlab_Floor_L5','KRAN_FloorSlab_Floor_L6','KRAN_FloorSlab_Floor_L7','KRAN_FloorSlab_Roof_Deck','KRAN_New_DrawingRoom_Carpet']:
 o=bpy.data.objects.get(n)
 if o:
  pts=[o.matrix_world@Vector(v) for v in o.bound_box];print(n,'bounds',[(round(min(v[i] for v in pts),2),round(max(v[i] for v in pts),2)) for i in range(3)],'location',tuple(round(v,2) for v in o.location),'parent',o.parent.name if o.parent else None)
for o in C.all_objects:
 if o.name.startswith(('KRAN_New_DrawingRoom_OakTable','KRAN_New_Parrish','KRAN_New_AcousticBlueDivider','KRAN_New_StudyDesk','KRAN_New_Seat','KRAN_New_Back')):
  print(o.name,'loc',tuple(round(v,2) for v in o.location),'dim',tuple(round(v,2) for v in o.dimensions),'parent',o.parent.name if o.parent else None)
