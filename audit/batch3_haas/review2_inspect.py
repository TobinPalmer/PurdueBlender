import bpy,json,collections
p=r'C:\Users\Tobin\Documents\Blender\PurdueMap\modular\buildings\felix_haas_hall.blend'
bpy.ops.wm.open_mainfile(filepath=p)
c=bpy.data.collections['Asset_felix_haas_hall']
objs=list(c.objects)
print('COUNT',len(objs),'TYPES',collections.Counter(o.type for o in objs))
for key in ['Tread','Stair','Cupola','Roof','Window','Skin','Label','Office','Conference','Restroom','StairCore','Lift','Door','Entry']:
 a=[o for o in objs if key.lower() in o.name.lower()]
 print('KEY',key,len(a),[o.name for o in a[:30]])
print('MATERIALS', sorted(set(m.name for o in objs if o.type=='MESH' for m in o.data.materials if m)))
for n in sorted(set(m.name for o in objs if o.type=='MESH' for m in o.data.materials if m)):
 m=bpy.data.materials[n]
 pbs=m.node_tree.nodes.get('Principled BSDF') if m.use_nodes else None
 print('MAT',n, 'diffuse',tuple(round(x,3) for x in m.diffuse_color), 'base',tuple(round(x,3) for x in pbs.inputs['Base Color'].default_value) if pbs else None,'nodes',[(node.bl_idname,node.name) for node in m.node_tree.nodes] if m.use_nodes else None)
