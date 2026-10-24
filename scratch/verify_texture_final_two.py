import bpy,os
for key in ('mccutcheon_hall','niswonger_aviation_tech'):
 bpy.ops.wm.open_mainfile(filepath=os.path.abspath('modular/buildings/'+key+'.blend'))
 finished=[m.name for m in bpy.data.materials if m.get('texture_finish_final_two')]
 saved_nodes=sum(1 for m in bpy.data.materials if m.node_tree for n in m.node_tree.nodes if n.get('texture_final_two'))
 print(key,'finish_count',len(finished),'node_markers',saved_nodes,'materials',', '.join(finished))
