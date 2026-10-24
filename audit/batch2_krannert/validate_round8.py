import bpy, hashlib, json, os
from pathlib import Path
ROOT=Path(r'C:/Users/Tobin/Documents/Blender/PurdueMap')
ASSET=ROOT/'modular/buildings/krannert_building.blend'
OUT=ROOT/'audit/batch2_krannert/validation_round8.json'
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
roof=bpy.data.objects.get('KRAN_FloorSlab_Roof_Deck')
ring=[]
if roof and roof.type=='MESH':
    top=max(v.co.z for v in roof.data.vertices)
    seen=set()
    for v in roof.data.vertices:
        if abs(v.co.z-top)<1e-5:
            xy=(round(float(v.co.x),6),round(float(v.co.y),6))
            if xy not in seen: seen.add(xy);ring.append(list(xy))
root_identity=bool(root and all(abs(root.matrix_world[i][j]-(1.0 if i==j else 0.0))<1e-7 for i in range(4) for j in range(4)))
sha=hashlib.sha256(ASSET.read_bytes()).hexdigest()
result={'revision':8,'asset_reopened':'PASS','asset_file':'modular/buildings/krannert_building.blend','asset_sha256':sha,'blender_version':bpy.app.version_string,
 'export_collection_present':col is not None,'export_collection_object_count':len(objs),'mesh_count':len(meshes),
 'source_root_present':root is not None,'source_root_identity_transform':root_identity,
 'missing_external_images':missing,'material_output_issues':material_issues,
 'roof_deck_mesh_present':roof is not None,'roof_deck_top_z_m':float(max(v.co.z for v in roof.data.vertices)) if roof else None,'top_ring_vertex_count':len(ring),'top_ring_extracted_from_saved_asset':bool(ring),'roof_deck_asset_local_xy_m':ring,
 'orthophoto_overlay_exists':(ROOT/'audit/batch2_krannert/krannert_asset_footprint_ortho_overlay_r8.png').exists(),
 'geometry_material_placement_changed':False,'source_asset_saved_in_r8':False,'master_manifest_shared_files_edited':False,
 'issues':[] if col and len(objs)==670 and len(meshes)==662 and root_identity and not missing and not material_issues and len(ring)==41 else ['recheck reopened asset']}
OUT.write_text(json.dumps(result,indent=2),encoding='utf-8');print(json.dumps({k:v for k,v in result.items() if k!='roof_deck_asset_local_xy_m'},indent=2))
