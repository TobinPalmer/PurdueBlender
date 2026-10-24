import bpy, os
for fn in ['walc.blend','felix_haas_hall.blend','mccutcheon_hall.blend']:
 bpy.ops.wm.open_mainfile(filepath=os.path.join('modular','buildings',fn)); print('\n###',fn)
 mats=['Roof.009','WALC_Reference_Roof','HAAS_Slate_Roof','Roof_Membrane']
 for mn in mats:
  m=bpy.data.materials.get(mn)
  if not m: continue
  nt=m.node_tree; print('MATERIAL',mn)
  for n in nt.nodes:
   print(' NODE',n.name,n.type,n.label, {i.name:(tuple(round(v,4) for v in i.default_value) if hasattr(i.default_value,'__len__') else round(i.default_value,4)) for i in n.inputs if not i.is_linked and hasattr(i,'default_value')})
   for i in n.inputs:
    if i.is_linked: print('  IN',i.name,'<-',[(l.from_node.name,l.from_socket.name) for l in i.links])
  for o in bpy.data.objects:
   if o.type=='MESH' and any(s.material==m for s in o.material_slots):
    coords=[o.matrix_world@__import__('mathutils').Vector(c) for c in o.bound_box]; lo=[min(v[k] for v in coords) for k in range(3)]; hi=[max(v[k] for v in coords) for k in range(3)]; print('OBJ',o.name,'bounds',tuple(round(x,2) for x in lo),tuple(round(x,2) for x in hi),'verts',len(o.data.vertices),'mods',[(mod.name,mod.type) for mod in o.modifiers])
