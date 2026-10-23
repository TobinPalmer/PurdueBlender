import bpy
P=r'C:/Users/Tobin/Documents/Blender/PurdueMap/modular/buildings/potter_engineering.blend';bpy.ops.wm.open_mainfile(filepath=P);c=bpy.data.collections['Asset_potter_engineering'];o=c.objects['POTR_Official_864_Roof'];print('roofmats',[(m.name if m else None) for m in o.data.materials]);print([(i,p.material_index) for i,p in enumerate(o.data.polygons[:5])]);
