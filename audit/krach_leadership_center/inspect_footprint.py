import bpy, json
s=bpy.data.objects['KRCH structural shell | GIS outline']; rows=[]
for p in s.data.polygons:
 zs=[s.data.vertices[i].co.z for i in p.vertices]
 if max(zs)-min(zs)<1e-5:
  rows.append({'z':zs[0],'vertices':list(p.vertices),'xy':[[round(s.data.vertices[i].co.x,3),round(s.data.vertices[i].co.y,3)] for i in p.vertices]})
print(json.dumps({'collection_tree':[(c.name,[x.name for x in c.children],len(c.objects)) for c in bpy.data.collections],'horizontal_faces':rows},indent=2))
