import bpy,os
from mathutils import Vector
for key in ('mccutcheon_hall','niswonger_aviation_tech'):
 bpy.ops.wm.open_mainfile(filepath=os.path.abspath('modular/buildings/'+key+'.blend'))
 print('\n',key)
 for o in bpy.data.objects:
  if o.type!='MESH': continue
  n=o.name.lower()
  if 'roof' in n or 'rtu' in n or 'parapet' in n or 'plinth' in n or 'site_' in n:
   pts=[o.matrix_world@Vector(c) for c in o.bound_box]
   mn=Vector(tuple(min(p[i] for p in pts) for i in range(3))); mx=Vector(tuple(max(p[i] for p in pts) for i in range(3))); c=(mn+mx)*.5
   print(o.name,'center',tuple(round(v,2) for v in c),'dim',tuple(round(v,2) for v in mx-mn),'hide',o.hide_render,'mats',[m.name for m in o.data.materials],'coll',[x.name for x in o.users_collection])
 for m in bpy.data.materials:
  if any(t in m.name.lower() for t in ('roof_membrane','airport_apron','campus_turf','concrete_pavement')):
   print('MAT',m.name,'finish',m.get('texture_finish_final_two'),'nodes',[(n.type,n.label) for n in m.node_tree.nodes] if m.node_tree else None)
