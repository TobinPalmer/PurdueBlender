import bpy,json,os
p=r'C:\Users\Tobin\Documents\Blender\PurdueMap\modular\buildings\massing_yue_kong_pao_hall_a3cb766.blend'; bpy.ops.wm.open_mainfile(filepath=p); names=set(m.name for o in bpy.data.collections['Asset_massing_yue_kong_pao_hall_a3cb766'].objects if o.type=='MESH' for m in o.data.materials if m); out=[]
for m in sorted([m for m in bpy.data.materials if m.name in names],key=lambda x:x.name):
 nodes=[]
 for n in m.node_tree.nodes if m.node_tree else []:
  vals={}
  if n.type=='BSDF_PRINCIPLED':
   for k in ('Base Color','Roughness','Metallic','Alpha','Normal'):
    s=n.inputs.get(k)
    if s and not s.is_linked: vals[k]=list(s.default_value) if hasattr(s.default_value,'__len__') else s.default_value
  nodes.append({'type':n.type,'label':n.label,'name':n.name,'values':vals})
 out.append({'name':m.name,'use_nodes':m.use_nodes,'nodes':nodes})
outp=r'C:\Users\Tobin\Documents\Blender\PurdueMap\audit\yue_kong_pao_hall\independent_grade_r1_materials.json';open(outp,'w').write(json.dumps(out,indent=2));print(json.dumps(out,indent=2))
