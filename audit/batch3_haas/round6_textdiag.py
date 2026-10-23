import bpy
for o in bpy.data.collections['Asset_felix_haas_hall'].objects:
 if o.type=='FONT':print(o.name,repr(o.data.body),o.data.size,tuple(round(v,2) for v in o.location),tuple(round(v,2) for v in o.dimensions))
