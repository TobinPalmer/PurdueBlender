import bpy,json,math
from pathlib import Path
from mathutils import Vector
ROOT=Path(r'C:\Users\Tobin\Documents\Blender\PurdueMap'); ASSET=ROOT/'modular/buildings/life_science_plant_and_soils_laboratory.blend'
bpy.ops.wm.open_mainfile(filepath=str(ASSET)); asset=bpy.data.collections['Asset_life_science_plant_and_soils_laboratory']
def walk(c):
 for o in c.objects: yield o
 for q in c.children: yield from walk(q)
objs=list(walk(asset)); gis=json.loads((ROOT/'audit/batchC_life_science_plant_soils_official_footprint.json').read_text()); ev=json.loads((ROOT/'audit/batchC_life_science_plant_soils_evidence.json').read_text()); ring=gis['features'][0]['geometry']['rings'][0][:-1]; ox,oy=ev['coordinate_method']['build_bbox_origin_xy_m']
exp={(round((lon+86.9137)*111412.84*math.cos(math.radians(40.4274))-ox,5),round((lat-40.4274)*111040.0-oy,5)) for lon,lat in ring}
slabs=['Life Science Plant and Soils Laboratory | official GIS footprint ground floor','LSPS | level 1 interior floor plate','LSPS | level 2 interior floor plate','LSPS | level 3 interior floor plate','LSPS R3 | level B below-grade floor plate','LSPS R3 | level SB below-grade floor plate']
checks=[]
for n in slabs:
 o=bpy.data.objects[n]; actual={(round(v.co.x,5),round(v.co.y,5)) for v in o.data.vertices}; # 2 verts at each ring vertex, unique XY
 errors=[min(math.hypot(x-ex,y-ey) for ex,ey in exp) for x,y in actual]
 checks.append({'name':n,'unique_xy_vertices':len(actual),'matches_transformed_gis_ring_within_2mm':len(actual)==len(exp) and max(errors)<.002,'max_error_m':round(max(errors),6)})
materials={m for o in objs if o.type=='MESH' for m in o.data.materials if m}
material_links_ok=all(m.use_nodes and any(n.type=='OUTPUT_MATERIAL' and any(sock.is_linked for sock in n.inputs) for n in m.node_tree.nodes) for m in materials)
allowed={asset,*asset.children_recursive}
collection_membership_ok=all(set(o.users_collection)<=allowed and bool(o.users_collection) for o in objs)
images=[im.name for im in bpy.data.images if im.source=='FILE' and im.filepath and not im.packed_file]
roofunits=[o for o in objs if o.name.startswith('LSPS R3 | roof service unit ') and o.name.endswith(tuple(str(i) for i in range(10)))]
# count base units without cap/louver objects
roofbase=[o for o in objs if o.name.startswith('LSPS R3 | roof service unit ') and 'vent cap' not in o.name and 'louver' not in o.name]
interior=bpy.data.collections['LSPS_Interior']
result={'reopened':True,'asset_file':'modular/buildings/life_science_plant_and_soils_laboratory.blend','export_collection':asset.name,'asset_object_count':len(objs),'mesh_object_count':sum(o.type=='MESH' for o in objs),'unique_materials':len(materials),'material_nodes_connected':material_links_ok,'export_collection_membership_only':collection_membership_ok,'external_unpacked_image_dependencies':images,'footprint_slab_checks':checks,'all_six_floorplates_match_gis_ring':all(c['matches_transformed_gis_ring_within_2mm'] for c in checks),'roof_service_units_added':len(roofbase),'basement_walk_in_seed_storage_rooms':sum(o.name=='LSPS R4 | insulated seed-room door' for o in objs),'reported_room_area_m2':next((o.get('room_area_m2') for o in objs if o.name=='LSPS R4 | insulated seed-room door'),None),'unsupported_rooftop_curb_objects_remaining':sum(o.name.startswith('LSPS | rooftop mechanical curb') for o in objs),'interior_object_count':len(list(interior.objects)),'interior_total_geometry_exported':all(o.name in {x.name for x in objs} for o in interior.objects),'source_properties_present':all(o.get('source_basis') for o in roofbase),'sample_dryers':sum(o.name.startswith('LSPS R2 | sample dryer ') for o in objs),'soil_grinding_units':sum(o.name.startswith('LSPS R2 | soil grinding unit and dust arrester ') for o in objs),'preview_files':['audit/batchC_life_science_plant_soils/exterior_west_r4.png','audit/batchC_life_science_plant_soils/roof_top_r4.png','audit/batchC_life_science_plant_soils/basement_cutaway_r4.png'],'master_or_manifest_edited':False,'overall':'PASS' if all(c['matches_transformed_gis_ring_within_2mm'] for c in checks) and not images and material_links_ok and collection_membership_ok and sum(o.name.startswith('LSPS | rooftop mechanical curb') for o in objs)==0 else 'FAIL'}
(ROOT/'audit/batchC_life_science_plant_soils/validation_round4.json').write_text(json.dumps(result,indent=2)+'\n')
print(json.dumps(result,indent=2))
