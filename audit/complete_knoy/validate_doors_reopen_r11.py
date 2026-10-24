import bpy,json,hashlib
from pathlib import Path
ROOT=Path(r'C:\Users\Tobin\Documents\Blender\PurdueMap');BLEND=ROOT/'modular/buildings/knoy_hall.blend'
bpy.ops.wm.open_mainfile(filepath=str(BLEND))
asset=bpy.data.collections['Asset_knoy_hall'];allobj=list(asset.all_objects)
asset_direct=list(asset.objects);children={c.name:c for c in asset.children}
door_coll=children['KNOY_TypicalPlan_Doors_L2-L4']
assert len(door_coll.objects)==45
assert len(allobj)==118
src=json.loads((ROOT/'audit/complete_knoy/typical_plan_door_candidates_r11.json').read_text(encoding='utf-8'))
by={(o.get('source_level'),int(o.get('source_pixel_center')[0]),int(o.get('source_pixel_center')[1])) for o in door_coll.objects}
assert len(by)==45
assert all(o.type=='MESH' and o.parent is None for o in door_coll.objects)
assert {o.get('source_level') for o in door_coll.objects}=={'L2','L3','L4'}
assert all('source typical plan' in o.get('door_position_status','') for o in door_coll.objects)
# Hash all existing direct asset meshes, excluding the R10/R11 sign and new doors.
h=hashlib.sha256();n=0
for o in sorted(asset_direct,key=lambda x:x.name):
 if o.type!='MESH' or o.name=='KNOY_Entrance_Sign_Lettering' or o.name.startswith('KNOY_L2_TypicalPlan_Door_'):continue
 n+=1;h.update(o.name.encode())
 for row in o.matrix_world:h.update(','.join(f'{v:.8f}' for v in row).encode())
 for v in o.data.vertices:h.update(','.join(f'{c:.8f}' for c in v.co).encode())
 for p in o.data.polygons:h.update(','.join(str(i) for i in p.vertices).encode())
expected='c51a34c4704891f3442b17f7df0d9edc3741fc1cee7416041858dbeed39c9ed1'
assert n==62 and h.hexdigest()==expected,(n,h.hexdigest())
sign=bpy.data.objects['KNOY_Entrance_Sign_Lettering'];wall=bpy.data.objects['KNOY_Exterior_Masonry_Walls']
assert sign.matrix_parent_inverse==wall.matrix_parent_inverse
assert all(abs(v-.8)<1e-5 for v in sign.scale)
pts=[sign.matrix_world@v.co for v in sign.data.vertices]
bounds=[[min(p[i] for p in pts),max(p[i] for p in pts)] for i in range(3)]
center=[(a+b)/2 for a,b in bounds]
assert abs(center[0]-.77)<.2 and abs(center[1]+46.34)<.2 and abs(center[2]-4.02)<.3
# Collection export is hierarchical: verify nested collections and every descendant object.
assert set(children)=={'KNOY_UpperLevel_TypicalPartitions_L2-L4','KNOY_TypicalPlan_StairRuns_L2-L4','KNOY_TypicalPlan_Doors_L2-L4'}
assert len(children['KNOY_UpperLevel_TypicalPartitions_L2-L4'].objects)==3
assert len(children['KNOY_TypicalPlan_StairRuns_L2-L4'].objects)==6
report={'reopened_asset':'PASS','blend_path':str(BLEND),'direct_asset_objects':len(asset_direct),'asset_descendant_objects':len(allobj),'nested_collections':{name:len(c.objects) for name,c in children.items()},'door_panels':len(door_coll.objects),'door_positions':15,'door_levels':['L2','L3','L4'],'door_source_plan':'2018 Purdue Gateway study, PDF page 24, Typical Plan Levels 2-4','door_panel_dimensions':'Plan-derived opening width 0.82–1.07 m; panel height 2.10 m and thickness 0.045 m estimated, not dimensioned by source. Closed leaves only; swing direction/finish not asserted.','sign_world_bounds_m':bounds,'sign_world_center_m':center,'sign_scale_factor_vs_r10':0.8,'sign_parent_inverse_matches_shell':True,'preexisting_direct_mesh_count':n,'preexisting_direct_geometry_sha256':h.hexdigest(),'preexisting_geometry_changed':False,'roof_l5_pv_or_gis_registration_geometry_changed':False,'validation_passed':True}
(ROOT/'audit/complete_knoy/door_model_validation_r11.json').write_text(json.dumps(report,indent=2),encoding='utf-8')
print(json.dumps(report,indent=2))
