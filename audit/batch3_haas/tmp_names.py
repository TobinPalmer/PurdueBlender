import bpy
C=bpy.data.collections['Asset_felix_haas_hall']
for o in C.objects:
 if any(s in o.name.lower() for s in ['side','belt','west','north','south','stair','projection','awning','canopy']): print(o.name,o.type)
