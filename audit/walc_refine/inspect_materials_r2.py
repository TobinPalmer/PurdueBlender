import bpy,json
from pathlib import Path
res=[]
for m in sorted({s.material for o in bpy.data.collections['Asset_walc'].all_objects for s in o.material_slots if s.material}, key=lambda m:m.name):
 d={'name':m.name,'diffuse':list(m.diffuse_color),'roughness':m.roughness,'metallic':m.metallic,'use_nodes':m.use_nodes,'nodes':[]}
 if m.use_nodes:
  for n in m.node_tree.nodes:
   x={'type':n.type,'name':n.name}
   if n.type=='BSDF_PRINCIPLED':
    x['base_color']=list(n.inputs['Base Color'].default_value);x['roughness']=n.inputs['Roughness'].default_value;x['metallic']=n.inputs['Metallic'].default_value
   if n.type=='TEX_IMAGE':x['image']=n.image.name if n.image else None
   d['nodes'].append(x)
 res.append(d)
libs=[{'name':l.name,'filepath':l.filepath,'absolute':bpy.path.abspath(l.filepath)} for l in bpy.data.libraries]
out=Path(__file__).with_name('materials_and_libraries_r1.json');out.write_text(json.dumps({'materials':res,'libraries':libs},indent=2)+'\n',encoding='utf8');print(json.dumps({'materials':len(res),'libraries':libs}))
