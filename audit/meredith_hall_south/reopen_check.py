"""Fresh-open QA for Meredith South's source-derived campus massing asset."""
import json, math
from pathlib import Path
import bpy

ROOT=Path(__file__).resolve().parents[2]
ASSET_ID='massing_meredith_hall_south_ffbc444'
COLLECTION=f'Asset_{ASSET_ID}'
GIS=json.loads((ROOT/'audit'/'official_purdue_buildings_wgs84.json').read_text(encoding='utf-8'))
feature=next(f for f in GIS['features'] if int(f['attributes']['FID'])==410)
assert feature['attributes']['BUILDING_N']=='Virginia C. Meredith Residence Hall South'
ring=feature['geometry']['rings'][0]
xy=[((lon+86.9137)*111412.84*math.cos(math.radians(40.4274)),
     (lat-40.4274)*111040.0) for lon,lat in ring]
source_bounds=[[min(p[i] for p in xy),max(p[i] for p in xy)] for i in range(2)]
col=bpy.data.collections.get(COLLECTION)
assert col is not None
base=bpy.data.objects.get('MRDS_Exterior_Base_B_C_and_A_Floors_1_to_6')
west=bpy.data.objects.get('MRDS_West_A_Section_Floors_7_to_8')
assert base and west
base_xy=[tuple(v.co)[:2] for v in base.data.vertices]
shell_bounds=[[min(p[i] for p in base_xy),max(p[i] for p in base_xy)] for i in range(2)]
max_bound_delta=max(abs(source_bounds[a][b]-shell_bounds[a][b]) for a in range(2) for b in range(2))
assert max_bound_delta<0.3,max_bound_delta
assert len([o for o in col.objects if o.name.startswith('MRDS_Interior_Floor_Plate_L')])==8
for stem in ('MRDS_Interior_Corridor_Floor_L','MRDS_Interior_Room_Partitions_L',
             'MRDS_Interior_Double_Room_Beds_L','MRDS_Interior_Desks_L'):
    assert len([o for o in col.objects if o.name.startswith(stem)])==8,stem
assert not any(o.type=='MESH' and (not o.data.vertices or not o.data.polygons) for o in col.objects)
external_images=[im.filepath for im in bpy.data.images if im.source=='FILE' and im.users]
assert not external_images,external_images

def bounds_world(objects):
    coords=[o.matrix_world@v.co for o in objects if o.type=='MESH' for v in o.data.vertices]
    return [[min(v[i] for v in coords),max(v[i] for v in coords)] for i in range(3)]

asset_bounds=bounds_world(list(col.objects))
exterior_objects=[o for o in col.objects
                  if not (o.name.startswith('MRDS_Interior_')
                          or o.name.startswith('MRDS_Schematic_')
                          or o.name=='MRDS_Basement_B_Maintenance_and_Mechanical')]
exterior_bounds=bounds_world(exterior_objects)
def boundary_count(obj):
    edge_use={}
    for poly in obj.data.polygons:
        for key in poly.edge_keys: edge_use[key]=edge_use.get(key,0)+1
    return {'boundary_edges':sum(n==1 for n in edge_use.values()),
            'nonmanifold_edges':sum(n!=2 for n in edge_use.values())}

closed_meshes={o.name:boundary_count(o) for o in col.objects if o.type=='MESH'
               and o.name in ('MRDS_Exterior_Base_B_C_and_A_Floors_1_to_6',
                              'MRDS_West_A_Section_Floors_7_to_8',
                              'MRDS_Roof_B_C','MRDS_Roof_West_A',
                              'MRDS_Basement_B_Maintenance_and_Mechanical')}
assert all(v['nonmanifold_edges']==0 for v in closed_meshes.values()),closed_meshes

result={
 'building':'Virginia C. Meredith Residence Hall South','asset_id':ASSET_ID,
 'asset':f'modular/buildings/{ASSET_ID}.blend','blender_version':bpy.app.version_string,
 'source_feature_id':410,'source_name':feature['attributes']['BUILDING_N'],
 'source_provider':'Purdue University BuildingShapes ArcGIS FeatureServer; local project snapshot audit/official_purdue_buildings_wgs84.json',
 'source_crs':'Feature service is Web Mercator (WKID 102100/3857); local snapshot is EPSG:4326.',
 'retrieval_date':'2026-10-22 source snapshot; newer live-feature geometry may differ.',
 'transform':'X=(longitude + 86.9137) * 111412.84 * cos(radians(40.4274)); Y=(latitude - 40.4274) * 111040; project local approximation, not surveyed control.',
 'measurement_method':'Official polygon transformed into campus coordinates; iterative collinear simplification at 0.2 m maximum point-to-segment tolerance; structural base shell retains the simplified source ring.',
 'source_ring_vertex_count':len(ring)-1,'model_structural_vertex_count':len(base_xy),
 'source_bounds_xy_m':source_bounds,'shell_bounds_xy_m':shell_bounds,
 'max_axis_bounds_delta_m':max_bound_delta,'asset_bounds_xyz_m':asset_bounds,
 'exterior_bounds_xyz_m':exterior_bounds,
 'structural_closed_mesh_check':closed_meshes,
 'collection':COLLECTION,'collection_object_count':len(col.objects),
 'named_objects':[o.name for o in col.objects],'external_image_paths':external_images,
 'height':'Current Purdue Emergency Plan lists west A as 8 floors and middle B/east C as 6 floors. Modeled floor-to-floor height is an estimate of 3.3 m; B/C roof 19.8 m, west-A roof 26.4 m. The 3.3 m height is not a surveyed elevation.',
 'materials':'Procedural red-brown brick, reflective blue-gray glazing, pale metal/stone bay frames, dark bronze window frames, gray roof and concrete mechanical screens.',
 'interior':'Schematic central corridor, double-room modules, beds, desks and floor plates on levels 1–8; typical room width/length follows Purdue Residences published illustration (11 ft 4 in × 16 ft 4 in), but building-wide room arrangement and exact interior dimensions remain estimates, not a measured floor plan.',
 'master_integration':'Fresh-opened and integrated into purdue_campus_master.blend; see modular/verification.json for current master result.',
 'independent_grade':'Pending new independent review of current asset hash.'
}
out=ROOT/'audit'/'meredith_hall_south'/'reopen_check.json'
out.write_text(json.dumps(result,indent=2),encoding='utf-8')
print(json.dumps(result,indent=2))
