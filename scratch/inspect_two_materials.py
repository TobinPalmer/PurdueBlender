import bpy, json, os
for fn in ['mccutcheon_hall.blend','niswonger_aviation_tech.blend']:
 p=os.path.abspath(os.path.join('modular','buildings',fn)); bpy.ops.wm.open_mainfile(filepath=p)
 print('\nFILE',fn,'objects',len(bpy.data.objects),'materials',len(bpy.data.materials))
 for m in bpy.data.materials:
  if not m.use_nodes or not m.node_tree: continue
  pbs=next((n for n in m.node_tree.nodes if n.type=='BSDF_PRINCIPLED'),None)
  if pbs:
   color=tuple(round(c,3) for c in pbs.inputs['Base Color'].default_value)
   print('MAT',m.name,'color',color,'rough',round(pbs.inputs['Roughness'].default_value,3),'nodes',len(m.node_tree.nodes),'linkedbase',pbs.inputs['Base Color'].is_linked)
 for o in bpy.data.objects:
  if o.type=='MESH': print('OBJ',o.name, 'dim',tuple(round(v,2) for v in o.dimensions),'mats',[m.name if m else None for m in o.data.materials])
