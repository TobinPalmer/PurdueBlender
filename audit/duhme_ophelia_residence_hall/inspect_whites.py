import bpy,json
c=bpy.data.collections['Asset_massing_duhme_ophelia_residence_hall_1bb4e9c'];out=[]
for o in c.all_objects:
 if o.type!='MESH': continue
 m=[x.name for x in o.data.materials if x]
 if any('Off_White' in x or 'Limestone' in x or 'Interior' in x for x in m):
  b=o.dimensions
  if max(b)>2: out.append((o.name,tuple(round(v,2) for v in b),m))
print(json.dumps(out[:150],indent=2))
