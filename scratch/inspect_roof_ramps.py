import bpy, os
for fn,names in [('walc.blend',['Roof.009','WALC_Reference_Roof']),('felix_haas_hall.blend',['HAAS_Slate_Roof']),('mccutcheon_hall.blend',['Roof_Membrane'])]:
 bpy.ops.wm.open_mainfile(filepath=os.path.join('modular','buildings',fn)); print('\n',fn)
 for mn in names:
  m=bpy.data.materials[mn]; print('MAT',mn)
  for n in m.node_tree.nodes:
   if n.type=='VALTORGB': print(n.name,n.label,[(round(e.position,3),tuple(round(x,4) for x in e.color)) for e in n.color_ramp.elements])
   elif n.type=='MAP_RANGE': print(n.name,n.label,{i.name:tuple(round(x,4) for x in i.default_value) if hasattr(i.default_value,'__len__') else round(i.default_value,4) for i in n.inputs})
