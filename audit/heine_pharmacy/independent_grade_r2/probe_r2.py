import bpy,json,hashlib,os
from mathutils import Vector
asset=os.path.abspath('modular/buildings/heine_pharmacy.blend')
bpy.ops.wm.open_mainfile(filepath=asset)
c=bpy.data.collections.get('Asset_heine_pharmacy')
objs=list(c.all_objects) if c else []
meshes=[o for o in objs if o.type=='MESH']
pts=[o.matrix_world @ Vector(v) for o in meshes for v in o.bound_box]
bounds=[[min(p[i] for p in pts),max(p[i] for p in pts)] for i in range(3)] if pts else None
shell=bpy.data.objects.get('RHPH structural shell | GIS outline')
shell_vertices=[list(shell.matrix_world@v.co) for v in shell.data.vertices] if shell else []
material_report=[]; missing=[]
for m in bpy.data.materials:
 if m.users==0: continue
 nodes=[]
 if m.node_tree:
  nodes=[n.type for n in m.node_tree.nodes]
  for n in m.node_tree.nodes:
   if n.type=='TEX_IMAGE' and n.image and n.image.source=='FILE':
    path=bpy.path.abspath(n.image.filepath)
    if not os.path.exists(path): missing.append(path)
 material_report.append({'name':m.name,'node_types':nodes})
selected=[o.name for o in objs if any(k in o.name.lower() for k in ['facade','glazing','window','spandrel','arcade','arch','pier','crown','roof','schematic_only','schematic interior'])]
custom={str(k):str(v) for k,v in (c.items() if c else [])}
out={'asset_path':asset,'sha256':hashlib.sha256(open(asset,'rb').read()).hexdigest(),'collection':c.name if c else None,'object_count':len(objs),'mesh_count':len(meshes),'bounds_local_m':bounds,'shell_mesh_vertex_count':len(shell_vertices),'shell_mesh_vertices':shell_vertices,'selected_object_names':selected,'materials':material_report,'missing_external_texture_paths':sorted(set(missing)),'collection_custom_properties':custom,'scenes':[s.name for s in bpy.data.scenes]}
json.dump(out,open('audit/heine_pharmacy/independent_grade_r2/probe.json','w'),indent=2)
print(json.dumps({k:v for k,v in out.items() if k not in ('shell_mesh_vertices','materials','selected_object_names')},indent=2))
