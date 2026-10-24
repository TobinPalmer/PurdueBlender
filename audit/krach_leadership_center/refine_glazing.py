import bpy,json
src=bpy.data.filepath
assert src.lower().endswith('krach_leadership_center.blend')
for name in ['KRACH_LEADERSHIP_CENTER | evidence palette glazing','KRCH | blue charcoal architectural glazing']:
 m=bpy.data.materials.get(name)
 if not m: continue
 m.diffuse_color=(0.22,0.42,0.46,0.26); m.use_nodes=True
 bs=m.node_tree.nodes.get('Principled BSDF')
 if bs:
  bs.inputs['Base Color'].default_value=(0.16,0.31,0.34,0.26)
  bs.inputs['Alpha'].default_value=0.26
  bs.inputs['Roughness'].default_value=0.12
  if 'Transmission Weight' in bs.inputs: bs.inputs['Transmission Weight'].default_value=0.22
  if 'IOR' in bs.inputs: bs.inputs['IOR'].default_value=1.45
 m.surface_render_method='DITHERED'
# Save this local source-only change; facade openings already carry the explicit evidence note.
bpy.ops.wm.save_as_mainfile(filepath=src)
print(json.dumps({'saved':src,'changed_materials':['KRACH_LEADERSHIP_CENTER | evidence palette glazing','KRCH | blue charcoal architectural glazing']}))
