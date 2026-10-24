import bpy
from collections import defaultdict,deque
bpy.ops.wm.open_mainfile(filepath=r'C:\Users\Tobin\Documents\Blender\PurdueMap\modular\buildings\morgan_j_burke_boilermaker_aquatic_center.blend')
o=bpy.data.objects['AQUA R2 | 300 individual schematic spectator seats']; adj=[set() for _ in o.data.vertices]
for p in o.data.polygons:
 vs=list(p.vertices)
 for i,v in enumerate(vs):
  for w in (vs[(i+1)%len(vs)],):adj[v].add(w);adj[w].add(v)
seen=set(); comps=[]
for i in range(len(adj)):
 if i in seen:continue
 q=[i];seen.add(i);vs=[]
 while q:
  a=q.pop();vs.append(a)
  for b in adj[a]:
   if b not in seen:seen.add(b);q.append(b)
 coords=[o.data.vertices[k].co for k in vs]
 comps.append((len(vs),tuple(sum(v[j] for v in coords)/len(coords) for j in range(3)),tuple((min(v[j] for v in coords),max(v[j] for v in coords)) for j in range(3))))
print('components',len(comps));print('first',comps[:6]);print('yrange',min(c[1][1] for c in comps),max(c[1][1] for c in comps),'xs',min(c[1][0] for c in comps),max(c[1][0] for c in comps));print('unique y',sorted(set(round(c[1][1],1) for c in comps))[:40])
