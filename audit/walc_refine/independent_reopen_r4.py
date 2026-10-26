import bpy, hashlib, json, math
from pathlib import Path
from mathutils import Vector

ROOT=Path(__file__).resolve().parents[2]
ASSET=ROOT/'modular/buildings/walc.blend'
OUT=ROOT/'audit/walc_refine'
COLLECTION=bpy.data.collections.get('Asset_walc')
ROOT_OBJ=bpy.data.objects.get('AssetRoot_walc')
if not COLLECTION or not ROOT_OBJ:
    raise RuntimeError('Fresh open did not contain the expected collection/root')
objects=list(COLLECTION.all_objects)
meshes=[o for o in objects if o.type=='MESH']
materialless=[]; invalid_slots=[]; used={}; image_nodes=[]; missing=[]; links=[]
for obj in meshes:
    slots=[s.material for s in obj.material_slots]
    if not slots or all(m is None for m in slots): materialless.append(obj.name)
    if obj.data.polygons and any(p.material_index>=len(slots) or slots[p.material_index] is None for p in obj.data.polygons): invalid_slots.append(obj.name)
    for m in slots:
        if m: used[m.name]=m
for m in used.values():
    if not m.use_nodes: continue
    for n in m.node_tree.nodes:
        if n.type=='TEX_IMAGE' and n.image:
            path=bpy.path.abspath(n.image.filepath) if n.image.source=='FILE' else None
            image_nodes.append({'material':m.name,'image':n.image.name,'source':n.image.source,'filepath':path,'packed':bool(n.image.packed_file)})
            if n.image.source=='FILE' and path and not Path(path).exists() and not n.image.packed_file: missing.append(path)
for lib in bpy.data.libraries:
    p=bpy.path.abspath(lib.filepath)
    links.append({'name':lib.name,'filepath':lib.filepath,'resolved_path':p,'exists':Path(p).exists()})

deps=bpy.context.evaluated_depsgraph_get(); pts=[]; countv=0
for o in meshes:
    ev=o.evaluated_get(deps); me=ev.to_mesh()
    try:
        countv+=len(me.vertices)
        pts.extend(ev.matrix_world@v.co for v in me.vertices)
    finally: ev.to_mesh_clear()
bounds=[[min(p[i] for p in pts),max(p[i] for p in pts)] for i in range(3)] if pts else None

# Confirm original traced outline object stayed unchanged at the mesh-data level.
roof=bpy.data.objects.get('WALC_Official_906_Roof')
roof_count=len(roof.data.vertices) if roof and roof.type=='MESH' else None
roof_bounds=None
if roof:
    rp=[roof.matrix_world@v.co for v in roof.data.vertices]
    roof_bounds=[[min(p[i] for p in rp),max(p[i] for p in rp)] for i in range(3)]
root_info={'location':list(ROOT_OBJ.location),'rotation':list(ROOT_OBJ.rotation_euler),'scale':list(ROOT_OBJ.scale),'matrix_world':[[float(x) for x in row] for row in ROOT_OBJ.matrix_world]}
report={'asset':str(ASSET),'sha256':hashlib.sha256(ASSET.read_bytes()).hexdigest(),'blender_version':bpy.app.version_string,
        'scene':(bpy.data.scenes.get('Building_walc') or bpy.context.scene).name,'export_collection':COLLECTION.name,
        'collection_object_count':len(objects),'mesh_count':len(meshes),'mesh_vertex_count':countv,'used_material_count':len(used),
        'materialless_meshes':materialless,'invalid_material_slot_meshes':invalid_slots,'image_texture_nodes':image_nodes,
        'missing_external_images':missing,'linked_libraries':links,'evaluated_bounds_local_m':bounds,'root_transform':root_info,
        'roof_trace':{'object':roof.name if roof else None,'vertex_count':roof_count,'bounds_local_m':roof_bounds,
                      'note':'Original GIS-traced roof polygon was preserved; this is not height/roof-survey verification.'},
        'new_facade_objects':[o.name for o in objects if o.name.startswith('WALC_R4_')],
        'scope_limit':'Standalone reopen only; no master Placement_walc or neighboring campus alignment.'}
expected='01f0ba7bd8fbdee2da267e85c8d35e327cf891d68a05cbeea5876b5b692b5dd4'
if report['sha256']!=expected: raise RuntimeError('Hash mismatch on fresh reopen')
if materialless or invalid_slots or missing or any(not x['exists'] for x in links): raise RuntimeError('Reopen check failed')
if not ROOT_OBJ.matrix_world.is_identity: raise RuntimeError('Asset root is not identity')
(OUT/'independent_reopen_r4.json').write_text(json.dumps(report,indent=2,ensure_ascii=False)+'\n',encoding='utf-8')
print(json.dumps(report,indent=2,ensure_ascii=False))
