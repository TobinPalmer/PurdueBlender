import bpy, json
p=bpy.data.filepath
m=bpy.data.materials.get('Roof_Membrane')
out={'file':p,'materials':{}}
for matname in ['Roof_Membrane','Official_GIS_Ring_Overlay']:
 m=bpy.data.materials.get(matname)
 if not m: continue
 x={'diffuse_color':list(m.diffuse_color),'use_nodes':m.use_nodes,'nodes':[]}
 for n in m.node_tree.nodes:
  d={'name':n.name,'type':n.type,'location':list(n.location)}
  for key in ['inputs']:
   try: d[key]=[{ 'name':s.name,'default_value':list(s.default_value) if hasattr(s.default_value,'__len__') else s.default_value} for s in n.inputs if hasattr(s,'default_value')]
   except: pass
  x['nodes'].append(d)
 out['materials'][matname]=x
objs=[o for o in bpy.data.objects if o.name=='MCUT_Official_Footprint_Overlay']
out['overlay']=[{'name':o.name,'hide_render':o.hide_render,'hide_viewport':o.hide_viewport,'display_type':o.display_type} for o in objs]
print('MCUT_NODE_REPORT='+json.dumps(out))
