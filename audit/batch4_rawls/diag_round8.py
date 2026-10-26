import bpy,json
bpy.ops.wm.open_mainfile(filepath=r'modular/buildings/rawls_hall.blend')
for m in bpy.data.materials:
 if any(k in m.name.lower() for k in ('mortar','brick','masonry')):
  vals={}
  if m.node_tree:
   for n in m.node_tree.nodes:
    vals[n.name]={s.name:tuple(s.default_value) if hasattr(s.default_value,'__len__') and not isinstance(s.default_value,str) else s.default_value for s in n.inputs if hasattr(s,'default_value')}
  print(m.name, 'diff',tuple(m.diffuse_color), vals)
for o in bpy.data.objects:
 if o.type=='MESH' and ('Wall' in o.name or 'Shell' in o.name or 'Masonry' in o.name):
  print('SHELL_CANDIDATE',o.name, 'verts',len(o.data.vertices),'parent',o.parent.name if o.parent else None,'bounds',[[min((o.matrix_world@v.co)[i] for v in o.data.vertices),(max((o.matrix_world@v.co)[i] for v in o.data.vertices))] for i in range(3)] if o.data.vertices else None)
