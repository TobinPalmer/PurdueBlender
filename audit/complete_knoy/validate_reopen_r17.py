import bpy, hashlib, json
from pathlib import Path
ROOT=Path(r'C:\Users\Tobin\Documents\Blender\PurdueMap')
BASE=ROOT/'audit/complete_knoy/knoy_hall_before_r17.blend'
ASSET=ROOT/'modular/buildings/knoy_hall.blend'
OUT=ROOT/'audit/complete_knoy/validation_round17.json'

def mesh_hash(obj):
    payload={'verts':[tuple(round(x,7) for x in v.co) for v in obj.data.vertices],
             'faces':[tuple(p.vertices) for p in obj.data.polygons],
             'matrix':[tuple(round(x,7) for x in row) for row in obj.matrix_world]}
    return hashlib.sha256(json.dumps(payload,sort_keys=True).encode()).hexdigest()
def band_vertex_counts(obj, levels):
    return {str(z):sum(abs((obj.matrix_world@v.co).z-z)<1e-5 for v in obj.data.vertices) for z in levels}
bpy.ops.wm.open_mainfile(filepath=str(BASE))
base_objs={o.name:o for o in bpy.data.objects}
base_meshes={n:o for n,o in base_objs.items() if o.type=='MESH'}
base_hashes={n:mesh_hash(o) for n,o in base_meshes.items()}
base_transforms={n:[round(x,7) for row in o.matrix_world for x in row] for n,o in base_objs.items()}
base_top={n:band_vertex_counts(base_objs[n],[18.0,19.1]) for n in ('KNOY_Fenestration_Ribbon_Glass','KNOY_Fenestration_Bronze_Mullions')}
bpy.ops.wm.open_mainfile(filepath=str(ASSET))
new_objs={o.name:o for o in bpy.data.objects}
new_meshes={n:o for n,o in new_objs.items() if o.type=='MESH'}
new_hashes={n:mesh_hash(o) for n,o in new_meshes.items()}
expected={'KNOY_Fenestration_Ribbon_Glass','KNOY_Fenestration_Bronze_Mullions'}
added='KNOY_Facade_Brick_Spandrels_R17'
changed=[n for n,h in base_hashes.items() if new_hashes.get(n)!=h]
unchanged=[n for n,h in base_hashes.items() if new_hashes.get(n)==h]
assert set(changed)==expected, changed
assert len(new_objs)==len(base_objs)+1 and len(new_meshes)==len(base_meshes)+1
assert added in new_meshes
assert all(base_transforms[n]==[round(x,7) for row in new_objs[n].matrix_world for x in row] for n in base_objs)
assert new_objs[added].parent.name=='AssetRoot_knoy_hall'
new_top={n:band_vertex_counts(new_objs[n],[18.0,19.1]) for n in expected}
assert base_top==new_top, (base_top,new_top)
assert not [i.filepath for i in bpy.data.images if i.source=='FILE' and i.filepath and not i.packed_file]
for z in [1.4,2.8,5.88,7.28,10.36,11.76,14.84,16.24,18.0,19.1]:
    assert any(abs((new_objs['KNOY_Fenestration_Ribbon_Glass'].matrix_world@v.co).z-z)<0.015 for v in new_objs['KNOY_Fenestration_Ribbon_Glass'].data.vertices), z
assert len(new_objs[added].data.vertices)>0 and len(new_objs[added].data.polygons)>0
assert 'ROUND 17' in bpy.data.texts['EVIDENCE_AND_INTERIOR_NOTES.txt'].as_string()
res={'revision':17,'asset_reopened':True,'passed':True,'blender_version':bpy.app.version_string,
 'object_counts_before':{'objects':len(base_objs),'meshes':len(base_meshes)},
 'object_counts_after':{'objects':len(new_objs),'meshes':len(new_meshes)},
 'changed_meshes':changed,'added_meshes':[added],'unchanged_mesh_count':len(unchanged),
 'all_preexisting_world_matrices_unchanged':True,'added_mesh_parent':new_objs[added].parent.name,
 'L5_band_vertex_counts_before':base_top,'L5_band_vertex_counts_after':new_top,
 'glass_bands_m':[[1.4,2.8],[5.88,7.28],[10.36,11.76],[14.84,16.24],[18.0,19.1]],
 'glass_mesh_vertices':len(new_objs['KNOY_Fenestration_Ribbon_Glass'].data.vertices),
 'mullion_mesh_vertices':len(new_objs['KNOY_Fenestration_Bronze_Mullions'].data.vertices),
 'brick_spandrel_mesh_vertices':len(new_objs[added].data.vertices),
 'external_unpacked_images':[],
 'scope':'L1-L4 glazing/mullion vertex Z coordinates changed and one source-supported brick spandrel mesh was added. All other mesh geometry and preexisting object transforms remained unchanged; L5/top band remained unchanged.'}
OUT.write_text(json.dumps(res,indent=2)+'\n',encoding='utf-8')
print(json.dumps(res,indent=2))
