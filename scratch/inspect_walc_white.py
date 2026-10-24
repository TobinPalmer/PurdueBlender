import bpy, os
bpy.ops.wm.open_mainfile(filepath=os.path.join('modular','buildings','walc.blend'))
for n in ['White.009','Roof.009','WALC_Reference_Roof']:
 m=bpy.data.materials.get(n); print('\n',n,'users',m.users)
 print('OBJECTS',[(o.name,[sum(1 for p in o.data.polygons if p.material_index==i) for i,s in enumerate(o.material_slots) if s.material==m]) for o in bpy.data.objects if o.type=='MESH' and any(s.material==m for s in o.material_slots)])
 for nd in m.node_tree.nodes: print(' NODE',nd.name,nd.type,nd.label)
