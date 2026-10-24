import bpy,json,hashlib
from pathlib import Path
ROOT=Path(r'C:\Users\Tobin\Documents\Blender\PurdueMap');BLEND=ROOT/'modular/buildings/knoy_hall.blend'
bpy.ops.wm.open_mainfile(filepath=str(BLEND))
asset=bpy.data.collections['Asset_knoy_hall'];direct=list(asset.objects);desc=list(asset.all_objects);children={c.name:c for c in asset.children}
expected_counts={'KNOY_UpperLevel_TypicalPartitions_L2-L4':3,'KNOY_TypicalPlan_StairRuns_L2-L4':6,'KNOY_TypicalPlan_Doors_L2-L4':45,'KNOY_TypicalPlan_WashroomFixtures_L2-L4':39}
assert len(direct)==64 and len(desc)==157
assert {k:len(children[k].objects) for k in expected_counts}==expected_counts
fixture=children['KNOY_TypicalPlan_WashroomFixtures_L2-L4']
for lv in ('L2','L3','L4'):
    items=[o for o in fixture.objects if o.name.startswith(f'KNOY_{lv}_')]
    assert len(items)==13 and sum(o.get('interpreted_fixture_type')=='toilet' for o in items)==6 and sum(o.get('interpreted_fixture_type')=='basin' for o in items)==7
stairs=children['KNOY_TypicalPlan_StairRuns_L2-L4']
assert all('illustrative' in o.get('geometry_status','').lower() for o in stairs.objects)
assert all(o.get('levels_connected') in ('L2 to L3','L3 to L4') for o in stairs.objects)
door=children['KNOY_TypicalPlan_Doors_L2-L4'];assert {o.get('source_level') for o in door.objects}=={'L2','L3','L4'}
h=hashlib.sha256();n=0
for o in sorted(direct,key=lambda x:x.name):
    if o.type!='MESH' or o.name=='KNOY_Entrance_Sign_Lettering':continue
    n+=1;h.update(o.name.encode())
    for row in o.matrix_world:h.update(','.join(f'{v:.8f}' for v in row).encode())
    for v in o.data.vertices:h.update(','.join(f'{c:.8f}' for c in v.co).encode())
    for p in o.data.polygons:h.update(','.join(str(i) for i in p.vertices).encode())
expected='c51a34c4704891f3442b17f7df0d9edc3741fc1cee7416041858dbeed39c9ed1'
assert n==62 and h.hexdigest()==expected,(n,h.hexdigest())
brick=bpy.data.materials['KNOY_Purdue_Red_Brick'];glass=bpy.data.materials['KNOY_Dark_Tinted_Glass']
assert brick.use_nodes and glass.use_nodes
images=[i.filepath for i in bpy.data.images if i.source=='FILE' and i.filepath]
report={'reopened_saved_asset':'PASS','asset':str(BLEND),'direct_objects':len(direct),'descendant_objects':len(desc),'nested_counts':expected_counts,'fixtures_by_floor':{'L2':'7 basin-like + 6 toilet-like','L3':'7 basin-like + 6 toilet-like','L4':'7 basin-like + 6 toilet-like'},'stair_runs':len(stairs.objects),'doors':len(door.objects),'brick_material_nodes_present':True,'dark_glazing_material_nodes_present':True,'external_image_dependencies':images,'preexisting_shell_mesh_count':n,'preexisting_shell_mesh_sha256':h.hexdigest(),'preexisting_shell_mesh_geometry_changed':False,'roof_L5_penthouse_PV_or_placement_geometry_changed':False,'L5_status':'Unverified/source-conflicted; preserved.','result':'PASS'}
(ROOT/'audit/complete_knoy/validation_round13.json').write_text(json.dumps(report,indent=2)+'\n',encoding='utf-8');print(json.dumps(report,indent=2))
