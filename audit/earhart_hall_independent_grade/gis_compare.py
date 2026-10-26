import bpy,json,math,hashlib,os
p=r'C:\Users\Tobin\Documents\Blender\PurdueMap\modular\buildings\massing_earhart_hall_0f14209.blend'
gis=r'C:\Users\Tobin\Documents\Blender\PurdueMap\audit\earhart_hall\sources\purdue_building_shapes_erht_2026-10-26.geojson'
out=r'C:\Users\Tobin\Documents\Blender\PurdueMap\audit\earhart_hall_independent_grade'
bpy.ops.wm.open_mainfile(filepath=p)
ob=bpy.data.objects['ERHT_Floor_00.00']; deps=bpy.context.evaluated_depsgraph_get(); ev=ob.evaluated_get(deps); me=ev.to_mesh()
a=[(float((ev.matrix_world@v.co).x),float((ev.matrix_world@v.co).y)) for v in me.vertices]; ev.to_mesh_clear()
feat=json.load(open(gis,encoding='utf8'))['features'][0]; ring=feat['geometry']['coordinates'][0]
# Project source WGS84 using the documented project approximation.
lat0,lon0=40.4274,-86.9137
b=[((lon-lon0)*111412.84*math.cos(math.radians(lat0)),(lat-lat0)*111040.0) for lon,lat in ring]
def point_segment(p,x,y):
 dx=y[0]-x[0];dy=y[1]-x[1]; den=dx*dx+dy*dy
 t=0 if den==0 else max(0,min(1,((p[0]-x[0])*dx+(p[1]-x[1])*dy)/den))
 return math.hypot(p[0]-(x[0]+t*dx),p[1]-(x[1]+t*dy))
def ring_dist(points,segments):
 return [min(point_segment(p,segments[i],segments[(i+1)%len(segments)]) for i in range(len(segments))) for p in points]
# simplify comparison: GIS has 108 vertices while wall/floor ring has 38 vertices. report direct vertex->segment error, symmetric.
ab=ring_dist(a,b);ba=ring_dist(b,a)
report={'source_url':'https://services.arcgis.com/uCvss3umN5nvK9wW/arcgis/rest/services/BuildingShapes/FeatureServer/0','provider':'Purdue University GIS ArcGIS FeatureServer','feature_id':feat['properties']['FID'],'building_abbr':feat['properties']['BLDG_ABBR'],'retrieval_date':'2026-10-26 (snapshot filename)','source_crs':'EPSG:4326','measurement_method':'independent vertex-to-segment distances after applying project local geographic approximation; raw source has 108 ring vertices, asset floor mesh has 38 vertices','conversion':'X=(longitude+86.9137)*111412.84*cos(radians(40.4274)); Y=(latitude-40.4274)*111040.0','asset_ring_vertices':len(a),'source_ring_vertices':len(b),'source_vertices_max_to_asset_segment_m':max(ba),'asset_vertices_max_to_source_segment_m':max(ab),'candidate_footprint_bounds_m':[[min(x for x,y in a),max(x for x,y in a)],[min(y for x,y in a),max(y for x,y in a)]],'source_footprint_bounds_m':[[min(x for x,y in b),max(x for x,y in b)],[min(y for x,y in b),max(y for x,y in b)]],'uncertainty':'Local projection is project approximation rather than surveyed CRS; simplified/unsimplified line comparison is a vertex-based check, not a continuous Hausdorff proof.'}
json.dump(report,open(os.path.join(out,'gis_footprint_comparison.json'),'w'),indent=2)
print(json.dumps(report,indent=2))
