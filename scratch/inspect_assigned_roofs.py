import bpy, os
for fn in ['walc.blend','felix_haas_hall.blend','mccutcheon_hall.blend']:
 bpy.ops.wm.open_mainfile(filepath=os.path.join('modular','buildings',fn))
 print('\nFILE',fn)
 for m in bpy.data.materials:
  if any(k in m.name.lower() for k in ['roof','membrane','gravel','ballast']):
   bs=next((n for n in m.node_tree.nodes if n.type=='BSDF_PRINCIPLED'),None) if m.use_nodes else None
   if bs:
    print('MAT',m.name,'users',m.users,'base',tuple(round(x,3) for x in bs.inputs['Base Color'].default_value),'rough',bs.inputs['Roughness'].default_value,'nodes',[(n.type,n.label,n.name) for n in m.node_tree.nodes])
    objs=[o.name for o in bpy.data.objects if o.type=='MESH' and any(s.material==m for s in o.material_slots)]
    print('OBJS',objs[:30], 'count',len(objs))
