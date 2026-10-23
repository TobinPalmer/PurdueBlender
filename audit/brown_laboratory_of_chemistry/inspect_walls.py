import bpy,collections
bpy.ops.wm.open_mainfile(filepath=r'C:\Users\Tobin\Documents\Blender\PurdueMap\modular\buildings\massing_brown_laboratory_of_chemistry_brwn_aed3885.blend')
m=bpy.context.scene.objects[0].data
edges=set()
for p in m.polygons:
 zs=[m.vertices[i].co.z for i in p.vertices]
 if min(zs)<1e-6 and max(zs)>1e-6:
  ids=[i for i in p.vertices if abs(m.vertices[i].co.z)<1e-6]
  if len(ids)>=2:
   for a,b in zip(ids,ids[1:]+ids[:1]):
    if (m.vertices[a].co-m.vertices[b].co).length>1e-5: edges.add(tuple(sorted((a,b))))
adj=collections.defaultdict(set)
for a,b in edges: adj[a].add(b);adj[b].add(a)
print('EDGECOUNT',len(edges),'degrees',collections.Counter(map(len,adj.values())))
comps=[]; remaining=set(adj)
while remaining:
 seed=remaining.pop(); comp={seed}; todo=[seed]
 while todo:
  v=todo.pop()
  for w in adj[v]:
   if w not in comp: comp.add(w);remaining.discard(w);todo.append(w)
 comps.append(comp)
print('comps',list(map(len,comps)))
for i in comps[0]: print(i,tuple(round(float(x),2) for x in m.vertices[i].co), sorted(adj[i]))
