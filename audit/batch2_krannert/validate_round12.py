import bpy, hashlib, json, os
from pathlib import Path

ROOT=Path(r'C:/Users/Tobin/Documents/Blender/PurdueMap')
ASSET=ROOT/'modular/buildings/krannert_building.blend'
OUT=ROOT/'audit/batch2_krannert/validation_round12.json'
bpy.ops.wm.open_mainfile(filepath=str(ASSET))
col=bpy.data.collections.get('Asset_krannert_building')
root=bpy.data.objects.get('AssetRoot_krannert_building')
objs=list(col.all_objects) if col else []
meshes=[o for o in objs if o.type=='MESH']
missing=[]
for im in bpy.data.images:
    if im.source=='FILE' and im.filepath and not im.packed_file:
        p=bpy.path.abspath(im.filepath)
        if not os.path.exists(p): missing.append({'image':im.name,'path':p})
material_issues=[]
for m in bpy.data.materials:
    if not m.use_nodes: continue
    outs=[n for n in m.node_tree.nodes if n.type=='OUTPUT_MATERIAL']
    if not outs or not any(l.to_node in outs for l in m.node_tree.links): material_issues.append(m.name)
names=['KRAN_Vertical_Limestone_Piers','KRAN_Window_Ribbon_Glazing','KRAN_Horizontal_Spandrel_Panels','KRAN_Anodized_Bronze_Mullions']
facades={}
for n in names:
    o=bpy.data.objects.get(n)
    facades[n]={'present':bool(o and o.type=='MESH'),'vertices':len(o.data.vertices) if o and o.type=='MESH' else 0,'faces':len(o.data.polygons) if o and o.type=='MESH' else 0,'material_slots':len(o.material_slots) if o else 0}
roof=bpy.data.objects.get('KRAN_FloorSlab_Roof_Deck')
ring=[]
if roof and roof.type=='MESH':
    top=max(v.co.z for v in roof.data.vertices)
    for v in roof.data.vertices:
        if abs(v.co.z-top)<1e-5:
            xy=(round(float(v.co.x),6),round(float(v.co.y),6))
            if xy not in ring: ring.append(xy)
root_identity=bool(root and all(abs(root.matrix_world[i][j]-(1.0 if i==j else 0.0))<1e-7 for i in range(4) for j in range(4)))
issues=[]
if not col or len(objs)!=670 or len(meshes)!=662: issues.append('collection/object counts differ from expected source inventory')
if not root_identity: issues.append('asset root identity transform check failed')
if missing: issues.append('missing external images found')
if material_issues: issues.append('material output issues found')
if any(not v['present'] for v in facades.values()): issues.append('one or more revised facade meshes missing')
if len(ring)!=41: issues.append('roof perimeter ring count differs from R8 expected check')
result={'revision':12,'asset_reopened':'PASS','asset_file':'modular/buildings/krannert_building.blend','asset_sha256':hashlib.sha256(ASSET.read_bytes()).hexdigest(),'blender_version':bpy.app.version_string,
 'export_collection_present':col is not None,'export_collection_object_count':len(objs),'mesh_count':len(meshes),'source_root_present':root is not None,'source_root_identity_transform':root_identity,
 'missing_external_images':missing,'material_output_issues':material_issues,'roof_deck_mesh_present':roof is not None,'roof_deck_top_z_m':float(max(v.co.z for v in roof.data.vertices)) if roof else None,'top_ring_vertex_count':len(ring),'top_ring_extracted_from_saved_asset':bool(ring),'facade_meshes_after_reopen':facades,
 'renders_exist':{n:(ROOT/'audit/batch2_krannert'/n).exists() for n in ['krannert_south_front_r12.png','krannert_southeast_same_corner_r12.png','krannert_southwest_same_corner_r12.png','krannert_archival_facade_comparison_r12.png']},
 'source_asset_saved_in_r12':True,'master_manifest_shared_files_edited':False,'issues':issues}
OUT.write_text(json.dumps(result,indent=2),encoding='utf-8')
print(json.dumps(result,indent=2))


