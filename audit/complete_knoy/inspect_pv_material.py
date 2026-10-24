import bpy,json
bpy.ops.wm.open_mainfile(filepath=r'C:/Users/Tobin/Documents/Blender/PurdueMap/audit/complete_knoy/knoy_hall_round6_candidate.blend')
m=bpy.data.materials['KNOY_Solar_Panel']
print(json.dumps({'diffuse':list(m.diffuse_color),'nodes':[{'name':n.name,'type':n.type,'inputs':{k:[round(v,3) for v in i.default_value] if hasattr(i.default_value,'__iter__') and not isinstance(i.default_value,str) else (round(i.default_value,3) if hasattr(i.default_value,'__float__') else None) for k,i in n.inputs.items() if hasattr(i,'default_value')} for n in m.node_tree.nodes]},indent=2))
