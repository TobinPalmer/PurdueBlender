import bpy\nfrom mathutils import Vector
p=r'C:\Users\Tobin\Documents\Blender\PurdueMap\modular\buildings\stanley_coulter_hall.blend';bpy.ops.wm.open_mainfile(filepath=p)
for n in ['Architectural_Glazing','Bedford_Indiana_Limestone','Dark_Bronze_Framing','Warm_Red_Brick']:
 m=bpy.data.materials.get(n);print('\nMAT',n, 'color', tuple(m.diffuse_color) if m else None,'nodes',bool(m and m.use_nodes))
 if m and m.use_nodes:
  for nd in m.node_tree.nodes:
   if nd.type=='BSDF_PRINCIPLED':
    print([(k,nd.inputs[k].default_value) for k in ['Base Color','Metallic','Roughness','Alpha','Transmission Weight','IOR'] if k in nd.inputs])
for cn in ['SC_Roof_and_Dormers']:
 print('\nROOF')
 for o in bpy.data.collections[cn].objects:
  pts=[o.matrix_world@Vector(c) for c in o.bound_box];lo=[min(q[i] for q in pts) for i in range(3)];hi=[max(q[i] for q in pts) for i in range(3)]
  print(o.name, [round(hi[i]-lo[i],2) for i in range(3)], 'at',[round((hi[i]+lo[i])/2,2) for i in range(3)], [m.name for m in o.data.materials if m] if o.type=='MESH' else '')
