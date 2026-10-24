import bpy,json
s=bpy.data.objects['KRCH structural shell | GIS outline']
rows=[]
for p in s.data.polygons:
 zs=[s.data.vertices[i].co.z for i in p.vertices]
 if max(zs)-min(zs)<0.0001: rows.append({'z':zs[0],'n':len(p.vertices),'coords':[[round(s.data.vertices[i].co.x,2),round(s.data.vertices[i].co.y,2)] for i in p.vertices]})
print(json.dumps(rows,indent=2))
