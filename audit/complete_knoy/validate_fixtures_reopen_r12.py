import bpy, json, hashlib
from pathlib import Path

ROOT=Path(r'C:\Users\Tobin\Documents\Blender\PurdueMap')
BLEND=ROOT/'modular/buildings/knoy_hall.blend'
bpy.ops.wm.open_mainfile(filepath=str(BLEND))
asset=bpy.data.collections['Asset_knoy_hall']
direct=list(asset.objects); descendants=list(asset.all_objects)
children={c.name:c for c in asset.children}
fixture=children['KNOY_TypicalPlan_WashroomFixtures_L2-L4']
doors=children['KNOY_TypicalPlan_Doors_L2-L4']
assert len(direct)==64 and len(descendants)==157,(len(direct),len(descendants))
assert len(children['KNOY_UpperLevel_TypicalPartitions_L2-L4'].objects)==3
assert len(children['KNOY_TypicalPlan_StairRuns_L2-L4'].objects)==6
assert len(doors.objects)==45 and len(fixture.objects)==39
floors={}
for floor in ('L2','L3','L4'):
    obs=[o for o in fixture.objects if o.name.startswith(f'KNOY_{floor}_PlanFixture_')]
    assert len(obs)==13,(floor,len(obs))
    wc=sum(o.get('interpreted_fixture_type')=='toilet' for o in obs)
    basin=sum(o.get('interpreted_fixture_type')=='basin' for o in obs)
    assert (wc,basin)==(6,7),(floor,wc,basin)
    floors[floor]={'objects':len(obs),'interpreted_toilet_symbols':wc,'interpreted_basin_symbols':basin}
for o in fixture.objects:
    assert o.type=='MESH'
    assert o.get('source_url','').startswith('https://engineering.purdue.edu/')
    assert o.get('source_plan_page')==24
    assert 'simplified 3d stand-in' in o.get('geometry_status','').lower()
    assert len(o.get('source_feature_pixel_center',[]))==2
# Hash the original direct shell meshes, excluding the sign whose scale changed in R11.
h=hashlib.sha256();n=0
for o in sorted(direct,key=lambda x:x.name):
    if o.type!='MESH' or o.name=='KNOY_Entrance_Sign_Lettering':continue
    n+=1;h.update(o.name.encode())
    for row in o.matrix_world:h.update(','.join(f'{v:.8f}' for v in row).encode())
    for v in o.data.vertices:h.update(','.join(f'{c:.8f}' for c in v.co).encode())
    for p in o.data.polygons:h.update(','.join(str(i) for i in p.vertices).encode())
expected='c51a34c4704891f3442b17f7df0d9edc3741fc1cee7416041858dbeed39c9ed1'
assert n==62 and h.hexdigest()==expected,(n,h.hexdigest())
report={
 'reopened_asset':'PASS','blend_path':str(BLEND),'direct_asset_objects':len(direct),
 'asset_descendant_objects':len(descendants),
 'nested_collection_counts':{k:len(v.objects) for k,v in children.items()},
 'fixture_objects':len(fixture.objects),'fixture_counts_by_level':floors,
 'fixture_interpretation':'Source plan visual interpretation only; no fixture legend. Dimensions and finish are estimated render placeholders.',
 'source_plan':'Purdue Engineering and Polytechnic Gateway Formation Study, 2018-05-31, PDF page 24, Typical Plan Levels 2-4',
 'preexisting_direct_mesh_count':n,'preexisting_direct_geometry_sha256':h.hexdigest(),
 'preexisting_geometry_changed':False,'roof_L5_PV_or_GIS_registration_geometry_changed':False,
 'validation_passed':True}
(ROOT/'audit/complete_knoy/fixture_validation_r12.json').write_text(json.dumps(report,indent=2),encoding='utf-8')
print(json.dumps(report,indent=2))
