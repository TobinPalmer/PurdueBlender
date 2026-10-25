import bpy, json, hashlib
from pathlib import Path
from mathutils import Vector
root=Path(r'C:\Users\Tobin\Documents\Blender\PurdueMap')
asset=root/'modular/buildings/purdue_memorial_union.blend'
baseline=root/'modular/buildings/purdue_memorial_union.blend1'
out=root/'audit/purdue_memorial_union_refine/independent_reopen_r1.json'
def sha(p): return hashlib.sha256(p.read_bytes()).hexdigest()
def inspect(path):
    bpy.ops.wm.open_mainfile(filepath=str(path))
    col=bpy.data.collections.get('Asset_purdue_memorial_union')
    if col is None: raise RuntimeError('Asset collection missing')
    objs=list(col.all_objects)
    meshes=[o for o in objs if o.type=='MESH']
    pts=[o.matrix_world @ Vector(c) for o in meshes for c in o.bound_box]
    bounds=[[round(min(v[i] for v in pts),4),round(max(v[i] for v in pts),4)] for i in range(3)]
    roots=[]
    for name in ('AssetRoot_purdue_memorial_union','Root_purdue_memorial_union','PMU_Root'):
        o=bpy.data.objects.get(name)
        if o: roots.append({'name':name,'location':list(o.location),'rotation':list(o.rotation_euler),'scale':list(o.scale)})
    structural={}
    for o in meshes:
        if 'Wall' in o.name or 'Base' in o.name:
            points=[o.matrix_world @ Vector(c) for c in o.bound_box]
            structural[o.name]=[[round(min(v[i] for v in points),4),round(max(v[i] for v in points),4)] for i in range(3)]
    return {'objects':len(objs),'meshes':len(meshes),'mesh_materialless':[o.name for o in meshes if len(o.data.materials)==0],
            'external_images':[im.filepath for im in bpy.data.images if im.source=='FILE' and im.filepath and not im.packed_file],
            'bounds':bounds,'roots':roots,'structural':structural,'refinement_objects':[o.name for o in objs if o.name.startswith('PMU_R1_')],
            'scenes':[s.name for s in bpy.data.scenes], 'collection_library':str(col.library.filepath) if col.library else None}
current=inspect(asset)
old=inspect(baseline)
common=sorted(set(current['structural']) & set(old['structural']))
changed={k:{'baseline':old['structural'][k],'current':current['structural'][k]} for k in common if old['structural'][k]!=current['structural'][k]}
result={'asset':str(asset),'sha256':sha(asset),'baseline_sha256':sha(baseline),'collection':'Asset_purdue_memorial_union','current':current,'baseline':{'objects':old['objects'],'meshes':old['meshes'],'roots':old['roots'],'structural_count':len(old['structural'])},'common_structural_count':len(common),'changed_structural_bounds':changed}
out.write_text(json.dumps(result,indent=2)+'\n',encoding='utf-8')
print(json.dumps({k:v for k,v in result.items() if k not in ('current','baseline')},indent=2))
print('CURRENT',json.dumps({k:v for k,v in current.items() if k not in ('structural','refinement_objects')},indent=2))
print('BASELINE OBJECTS',old['objects'],'MESHES',old['meshes'],'STRUCTURAL',len(old['structural']))
print('REFINEMENT COUNT',len(current['refinement_objects']))
print('CHANGED STRUCTURAL',changed)
