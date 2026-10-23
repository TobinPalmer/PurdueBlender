import bpy
w=bpy.data.objects['CL50_Corrected_GIS_Wall_Envelope'];m=bpy.data.materials.get('CL50_Finish_Brick');w.data.materials[0]=m
for o in bpy.data.collections['Asset_class_of_1950'].all_objects:
 if o and 'RoundBrickColumn' in o.name:o.data.materials.clear();o.data.materials.append(m)
bpy.ops.wm.save_as_mainfile(filepath=bpy.data.filepath)
