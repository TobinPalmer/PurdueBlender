import bpy
from mathutils import Vector
p=r'C:/Users/Tobin/Documents/Blender/PurdueMap/modular/buildings/hovde_hall.blend';bpy.ops.wm.open_mainfile(filepath=p);c=bpy.data.collections['Asset_hovde_hall']
for o in c.all_objects:
 if 'Capital' in o.name or 'Acanthus' in o.name or 'Column_3' in o.name or 'Leaf' in o.name:
  print(o.name,o.type,'loc',tuple(round(v,3) for v in o.location),'dim',tuple(round(v,3) for v in o.dimensions),'parent',o.parent.name if o.parent else None,'mat',[m.name for m in o.data.materials] if hasattr(o.data,'materials') else None)
print('roof', bpy.data.objects['HOVD_Inferred_Hipped_Roof'].dimensions, bpy.data.objects['HOVD_Inferred_Hipped_Roof'].location, 'vertZ',min(v.co.z for v in bpy.data.objects['HOVD_Inferred_Hipped_Roof'].data.vertices),max(v.co.z for v in bpy.data.objects['HOVD_Inferred_Hipped_Roof'].data.vertices))
