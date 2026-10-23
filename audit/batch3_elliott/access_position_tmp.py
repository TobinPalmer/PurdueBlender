import bpy
from collections import defaultdict
bpy.ops.wm.open_mainfile(filepath=r'C:/Users/Tobin/Documents/Blender/PurdueMap/audit/batch3_elliott/before_resume.blend');o=bpy.data.objects['ELLT_B3_access'];n=len(o.data.vertices);parent=list(range(n))
def f(x):
 while parent[x]!=x: parent[x]=parent[parent[x]];x=parent[x]
 return x
for e in o.data.edges:
 a,b=map(int,e.vertices);ra,rb=f(a),f(b);parent[ra]=rb
comps=defaultdict(list)
for i,v in enumerate(o.data.vertices):comps[f(i)].append(v.co)
for cs in comps.values():
 if len(cs)>5:
  print(len(cs),[round(min(v[i] for v in cs),1) for i in range(3)],[round(max(v[i] for v in cs),1) for i in range(3)])
