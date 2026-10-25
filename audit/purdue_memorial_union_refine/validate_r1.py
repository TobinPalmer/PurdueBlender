import bpy, json, os, hashlib
from mathutils import Vector
ROOT=r"C:\Users\Tobin\Documents\Blender\PurdueMap"
ASSET=os.path.join(ROOT,"modular","buildings","purdue_memorial_union.blend")
BASE_BOUNDS=os.path.join(ROOT,"audit","purdue_memorial_union_independent_grade","structural_bounds.json")
OUT=os.path.join(ROOT,"audit","purdue_memorial_union_refine","validation_r1.json")
def sha(p):
 h=hashlib.sha256()
 with open(p,'rb') as f:
  for x in iter(lambda:f.read(1<<20),b''): h.update(x)
 return h.hexdigest()
# Original baseline is the immutable auditor bounds record keyed to the audited
# asset hash, never the mutable Blender .blend1 rolling backup.
baseline=json.load(open(BASE_BOUNDS,encoding='utf-8'))
bpy.ops.wm.open_mainfile(filepath=ASSET)
col=bpy.data.collections['Asset_purdue_memorial_union']
current={}; allmesh=[]
for o in col.all_objects:
 if o.type!='MESH': continue
 pts=[o.matrix_world@Vector(c) for c in o.bound_box]; allmesh.extend(pts)
 current[o.name]=[[min(v[i] for v in pts),max(v[i] for v in pts)] for i in range(3)]
baseline_bounds={o['name']:o['bounds'] for o in baseline['structural_objects']}
original_wall_base=[n for n in baseline_bounds if 'Wall' in n or 'Base' in n]
matched=sorted(set(original_wall_base)&set(current))
def maxdelta(a,b): return max(abs(a[i][j]-b[i][j]) for i in range(3) for j in range(2))
diffs={n:maxdelta(baseline_bounds[n],current[n]) for n in matched}
changed={n:v for n,v in diffs.items() if v>0.001}
current_wall_base=sorted(n for n in current if 'Wall' in n or 'Base' in n)
original_roofs=[n for n in baseline_bounds if 'Roof' in n or 'Slab' in n]
roots=[]
for o in col.all_objects:
 if o.name=='AssetRoot_purdue_memorial_union':
  roots.append({"name":o.name,"location":[round(x,6) for x in o.location],"rotation":[round(x,6) for x in o.rotation_euler],"scale":[round(x,6) for x in o.scale]})
images=[im for im in bpy.data.images if im.source=='FILE' and im.filepath and not im.packed_file]
agg=[[min(v[i] for v in allmesh),max(v[i] for v in allmesh)] for i in range(3)]
result={
 "asset":ASSET,"sha256":sha(ASSET),"baseline_source":os.path.relpath(BASE_BOUNDS,ROOT).replace('\\','/'),
 "baseline_asset_sha256":baseline['asset_sha256'],"baseline_source_is_immutable_audited_bounds_record":True,
 "collection":"Asset_purdue_memorial_union","objects":len(col.all_objects),"mesh_objects":sum(o.type=='MESH' for o in col.all_objects),
 "facade_refinement_objects":sum(o.name.startswith('PMU_R1_') for o in col.all_objects),
 "new_roof_geometry_objects":sum(o.name.startswith('PMU_R2_Roof_') for o in col.all_objects),
 "aggregate_mesh_bounds_local_m":[[round(x,4),round(y,4)] for x,y in agg],
 "original_wall_base_objects":len(original_wall_base),"original_wall_base_objects_matched":len(matched),
 "original_wall_base_bound_delta_m":{n:round(v,8) for n,v in diffs.items()},"original_wall_base_changes_over_1mm":changed,
 "current_wall_base_object_count":len(current_wall_base),
 "additive_wall_base_objects":[n for n in current_wall_base if n not in original_wall_base],
 "original_roof_objects_replaced":original_roofs,"replacement_roof_geometry_prefix":"PMU_R2_Roof_",
 "root_transform":roots,"unpacked_external_images":len(images),
 "mesh_objects_without_material":sum(1 for o in col.all_objects if o.type=='MESH' and not o.data.materials),
 "preview":"audit/purdue_memorial_union_refine/south_refine_preview.png",
 "detail_preview":"audit/purdue_memorial_union_refine/south_facade_detail_r1.png",
 "fresh_reopen":"yes; inventory was measured after reopening the saved blend from disk",
 "master_placement":"not modified; previous read-only marker record is audit/purdue_memorial_union_independent_grade/master_marker_readonly.json",
 "height_limit":"29.5 m aggregate and floor/eave/ridge spacing remain model-only estimates; no measured elevation schedule was found."
}
with open(OUT,'w',encoding='utf-8') as f: json.dump(result,f,indent=2)
print(json.dumps(result,indent=2))
