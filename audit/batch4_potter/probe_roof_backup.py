import bpy
P=r'C:/Users/Tobin/Documents/Blender/PurdueMap/audit/batch4_potter/round2.blend';bpy.ops.wm.open_mainfile(filepath=P);c=bpy.data.collections['Asset_potter_engineering'];o=c.objects['POTR_Official_864_Roof'];print(o.data.name, len(o.data.vertices),len(o.data.polygons), min(v.co.z for v in o.data.vertices),max(v.co.z for v in o.data.vertices))
