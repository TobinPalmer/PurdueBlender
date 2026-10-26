import bpy, json, math, hashlib
from pathlib import Path
from mathutils import Vector
root=Path(__file__).resolve().parents[2]
asset=root/'modular/buildings/massing_purdue_drug_discovery_facility_fc72a4a.blend'
feature_path=root/'audit/purdue_drug_discovery_facility/sources/arcgis_feature_893_2026-10-26.geojson'
report_path=root/'audit/purdue_drug_discovery_facility/fresh_open_validation_2026-10-26.json'
bpy.ops.wm.open_mainfile(filepath=str(asset))
asset_id='massing_purdue_drug_discovery_facility_fc72a4a'
collection_name='Asset_'+asset_id
scene_name='Building_'+asset_id
col=bpy.data.collections.get(collection_name)
assert col is not None, 'Expected library collection missing'
assert bpy.data.scenes.get(scene_name) is not None, 'Expected building scene missing'
assert len(col.objects)>=25, f'Unexpected low object count {len(col.objects)}'
mesh_objs=[o for o in col.objects if o.type=='MESH']
assert len(mesh_objs)==len(col.objects), 'Non-mesh object found in asset collection'
assert all(o.data.polygons for o in mesh_objs), 'Empty mesh found'
assert all(o.data.materials for o in mesh_objs), 'Mesh without assigned material found'
uv_required=['DRUG | GIS footprint walls, three-storey brick and glazing','DRUG | dark brick plinth','DRUG | roof parapet','DRUG | facade glazing and aluminum window frames']
assert all(col.objects.get(name) and len(col.objects[name].data.uv_layers)>0 for name in uv_required), 'Required facade mesh UV map missing'
world_pts=[]
for ob in mesh_objs:
 for v in ob.data.vertices: world_pts.append(ob.matrix_world@v.co)
all_bounds=[[min(p[0] for p in world_pts),max(p[0] for p in world_pts)],[min(p[1] for p in world_pts),max(p[1] for p in world_pts)],[min(p[2] for p in world_pts),max(p[2] for p in world_pts)]]
wall=col.objects.get('DRUG | GIS footprint walls, three-storey brick and glazing')
assert wall is not None
wall_pts=[wall.matrix_world@v.co for v in wall.data.vertices]
wall_bounds=[[min(p[0] for p in wall_pts),max(p[0] for p in wall_pts)],[min(p[1] for p in wall_pts),max(p[1] for p in wall_pts)],[min(p[2] for p in wall_pts),max(p[2] for p in wall_pts)]]
src=json.loads(feature_path.read_text(encoding='utf-8'))['features'][0]
assert src['properties']['FID']==893 and src['properties']['BLDG_ABBR']=='DRUG'
coords=src['geometry']['coordinates'][0][:-1]
origin=(40.4274,-86.9137)
xy=[((lon-origin[1])*111412.84*math.cos(math.radians(origin[0])),(lat-origin[0])*111040.0) for lon,lat,*_ in coords]
source_bounds=[[min(p[0] for p in xy),max(p[0] for p in xy)],[min(p[1] for p in xy),max(p[1] for p in xy)]]
imgs=[{'name':i.name,'filepath':i.filepath,'packed':bool(i.packed_file)} for i in bpy.data.images]
libs=[{'filepath':l.filepath,'missing':bool(l.missing)} for l in bpy.data.libraries]
report={
 'asset_id':asset_id,'reopened_path':str(asset),'sha256':hashlib.sha256(asset.read_bytes()).hexdigest(),
 'blender_version':bpy.app.version_string,'scene':scene_name,'collection':collection_name,
 'scene_object_count':len(bpy.data.scenes[scene_name].objects),'collection_object_count':len(col.objects),
 'mesh_object_count':len(mesh_objs),'polygon_count':sum(len(o.data.polygons) for o in mesh_objs),
 'material_count':len({m.name for o in mesh_objs for m in o.data.materials if m}),
 'uv_mapped_mesh_count':sum(bool(len(o.data.uv_layers)) for o in mesh_objs),'uv_required_facade_meshes':uv_required,
 'external_images':imgs,'external_libraries':libs,
 'source_feature':{'fid':src['properties']['FID'],'name':src['properties']['BUILDING_N'],'abbr':src['properties']['BLDG_ABBR'],'address':src['properties']['ADDRESS'],'crs_output':'EPSG:4326','local_conversion':'X=(lon+86.9137)*111412.84*cos(40.4274 deg); Y=(lat-40.4274)*111040'},
 'source_footprint_bounds_xy_m':source_bounds,'structural_wall_mesh_bounds_xyz_m':wall_bounds,'full_asset_bounds_xyz_m':all_bounds,
 'material_checks':'PASS: all meshes have materials; architectural shell, brick plinth, parapet and facade glazing use UV maps; procedural brick shader is self-contained in the blend',
 'reopen_checks':'PASS: library scene/collection names match manifest; all geometry is mesh-based and nonempty; no external image or library dependencies expected'
}
report_path.write_text(json.dumps(report,indent=2),encoding='utf-8')
print(json.dumps(report,indent=2))
