import bpy
p=r'C:\Users\Tobin\Documents\Blender\PurdueMap\modular\buildings\krannert_building.blend';bpy.ops.wm.open_mainfile(filepath=p)
for n in ['KRAN_Vertical_Limestone_Piers','KRAN_Window_Ribbon_Glazing','KRAN_Horizontal_Spandrel_Panels','KRAN_Anodized_Bronze_Mullions']:
 o=bpy.data.objects.get(n);print(n, o and o.type, len(o.data.vertices) if o and o.type=='MESH' else 0, len(o.data.polygons) if o and o.type=='MESH' else 0, tuple(o.location) if o else None)
print('collection',len(bpy.data.collections['Asset_krannert_building'].all_objects))
