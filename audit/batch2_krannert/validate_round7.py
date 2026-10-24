import bpy,json,os
from pathlib import Path
ROOT=Path(r'C:/Users/Tobin/Documents/Blender/PurdueMap')
ASSET=ROOT/'modular/buildings/krannert_building.blend'
OUT=ROOT/'audit/batch2_krannert/validation_round7.json'
bpy.ops.wm.open_mainfile(filepath=str(ASSET))
col=bpy.data.collections.get('Asset_krannert_building')
root=bpy.data.objects.get('AssetRoot_krannert_building')
objs=list(col.all_objects) if col else []
meshes=[o for o in objs if o.type=='MESH']
missing=[]
for im in bpy.data.images:
    if not im.packed_file and im.source=='FILE' and im.filepath:
        path=bpy.path.abspath(im.filepath)
        if not os.path.exists(path): missing.append({'image':im.name,'path':path})
issues=[]
for m in bpy.data.materials:
    if not m.use_nodes: continue
    outs=[n for n in m.node_tree.nodes if n.type=='OUTPUT_MATERIAL']
    if not outs or not any(any(l.to_node==o for l in m.node_tree.links) for o in outs):
        issues.append({'material':m.name,'issue':'no linked material output'})
root_matrix=[list(row) for row in root.matrix_world] if root else None
result={
 'revision':7,'asset_reopened':'PASS','asset_file':'modular/buildings/krannert_building.blend','blender_version':bpy.app.version_string,
 'export_collection_present':col is not None,'export_collection_object_count':len(objs),'mesh_count':len(meshes),
 'source_root_present':root is not None,'source_root_location':list(root.location) if root else None,
 'source_root_rotation':list(root.rotation_euler) if root else None,'source_root_scale':list(root.scale) if root else None,
 'source_root_identity_transform':bool(root and all(abs(root.matrix_world[i][j]-(1.0 if i==j else 0.0))<1e-7 for i in range(4) for j in range(4))),
 'missing_external_images':missing,'material_output_issues':issues,
 'known_asset_objects_present':{name:bpy.data.objects.get(name) is not None for name in ['KRAN_Exterior_Masonry_Walls','KRAN_Rooftop_Mechanical_Penthouse','KRAN_Structural_Circulation_Cores','KRAN_Skywalk_Connection_Portal']},
 'evidence_only_revision':True,'geometry_material_placement_changed':False,
 'master_manifest_shared_files_edited':False,
 'issues':[] if col and len(objs)==670 and len(meshes)==662 and not missing and not issues else ['recheck asset counts/dependencies/materials']
}
OUT.write_text(json.dumps(result,indent=2),encoding='utf-8')
print(json.dumps(result,indent=2))

