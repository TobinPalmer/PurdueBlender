import bpy, collections
obj=bpy.data.objects['PHYS | recessed dark sash glazing']; m=obj.data
adj=[set() for _ in m.vertices]
for e in m.edges: adj[e.vertices[0]].add(e.vertices[1]); adj[e.vertices[1]].add(e.vertices[0])
seen=set(); comps=[]
for i in range(len(m.vertices)):
    if i in seen: continue
    q=[i]; seen.add(i); c=[]
    while q:
        v=q.pop(); c.append(v)
        for n in adj[v]:
            if n not in seen: seen.add(n); q.append(n)
    if len(c)>1: comps.append(c)
print('components',len(comps),'sizes',collections.Counter(map(len,comps)))
print('dims',[(round(max(m.vertices[i].co.x for i in c)-min(m.vertices[i].co.x for i in c),2),round(max(m.vertices[i].co.y for i in c)-min(m.vertices[i].co.y for i in c),2),round(max(m.vertices[i].co.z for i in c)-min(m.vertices[i].co.z for i in c),2)) for c in comps[:12]])
