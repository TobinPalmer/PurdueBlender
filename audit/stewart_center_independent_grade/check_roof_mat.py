import bpy
m=bpy.data.materials.get('Stewart_GIS_Roof_Estimated');print(m.name,m.diffuse_color[:],m.use_nodes,[(n.name,n.type,n.inputs.get('Base Color').default_value[:] if n.inputs.get('Base Color') else None) for n in m.node_tree.nodes])
for o in bpy.data.objects:
 if o.name=='STEW_Roof_GIS_Trace_ESTIMATED': print('roof mats',[(x.name if x else None) for x in o.data.materials],o.location[:],o.parent.name if o.parent else None)
