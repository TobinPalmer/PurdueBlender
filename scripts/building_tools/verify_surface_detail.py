import bpy, os
for p in [r'modular/buildings/bell_tower.blend',r'modular/buildings/felix_haas_hall.blend',r'modular/buildings/psychological_sciences.blend']:
 bpy.ops.wm.open_mainfile(filepath=os.path.abspath(p))
 mats=[m for m in bpy.data.materials if m.use_nodes and any(n.get('codex_surface_detail') for n in m.node_tree.nodes)]
 print(os.path.basename(p),'opened',len(bpy.data.objects),'objects;',len(mats),'materials with detail nodes;', 'cameras',sum(o.type=='CAMERA' for o in bpy.data.objects))
