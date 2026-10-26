import bpy, hashlib, json, math
from pathlib import Path
from mathutils import Vector

ROOT = Path(__file__).resolve().parents[2]
ASSET = ROOT / 'modular/buildings/walc.blend'
OUT = ROOT / 'audit/walc_refine'
MANIFEST = json.loads((ROOT / 'modular/manifest.json').read_text(encoding='utf-8'))
REFS = json.loads((ROOT / 'audit/official_building_references.json').read_text(encoding='utf-8'))
ASSET_INFO = next(a for a in MANIFEST['assets'] if a['id'] == 'walc')
SOURCE = next(b for b in REFS['buildings'] if b['fid'] == 906)
COLLECTION = bpy.data.collections.get('Asset_walc')
if not COLLECTION:
    raise RuntimeError('Asset_walc not found on fresh standalone open')
SCENE = bpy.data.scenes.get('Building_walc') or bpy.context.scene
ROOT_OBJ = bpy.data.objects.get('AssetRoot_walc')
DEPS = bpy.context.evaluated_depsgraph_get()

objects = list(COLLECTION.all_objects)
meshes = [o for o in objects if o.type == 'MESH']
materialless=[]; used_materials={}; image_nodes=[]; missing_images=[]; external_links=[]
for obj in meshes:
    mats=[slot.material for slot in obj.material_slots]
    if not mats or all(m is None for m in mats): materialless.append(obj.name)
    for mat in mats:
        if not mat: continue
        used_materials[mat.name]=mat
for mat in used_materials.values():
    if not mat.use_nodes: continue
    for node in mat.node_tree.nodes:
        if node.type=='TEX_IMAGE' and node.image:
            image=node.image
            path=bpy.path.abspath(image.filepath) if image.source=='FILE' else None
            image_nodes.append({'material':mat.name,'image':image.name,'source':image.source,'filepath':path,'packed':bool(image.packed_file)})
            if image.source=='FILE' and path and not Path(path).exists() and not image.packed_file: missing_images.append(path)
for lib in bpy.data.libraries:
    external_links.append({'name':lib.name,'filepath':lib.filepath})

pts=[]; total_vertices=0
for obj in meshes:
    evaluated=obj.evaluated_get(DEPS); me=evaluated.to_mesh()
    try:
        total_vertices += len(me.vertices)
        pts.extend(evaluated.matrix_world @ v.co for v in me.vertices)
    finally: evaluated.to_mesh_clear()
bounds=[[min(p[i] for p in pts),max(p[i] for p in pts)] for i in range(3)] if pts else None

# Recompute the GIS perimeter agreement from the saved structural wall mesh(es).
ox,oy=ASSET_INFO['placement_origin_xy_m']
source_ring=SOURCE['rings_xy_m'][0]
structural=[o for o in meshes if o.get('source_fid')==906 or ('Structural_Envelope' in o.name and o.get('source_fid')==906)]
structural_xy=[]
for obj in structural:
    evaluated=obj.evaluated_get(DEPS); me=evaluated.to_mesh()
    try:
        for v in me.vertices:
            q=evaluated.matrix_world @ v.co
            structural_xy.append((q.x+ox,q.y+oy))
    finally: evaluated.to_mesh_clear()
def nearest(a, arr):
    return min(math.hypot(a[0]-b[0],a[1]-b[1]) for b in arr)
source_xy=[(float(x),float(y)) for x,y in source_ring]
source_to_model=max(nearest(p,structural_xy) for p in source_xy) if structural_xy else None
model_to_source=max(nearest(p,source_xy) for p in structural_xy) if structural_xy else None

# Inspect object parenting and root coordinate frame without changing the asset.
root_info=None
if ROOT_OBJ:
    root_info={'name':ROOT_OBJ.name,'parent':ROOT_OBJ.parent.name if ROOT_OBJ.parent else None,
               'location':list(ROOT_OBJ.location),'rotation_euler':list(ROOT_OBJ.rotation_euler),
               'scale':list(ROOT_OBJ.scale),'matrix_world':[[float(v) for v in row] for row in ROOT_OBJ.matrix_world]}

report={
 'asset':str(ASSET),'sha256':hashlib.sha256(ASSET.read_bytes()).hexdigest(),
 'blender_version':bpy.app.version_string,'scene':SCENE.name,
 'export_collection':COLLECTION.name,'collection_object_count':len(objects),'mesh_count':len(meshes),
 'mesh_vertex_count':total_vertices,'material_count_used':len(used_materials),
 'materialless_meshes':materialless,'image_texture_nodes':image_nodes,
 'missing_external_images':missing_images,'linked_libraries':external_links,
 'evaluated_bounds_local_m':bounds,'root_transform':root_info,
 'manifest_origin_xy_m':ASSET_INFO['placement_origin_xy_m'],
 'source_identity':{'provider':'Purdue University campus GIS, BuildingShapesZip4 layer 0','fid':906,
   'name':SOURCE.get('name'),'source_crs':SOURCE.get('source_crs'),
   'retrieval_snapshot':'audit/official_building_references.json (2026-10-22)',
   'source_xy_ring_vertex_count':len(source_xy),'structural_objects_with_fid906':[o.name for o in structural],
   'max_source_to_model_xy_m':source_to_model,'max_model_to_source_xy_m':model_to_source,
   'comparison':'nearest-neighbor XY residual over evaluated structural mesh vertices and source ring vertices; this checks agreement with cached Purdue GIS trace, not survey accuracy'},
 'collection_counts_by_type':{typ:sum(o.type==typ for o in objects) for typ in sorted(set(o.type for o in objects))},
 'scope_limit':'Standalone asset inspection; no master marker reload, neighborhood view, or full architectural survey.'
}
(OUT/'independent_reopen.json').write_text(json.dumps(report,indent=2,ensure_ascii=False)+'\n',encoding='utf-8')
print(json.dumps(report,indent=2,ensure_ascii=False))
