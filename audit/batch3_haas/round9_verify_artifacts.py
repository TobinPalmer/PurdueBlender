import bpy
C=bpy.data.collections['Asset_felix_haas_hall'];A=bpy.data.collections.get('Reference_Incompatible_Geometry_felix_haas_hall')
print('ALG',[(n,bpy.data.objects.get(n).users_collection[0].name if bpy.data.objects.get(n) else None) for n in ['HAAS_Algorithm_1','HAAS_Algorithm_2','HAAS_Algorithm_3']])
print('ARCHIVE',A.hide_render,A.hide_viewport if hasattr(A,'hide_viewport') else None)
print('BANDS',[(n,bool(bpy.data.objects.get(n))) for n in ['HAAS_R4_Long_South_Band_1','HAAS_R4_Long_North_Band_1','HAAS_R5_Pavilion_SouthBand_1','HAAS_R5_Pavilion_NorthBand_1']])
print('BLUE_TEXT',[(o.name,o.hide_render,[c.name for c in o.users_collection]) for o in bpy.data.objects if o.type=='FONT' and o.name.startswith('HAAS_Algorithm')])
