import bpy
C=bpy.data.collections['Asset_felix_haas_hall']
for o in C.objects:
 if any(x in o.name.lower() for x in ['room','office','toilet','restroom','conference','stair','elevator','lift','desk','partition','interior']):print(o.name)
