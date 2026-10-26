import bpy, hashlib, json
from pathlib import Path
from collections import Counter
ASSET = Path(bpy.data.filepath).resolve()
AUDIT = Path(__file__).resolve().parent
EXPECTED = 'a06977c0783442a0eb7561d23e294bfc65d11546b3aa4a0c13d9c9b62f68a330'
COLLECTION = 'Asset_massing_st_thomas_aquinas_5535390'
ROOT = 'AssetRoot_massing_st_thomas_aquinas_5535390'
sha = hashlib.sha256(ASSET.read_bytes()).hexdigest()
if sha != EXPECTED:
    raise RuntimeError(f'Wrong candidate SHA: {sha}')
coll = bpy.data.collections.get(COLLECTION)
root = bpy.data.objects.get(ROOT)
if coll is None or root is None:
    raise RuntimeError('Expected export collection or root missing')
root_matrix = [[float(root.matrix_world[r][c]) for c in range(4)] for r in range(4)]
identity = all(abs(root_matrix[r][c] - (1.0 if r == c else 0.0)) < 1e-6 for r in range(4) for c in range(4))
objs = list(coll.all_objects)
types = Counter(o.type for o in objs)
matless, invalid, empty, object_bounds = [], [], [], []
mins=[float('inf')]*3; maxs=[float('-inf')]*3
deps=bpy.context.evaluated_depsgraph_get()
for ob in objs:
    if ob.type != 'MESH':
        continue
    if len(ob.data.vertices)==0 or len(ob.data.polygons)==0: empty.append(ob.name)
    if not ob.material_slots: matless.append(ob.name)
    if any(p.material_index < 0 or p.material_index >= len(ob.material_slots) or ob.material_slots[p.material_index].material is None for p in ob.data.polygons): invalid.append(ob.name)
    ev=ob.evaluated_get(deps); me=ev.to_mesh()
    try:
        coords=[ev.matrix_world @ v.co for v in me.vertices]
        if not coords: continue
        lo=[min(float(v[i]) for v in coords) for i in range(3)]
        hi=[max(float(v[i]) for v in coords) for i in range(3)]
        for i in range(3): mins[i]=min(mins[i],lo[i]); maxs[i]=max(maxs[i],hi[i])
        if any(k in ob.name.lower() for k in ['base','shell','foundation','truss','window','belltower','entry','classroom','stair','board','lectern','cabinet','roof','wall']):
            object_bounds.append({'name':ob.name,'bounds_local_m':[[round(x,4) for x in lo],[round(x,4) for x in hi]],'vertices':len(me.vertices),'polygons':len(me.polygons),'material_slots':len(ob.material_slots)})
    finally:
        ev.to_mesh_clear()
used_mats=sorted({s.material.name for ob in objs if ob.type=='MESH' for s in ob.material_slots if s.material})
images=[]
for im in bpy.data.images:
    if im.source=='FILE' and im.filepath:
        resolved=Path(bpy.path.abspath(im.filepath,library=im.library))
        images.append({'name':im.name,'path':im.filepath,'packed':bool(im.packed_file),'exists':resolved.exists()})
tex_nodes=[]
for name in used_mats:
    mat=bpy.data.materials.get(name)
    if mat and mat.use_nodes and mat.node_tree:
        tex_nodes.extend(f'{name}:{n.type}' for n in mat.node_tree.nodes if n.type=='TEX_IMAGE')
def jsonable(value):
    if value is None or isinstance(value,(str,int,float,bool)):
        return value
    try:
        return [jsonable(item) for item in value]
    except TypeError:
        return str(value)
props={k:jsonable(root[k]) for k in root.keys()}
selected_prefixes=['SOTAC_R4_SanctuaryTruss_','SOTAC_R4_Sanctuary_North_GableEnd','SOTAC_R4_Classroom_','SOTAC_R4_Stone_Stringcourse_','SOTAC_Classroom_']
prefix_counts={p:sum(1 for o in objs if o.name.startswith(p)) for p in selected_prefixes}
result={'fresh_process_reopen':True,'asset':str(ASSET),'sha256':sha,'hash_matches_expected':sha==EXPECTED,'blender_version':bpy.app.version_string,'scene':bpy.context.scene.name,'export_collection':coll.name,'object_count':len(objs),'object_type_counts':dict(types),'identity_root':identity,'root_world_matrix':root_matrix,'root_properties':props,'bounds_local_m':[[mins[i],maxs[i]] for i in range(3)],'used_material_count':len(used_mats),'used_materials':used_mats,'image_texture_nodes_in_used_materials':tex_nodes,'file_images':images,'linked_libraries':[l.filepath for l in bpy.data.libraries],'materialless_meshes':matless,'invalid_material_meshes':invalid,'empty_meshes':empty,'selected_prefix_counts':prefix_counts,'selected_object_bounds':object_bounds}
(AUDIT/'independent_grade_r4_reopen.json').write_text(json.dumps(result,indent=2,ensure_ascii=False)+'\n',encoding='utf-8')
print(json.dumps(result,indent=2,ensure_ascii=False))

