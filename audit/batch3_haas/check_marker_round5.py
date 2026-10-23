import bpy
for o in bpy.data.collections['Asset_felix_haas_hall'].objects:
 if any(k in o.name.lower() for k in ['marker','origin','gis','envelope']):print(o.name,tuple(round(v,4) for v in o.location),tuple(round(v,4) for v in o.scale),tuple(round(v,4) for v in o.rotation_euler))
