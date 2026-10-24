import bpy, os
bpy.ops.wm.open_mainfile(filepath=os.path.join('modular','buildings','mccutcheon_hall.blend'))
m=bpy.data.materials['Roof_Membrane']
for n in m.node_tree.nodes:
 print(n.name,n.type,n.label)
 for i in n.inputs:
  try: v=tuple(round(float(x),4) for x in getattr(i,"default_value",None))
  except: 
   try:v=round(float(getattr(i,"default_value",None)),4)
   except:v=str(getattr(i,"default_value",None))
  print(' ',i.name, i.identifier,i.type,'linked',i.is_linked,'value',v)
