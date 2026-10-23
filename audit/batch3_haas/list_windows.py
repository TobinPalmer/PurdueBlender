import bpy
for o in bpy.data.collections['Asset_felix_haas_hall'].objects:
 if any(k in o.name for k in ['Win_Floor1_East','East_Door','Water_Table_East','HAAS_Photo_Glazing']):print(o.name)
