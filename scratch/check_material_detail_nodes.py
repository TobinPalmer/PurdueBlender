import bpy,os
for f in ['hovde_hall','hansen_life_sciences','knoy_hall']:
 bpy.ops.wm.open_mainfile(filepath=os.path.abspath(f'modular/buildings/{f}.blend')); print('\n',f)
 for m in bpy.data.materials:
  tagged=[n for n in m.node_tree.nodes if n.get('surface_detail_pass')=='campus_2026_10'] if m.use_nodes else []
  if tagged:
   print(m.name,[(n.type,n.label,[(o.name,len(o.links)) for o in n.outputs if o.is_linked],[(i.name,len(i.links)) for i in n.inputs if i.is_linked]) for n in tagged])
