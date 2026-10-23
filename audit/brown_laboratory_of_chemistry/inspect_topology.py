import bpy,collections
bpy.ops.wm.open_mainfile(filepath=r'C:\Users\Tobin\Documents\Blender\PurdueMap\modular\buildings\massing_brown_laboratory_of_chemistry_brwn_aed3885.blend')
o=bpy.context.scene.objects[0]; mesh=o.data
ids={i for i,v in enumerate(mesh.vertices) if abs(v.co.z)<1e-5}; adj=collections.defaultdict(set)
for e in mesh.edges:
 a,b=e.vertices
 if a in ids and b in ids: adj[a].add(b);adj[b].add(a)
print('bottom',len(ids),'edges',sum(len(x) for x in adj.values())//2,'degrees',collections.Counter(map(len,adj.values())))
for i in ids: print(i, tuple(round(float(v),2) for v in mesh.vertices[i].co), list(adj[i]))
