import bpy,os
for f in ['south_hall','stewart_center','tarkington_hall','university_hall','walc']:
 bpy.ops.wm.open_mainfile(filepath=os.path.abspath(f'modular/buildings/{f}.blend')); print('\n',f)
 for m in bpy.data.materials:
  if not m.users or not m.node_tree: continue
  name=m.name.lower()
  if any(k in name for k in ('brick','limestone','concrete','roof','membrane','slate','metal panel')):
   print(m.name,[(n.name,n.type) for n in m.node_tree.nodes])
