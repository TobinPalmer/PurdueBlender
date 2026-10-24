import bpy, os
for fn in ['walc.blend','felix_haas_hall.blend','mccutcheon_hall.blend']:
 bpy.ops.wm.open_mainfile(filepath=os.path.join('modular','buildings',fn)); print('\n',fn)
 for o in bpy.data.objects:
  if o.type!='MESH': continue
  mats=[]
  for i,s in enumerate(o.material_slots):
   m=s.material
   count=sum(1 for p in o.data.polygons if p.material_index==i)
   if m and (('roof' in m.name.lower() or o.name.lower().find('roof')>=0) or count>0 and 'ground' not in m.name.lower()): mats.append((i,m.name,count,tuple(round(float(x),2) for x in next((n.inputs['Base Color'].default_value for n in m.node_tree.nodes if n.type=='BSDF_PRINCIPLED'),(.2,.2,.2,1))[:3]) if m.use_nodes else None))
  if mats and ('roof' in o.name.lower() or any('roof' in x[1].lower() or 'membrane' in x[1].lower() for x in mats)):
   print(o.name,'slots',mats)
