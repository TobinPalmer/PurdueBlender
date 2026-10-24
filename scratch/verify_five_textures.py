import bpy, os
root=r'C:\Users\Tobin\Documents\Blender\PurdueMap\modular\buildings'
files=['math_sciences.blend','neil_armstrong_hall.blend','owen_hall.blend','purdue_memorial_union.blend','ross_ade.blend']
for fn in files:
 bpy.ops.wm.open_mainfile(filepath=os.path.join(root,fn))
 missing=[]; marked=0; linked=0
 for m in bpy.data.materials:
  if not m.node_tree: continue
  for n in m.node_tree.nodes:
   if n.get('codex_surface_finish'): marked+=1
  if any(n.get('codex_surface_finish') for n in m.node_tree.nodes):
   tc=next((n for n in m.node_tree.nodes if n.name=='Surface Detail Coordinates'),None)
   noise=next((n for n in m.node_tree.nodes if n.name=='Subtle Surface Variation'),None)
   if not tc or not noise or not any(l.from_node==tc and l.to_node==noise and l.from_socket.name=='Object' for l in m.node_tree.links): missing.append(m.name)
 print(fn,'reopened', 'textured_nodes',marked,'materials_missing_object_coords',missing,'missing_material_slots',sum(1 for o in bpy.data.objects if o.type=='MESH' and any(not s.material for s in o.material_slots)))
