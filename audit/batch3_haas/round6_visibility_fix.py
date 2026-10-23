import bpy
for old,new in [('HAAS_R6_Estimated_Interior_Door_Leaves','HAAS_Plan_R6_Estimated_Door_Leaves'),('HAAS_R6_Estimated_Interior_Door_Frames','HAAS_Plan_R6_Estimated_Door_Frames')]:
 o=bpy.data.objects.get(old)
 if o:o.name=new;o.data.name=new+'_Mesh'
bpy.ops.wm.save_as_mainfile(filepath=bpy.data.filepath)
print('R6_INTERIOR_VISIBLE',len(bpy.data.collections['Asset_felix_haas_hall'].objects))
