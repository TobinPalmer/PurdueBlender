import bpy,json,bmesh
from pathlib import Path
P=Path(r'C:/Users/Tobin/Documents/Blender/PurdueMap/modular/buildings/potter_engineering.blend');D=Path(r'C:/Users/Tobin/Documents/Blender/PurdueMap/audit/batch4_potter')
bpy.ops.wm.open_mainfile(filepath=str(P))
# Remove scene-only cameras, lights, grade and camera walls used for evidence renders.
remove_prefixes=('POTR_Evidence_','POTR_Exterior_Evidence_','POTR_Lab_Evidence_','POTR_Facade_Detail_','POTR_Facade_Fill','POTR_Temporary_Lab')
for o in list(bpy.data.objects):
 if o.name.startswith(remove_prefixes): bpy.data.objects.remove(o,do_unlink=True)
# Save clean standalone with active default selection at the origin and no missing external images.
col=bpy.data.collections['Asset_potter_engineering'];bpy.ops.wm.save_as_mainfile(filepath=str(P));bpy.ops.wm.open_mainfile(filepath=str(P));col=bpy.data.collections['Asset_potter_engineering'];dg=bpy.context.evaluated_depsgraph_get()
checks={'reopened':True,'file':str(P),'export_collection':col.name,'object_count':len(col.all_objects),'root_origin':list(col.objects['AssetRoot_potter_engineering'].location),'structural_shell_bounds':[round(v,4) for v in col.objects['POTR_Official_864_Structural_Envelope'].dimensions],'roof_bounds':[round(v,4) for v in col.objects['POTR_Official_864_Roof'].dimensions],'window_openings':len([o for o in col.objects if o.name.startswith('POTR_RealOpening_Glazing')]),'joined_window_frame_faces':len(col.objects['POTR_All_Window_Frames_Batch4'].data.polygons),'lab205_detail_objects':len([o for o in col.all_objects if o.name.startswith('POTR_R205_')]),'missing_external_images':[im.filepath for im in bpy.data.images if im.source=='FILE' and not im.packed_file],'scene_only_evidence_objects_remaining':[o.name for o in bpy.data.objects if o.name.startswith(remove_prefixes)],'geometry':[]}
for name in ['POTR_Official_864_Structural_Envelope','POTR_Full_Basement_Walls','POTR_Historic2016_Plan51_MergedPartitions','POTR_Historic2016_Plan53_MergedPartitions','POTR_Historic2016_Plan54_MergedPartitions','POTR_Historic2016_Plan55_MergedPartitions']:
 o=col.objects.get(name)
 if not o: continue
 eo=o.evaluated_get(dg);me=eo.to_mesh();bm=bmesh.new();bm.from_mesh(me);checks['geometry'].append({'name':name,'faces':len(bm.faces),'nonmanifold_edges':sum(not e.is_manifold for e in bm.edges)});bm.free();eo.to_mesh_clear()
(D/'reopen_checks.json').write_text(json.dumps(checks,indent=2));print(json.dumps(checks,indent=2))
