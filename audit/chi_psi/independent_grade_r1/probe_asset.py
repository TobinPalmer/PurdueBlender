import bpy,json,hashlib
p=bpy.data.filepath
c=bpy.data.collections.get('Asset_chi_psi')
objs=list(c.all_objects) if c else []
materials={}
for o in objs:
 if o.type=='MESH':
  for m in o.data.materials:
   if m: materials[m.name]=materials.get(m.name,0)+1
ext=[{'path':i.filepath,'packed':bool(i.packed_file)} for i in bpy.data.images if i.source=='FILE']
interior=bpy.data.collections.get('Schematic_Interior_chi_psi')
scene=bpy.context.scene
result={'path':p,'sha256':hashlib.sha256(open(p,'rb').read()).hexdigest(),'scenes':[s.name for s in bpy.data.scenes], 'collections':[x.name for x in bpy.data.collections], 'target_collection_count':len(objs),'target_mesh_count':sum(o.type=='MESH' for o in objs),'interior_count':len(list(interior.all_objects)) if interior else None,'interior_objects':[o.name for o in interior.all_objects] if interior else [],'materials':materials,'images':ext,'asset_bounds':{a:[min((o.matrix_world @ __import__('mathutils').Vector(c))[i] for o in objs if o.type=='MESH' for c in o.bound_box) for i in (0,1,2)] for a in []}}
# bounds explicit
from mathutils import Vector
coords=[o.matrix_world@Vector(c) for o in objs if o.type=='MESH' for c in o.bound_box]
if coords: result['bounds']=[[min(v[i] for v in coords),max(v[i] for v in coords)] for i in range(3)]
open(r'audit/chi_psi/independent_grade_r1/asset_probe.json','w').write(json.dumps(result,indent=2))
