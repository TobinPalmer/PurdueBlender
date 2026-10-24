import bpy, os
for p in ['modular/buildings/hicks_library.blend','modular/buildings/lawson_hall.blend','modular/buildings/krannert_building.blend']:
 bpy.ops.wm.open_mainfile(filepath=p)
 print('REOPENED',p,'objects',len(bpy.data.objects))
 for m in bpy.data.materials:
  if m.users and any(n.get('purdue_surface_detail') for n in m.node_tree.nodes):
   bs=next((n for n in m.node_tree.nodes if n.type=='BSDF_PRINCIPLED'),None)
   print('DETAIL',m.name,'noise+bump',sum(1 for n in m.node_tree.nodes if n.type=='TEX_NOISE'),sum(1 for n in m.node_tree.nodes if n.type=='BUMP'),'normal linked',bs.inputs['Normal'].is_linked)
