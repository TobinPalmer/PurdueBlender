import bpy, json, hashlib
from pathlib import Path
root=Path(__file__).resolve().parents[2]
p=root/'modular/buildings/massing_life_science_ranges_greenhouse_and_service_building_c96231f.blend'
bpy.ops.wm.open_mainfile(filepath=str(p))
scene='Building_massing_life_science_ranges_greenhouse_and_service_building_c96231f'
coll='Asset_massing_life_science_ranges_greenhouse_and_service_building_c96231f'
sc=bpy.data.scenes.get(scene); co=bpy.data.collections.get(coll)
assert sc and co
objs=list(co.objects)
assert len(objs)>=45
assert all(o.type in {'MESH','FONT','CURVE','EMPTY'} for o in objs)
assert len([m for m in bpy.data.materials if m.use_nodes])>=10
for o in objs:
    if o.type=='MESH': assert len(o.data.polygons)>0
assert co.get('official_gis_feature_id')==915
assert co.get('official_gis_building_abbr')=='LSR'
assert co.get('official_gis_extrution_value')==12
assert 'units and semantics are undocumented' in co.get('official_gis_extrution_interpretation','')
assert 'Estimated visual reconstruction' in co.get('height_status','')
# evaluate local bounds from asset collection objects using object world matrices
pts=[]
for o in objs:
    if o.type=='MESH':
        pts.extend([o.matrix_world @ v.co for v in o.data.vertices])
bounds={axis:[min(getattr(v,axis.lower()) for v in pts),max(getattr(v,axis.lower()) for v in pts)] for axis in ('X','Y','Z')}
report={'file':str(p),'scene':sc.name,'collection':co.name,'objects':len(objs),'materials':len(bpy.data.materials),'bounds_m':bounds,'packed_images':sum(bool(i.packed_file) for i in bpy.data.images),'external_unpacked_images':[i.filepath for i in bpy.data.images if i.source=='FILE' and not i.packed_file], 'height_evidence':{'GIS_Extrution':co.get('official_gis_extrution_value'),'interpretation':co.get('official_gis_extrution_interpretation'),'status':co.get('height_status'),'estimated_eave_m':co.get('estimated_greenhouse_eave_height_m'),'estimated_ridge_m':co.get('estimated_greenhouse_ridge_height_m'),'estimated_service_height_m':co.get('estimated_service_wing_height_m')}, 'status':'PASS'}
out=root/'audit/life_science_ranges_greenhouse_and_service_building_c96231f/fresh_open_validation.json'
out.write_text(json.dumps(report,indent=2),encoding='utf-8')
print(json.dumps(report))
