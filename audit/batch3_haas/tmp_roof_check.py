import bpy
for n in ['HAAS_Hipped_Roof','HAAS_Photo_Main_Hipped_Roof','HAAS_Photo_Entrance_Hipped_Roof']:
 o=bpy.data.objects[n];print(n,'hide',o.hide_render,[c.name for c in o.users_collection],[(m.name if m else None) for m in o.data.materials])
 if o.data.materials: print('emission',[(node.inputs['Emission Strength'].default_value if node.type=='BSDF_PRINCIPLED' and 'Emission Strength' in node.inputs else None) for node in o.data.materials[0].node_tree.nodes] if o.data.materials[0].use_nodes else None)
