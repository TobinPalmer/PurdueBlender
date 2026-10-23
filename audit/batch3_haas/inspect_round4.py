import bpy
c=bpy.data.collections['Asset_felix_haas_hall']
for o in c.objects:
 if any(s in o.name.lower() for s in ['pier','window','sill','jamb','course','cupola','drum','dome','spire','roof']):
  print(o.name, [m.name if m else None for m in getattr(o.data,'materials',[])])
