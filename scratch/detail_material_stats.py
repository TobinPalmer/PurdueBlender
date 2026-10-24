import bpy,os
ROOT=r'C:\Users\Tobin\Documents\Blender\PurdueMap'
names=['armory','beering_hall','american_railway_building','brown_laboratory_of_chemistry','peirce_hall']
for name in names:
 bpy.ops.wm.open_mainfile(filepath=os.path.join(ROOT,'modular','buildings',name+'.blend'))
 counts={}
 for o in bpy.data.objects:
  if o.type=='MESH':
   for m in o.data.materials:
    if m: counts[m.name]=counts.get(m.name,0)+1
 fn=os.path.join(ROOT,'audit','texture_batch_1',name+'_stats.txt')
 with open(fn,'w',encoding='utf8') as f:
  for m in sorted([m for m in bpy.data.materials if m.name in counts],key=lambda x:-counts[x.name]):
   f.write(f'\n{m.name}: objects={counts[m.name]}\n')
   if not m.use_nodes: continue
   nt=m.node_tree; links=nt.links
   for n in nt.nodes:
    if n.type=='BSDF_PRINCIPLED':
     for key in ['Base Color','Roughness','Metallic','Normal']:
      s=n.inputs.get(key)
      if s:
       l=next((l for l in links if l.to_socket==s),None)
       f.write(f'  {key}: linked={bool(l)}, default={tuple(round(float(x),4) for x in s.default_value) if hasattr(s.default_value,"__len__") else s.default_value}\n')
    if n.type in {'TEX_NOISE','TEX_BRICK','BUMP','TEX_VORONOI','MAP_RANGE'}:
     vals={}
     for s in n.inputs:
      if not next((l for l in links if l.to_socket==s),None) and hasattr(s,'default_value'):
       try: vals[s.name]=tuple(round(float(x),4) for x in s.default_value) if hasattr(s.default_value,'__len__') else round(float(s.default_value),4)
       except: pass
     f.write(f'  {n.name} {n.type}: {vals}\n')
