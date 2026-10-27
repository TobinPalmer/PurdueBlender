import bpy,json
obj=bpy.data.objects['RHPH structural shell | GIS outline']
vs=[]
for v in obj.data.vertices:
 p=obj.matrix_world @ v.co
 if abs(p.z+1.0)<1e-3: vs.append([round(p.x,3),round(p.y,3)])
# unique and order by vertex index
seen=[]
for v in vs:
 if v not in seen: seen.append(v)
print(json.dumps(seen))
