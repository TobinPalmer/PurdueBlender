import bpy
bpy.ops.wm.open_mainfile(filepath=r'modular/buildings/stanley_coulter_hall.blend')
for c in ['SC_Portico_and_Entrances','SC_Interior_Shell','SC_Roof_and_Dormers']:
 col=bpy.data.collections.get(c); print('\n',c)
 for o in col.objects:
  if c!='SC_Roof_and_Dormers' or any(s in o.name.lower() for s in ('dormer','hvac','roof','chimney')): print(o.name,o.type)
