import bpy
bpy.ops.wm.open_mainfile(filepath='modular/buildings/rawls_hall.blend')
for nm in ['RAWL_North_Windows_Glass','RAWL_North_Windows_BronzeMullions']:
 o=bpy.data.objects[nm];print(nm,'polys',len(o.data.polygons),'verts',len(o.data.vertices),'matidx',sorted(set(p.material_index for p in o.data.polygons)),'loc',tuple(o.location))
 for m in o.data.materials:
  print('MAT',m.name,'diffuse',tuple(m.diffuse_color),'nodes',m.use_nodes)
  if m.use_nodes:
   for n in m.node_tree.nodes:
    print(n.name,n.type)
    if n.type=='BSDF_PRINCIPLED':
     for inp in ['Base Color','Roughness','Metallic','Transmission Weight','Alpha','Emission Color','Emission Strength']:
      if inp in n.inputs:print(inp,n.inputs[inp].default_value)
print('North glass first polys:')
o=bpy.data.objects['RAWL_North_Windows_Glass'];
for p in list(o.data.polygons)[:3]:print(p.index,p.material_index,p.normal[:], [tuple(o.matrix_world@o.data.vertices[i].co) for i in p.vertices])
