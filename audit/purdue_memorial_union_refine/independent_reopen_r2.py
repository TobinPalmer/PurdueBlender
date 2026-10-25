import bpy, json, hashlib
from pathlib import Path
from mathutils import Vector
root=Path(r'C:\Users\Tobin\Documents\Blender\PurdueMap')
asset=root/'modular/buildings/purdue_memorial_union.blend'
out=root/'audit/purdue_memorial_union_refine/independent_reopen_r2.json'
base_path=root/'audit/purdue_memorial_union_independent_grade/structural_bounds.json'
bpy.ops.wm.open_mainfile(filepath=str(asset))
col=bpy.data.collections.get('Asset_purdue_memorial_union')
if col is None: raise RuntimeError('Expected export collection missing')
objs=list(col.all_objects); meshes=[o for o in objs if o.type=='MESH']; scene=bpy.context.scene; deps=bpy.context.evaluated_depsgraph_get()
root_obj=bpy.data.objects.get('AssetRoot_purdue_memorial_union')
pts=[]; materialless=[]; structural={}
for obj in meshes:
    if len(obj.data.materials)==0 or any(m is None for m in obj.data.materials): materialless.append(obj.name)
    evaluated=obj.evaluated_get(deps)
    opoints=[evaluated.matrix_world @ Vector(c) for c in evaluated.bound_box]
    pts.extend(opoints)
    if 'Wall' in obj.name or 'Base' in obj.name:
        structural[obj.name]=[[min(p[i] for p in opoints),max(p[i] for p in opoints)] for i in range(3)]
bounds=[[min(p[i] for p in pts),max(p[i] for p in pts)] for i in range(3)] if pts else None
base=json.loads(base_path.read_text(encoding='utf-8'))
original={o['name']:o['bounds'] for o in base['structural_objects']}
common=sorted(set(original)&set(structural))
delta={name:max(abs(structural[name][axis][edge]-original[name][axis][edge]) for axis in range(3) for edge in range(2)) for name in common}
images=[im.filepath for im in bpy.data.images if im.source=='FILE' and im.filepath and not im.packed_file]
result={
  'asset':str(asset),'sha256':hashlib.sha256(asset.read_bytes()).hexdigest(),'baseline_sha256':base['asset_sha256'],
  'reopened_saved_asset':True,'scene':scene.name,'collection':col.name,'collection_objects':len(objs),'mesh_objects':len(meshes),
  'root':({'name':root_obj.name,'location':list(root_obj.location),'rotation_euler':list(root_obj.rotation_euler),'scale':list(root_obj.scale)} if root_obj else None),
  'evaluated_collection_bounds_local_m':bounds,'materialless_meshes':materialless,'missing_external_images':images,
  'original_structural_names':len(original),'matched_original_structural_names':len(common),
  'changed_original_structural_bounds_over_1mm':{k:v for k,v in delta.items() if v>0.001},
  'max_original_structural_bound_delta_m':max(delta.values()) if delta else None,
  'missing_original_structural_names':sorted(set(original)-set(structural)),
  'additive_structural_names':sorted(set(structural)-set(original)),
  'structural_bounds_current_m':structural,'object_names':sorted(o.name for o in objs)
}
out.write_text(json.dumps(result,indent=2)+'\n',encoding='utf-8')
print(json.dumps({k:v for k,v in result.items() if k not in ['object_names','structural_bounds_current_m']},indent=2))
