import bpy,json
from pathlib import Path
r=[]
for m in bpy.data.materials:
 if m.node_tree:
  p=next((n for n in m.node_tree.nodes if n.type=='BSDF_PRINCIPLED'),None)
  if p:r.append([m.name,list(m.diffuse_color),list(p.inputs['Base Color'].default_value),p.inputs['Roughness'].default_value])
print(json.dumps(r,indent=1))
