import bpy, json, re
from mathutils import Vector

names = ['RAWL_SE_Diagonal_CurtainWall_Glass','RAWL_CurtainWall_Glass','RAWL_2026_Plan1086_01_00','RAWL_2026_Plan1086_02_00','RAWL_1086_R10_Schematic_Projection_Surface_01','RAWL_1086_R10_Schematic_Projection_Surface_02','RAWL_1086_R10_Schematic_Lectern_Pedestal','RAWL_1086_R10_Schematic_Lectern_Top']
def objrec(o):
    pts=[o.matrix_world @ Vector(c) for c in o.bound_box]
    return {'name':o.name,'type':o.type,'location':list(o.location),'rotation':list(o.rotation_euler),'dimensions':list(o.dimensions),'bounds':[[min(p[i] for p in pts),max(p[i] for p in pts)] for i in range(3)],'hide_render':o.hide_render,'collections':[c.name for c in o.users_collection]}
report={'named':[objrec(bpy.data.objects[n]) for n in names if bpy.data.objects.get(n)],'desk_chair_pairs':[]}
desks=sorted([o for o in bpy.data.objects if re.fullmatch(r'RAWL_2026_1086_Desk(?:\.\d{3})?',o.name)],key=lambda o:int(o.name.rsplit('.',1)[1]) if '.' in o.name else 0)
for i,d in enumerate(desks):
 suffix=d.name[len('RAWL_2026_1086_Desk'):]
 ch=bpy.data.objects.get('RAWL_2026_1086_Chair'+suffix)
 report['desk_chair_pairs'].append({'desk':objrec(d),'chair':objrec(ch) if ch else None})
materials={}
for o in bpy.data.objects:
 if o.type!='MESH':continue
 for m in o.data.materials:
  if m and ('Glass' in m.name or 'glaz' in m.name.lower()):
   if m.name in materials:continue
   nodes=[]
   if m.use_nodes:
    for n in m.node_tree.nodes:
     if n.type=='BSDF_PRINCIPLED':
      nodes.append({'node':n.name,'roughness':float(n.inputs['Roughness'].default_value),'metallic':float(n.inputs['Metallic'].default_value),'transmission':float(n.inputs['Transmission Weight'].default_value),'ior':float(n.inputs['IOR'].default_value),'coat':float(n.inputs['Coat Weight'].default_value),'specular':float(n.inputs['Specular IOR Level'].default_value),'base':list(n.inputs['Base Color'].default_value)})
   materials[m.name]=nodes
report['glass_materials']=materials
with open('audit/batch4_rawls/r11_scene_diagnostics.json','w',encoding='utf-8') as f: json.dump(report,f,indent=2)
print(json.dumps({'desk_count':len(desks),'objects':report['named'],'glass_materials':materials},indent=2))
