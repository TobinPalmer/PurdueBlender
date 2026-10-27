import bpy,json
from mathutils import Vector
for o in sorted(bpy.data.objects,key=lambda x:x.name):
 if o.type=='MESH' and (o.name.startswith('RHPH') or o.name.startswith('Heine')):
  bb=[o.matrix_world @ Vector(c) for c in o.bound_box]
  bounds=[[min(v[i] for v in bb),max(v[i] for v in bb)] for i in range(3)]
  print(o.name,'loc',tuple(round(v,3) for v in o.location),'b',[[round(v,3) for v in d] for d in bounds],'mat',[m.name for m in o.data.materials])
print('\nCAMERAS')
for o in bpy.data.objects:
 if o.type=='CAMERA': print(o.name, tuple(o.location), tuple(o.rotation_euler),o.data.lens)
print('\nMATERIAL NODE GRAPHS')
for m in bpy.data.materials:
 if 'masonry' in m.name.lower() or 'glazing' in m.name.lower() or 'stone' in m.name.lower():
  print('MATERIAL',m.name)
  for n in m.node_tree.nodes:
   links=[(l.from_node.name,l.from_socket.name) for l in m.node_tree.links if l.to_node==n]
   print(' ',n.name,n.type, 'inputs',[(i.name,str(i.default_value)[:40]) for i in n.inputs if hasattr(i,'default_value')], 'from',links)
