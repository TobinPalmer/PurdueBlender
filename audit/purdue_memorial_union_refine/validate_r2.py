import bpy,json,os,hashlib
from mathutils import Vector
ROOT=r"C:\Users\Tobin\Documents\Blender\PurdueMap"
ASSET=os.path.join(ROOT,"modular","buildings","purdue_memorial_union.blend")
BASE=os.path.join(ROOT,"audit","purdue_memorial_union_independent_grade","structural_bounds.json")
OUT=os.path.join(ROOT,"audit","purdue_memorial_union_refine","validation_r2.json")
def sha(p):
 h=hashlib.sha256()
 with open(p,'rb') as f:
  for b in iter(lambda:f.read(1<<20),b''):h.update(b)
 return h.hexdigest()
baseline=json.load(open(BASE,encoding='utf-8')); bpy.ops.wm.open_mainfile(filepath=ASSET)
col=bpy.data.collections['Asset_purdue_memorial_union']; current={}; verts=[]
for o in col.all_objects:
 if o.type=='MESH':
  p=[o.matrix_world@Vector(c) for c in o.bound_box]; verts.extend(p)
  current[o.name]=[[min(v[i] for v in p),max(v[i] for v in p)] for i in range(3)]
old={o['name']:o['bounds'] for o in baseline['structural_objects']}
orig=[n for n in old if 'Wall' in n or 'Base' in n]; matched=sorted(set(orig)&set(current))
delta={n:max(abs(old[n][i][j]-current[n][i][j]) for i in range(3) for j in range(2)) for n in matched}
changed={n:d for n,d in delta.items() if d>.001}
additive=sorted(n for n in current if ('Wall' in n or 'Base' in n) and n not in orig)
removed_roofs=sorted(n for n in old if ('Roof' in n or 'Slab' in n) and n not in current)
root=next((o for o in col.all_objects if o.name=='AssetRoot_purdue_memorial_union'),None)
images=sum(1 for im in bpy.data.images if im.source=='FILE' and im.filepath and not im.packed_file)
result={"asset":ASSET,"sha256":sha(ASSET),"collection":"Asset_purdue_memorial_union",
 "original_baseline":{"bounds_file":os.path.relpath(BASE,ROOT).replace('\\','/'),"asset_sha256":baseline['asset_sha256']},
 "objects":len(col.all_objects),"mesh_objects":sum(o.type=='MESH' for o in col.all_objects),
 "facade_refinement_objects":sum(o.name.startswith('PMU_R1_') for o in col.all_objects),
 "R2_roof_objects":sum(o.name.startswith('PMU_R2_Roof_') for o in col.all_objects),
 "aggregate_mesh_bounds_local_m":[[round(min(v[i] for v in verts),4),round(max(v[i] for v in verts),4)] for i in range(3)],
 "original_wall_base_objects":len(orig),"matched_original_wall_base_objects":len(matched),
 "original_wall_base_bound_delta_m":{n:round(d,8) for n,d in delta.items()},"changes_over_1mm":changed,
 "additive_wall_base_objects":additive,"original_roof_objects_intentionally_replaced":removed_roofs,
 "root_transform":None if root is None else {"location":[round(x,6) for x in root.location],"rotation":[round(x,6) for x in root.rotation_euler],"scale":[round(x,6) for x in root.scale]},
 "unpacked_external_images":images,"mesh_objects_without_material":sum(1 for o in col.all_objects if o.type=='MESH' and not o.data.materials),
 "previews":["audit/purdue_memorial_union_refine/south_refine_preview_r2.png","audit/purdue_memorial_union_refine/south_facade_detail_r2.png"],
 "fresh_reopen":"yes; inventory measured after opening saved asset from disk",
 "master_placement":"untouched; read-only record remains in audit/purdue_memorial_union_independent_grade/master_marker_readonly.json",
 "uncertainty":"29.5 m total height, floor spacing, eave/ridge heights and roof intersections remain estimates; no measured elevation schedule is available."}
with open(OUT,'w',encoding='utf-8') as f:json.dump(result,f,indent=2)
print(json.dumps(result,indent=2))
