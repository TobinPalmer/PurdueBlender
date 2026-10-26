import bpy,json,math
from pathlib import Path
f=bpy.data.filepath
c=bpy.data.collections.get('Asset_massing_earhart_hall_0f14209')
objects=[]
for o in c.all_objects:
 mw=o.matrix_world
 vs=[mw@v.co for v in o.data.vertices] if o.type=='MESH' else []
 b=[[min((v[i] for v in vs),default=0),max((v[i] for v in vs),default=0)] for i in range(3)]
 objects.append({'name':o.name,'type':o.type,'vertices':len(vs),'polygons':len(o.data.polygons) if o.type=='MESH' else None,'bounds':b})
print(json.dumps({'file':f,'scene':[s.name for s in bpy.data.scenes],'collection':c.name if c else None,'objects':objects},indent=2))
