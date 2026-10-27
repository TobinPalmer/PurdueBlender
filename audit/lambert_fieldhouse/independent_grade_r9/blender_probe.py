import bpy, hashlib, json
from pathlib import Path
p=Path(bpy.data.filepath)
col=bpy.data.collections.get('Asset_lambert_fieldhouse')
if col is None: raise RuntimeError('Expected asset collection missing')
obs=list(col.all_objects)
meshes=[o for o in obs if o.type=='MESH']
missing=[o.name for o in meshes if not o.material_slots or not any(s.material for s in o.material_slots)]
lib=[str(x.filepath) for x in bpy.data.libraries]
imgs=[{'name':i.name,'filepath':i.filepath,'packed':bool(i.packed_file)} for i in bpy.data.images if i.source=='FILE']
ctx=[n for n in ('LAMB | Stadium sidewalk round4','LAMB | Stadium curb round4','LAMB | Stadium Avenue roadway round4') if any(o.name==n for o in obs)]
dg=bpy.context.evaluated_depsgraph_get(); pts=[]
for o in obs:
 if o.type not in {'MESH','CURVE','FONT'}: continue
 eo=o.evaluated_get(dg)
 pts.extend(o.matrix_world @ __import__('mathutils').Vector(c) for c in eo.bound_box)
bounds=[[min(v[i] for v in pts),max(v[i] for v in pts)] for i in range(3)] if pts else None
out={'candidate':str(p),'sha256':hashlib.sha256(p.read_bytes()).hexdigest(),'blender_version':bpy.app.version_string,'scene':bpy.context.scene.name,'scene_objects':len(bpy.context.scene.objects),'collection':'Asset_lambert_fieldhouse','collection_objects':len(obs),'mesh_objects':len(meshes),'materialless_mesh_count':len(missing),'materialless_mesh_names':missing[:100],'linked_libraries':lib,'external_images':imgs,'retained_context_objects_in_asset_collection':ctx,'evaluated_collection_bounds':bounds,'mesh_count_by_type':{t:sum(o.type==t for o in obs) for t in sorted(set(o.type for o in obs))}}
Path(__file__).with_name('fresh_open_probe.json').write_text(json.dumps(out,indent=2)+'\n',encoding='utf-8')
print(json.dumps(out,indent=2))
