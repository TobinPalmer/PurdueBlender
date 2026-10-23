import bpy
from collections import defaultdict
bpy.ops.wm.open_mainfile(filepath=r'C:/Users/Tobin/Documents/Blender/PurdueMap/audit/batch3_elliott/before_resume.blend')
o=bpy.data.objects['ELLT_B3_access'];par=list(range(len(o.data.vertices)))
def f(x):
 while par[x]!=x: par[x]=par[par[x]]; x=par[x]
 return x
for e in o.data.edges:
 a,b=map(int,e.vertices); par[f(a)]=f(b)
cs=defaultdict(list)
for v in o.data.vertices:cs[f(v.index)].append(v.co)
for vs in cs.values():
 if len(vs)>4:
  print(len(vs),tuple(round(sum(v[i] for v in vs)/len(vs),2) for i in range(3)),[(round(min(v[i] for v in vs),2),round(max(v[i] for v in vs),2)) for i in range(3)])
