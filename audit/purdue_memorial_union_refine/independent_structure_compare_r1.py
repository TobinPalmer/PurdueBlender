import bpy,json
from pathlib import Path
from mathutils import Vector
root=Path(r'C:\Users\Tobin\Documents\Blender\PurdueMap')
asset=root/'modular/buildings/purdue_memorial_union.blend'
oldpath=root/'audit/purdue_memorial_union_independent_grade/structural_bounds.json'
out=root/'audit/purdue_memorial_union_refine/structural_comparison_r1.json'
old=json.loads(oldpath.read_text(encoding='utf-8'))
bpy.ops.wm.open_mainfile(filepath=str(asset)); col=bpy.data.collections['Asset_purdue_memorial_union']
def bounds(o):
 pts=[o.matrix_world@Vector(c) for c in o.bound_box]
 return [[min(v[i] for v in pts),max(v[i] for v in pts)] for i in range(3)]
current={o.name:bounds(o) for o in col.all_objects if o.type=='MESH'}
base={x['name']:x['bounds'] for x in old['structural_objects']}
common=set(base)&set(current)
def diff(a,b): return max(abs(a[i][j]-b[i][j]) for i in range(3) for j in range(2))
comparisons={k:{'max_abs_bound_delta_m':diff(base[k],current[k]),'baseline':base[k],'current':current[k]} for k in sorted(common)}
changed={k:v for k,v in comparisons.items() if v['max_abs_bound_delta_m']>0.001}
wallbase=[k for k in base if 'Wall' in k or 'Base' in k]
current_wallbase=[k for k in current if 'Wall' in k or 'Base' in k]
wb_common=set(wallbase)&set(current_wallbase)
result={'baseline_sha256':old['asset_sha256'],'current_sha256':'9f3d804155efb70e13ba49706f7da88f61a93a30f981612ec318eca2f3cac0f6',
 'baseline_named_structural_count':len(base),'current_wall_base_count':len(current_wallbase),'old_wall_base_count':len(wallbase),
 'common_wall_base_count':len(wb_common),'wall_base_bound_changes_over_1mm':{k:comparisons[k] for k in wb_common if k in changed},
 'all_named_structural_common_count':len(common),'all_named_structural_removed':sorted(set(base)-set(current)),
 'all_named_structural_added_not_applicable':sorted(set(current_wallbase)-set(base)),
 'comparison_tolerance_m':0.001,'wall_base_bounds_within_tolerance':len(wb_common)==len(wallbase) and not any(k in changed for k in wb_common)}
out.write_text(json.dumps(result,indent=2,ensure_ascii=False)+'\n',encoding='utf-8')
print(json.dumps(result,indent=2,ensure_ascii=False))
