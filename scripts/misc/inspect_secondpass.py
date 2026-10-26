import bpy,os
for p in [r'modular/buildings/bell_tower.blend',r'modular/buildings/felix_haas_hall.blend',r'modular/buildings/psychological_sciences.blend']:
 bpy.ops.wm.open_mainfile(filepath=os.path.abspath(p)); sc=bpy.context.scene
 print('\n',os.path.basename(p),'camera',sc.camera.name if sc.camera else None,'objects',len(bpy.data.objects))
 for m in bpy.data.materials:
  if m.node_tree:
   b=next((n for n in m.node_tree.nodes if n.get('codex_surface_detail')),None)
   if b:
    print(m.name,'bump',round(b.inputs['Strength'].default_value,3),round(b.inputs['Distance'].default_value,5))
