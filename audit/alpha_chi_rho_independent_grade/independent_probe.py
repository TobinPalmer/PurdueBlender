import bpy, json, math
from pathlib import Path

root = Path(__file__).resolve().parents[2]
asset_path = root / 'modular/buildings/massing_alpha_chi_rho_0cb591a.blend'
gis_path = root / 'audit/alpha_chi_rho/sources/purdue_gis_FID775_alpha_chi_rho_2026-10-26.json'
out_path = root / 'audit/alpha_chi_rho_independent_grade/independent_probe.json'
gis_doc = json.loads(gis_path.read_text(encoding='utf-8'))
gis = gis_doc['features'][0]
attrs = gis['attributes']
ring = gis['geometry']['rings'][0]
origin_lat, origin_lon = 40.4274, -86.9137
projected = [((lon-origin_lon)*111412.84*math.cos(math.radians(origin_lat)), (lat-origin_lat)*111040.0) for lon,lat in ring[:-1]]

def area(poly):
    return abs(sum(poly[i][0]*poly[(i+1)%len(poly)][1]-poly[(i+1)%len(poly)][0]*poly[i][1] for i in range(len(poly)))/2)

def dist(a,b): return math.hypot(a[0]-b[0],a[1]-b[1])
col = bpy.data.collections.get('Asset_massing_alpha_chi_rho_0cb591a')
scene = bpy.data.scenes.get('Building_massing_alpha_chi_rho_0cb591a')
objects = list(col.all_objects) if col else []
mesh_objects = [o for o in objects if o.type=='MESH']
obj = mesh_objects[0] if len(mesh_objects)==1 else None
all_scene_objects = [o for o in scene.objects] if scene else []
source_vertex_nearest_errors=[]
model_points=[]
if obj:
    for v in obj.data.vertices:
        w=obj.matrix_world @ v.co
        model_points.append((float(w.x),float(w.y),float(w.z)))
    # Compare each source perimeter corner to the closest mesh vertex at ground Z.
    ground=[p for p in model_points if abs(p[2])<1e-5]
    source_vertex_nearest_errors=[min((dist(p,q[:2]) for q in ground),default=None) for p in projected]
    bounds=[[min(p[k] for p in model_points),max(p[k] for p in model_points)] for k in range(3)]
    materials=sorted({m.name for m in obj.data.materials if m})
    modifiers=[m.type for m in obj.modifiers]
else:
    bounds=None; materials=[]; modifiers=[]
images=[]
for img in bpy.data.images:
    if img.source=='FILE': images.append({'name':img.name,'filepath':img.filepath,'packed':bool(img.packed_file)})
all_asset_collections=[c.name for c in bpy.data.collections if c.name.startswith('Asset_')]
probe={
 'asset_path':str(asset_path),
 'asset_file_opens': bpy.data.filepath.endswith('massing_alpha_chi_rho_0cb591a.blend'),
 'scene_name':scene.name if scene else None,
 'expected_collection_present':col is not None,
 'asset_collections':all_asset_collections,
 'scene_object_count':len(all_scene_objects),
 'asset_object_count':len(objects),
 'mesh_object_count':len(mesh_objects),
 'asset_object_names':sorted(o.name for o in objects),
 'object_type':obj.type if obj else None,
 'mesh_vertices':len(obj.data.vertices) if obj else None,
 'mesh_polygons':len(obj.data.polygons) if obj else None,
 'material_names':materials,
 'modifiers':modifiers,
 'external_images':images,
 'bounds_world_m':bounds,
 'gis':{'feature_id':attrs.get('FID'),'building_name':attrs.get('BUILDING_N'),'abbreviation':attrs.get('BLDG_ABBR'),'address':attrs.get('ADDRESS'),'num_levels':attrs.get('NUM_LEVELS'),'extrution_raw':attrs.get('Extrution'),'elevation_raw':attrs.get('Elevation'),'source_crs':gis_doc.get('spatialReference',{}).get('wkid')},
 'gis_ring_count':len(projected),
 'gis_ring_area_project_approx_m2':area(projected),
 'gis_ring_bounds_world_m':[[min(p[k] for p in projected),max(p[k] for p in projected)] for k in range(2)],
 'source_ring_vertex_nearest_error_m':source_vertex_nearest_errors,
 'max_source_ring_vertex_nearest_error_m':max(source_vertex_nearest_errors,default=None),
 'source_ring_vertex_matching_is_independent_validation':False,
 'independent_survey_footprint_found':False,
}
out_path.write_text(json.dumps(probe,indent=2,ensure_ascii=False)+'\n',encoding='utf-8')
print('INDEPENDENT_PROBE='+json.dumps(probe,ensure_ascii=False))



