import bpy,json
from mathutils import Vector
p=r'C:/Users/Tobin/Documents/Blender/PurdueMap/modular/buildings/krannert_building.blend'
bpy.ops.wm.open_mainfile(filepath=p); c=bpy.data.collections['Asset_krannert_building']; root=bpy.data.objects['AssetRoot_krannert_building']
print('objects',len(c.objects),'children',len(c.all_objects),'root',list(root.location),list(root.rotation_euler),list(root.scale))
for n in ['KRAN_Exterior_Masonry_Walls','KRAN_Basement_Foundation_Walls','KRAN_Vertical_Limestone_Piers','KRAN_Window_Ribbon_Glazing','KRAN_Horizontal_Spandrel_Panels','KRAN_Entrance_Arcade_Portico','KRAN_Rooftop_Mechanical_Penthouse','KRAN_Iconic_Facade_Clocks','KRAN_Structural_Circulation_Cores','KRAN_Skywalk_Connection_Portal']:
 o=bpy.data.objects.get(n)
 if o:print(n,'loc',tuple(round(v,2) for v in o.location),'dims',tuple(round(v,2) for v in o.dimensions),'mats',[m.name for m in o.data.materials] if hasattr(o.data,'materials') else None)
print('CAMERAS')
for o in c.all_objects:
 if o.type=='CAMERA':print(o.name,tuple(round(v,2) for v in o.location),o.data.type)
print('IMAGES',[(i.name,i.filepath, bool(i.packed_file)) for i in bpy.data.images])
