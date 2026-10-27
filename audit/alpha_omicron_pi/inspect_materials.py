import bpy,json
c=bpy.data.collections['Asset_massing_house_970455277_a3fb72a']
for o in c.all_objects:
 if o.name.startswith('AOII_BrickWall'):
  print(o.name,[(m.name, m.diffuse_color[:],m.users) for m in o.data.materials],len(o.data.uv_layers),len(o.data.polygons)); print(o.data.uv_layers.active.data[0].uv[:]); break
for m in bpy.data.materials:
 if 'brick' in m.name.lower():
  print('MAT',m.name,m.diffuse_color[:],m.users,[(n.name,n.bl_idname) for n in m.node_tree.nodes]);
  for n in m.node_tree.nodes:
   if n.bl_idname=='ShaderNodeTexCoord': print('TC outputs',[(o.name,o.is_linked) for o in n.outputs])
   if n.bl_idname=='ShaderNodeTexBrick': print('brick inputs',n.inputs['Color1'].default_value[:],[(i.name,i.is_linked) for i in n.inputs])