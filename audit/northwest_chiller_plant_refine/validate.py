import bpy, os, json, hashlib
from mathutils import Vector
ROOT=os.path.abspath('.'); PATH=os.path.join(ROOT,'modular','buildings','northwest_chiller_plant.blend'); OUT=os.path.join(ROOT,'audit','northwest_chiller_plant_refine')
bpy.ops.wm.open_mainfile(filepath=PATH)
c=bpy.data.collections.get('Asset_northwest_chiller_plant'); assert c
objects=list(c.all_objects); assert len(objects)==572, len(objects)
shell=bpy.data.objects.get('northwest_chiller_plant_official_GIS_shell'); assert shell and shell.type=='MESH'
pts=[shell.matrix_world@Vector(v) for v in shell.bound_box]
bounds=[[round(min(p[i] for p in pts),4) for i in range(3)],[round(max(p[i] for p in pts),4) for i in range(3)]]
expected=[[-17.0048,-18.5665,.3],[20.4937,21.454,10.5]]
assert bounds==expected,(bounds,expected)
matnames=sorted({m.name for o in objects for m in getattr(o.data,'materials',[]) if m})
missing=[]
for m in bpy.data.materials:
 if not m.use_nodes: continue
 for n in m.node_tree.nodes:
  if n.type=='TEX_IMAGE' and n.image and n.image.source=='FILE':
   p=bpy.path.abspath(n.image.filepath)
   if not os.path.exists(p): missing.append([m.name,n.image.filepath])
assert not missing,missing
assert not [o.name for o in bpy.data.objects if o.name.startswith('NWCP_refine_') and o.type in {'CAMERA','LIGHT'}]
record={'reopened':True,'collection':c.name,'collection_object_count':len(objects),'object_types':{t:sum(o.type==t for o in objects) for t in sorted({o.type for o in objects})},'unique_linked_material_count':len(matnames),'missing_external_image_textures':missing,'GIS_shell':shell.name,'GIS_shell_bounds_local_m':bounds,'shell_bounds_unchanged':True,'overview_preview':os.path.relpath(os.path.join(OUT,'northwest_chiller_plant_refine_overview.png'),ROOT),'detail_preview':os.path.relpath(os.path.join(OUT,'northwest_chiller_plant_refine_detail.png'),ROOT)}
with open(os.path.join(OUT,'reopen_validation.json'),'w',encoding='utf-8') as f:json.dump(record,f,indent=2)
print(json.dumps(record,indent=2))
