import bpy,bmesh,json,os
from mathutils import Vector
f=bpy.data.filepath;s=bpy.context.scene;asset=bpy.data.collections.get('Asset_knoy_hall');root=bpy.data.objects.get('AssetRoot_knoy_hall');sub=bpy.data.collections.get('KNOY_UpperLevel_TypicalPartitions_L2-L4')
def ident(o):return bool(o and all(abs(o.matrix_world[i][j]-(1.0 if i==j else 0.0))<1e-6 for i in range(4) for j in range(4)))
def bounds(o):
 p=[o.matrix_world@Vector(c) for c in o.bound_box]
 return [[round(min(v[i] for v in p),4),round(max(v[i] for v in p),4)] for i in range(3)]
levels=['L2','L3','L4'];objects=[]
for lvl in levels:
 o=bpy.data.objects.get(f'KNOY_{lvl}_TypicalPlan_InteriorPartitions')
 if not o:objects.append({'level':lvl,'present':False});continue
 bm=bmesh.new();bm.from_mesh(o.data)
 nonmanifold=sum(1 for e in bm.edges if not e.is_manifold)
 bm.free()
 badmat=not bool(o.data.materials) or any(p.material_index>=len(o.data.materials) for p in o.data.polygons)
 objects.append({'level':lvl,'present':True,'name':o.name,'bounds_local_xyz_m':bounds(o),'vertices':len(o.data.vertices),'faces':len(o.data.polygons),'trace_segments':o.get('trace_segment_count'),'material_count':len(o.data.materials),'bad_material_indices':badmat,'nonmanifold_edges':nonmanifold,'location':list(o.location),'scale':list(o.scale),'source_url':o.get('source_url'),'partition_height_status':o.get('partition_height_status')})
expected_asset_ids=['Asset_knoy_hall'];collection_hierarchy_pass=bool(asset and sub and sub.name in [c.name for c in asset.children])
stairs=bpy.data.collections.get('KNOY_TypicalPlan_StairRuns_L2-L4')
stair_objs=list(stairs.objects) if stairs else []
report={'reopen':'PASS','blend_file':f,'asset_collection_present':asset is not None,'asset_direct_object_count':len(asset.objects) if asset else None,'asset_hierarchy_total_objects':len(asset.all_objects) if asset else None,'upper_plan_collection_nested_in_asset':collection_hierarchy_pass,'upper_plan_objects':objects,'stair_collection_present':stairs is not None,'illustrative_stair_run_count':len(stair_objs),'root_identity':ident(root),'root_matrix_world':[list(row) for row in root.matrix_world] if root else None,'original_shell_bounds_xyz_m':bounds(bpy.data.objects.get('KNOY_Exterior_Masonry_Walls')),'gis_plan_footprint_bounds_xy_m':[[-22.462,22.463],[-46.581,46.581]],'expected_export_collection':'Asset_knoy_hall','source_plan_sheet':s.get('evidence_primary_plan_sheet'),'upper_plan_source':s.get('evidence_primary_plan_url'),'typical_plan_trace_count_per_level':s.get('typical_upper_plan_trace_count_per_level'),'l5_status':bpy.data.objects.get('KNOY_FloorSlab_L5').get('story_status'),'slab_bounds_z_m':{n:bounds(bpy.data.objects[n])[2] for n in ['KNOY_FloorSlab_L1_Ground','KNOY_FloorSlab_L2','KNOY_FloorSlab_L3','KNOY_FloorSlab_L4','KNOY_FloorSlab_L5','KNOY_FloorSlab_RoofDeck']},'geometry_changed_since_prior_report':['Added 3 source-traced typical-level interior partition meshes and 6 illustrative stair runs for the L2-L3/L3-L4 intervals. Preserved exterior shell bounds, root placement, and explicit unverified L5 status.']}
report['validation_pass']=bool(report['reopen']=='PASS' and report['asset_collection_present'] and collection_hierarchy_pass and report['root_identity'] and len(stair_objs)==6 and all(o.get('present') and not o.get('bad_material_indices') and o.get('nonmanifold_edges')==0 and o.get('trace_segments')==report['typical_plan_trace_count_per_level'] for o in objects))
out=r'C:\Users\Tobin\Documents\Blender\PurdueMap\audit\complete_knoy\knoy_upper_plan_reopen_validation.json'
with open(out,'w',encoding='utf-8') as w:json.dump(report,w,indent=2)
print(json.dumps(report,indent=2))
