import bpy,json,os
from mathutils import Vector
out={'version':bpy.app.version_string,'filepath':bpy.data.filepath,'scenes':[s.name for s in bpy.data.scenes],'collections':[],'materials':[],'objects':[]}
for c in bpy.data.collections:
 if c.name=='Asset_heine_pharmacy' or c.name=='Collection':
  out['collections'].append({'name':c.name,'objects':[o.name for o in c.objects]})
for m in bpy.data.materials:
 rec={'name':m.name,'nodes':m.use_nodes,'diffuse':list(m.diffuse_color),'textures':[]}
 if m.node_tree:
  for n in m.node_tree.nodes:
   if n.type=='BSDF_PRINCIPLED': rec['principled']={i.name:list(i.default_value) if hasattr(i.default_value,'__iter__') else i.default_value for i in n.inputs if i.name in ['Base Color','Roughness','Metallic']}
   if n.type=='TEX_IMAGE': rec['textures'].append(n.image.filepath if n.image else None)
 out['materials'].append(rec)
for o in bpy.data.objects:
 if o.name.startswith(('Heine','RHPH','Schematic','Schematic')) or o.name.startswith('HEINE'):
  out['objects'].append({'name':o.name,'type':o.type,'location':list(o.location),'dimensions':list(o.dimensions),'rotation':list(o.rotation_euler),'materials':[s.material.name if s.material else None for s in o.material_slots],'modifiers':[m.type for m in o.modifiers]})
with open('audit/heine_pharmacy/initial_inspection.json','w') as f: json.dump(out,f,indent=2)
print('objects',len(bpy.data.objects),'collections',len(out['collections']),'materials',len(out['materials']),'file',bpy.data.filepath)
