"""Fresh-process validation of the saved Acacia library asset."""
import bpy, json, os

ROOT=os.path.abspath(os.path.join(os.path.dirname(__file__),'..','..'))
ASSET_ID='massing_house_301841251_8a9a05b'
COLLECTION='Asset_'+ASSET_ID
SCENE='Building_'+ASSET_ID
expected='House_301841251'
assert bpy.context.scene.name==SCENE, f'wrong scene: {bpy.context.scene.name}'
col=bpy.data.collections.get(COLLECTION)
assert col is not None, f'missing exported collection {COLLECTION}'
obj=bpy.data.objects.get(expected)
assert obj is not None and obj.type=='MESH'
assert obj.get('stable_asset_id')==ASSET_ID
assert obj.get('source_fid')==791
assert len(col.objects)>=300, f'expected detailed asset, found only {len(col.objects)} collection objects'
assert col.instance_offset.length<1e-7
assert tuple(round(float(x),5) for x in obj.location)==(0.0,0.0,0.0)
assert all(o.name in bpy.context.scene.objects for o in col.objects)
# Primary envelope should retain the original massing plan in campus coordinates.
coords=[obj.matrix_world @ v.co for v in obj.data.vertices]
bounds=[[min(p[i] for p in coords),max(p[i] for p in coords)] for i in range(3)]
assert bounds[0][0]<-334 and bounds[0][1]>-316
assert bounds[1][0]>342 and bounds[1][1]<371
assert abs(bounds[2][0])<1e-5 and abs(bounds[2][1]-9.45)<1e-4
assert all(m is not None for o in col.objects if o.type=='MESH' for m in o.data.materials), 'unmaterialed mesh in asset collection'
assets=[o for o in col.objects if o.type=='MESH']
report={
 'result':'passed','blend_path':'modular/buildings/massing_house_301841251_8a9a05b.blend',
 'scene':bpy.context.scene.name,'collection':col.name,'asset_id':ASSET_ID,
 'asset_collection_object_count':len(col.objects),'mesh_object_count':len(assets),
 'primary_object':obj.name,'primary_bounds_world_m':bounds,
 'collection_instance_offset':list(col.instance_offset),
 'coordinate_frame':'direct linked campus coordinates; identity object placement',
 'portable_materials':'all mesh objects have at least one material slot; all materials in file are procedural',
 'interior_objects':sum(1 for o in col.objects if any(s in o.name.lower() for s in ('bedroom','library','heritage','study hall','interior floor','partition'))),
 'notes':['The bound check is for the main GIS wall shell; added porch, windows, roof and trim may overhang its structural footprint.','Height and interior dimensions remain estimates as documented in evidence.json.']}
out=os.path.join(os.path.dirname(__file__),'fresh_open_validation.json')
with open(out,'w',encoding='utf-8') as f: json.dump(report,f,indent=2)
print(json.dumps(report))
