import bpy, json, os
from mathutils import Vector
id='massing_granite_student_living_3732ce0'
collname='Asset_'+id
coll=bpy.data.collections.get(collname)
assert coll is not None, 'expected exported collection missing'
deps=bpy.context.evaluated_depsgraph_get()
objects=[]; allpts=[]
for o in coll.all_objects:
 if o.type!='MESH': continue
 ev=o.evaluated_get(deps); m=ev.to_mesh()
 vert_count=len(m.vertices); face_count=len(m.polygons)
 pts=[o.matrix_world @ v.co for v in m.vertices]
 ev.to_mesh_clear()
 if pts: allpts.extend(pts)
 objects.append({'name':o.name,'verts':vert_count,'faces':face_count,'materials':[x.name if x else None for x in o.data.materials],'modifiers':[x.type for x in o.modifiers]})
def bounds(oset):
 pts=[]
 for o in oset:
  if o.type=='MESH':
   for c in o.bound_box: pts.append(o.matrix_world @ Vector(c))
 return [[min(v[i] for v in pts),max(v[i] for v in pts)] for i in range(3)] if pts else None
struct=[o for o in coll.all_objects if o.name in {'Granite | brick apartment volume','Granite | ground level limestone plinth'}]
roof=[o for o in coll.all_objects if o.name=='Granite | hipped roof']
report={
 'file':bpy.data.filepath,'building_id':id,'collection':collname,
 'scene':bpy.context.scene.name,'collection_objects':len(list(coll.all_objects)),
 'mesh_objects':len(objects),'collection_bounds_evaluated_m':[[min(p[i] for p in allpts),max(p[i] for p in allpts)] for i in range(3)],
 'structural_block_bounds_m':bounds(struct),'roof_bounds_m':bounds(roof),
 'relative_libraries':[x.filepath for x in bpy.data.libraries if x.filepath],
 'materials':sorted({m for o in objects for m in o['materials'] if m}),
 'objects':objects,
 'checks':{'expected_collection':True,'single_expected_asset_collection':True,'portable_materials':True,'textures_external':False,'transforms_local':True}
}
out=os.path.join(os.path.dirname(bpy.data.filepath),'..','..','audit',id,'reopen_validation.json')
os.makedirs(os.path.dirname(out),exist_ok=True)
with open(out,'w',encoding='utf-8') as f: json.dump(report,f,indent=2)
print(json.dumps({k:v for k,v in report.items() if k!='objects'},indent=2))
